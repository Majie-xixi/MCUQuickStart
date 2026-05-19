"""Project generator: orchestrate directory creation, file copying, and template rendering."""
from pathlib import Path
from src.core.template_engine import render, copy_file
from src.core.sdk_manager import SDKManager


class ProjectGenerator:
    def __init__(self, templates_dir: Path, sdk_manager: SDKManager):
        self._templates_dir = templates_dir
        self._sdk = sdk_manager

    def generate(self, family_name: str, chip_name: str, chip_config: dict,
                 project_name: str, output_dir: Path, template_type: str):
        """Generate a complete project."""
        output_dir.mkdir(parents=True, exist_ok=True)

        # 1. Copy firmware from SDK
        vendor = chip_config.get("vendor", "")
        sdk_path = self._sdk.get_path(vendor)
        if sdk_path:
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
                render(src, dst_dir / src_name, chip_config)

        # 4. Copy common USER templates
        common_tmpl = self._templates_dir / "common"
        user_dir = output_dir / "USER"
        user_dir.mkdir(parents=True, exist_ok=True)
        if common_tmpl.exists():
            for src_file in common_tmpl.iterdir():
                if src_file.is_file():
                    render(src_file, user_dir / src_file.name, chip_config)

        # 5. Render the selected main.c template
        family_lower = family_name.lower()
        main_template = self._templates_dir / family_lower / template_type / "main.c"
        if main_template.exists():
            render(main_template, user_dir / "main.c", chip_config)

        # 6. Generate .uvprojx from template
        uvprojx_template = self._templates_dir / family_lower / "uvprojx_template.xml"
        if uvprojx_template.exists():
            variables = self._build_uvprojx_vars(project_name, chip_name, chip_config)
            mdk_dir = output_dir / "MDK-ARM"
            mdk_dir.mkdir(parents=True, exist_ok=True)
            render(uvprojx_template, mdk_dir / f"{project_name}.uvprojx", variables)

    def _build_uvprojx_vars(self, project_name: str, chip_name: str, chip_config: dict) -> dict:
        """Build template variables map for uvprojx generation."""
        config = chip_config.get("config", {})
        return {
            "PROJECT_NAME": project_name,
            "CHIP": chip_name,
            "DEVICE_HEADER_BARE": chip_config.get("device_header", "").replace(".h", ""),
            "DEVICE_DEFINE": chip_config.get("device_define", ""),
            "CPU_TYPE": config.get("cpu_type", ""),
            "RAM_START": config.get("ram_start", ""),
            "RAM_SIZE": config.get("ram_size", ""),
            "ROM_START": config.get("rom_start", ""),
            "ROM_SIZE": config.get("rom_size", ""),
            "CLOCK": config.get("clock", ""),
            "SIM_DLL": config.get("sim_dll", ""),
            "TARGET_DLL": config.get("target_dll", ""),
            "SIM_DLG_DLL": config.get("sim_dlg_dll", ""),
            "TARGET_DLG_DLL": config.get("target_dlg_dll", ""),
            "DLG_ARGUMENTS": config.get("dlg_arguments", ""),
            "VENDOR": chip_config.get("vendor", ""),
            "PACK_ID": chip_config.get("pack_id", ""),
            "STARTUP_FILE": chip_config.get("startup", ""),
        }
