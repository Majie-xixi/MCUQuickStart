"""Project generator: orchestrate directory creation, file copying, and template rendering."""
from pathlib import Path
from src.core.template_engine import render
from src.core.sdk_manager import SDKManager


class ProjectGenerator:
    def __init__(self, templates_dir: Path, sdk_manager: SDKManager):
        self._templates_dir = templates_dir
        self._sdk = sdk_manager

    def _copy_sdk_templates(self, sdk_root: Path, user_dir: Path, chip_config: dict):
        """Copy chip-specific USER files from SDK Template directory (as-is, no rendering)."""
        cmsis = chip_config.get("cmsis", {})
        template_rel = cmsis.get("template_dir", "Template")
        template_dir = sdk_root / template_rel
        if not template_dir.is_dir():
            dirname = Path(template_rel).name
            matches = [d for d in sdk_root.rglob(dirname) if d.is_dir()]
            template_dir = matches[0] if matches else None
        if not template_dir or not template_dir.is_dir():
            return

        for src_file in template_dir.iterdir():
            if src_file.suffix in (".c", ".h") and src_file.name != "main.c":
                content = src_file.read_text(encoding="utf-8", errors="replace")
                sdk_patterns = ["led_spark", "TimingDelay"]
                lines = [l for l in content.splitlines(True)
                         if not any(p in l for p in sdk_patterns)]
                content = "".join(lines)
                (user_dir / src_file.name).write_text(content, encoding="utf-8")

    def _code_vars(self, chip_config: dict, use_freertos: bool = False) -> dict:
        """Map chip_config fields to template placeholder names."""
        cv = {
            "DEVICE_HEADER": chip_config.get("device_header", ""),
            "CHIP_FAMILY": chip_config.get("family", ""),
            "DEVICE_DEFINE": chip_config.get("device_define", ""),
            "DEBUG_USART": chip_config.get("debug_usart", "USART0"),
            "CONF_HEADER": chip_config.get("conf_header", ""),
            "SYSTEM_SUPPORT_OS": "2" if use_freertos else "0",
        }
        if use_freertos:
            freertos_cfg = chip_config.get("optional_libs", {}).get("freertos", {})
            div = freertos_cfg.get("systick_clock_div", 1)
            if div > 1:
                cv["SYSTICK_CLOCK_HZ_DEFINE"] = f"#define configSYSTICK_CLOCK_HZ    (SystemCoreClock / {div})"
            else:
                cv["SYSTICK_CLOCK_HZ_DEFINE"] = ""
        else:
            cv["SYSTICK_CLOCK_HZ_DEFINE"] = ""
        return cv

    def _setup_freertos(self, output_dir: Path, chip_config: dict, cv: dict):
        """Copy FreeRTOS kernel, port and heap files from SDK; render FreeRTOSConfig.h."""
        freertos_cfg = chip_config.get("optional_libs", {}).get("freertos", {})
        core_name = chip_config.get("core", "Cortex-M3")
        port_rel = freertos_cfg.get("port_map", {}).get(core_name, "portable/RVDS/ARM_CM3")

        # Resolve FreeRTOS SDK
        sdk_root = self._sdk.get_path("SDK_ROOT")
        freertos_sdk = self._sdk.resolve_sdk(sdk_root, freertos_cfg.get("sdk_subdir", "FreeRTOS"))
        if not freertos_sdk:
            raise FileNotFoundError(
                f"FreeRTOS SDK not found. Expected 'FreeRTOS*' under {sdk_root}.\n"
                f"Please download FreeRTOS and extract to the SDK directory.")

        sdk_base = Path(freertos_sdk)

        # Create FreeRTOS directory structure
        freertos_dir = output_dir / "FreeRTOS"
        freertos_dir.mkdir(exist_ok=True)

        # Copy kernel source files (root .c files)
        for fname in freertos_cfg.get("core_files", []):
            src = sdk_base / fname
            if src.exists():
                (freertos_dir / fname).write_bytes(src.read_bytes())

        # Copy headers from include/
        inc_src = sdk_base / "include"
        inc_dst = freertos_dir / "include"
        inc_dst.mkdir(exist_ok=True)
        if inc_src.is_dir():
            for h in inc_src.glob("*.h"):
                (inc_dst / h.name).write_bytes(h.read_bytes())

        # Copy port files
        port_src = sdk_base / port_rel
        port_dst = freertos_dir / port_rel
        port_dst.mkdir(parents=True, exist_ok=True)
        if port_src.is_dir():
            for f in port_src.iterdir():
                if f.is_file():
                    (port_dst / f.name).write_bytes(f.read_bytes())

        # Copy heap
        heap_name = freertos_cfg.get("heap", "heap_4.c")
        heap_src = sdk_base / "portable" / "MemMang" / heap_name
        heap_dst = freertos_dir / "portable" / "MemMang"
        heap_dst.mkdir(parents=True, exist_ok=True)
        if heap_src.exists():
            (heap_dst / heap_name).write_bytes(heap_src.read_bytes())

        # Render FreeRTOSConfig.h
        config_tmpl = self._templates_dir / "freertos" / "FreeRTOSConfig.h"
        if config_tmpl.exists():
            render(config_tmpl, inc_dst / "FreeRTOSConfig.h", cv)

        # Overwrite it.c and main.h with FreeRTOS versions
        family_lower = chip_config.get("family", "").lower()
        user_dir = output_dir / "USER"

        itc_tmpl = self._templates_dir / "freertos" / f"{family_lower}_it.c"
        if itc_tmpl.exists():
            render(itc_tmpl, user_dir / f"{family_lower}_it.c", cv)

        main_h_tmpl = self._templates_dir / "freertos" / f"{family_lower}_main.h"
        if main_h_tmpl.exists():
            render(main_h_tmpl, user_dir / "main.h", cv)

    def generate(self, family_name: str, chip_name: str, chip_config: dict,
                 project_name: str, output_dir: Path, template_type: str,
                 optional_libs: list[str] | None = None):
        """Generate a complete project."""
        output_dir.mkdir(parents=True, exist_ok=True)
        family_lower = family_name.lower()

        use_freertos = optional_libs and "freertos" in optional_libs
        cv = self._code_vars(chip_config, use_freertos)

        # 1. Copy firmware from SDK
        sdk_key = chip_config.get("sdk_key", chip_config.get("vendor", ""))
        sdk_root = self._sdk.get_path(sdk_key)
        sdk_path = self._sdk.resolve_sdk(sdk_root, chip_config.get("sdk_subdir", "")) if sdk_root else None
        if not sdk_path:
            subdir = chip_config.get("sdk_subdir", "unknown")
            raise FileNotFoundError(
                f"SDK package not found. Expected '{subdir}*' under {sdk_root}.\n"
                f"Please download the {chip_config.get('family', '')} firmware library package.")
        self._sdk.copy_firmware(Path(sdk_path), chip_config, output_dir)

        # 2. Create empty user directories
        for d in ["APP", "DRIVER", "HARDWARE"]:
            (output_dir / d).mkdir(exist_ok=True)

        # 3. Copy system templates into correct subdirectories
        sys_tmpl = self._templates_dir / "system"
        delay_dir = output_dir / "SYSTEM" / "delay"
        delay_dir.mkdir(parents=True, exist_ok=True)
        sys_dir = output_dir / "SYSTEM" / "sys"
        sys_dir.mkdir(parents=True, exist_ok=True)

        for src_name, dst_dir in [
            ("delay.c", delay_dir), ("delay.h", delay_dir),
            ("sysconfig.c", sys_dir), ("sysconfig.h", sys_dir),
        ]:
            src = sys_tmpl / src_name
            if src.exists():
                render(src, dst_dir / src_name, cv)

        # 4. Copy common USER templates
        user_dir = output_dir / "USER"
        user_dir.mkdir(parents=True, exist_ok=True)
        skip_files = set(chip_config.get("common_skip", []))
        global_common = self._templates_dir / "common"
        if global_common.exists():
            for src_file in global_common.iterdir():
                if src_file.is_file() and src_file.name not in skip_files:
                    render(src_file, user_dir / src_file.name, cv)

        # 5. Copy chip-specific USER files from SDK Template directory
        if sdk_path:
            self._copy_sdk_templates(Path(sdk_path), user_dir, chip_config)

        # 6. Patch system clock after ALL SDK files are copied (both CMSIS and USER copies)
        config = chip_config.get("config", {})
        if "hxtal_hz" in config:
            self._patch_system_clock(output_dir, family_lower, config["hxtal_hz"])

        # 7. Setup FreeRTOS if enabled (after SDK templates to overwrite it.c)
        if use_freertos:
            self._setup_freertos(output_dir, chip_config, cv)

        # 7. Render main.c
        if use_freertos:
            main_template = self._templates_dir / family_lower / "freertos" / template_type / "main.c"
        else:
            main_template = self._templates_dir / family_lower / template_type / "main.c"

        if main_template.exists():
            render(main_template, user_dir / "main.c", cv)
            main_content = (user_dir / "main.c").read_text(encoding="utf-8", errors="replace")
            if "fputc" in main_content or "_write" in main_content:
                rt = user_dir / "retarget_printf.c"
                if rt.exists():
                    rt.unlink()

        # 8. Generate .uvprojx from template
        uvprojx_template = self._templates_dir / family_lower / "uvprojx_template.xml"
        if uvprojx_template.exists():
            variables = self._build_uvprojx_vars(project_name, chip_name, chip_config, output_dir, use_freertos)
            mdk_dir = output_dir / "MDK-ARM"
            mdk_dir.mkdir(parents=True, exist_ok=True)
            render(uvprojx_template, mdk_dir / f"{project_name}.uvprojx", variables)

    @staticmethod
    def _patch_system_clock(output_dir: Path, family_lower: str, hxtal_hz: int):
        """Fix system_gd32f4xx.c / system_gd32f10x.c clock define to match actual HXTAL."""
        system_files = list(output_dir.rglob(f"system_{family_lower}.c"))
        if not system_files:
            return
        hxtal_mhz = hxtal_hz // 1000000
        target_suffix = f"{hxtal_mhz}M"
        import re
        for system_file in system_files:
            content = system_file.read_text(encoding="utf-8", errors="replace")
            # Fix GD32F4xx: __SYSTEM_CLOCK_*_PLL_25M_HXTAL → _PLL_8M_HXTAL
            content = re.sub(
                r'^(#define\s+__SYSTEM_CLOCK_\d+M_PLL)_\d+M(_HXTAL\s+)',
                rf'\1_{target_suffix}\2',
                content, flags=re.MULTILINE)
            # Fix STM32F4xx: PLL_M value must match HSE crystal frequency
            content = re.sub(
                r'^(\s*#define\s+PLL_M\s+)\d+',
                rf'\g<1>{hxtal_mhz}',
                content, flags=re.MULTILINE)
            system_file.write_text(content, encoding="utf-8")

    @staticmethod
    def _kb_to_hex(kb: int) -> str:
        return f"0x{int(kb) * 1024:X}"

    @staticmethod
    def _scan_fwlib_files(project_dir: Path, exclude: list[str] | None = None) -> str:
        """Scan FIRMWARE/ for actual .c and .h files, return FWLIB group XML."""
        exclude_set = set(exclude or [])
        lines = []
        for folder, ftype in [("Source", 1), ("Include", 5)]:
            fw_dir = project_dir / "FIRMWARE" / folder
            if fw_dir.is_dir():
                for f in sorted(fw_dir.iterdir()):
                    if f.is_file() and f.suffix in (".c", ".h") and f.name not in exclude_set:
                        lines.append(
                            f'            <File>\n'
                            f'              <FileName>{f.name}</FileName>\n'
                            f'              <FileType>{ftype}</FileType>\n'
                            f'              <FilePath>..\\FIRMWARE\\{folder}\\{f.name}</FilePath>\n'
                            f'            </File>'
                        )
        return "\n".join(lines)

    @staticmethod
    def _freertos_groups_xml(chip_config: dict) -> str:
        """Generate FreeRTOS_CORE and FreeRTOS_PORT group XML."""
        freertos_cfg = chip_config.get("optional_libs", {}).get("freertos", {})
        core_name = chip_config.get("core", "Cortex-M3")
        port_rel = freertos_cfg.get("port_map", {}).get(core_name, "portable/RVDS/ARM_CM3")
        port_rel_win = port_rel.replace("/", "\\\\")
        heap = freertos_cfg.get("heap", "heap_4.c")
        core_files = freertos_cfg.get("core_files", [])

        lines = []
        # FreeRTOS_CORE group
        lines.append('<Group><GroupName>FreeRTOS_CORE</GroupName><Files>')
        for f in core_files:
            lines.append(
                f'<File><FileName>{f}</FileName><FileType>1</FileType>'
                f'<FilePath>..\\FreeRTOS\\{f}</FilePath></File>'
            )
        lines.append('</Files></Group>')

        # FreeRTOS_PORT group
        lines.append('<Group><GroupName>FreeRTOS_PORT</GroupName><Files>')
        lines.append(
            f'<File><FileName>port.c</FileName><FileType>1</FileType>'
            f'<FilePath>..\\FreeRTOS\\{port_rel_win}\\port.c</FilePath></File>'
        )
        lines.append(
            f'<File><FileName>{heap}</FileName><FileType>1</FileType>'
            f'<FilePath>..\\FreeRTOS\\portable\\MemMang\\{heap}</FilePath></File>'
        )
        lines.append('</Files></Group>')

        return "\n".join(lines)

    @staticmethod
    def _freertos_includes(chip_config: dict) -> str:
        """Generate additional FreeRTOS include paths."""
        core_name = chip_config.get("core", "Cortex-M3")
        freertos_cfg = chip_config.get("optional_libs", {}).get("freertos", {})
        port_rel = freertos_cfg.get("port_map", {}).get(core_name, "portable/RVDS/ARM_CM3")
        port_rel_win = port_rel.replace("/", "\\\\")
        return f";..\\\\FreeRTOS\\\\include;..\\\\FreeRTOS\\\\{port_rel_win}"

    def _build_uvprojx_vars(self, project_name: str, chip_name: str, chip_config: dict,
                            output_dir: Path, use_freertos: bool = False) -> dict:
        """Build template variables map for uvprojx generation."""
        config = chip_config.get("config", {})
        startup = chip_config.get("startup", "")
        flash_driver = chip_config.get("flash_driver", "")
        device_define = chip_config.get("define", "")
        ram_kb = chip_config.get("ram_kb", 20)
        flash_kb = chip_config.get("flash_kb", 64)
        ram_start = int(config.get("ram_start", "0x20000000"), 16)
        rom_start = int(config.get("rom_start", "0x08000000"), 16)

        # HXTAL compiler define (overrides SDK header default)
        hxtal_hz = config.get("hxtal_hz", 0)
        hxtal_defines = ""
        if hxtal_hz > 0:
            family = chip_config.get("family", "")
            if "GD32" in family:
                hxtal_defines = f",HXTAL_VALUE={hxtal_hz}"
            elif "STM32" in family:
                hxtal_defines = f",HSE_VALUE={hxtal_hz}"

        variables = {
            "PROJECT_NAME": project_name,
            "CHIP": chip_config.get("device", chip_name),
            "DEVICE": chip_config.get("device", chip_name),
            "DEVICE_HEADER_BARE": chip_config.get("device_header", "").replace(".h", ""),
            "DEVICE_DEFINE": device_define,
            "CPU_TYPE": config.get("cpu_type", ""),
            "RAM_START": config.get("ram_start", ""),
            "RAM_SIZE": self._kb_to_hex(ram_kb),
            "RAM_START_END": f"0x{ram_start + ram_kb * 1024 - 1:X}",
            "ROM_START": config.get("rom_start", ""),
            "ROM_SIZE": self._kb_to_hex(flash_kb),
            "ROM_START_END": f"0x{rom_start + flash_kb * 1024 - 1:X}",
            "ROM_SIZE_KB": self._kb_to_hex(flash_kb),
            "CLOCK": config.get("clock", ""),
            "CPU_FLAGS": config.get("cpu_flags", ""),
            "SIM_DLL": config.get("sim_dll", ""),
            "TARGET_DLL": config.get("target_dll", ""),
            "SIM_DLG_DLL": config.get("sim_dlg_dll", ""),
            "TARGET_DLG_DLL": config.get("target_dlg_dll", ""),
            "DLG_ARGUMENTS": config.get("dlg_arguments", ""),
            "VENDOR": chip_config.get("vendor", ""),
            "PACK_ID": chip_config.get("pack_id", ""),
            "STARTUP_FILE": startup,
            "FLASH_DRIVER": flash_driver,
            "FWLIB_FILES": self._scan_fwlib_files(output_dir, chip_config.get("fwlib_exclude")),
            "HXTAL_DEFINES": hxtal_defines,
        }

        if use_freertos:
            variables["FREERTOS_GROUPS"] = self._freertos_groups_xml(chip_config)
            variables["FREERTOS_INCLUDES"] = self._freertos_includes(chip_config)
        else:
            variables["FREERTOS_GROUPS"] = ""
            variables["FREERTOS_INCLUDES"] = ""

        return variables
