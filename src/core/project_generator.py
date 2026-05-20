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
            # Fallback: recursive search
            dirname = Path(template_rel).name
            matches = [d for d in sdk_root.rglob(dirname) if d.is_dir()]
            template_dir = matches[0] if matches else None
        if not template_dir or not template_dir.is_dir():
            return

        for src_file in template_dir.iterdir():
            if src_file.suffix in (".c", ".h") and src_file.name != "main.c":
                content = src_file.read_text(encoding="utf-8", errors="replace")
                # Remove SDK example code not present in our minimal templates
                lines = [l for l in content.splitlines(True) if "led_spark" not in l]
                content = "".join(lines)
                (user_dir / src_file.name).write_text(content, encoding="utf-8")

    def _code_vars(self, chip_config: dict) -> dict:
        """Map chip_config fields to template placeholder names."""
        return {
            "DEVICE_HEADER": chip_config.get("device_header", ""),
            "CHIP_FAMILY": chip_config.get("family", ""),
            "DEVICE_DEFINE": chip_config.get("device_define", ""),
            "DEBUG_USART": chip_config.get("debug_usart", "USART0"),
            "CONF_HEADER": chip_config.get("conf_header", ""),
        }

    def generate(self, family_name: str, chip_name: str, chip_config: dict,
                 project_name: str, output_dir: Path, template_type: str):
        """Generate a complete project."""
        output_dir.mkdir(parents=True, exist_ok=True)
        family_lower = family_name.lower()
        cv = self._code_vars(chip_config)

        # 1. Copy firmware from SDK — resolve actual SDK dir from base root
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

        # 4. Copy our custom USER templates (debug_print, retarget_printf, RTE_Components)
        user_dir = output_dir / "USER"
        user_dir.mkdir(parents=True, exist_ok=True)
        skip_files = set(chip_config.get("common_skip", []))
        global_common = self._templates_dir / "common"
        if global_common.exists():
            for src_file in global_common.iterdir():
                if src_file.is_file() and src_file.name not in skip_files:
                    render(src_file, user_dir / src_file.name, cv)

        # 5. Copy chip-specific USER files from SDK Template directory
        #    (gd32f10x_it.c/h, gd32f10x_libopt.h, systick.c/h, main.h — always fresh from SDK)
        if sdk_path:
            self._copy_sdk_templates(Path(sdk_path), user_dir, chip_config)

        # 6. Render the selected main.c template
        main_template = self._templates_dir / family_lower / template_type / "main.c"
        if main_template.exists():
            render(main_template, user_dir / "main.c", cv)
            # If main.c has its own printf retarget, remove the common one to avoid conflict
            main_content = (user_dir / "main.c").read_text(encoding="utf-8", errors="replace")
            if "fputc" in main_content or "_write" in main_content:
                rt = user_dir / "retarget_printf.c"
                if rt.exists():
                    rt.unlink()

        # 7. Generate .uvprojx from template
        uvprojx_template = self._templates_dir / family_lower / "uvprojx_template.xml"
        if uvprojx_template.exists():
            variables = self._build_uvprojx_vars(project_name, chip_name, chip_config, output_dir)
            mdk_dir = output_dir / "MDK-ARM"
            mdk_dir.mkdir(parents=True, exist_ok=True)
            render(uvprojx_template, mdk_dir / f"{project_name}.uvprojx", variables)

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

    def _build_uvprojx_vars(self, project_name: str, chip_name: str, chip_config: dict, output_dir: Path) -> dict:
        """Build template variables map for uvprojx generation."""
        config = chip_config.get("config", {})
        startup = chip_config.get("startup", "")
        flash_driver = chip_config.get("flash_driver", "")
        device_define = chip_config.get("define", "")
        ram_kb = chip_config.get("ram_kb", 20)
        flash_kb = chip_config.get("flash_kb", 64)
        ram_start = int(config.get("ram_start", "0x20000000"), 16)
        rom_start = int(config.get("rom_start", "0x08000000"), 16)
        return {
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
        }
