"""SDK manager: persist SDK paths, find and copy library files from SDK."""
import json
from pathlib import Path

CONFIG_FILE = Path.home() / ".mcu_template_config.json"


class SDKManager:
    def __init__(self):
        self._paths: dict[str, str] = {}

    def load_config(self):
        """Load saved SDK paths from config file."""
        if CONFIG_FILE.exists():
            self._paths = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))

    def save_config(self):
        """Save current SDK paths to config file."""
        CONFIG_FILE.write_text(json.dumps(self._paths, indent=2, ensure_ascii=False), encoding="utf-8")

    def set_path(self, vendor: str, path: str):
        """Set SDK root path for a vendor."""
        self._paths[vendor] = path
        self.save_config()

    def get_path(self, vendor: str) -> str:
        """Get SDK root path for a vendor."""
        return self._paths.get(vendor, "")

    def find_file(self, sdk_root: Path, relative_path: str) -> Path | None:
        """Search for a file by relative path. Tries with and without Firmware/ prefix."""
        target = sdk_root / relative_path
        if target.exists():
            return target
        target = sdk_root / "Firmware" / relative_path
        if target.exists():
            return target
        # Fallback: recursive search by filename
        filename = Path(relative_path).name
        matches = list(sdk_root.rglob(filename))
        return matches[0] if matches else None

    def _find_dir(self, sdk_root: Path, relative_path: str) -> Path | None:
        """Search for a directory, trying with and without Firmware/ prefix."""
        target = sdk_root / relative_path
        if target.is_dir():
            return target
        target = sdk_root / "Firmware" / relative_path
        if target.is_dir():
            return target
        # Fallback: recursive search by directory name
        dirname = Path(relative_path).name
        matches = [d for d in sdk_root.rglob(dirname) if d.is_dir()]
        return matches[0] if matches else None

    def copy_firmware(self, sdk_root: Path, chip_config: dict, dest_dir: Path):
        """Copy firmware library files from SDK to project destination."""
        cmsis = chip_config["cmsis"]
        sdk_base = Path(sdk_root)

        # Copy CMSIS core headers
        for header in cmsis["core_headers"]:
            src = self.find_file(sdk_base, header)
            if src:
                dest = dest_dir / "CMSIS" / header
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(src.read_bytes())

        # Copy system source
        device_path = cmsis["device_path"]
        system_file = cmsis["system_source"]
        system_src = self.find_file(sdk_base, f"{device_path}/Source/{system_file}")
        if system_src:
            dest = dest_dir / "CMSIS" / device_path / "Source" / system_file
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(system_src.read_bytes())

        # Copy startup file(s)
        startup_rel = cmsis["startup_path"]
        startup_dir = dest_dir / "CMSIS" / startup_rel
        startup_dir.mkdir(parents=True, exist_ok=True)

        for s_file in sdk_base.rglob("*.s"):
            if "startup_gd32f10x" in s_file.name.lower():
                dest = startup_dir / s_file.name
                dest.write_bytes(s_file.read_bytes())

        # Copy firmware include files
        sdk_fw_inc = self._find_dir(sdk_base, cmsis["firmware_include"])
        dest_fw_inc = dest_dir / "FIRMWARE" / "Include"
        dest_fw_inc.mkdir(parents=True, exist_ok=True)
        if sdk_fw_inc:
            for h_file in sdk_fw_inc.glob("*.h"):
                (dest_fw_inc / h_file.name).write_bytes(h_file.read_bytes())

        # Copy firmware source files
        sdk_fw_src = self._find_dir(sdk_base, cmsis["firmware_source"])
        dest_fw_src = dest_dir / "FIRMWARE" / "Source"
        dest_fw_src.mkdir(parents=True, exist_ok=True)
        if sdk_fw_src:
            for c_file in sdk_fw_src.glob("*.c"):
                (dest_fw_src / c_file.name).write_bytes(c_file.read_bytes())
