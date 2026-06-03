"""Project generator: orchestrate directory creation, file copying, and template rendering."""
import shutil
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

    def _code_vars(self, chip_config: dict, use_freertos: bool = False,
                   use_rtt: bool = False) -> dict:
        """Map chip_config fields to template placeholder names."""
        if use_rtt:
            os_val = "3"
        elif use_freertos:
            os_val = "2"
        else:
            os_val = "0"
        cv = {
            "DEVICE_HEADER": chip_config.get("device_header", ""),
            "CHIP_FAMILY": chip_config.get("family", ""),
            "DEVICE_DEFINE": chip_config.get("device_define", ""),
            "DEBUG_USART": chip_config.get("debug_usart", "USART0"),
            "CONF_HEADER": chip_config.get("conf_header", ""),
            "SYSTEM_SUPPORT_OS": os_val,
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

    def _setup_rtt(self, output_dir: Path, chip_config: dict, cv: dict):
        """Copy RT-Thread Nano kernel, port files from SDK; render rtconfig.h and board.c."""
        rtt_cfg = chip_config.get("optional_libs", {}).get("rtt_nano", {})
        core_name = chip_config.get("core", "Cortex-M3")
        port_rel = rtt_cfg.get("port_map", {}).get(core_name, "libcpu/arm/cortex-m3")

        sdk_root = self._sdk.get_path("SDK_ROOT")
        rtt_sdk = self._sdk.resolve_sdk(sdk_root, rtt_cfg.get("sdk_subdir", "rt-thread"))
        if not rtt_sdk:
            raise FileNotFoundError(
                f"RT-Thread Nano SDK not found. Expected 'rt-thread*' under {sdk_root}.\n"
                f"Please download RT-Thread Nano and extract to the SDK directory.")

        sdk_base = Path(rtt_sdk)

        # Create RT-Thread directory structure
        rtt_dir = output_dir / "RT-Thread"
        rtt_dir.mkdir(exist_ok=True)

        # Copy kernel source files from src/
        for fname in rtt_cfg.get("core_files", []):
            src = sdk_base / "src" / fname
            if src.exists():
                (rtt_dir / fname).write_bytes(src.read_bytes())

        # Patch components.c: ARMCC V5 defines __CC_ARM, not __ARMCC_VERSION.
        # Two critical spots use this check:
        #   1. $Sub$$main hook (line ~139) — if missing, rtthread_startup()
        #      is never called, scheduler never starts.
        #   2. main_thread_entry() calls $Super$$main (line ~192) — if missing,
        #      the main thread never invokes user's main().
        # Both must also match __CC_ARM for ARMCC V5 compatibility.
        components_c = rtt_dir / "components.c"
        if components_c.exists():
            content = components_c.read_text(encoding="utf-8", errors="replace")
            content = content.replace(
                "#ifdef __ARMCC_VERSION",
                "#if defined(__ARMCC_VERSION) || defined(__CC_ARM)"
            )
            # The second occurrence is inside main_thread_entry, guards
            # $Super$$main() call for ARMCC. ARMCC V5 needs it too.
            content = content.replace(
                "#ifdef __ARMCC_VERSION",
                "#if defined(__ARMCC_VERSION) || defined(__CC_ARM)"
            )
            components_c.write_text(content, encoding="utf-8")

        # Copy headers from include/
        inc_src = sdk_base / "include"
        inc_dst = rtt_dir / "include"
        inc_dst.mkdir(exist_ok=True)
        if inc_src.is_dir():
            for h in inc_src.glob("*.h"):
                (inc_dst / h.name).write_bytes(h.read_bytes())

        # Copy port files (RVDS for Keil, cpuport.c is common)
        port_src = sdk_base / port_rel
        port_dst = rtt_dir / port_rel
        port_dst.mkdir(parents=True, exist_ok=True)
        if port_src.is_dir():
            for f in port_src.iterdir():
                if f.is_file() and f.name != "context_iar.S":
                    (port_dst / f.name).write_bytes(f.read_bytes())

        # Copy FinSH shell component
        finsh_src = sdk_base / "components" / "finsh"
        finsh_dst = rtt_dir / "finsh"
        if finsh_src.is_dir():
            finsh_dst.mkdir(exist_ok=True)
            for f in finsh_src.iterdir():
                if f.is_file():
                    (finsh_dst / f.name).write_bytes(f.read_bytes())

        # Render rtconfig.h
        config_tmpl = self._templates_dir / "rtt" / "rtconfig.h"
        if config_tmpl.exists():
            render(config_tmpl, inc_dst / "rtconfig.h", cv)

        # Render board.c (family-specific standard library adaptation)
        family_lower = chip_config.get("family", "").lower()
        board_tmpl = self._templates_dir / "rtt" / f"{family_lower}_board.c"
        user_dir = output_dir / "USER"
        if board_tmpl.exists():
            render(board_tmpl, user_dir / "board.c", cv)

        # Overwrite it.c and main.h with RT-Thread versions
        itc_tmpl = self._templates_dir / "rtt" / f"{family_lower}_it.c"
        if itc_tmpl.exists():
            render(itc_tmpl, user_dir / f"{family_lower}_it.c", cv)

        main_h_tmpl = self._templates_dir / "rtt" / f"{family_lower}_main.h"
        if main_h_tmpl.exists():
            render(main_h_tmpl, user_dir / "main.h", cv)

    def generate(self, family_name: str, chip_name: str, chip_config: dict,
                 project_name: str, output_dir: Path, template_type: str,
                 optional_libs: list[str] | None = None,
                 build_system: str = "keil"):
        """Generate a complete project.

        Args:
            build_system: "keil" (default), "gcc", or "both"
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        family_lower = family_name.lower()

        use_freertos = optional_libs and "freertos" in optional_libs
        use_rtt = optional_libs and "rtt_nano" in optional_libs
        use_gcc = build_system in ("gcc", "both")
        use_keil = build_system in ("keil", "both")
        cv = self._code_vars(chip_config, use_freertos, use_rtt)

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
        skip_files.update(["linker.ld", "CMakeLists.txt"])  # handled by _generate_gcc()
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

        # 7. Setup RTOS if enabled (after SDK templates to overwrite it.c)
        if use_freertos:
            self._setup_freertos(output_dir, chip_config, cv)
            if use_gcc:
                self._gcc_freertos_port(output_dir, chip_config)
        if use_rtt:
            self._setup_rtt(output_dir, chip_config, cv)

        # 8. Render main.c
        if use_rtt:
            main_template = self._templates_dir / family_lower / "rtt" / template_type / "main.c"
        elif use_freertos:
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

        # 9. Generate GCC/CMake output
        if use_gcc:
            cmake_vars = self._build_cmake_vars(project_name, chip_name, chip_config, use_freertos, use_rtt)
            self._generate_gcc(output_dir, project_name, chip_config, cmake_vars)

        # 10. Generate Keil .uvprojx from template
        if use_keil:
            uvprojx_template = self._templates_dir / family_lower / "uvprojx_template.xml"
            if uvprojx_template.exists():
                variables = self._build_uvprojx_vars(project_name, chip_name, chip_config, output_dir, use_freertos, use_rtt)
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

    def _build_cmake_vars(self, project_name: str, chip_name: str, chip_config: dict,
                           use_freertos: bool = False, use_rtt: bool = False) -> dict:
        """Build template variables for CMakeLists.txt and linker.ld generation."""
        config = chip_config.get("config", {})
        cpu_type = config.get("cpu_type", "Cortex-M3")
        cpu_flags = config.get("cpu_flags", "")
        ram_kb = chip_config.get("ram_kb", 20)
        flash_kb = chip_config.get("flash_kb", 64)
        startup_file = chip_config.get("startup", "")
        device_define = chip_config.get("define", "")
        device_path = chip_config.get("cmsis", {}).get("device_path", "")

        gcc_cpu = cpu_type.lower()
        fpu_flags = ""
        if cpu_flags in ("FPU2", "FPU"):
            fpu_flags = "-mfloat-abi=hard -mfpu=fpv4-sp-d16"
        else:
            fpu_flags = "-mfloat-abi=soft"

        hxtal_hz = config.get("hxtal_hz", 0)
        hxtal_defines = ""
        if hxtal_hz > 0:
            family = chip_config.get("family", "")
            if "GD32" in family:
                hxtal_defines = f"HXTAL_VALUE={hxtal_hz}"
            elif "STM32" in family:
                hxtal_defines = f"HSE_VALUE={hxtal_hz}"

        # TCMRAM for Cortex-M4 (GD32F4xx has 64KB at 0x10000000)
        is_m4 = "Cortex-M4" in cpu_type
        tcmram_memory = "  TCMRAM (xrw)   : ORIGIN = 0x10000000, LENGTH = 64K\n" if is_m4 else ""
        tcmram_section = (
            '  _sitcmram = LOADADDR(.tcmram);\n'
            '  .tcmram :\n'
            '  {\n'
            '    . = ALIGN(4);\n'
            '    .stcmram = .;\n'
            '    *(.tcmram)\n'
            '    *(.tcmram*)\n'
            '    . = ALIGN(4);\n'
            '    _etcmram = .;\n'
            '  } > TCMRAM AT> FLASH\n'
        ) if is_m4 else ""

        variables = {
            "PROJECT_NAME": project_name,
            "MCPU": gcc_cpu,
            "FPU_FLAGS": fpu_flags,
            "DEVICE_DEFINE": device_define,
            "HXTAL_DEFINES": hxtal_defines,
            "DEVICE_INC_REL": device_path,
            "STARTUP_FILE": startup_file,
            "LINKER_SCRIPT": f"{project_name}.ld",
            "RAM_START": config.get("ram_start", "0x20000000"),
            "RAM_SIZE": self._kb_to_hex(ram_kb),
            "ROM_START": config.get("rom_start", "0x08000000"),
            "ROM_SIZE": self._kb_to_hex(flash_kb),
            "TCMRAM_MEMORY": tcmram_memory,
            "TCMRAM_SECTION": tcmram_section,
        }

        if use_freertos:
            fr_cfg = chip_config.get("optional_libs", {}).get("freertos", {})
            core_name = chip_config.get("core", "Cortex-M3")
            port_rel = fr_cfg.get("port_map", {}).get(core_name, "portable/RVDS/ARM_CM3")
            gcc_port_rel = port_rel.replace("/RVDS/", "/GCC/")
            heap = fr_cfg.get("heap", "heap_4.c")
            core_files = fr_cfg.get("core_files", [])

            srcs = [f'"FreeRTOS/{f}"' for f in core_files]
            srcs.append(f'"FreeRTOS/{gcc_port_rel}/port.c"')
            srcs.append(f'"FreeRTOS/portable/MemMang/{heap}"')
            variables["FREERTOS_CMAKE_SOURCES"] = "\n    ".join(srcs)
            variables["FREERTOS_CMAKE_INCLUDES"] = (
                f"${{CMAKE_CURRENT_SOURCE_DIR}}/FreeRTOS/include\n"
                f"    ${{CMAKE_CURRENT_SOURCE_DIR}}/FreeRTOS/{gcc_port_rel}"
            )
        else:
            variables["FREERTOS_CMAKE_SOURCES"] = ""
            variables["FREERTOS_CMAKE_INCLUDES"] = ""

        if use_rtt:
            rtt_cfg = chip_config.get("optional_libs", {}).get("rtt_nano", {})
            core_name = chip_config.get("core", "Cortex-M3")
            port_rel = rtt_cfg.get("port_map", {}).get(core_name, "libcpu/arm/cortex-m3")
            core_files = rtt_cfg.get("core_files", [])
            srcs = [f'"RT-Thread/{f}"' for f in core_files]
            srcs.append(f'"RT-Thread/{port_rel}/cpuport.c"')
            srcs.append(f'"RT-Thread/{port_rel}/context_gcc.S"')
            variables["RTT_CMAKE_SOURCES"] = "\n    ".join(srcs)
            variables["RTT_CMAKE_INCLUDES"] = (
                f"${{CMAKE_CURRENT_SOURCE_DIR}}/RT-Thread/include\n"
                f"    ${{CMAKE_CURRENT_SOURCE_DIR}}/RT-Thread/{port_rel}"
            )
        else:
            variables["RTT_CMAKE_SOURCES"] = ""
            variables["RTT_CMAKE_INCLUDES"] = ""

        return variables

    def _generate_gcc(self, output_dir: Path, project_name: str, chip_config: dict,
                       variables: dict):
        """Generate CMakeLists.txt, linker script, and ensure GCC startup file exists."""
        # Render linker script (GD32 and STM32 use different vector section names/symbols)
        family = chip_config.get("family", "")
        ld_name = "linker_gd32.ld" if "GD32" in family else "linker_stm32.ld"
        ld_template = self._templates_dir / "common" / ld_name
        if ld_template.exists():
            render(ld_template, output_dir / f"{project_name}.ld", variables)

        # Generate filtered source file lists (SDK vs user code, dedup by name)
        exclude_fwlib = set(chip_config.get("fwlib_exclude", []))
        sdk_dirs = {"CMSIS", "FIRMWARE/Source"}
        sdk_sources = []
        user_sources = []
        seen = set()
        for d, pattern in [("CMSIS", "**/*.c"), ("FIRMWARE/Source", "*.c"),
                           ("SYSTEM", "**/*.c"), ("USER", "*.c"),
                           ("APP", "*.c"), ("DRIVER", "*.c"), ("HARDWARE", "*.c")]:
            src_dir = output_dir / d
            if src_dir.is_dir():
                for f in sorted(src_dir.glob(pattern)):
                    if f.name not in exclude_fwlib and f.name not in seen:
                        seen.add(f.name)
                        rel = f.relative_to(output_dir).as_posix()
                        if d in sdk_dirs:
                            sdk_sources.append(f"    {rel}")
                        else:
                            user_sources.append(f"    {rel}")
        variables["SDK_SOURCES"] = "\n".join(sdk_sources)
        variables["USER_SOURCES"] = "\n".join(user_sources)

        # Render CMakeLists.txt
        cmake_template = self._templates_dir / "common" / "CMakeLists.txt"
        if cmake_template.exists():
            render(cmake_template, output_dir / "CMakeLists.txt", variables)

        # GCC startup: SDK's copy_firmware already copies to STARTUP/ if SDK has GCC dir.
        # If missing, try to find from GD32 Embedded Builder in SDK root.
        startup_file = variables["STARTUP_FILE"]
        startup_dir = output_dir / "STARTUP"
        startup_dir.mkdir(parents=True, exist_ok=True)
        target = startup_dir / startup_file
        if not target.exists():
            self._resolve_gcc_startup_from_sdk(output_dir, chip_config, startup_file)

        if not target.exists():
            family = chip_config.get("family", "")
            vendor = chip_config.get("vendor", "")
            if "GD32" in family:
                download = (
                    f"Download 'GD32 Embedded Builder' from gigadevice.com:\n"
                    f"  https://www.gd32mcu.com/en/download?kw=GD32+Embedded+Builder\n"
                    f"After installation, copy the GD32EmbeddedBuilder folder to:\n"
                    f"  {self._sdk.get_path('SDK_ROOT') or 'your SDK root directory'}"
                )
            elif "STM32" in family:
                download = (
                    f"The STM32 standard peripheral library should include GCC startup\n"
                    f"files under 'startup/gcc_ride7/' or 'TrueSTUDIO/'.\n"
                    f"Make sure you have the full SPL package, not just CMSIS."
                )
            else:
                download = "Please ensure your SDK package includes GCC startup files."
            raise FileNotFoundError(
                f"GCC startup file '{startup_file}' not found for {family}.\n"
                f"{download}")

    def _resolve_gcc_startup_from_sdk(self, output_dir: Path, chip_config: dict,
                                        startup_file: str):
        """Search SDK root for GCC startup file (including GD32 Embedded Builder plugins)."""
        sdk_root = Path(self._sdk.get_path("SDK_ROOT")) if self._sdk.get_path("SDK_ROOT") else None
        if not sdk_root or not sdk_root.is_dir():
            return

        # Search GD32 Embedded Builder (recursive under any GD32EmbeddedBuilder* dir)
        for ext in (startup_file, startup_file.replace(".s", ".S")):
            for eb_dir in sdk_root.glob("GD32EmbeddedBuilder*"):
                if eb_dir.is_dir():
                    for match in eb_dir.rglob(f"gcc_startup/{ext}"):
                        target = output_dir / "STARTUP" / startup_file
                        target.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(match, target)
                        return

        # Broader SDK-wide search for GCC startup in gcc dirs
        base_name = Path(startup_file).stem
        for ext in [".S", ".s"]:
            for gcc_dir_pattern in [
                f"**/Source/GCC/{base_name}{ext}",
                f"**/startup/gcc_ride7/{base_name}{ext}",
                f"**/startup/TrueSTUDIO/{base_name}{ext}",
            ]:
                matches = list(sdk_root.glob(gcc_dir_pattern))
                for m in matches:
                    if "/IAR/" not in str(m) and "/ARM/" not in str(m):
                        target = output_dir / "STARTUP" / startup_file
                        target.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(m, target)
                        return

    def _gcc_freertos_port(self, output_dir: Path, chip_config: dict):
        """Copy GCC FreeRTOS port files (portable/GCC/ instead of portable/RVDS/)."""
        fr_cfg = chip_config.get("optional_libs", {}).get("freertos", {})
        core_name = chip_config.get("core", "Cortex-M3")
        port_rel = fr_cfg.get("port_map", {}).get(core_name, "portable/RVDS/ARM_CM3")
        gcc_port_rel = port_rel.replace("/RVDS/", "/GCC/")

        sdk_root = self._sdk.get_path("SDK_ROOT")
        freertos_sdk = self._sdk.resolve_sdk(sdk_root, fr_cfg.get("sdk_subdir", "FreeRTOS"))
        if not freertos_sdk:
            return

        gcc_port_src = Path(freertos_sdk) / gcc_port_rel
        gcc_port_dst = output_dir / "FreeRTOS" / gcc_port_rel
        if gcc_port_src.is_dir():
            gcc_port_dst.mkdir(parents=True, exist_ok=True)
            for f in gcc_port_src.iterdir():
                if f.is_file():
                    (gcc_port_dst / f.name).write_bytes(f.read_bytes())
        """Copy GCC FreeRTOS port files (separate from ARMCC/RVDS port)."""
        fr_cfg = chip_config.get("optional_libs", {}).get("freertos", {})
        core_name = chip_config.get("core", "Cortex-M3")
        port_rel = fr_cfg.get("port_map", {}).get(core_name, "portable/RVDS/ARM_CM3")
        gcc_port_rel = port_rel.replace("/RVDS/", "/GCC/")

        sdk_root = self._sdk.get_path("SDK_ROOT")
        freertos_sdk = self._sdk.resolve_sdk(sdk_root, fr_cfg.get("sdk_subdir", "FreeRTOS"))
        if not freertos_sdk:
            return

        gcc_port_src = Path(freertos_sdk) / gcc_port_rel
        gcc_port_dst = output_dir / "FreeRTOS" / gcc_port_rel
        if gcc_port_src.is_dir():
            gcc_port_dst.mkdir(parents=True, exist_ok=True)
            for f in gcc_port_src.iterdir():
                if f.is_file():
                    (gcc_port_dst / f.name).write_bytes(f.read_bytes())

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

    @staticmethod
    def _rtt_groups_xml(chip_config: dict) -> str:
        """Generate RT-Thread CORE and PORT group XML for Keil uvprojx."""
        rtt_cfg = chip_config.get("optional_libs", {}).get("rtt_nano", {})
        core_name = chip_config.get("core", "Cortex-M3")
        port_rel = rtt_cfg.get("port_map", {}).get(core_name, "libcpu/arm/cortex-m3")
        port_rel_win = port_rel.replace("/", "\\\\")
        core_files = rtt_cfg.get("core_files", [])

        lines = []
        # RT-Thread_CORE group
        lines.append('<Group><GroupName>RT-Thread_CORE</GroupName><Files>')
        for f in core_files:
            lines.append(
                f'<File><FileName>{f}</FileName><FileType>1</FileType>'
                f'<FilePath>..\\RT-Thread\\{f}</FilePath></File>'
            )
        lines.append('</Files></Group>')

        # RT-Thread_PORT group
        lines.append('<Group><GroupName>RT-Thread_PORT</GroupName><Files>')
        lines.append(
            f'<File><FileName>cpuport.c</FileName><FileType>1</FileType>'
            f'<FilePath>..\\RT-Thread\\{port_rel_win}\\cpuport.c</FilePath></File>'
        )
        lines.append(
            f'<File><FileName>context_rvds.S</FileName><FileType>2</FileType>'
            f'<FilePath>..\\RT-Thread\\{port_rel_win}\\context_rvds.S</FilePath></File>'
        )
        lines.append(
            f'<File><FileName>board.c</FileName><FileType>1</FileType>'
            f'<FilePath>..\\USER\\board.c</FilePath></File>'
        )
        lines.append('</Files></Group>')

        # FinSH disabled by default (ARMCC V5 C90 incompatible).
        # Uncomment the group below if using ARMCC V6 or GCC + RT_USING_FINSH.
        # lines.append('<Group><GroupName>RT-Thread_FINISH</GroupName><Files>')
        # ...

        return "\n".join(lines)

    @staticmethod
    def _rtt_includes(chip_config: dict) -> str:
        """Generate additional RT-Thread include paths."""
        core_name = chip_config.get("core", "Cortex-M3")
        rtt_cfg = chip_config.get("optional_libs", {}).get("rtt_nano", {})
        port_rel = rtt_cfg.get("port_map", {}).get(core_name, "libcpu/arm/cortex-m3")
        port_rel_win = port_rel.replace("/", "\\\\")
        return f";..\\\\RT-Thread\\\\include;..\\\\RT-Thread\\\\{port_rel_win};..\\\\RT-Thread\\\\finsh"

    def _build_uvprojx_vars(self, project_name: str, chip_name: str, chip_config: dict,
                            output_dir: Path, use_freertos: bool = False,
                            use_rtt: bool = False) -> dict:
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
            # Microlib must be OFF for RT-Thread's $Sub$$main/$Super$$main linker mechanism
            "USE_MICROLIB": "0" if use_rtt else "1",
        }

        if use_freertos:
            variables["FREERTOS_GROUPS"] = self._freertos_groups_xml(chip_config)
            variables["FREERTOS_INCLUDES"] = self._freertos_includes(chip_config)
        else:
            variables["FREERTOS_GROUPS"] = ""
            variables["FREERTOS_INCLUDES"] = ""

        if use_rtt:
            variables["RTT_GROUPS"] = self._rtt_groups_xml(chip_config)
            variables["RTT_INCLUDES"] = self._rtt_includes(chip_config)
        else:
            variables["RTT_GROUPS"] = ""
            variables["RTT_INCLUDES"] = ""

        return variables
