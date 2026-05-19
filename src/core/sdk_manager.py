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

    def resolve_sdk(self, sdk_root: str, sdk_subdir: str) -> str | None:
        """Find SDK directory by name prefix under the SDK root directory."""
        base = Path(sdk_root)
        if not base.is_dir():
            return None
        for entry in base.iterdir():
            if entry.is_dir() and entry.name.lower().startswith(sdk_subdir.lower()):
                return str(entry)
        return None

    def find_file(self, sdk_root: Path, relative_path: str) -> Path | None:
        """Search for a file by relative path, trying common SDK path prefixes."""
        for prefix in ("", "Firmware/", "Firmware/CMSIS/"):
            target = sdk_root / prefix / relative_path
            if target.exists():
                return target
        # Fallback: recursive search by filename
        filename = Path(relative_path).name
        matches = list(sdk_root.rglob(filename))
        return matches[0] if matches else None

    def _find_dir(self, sdk_root: Path, relative_path: str) -> Path | None:
        """Search for a directory, trying common SDK path prefixes."""
        for prefix in ("", "Firmware/", "Firmware/CMSIS/"):
            target = sdk_root / prefix / relative_path
            if target.is_dir():
                return target
        # Fallback: recursive search by directory name, prefer Firmware paths
        dirname = Path(relative_path).name
        matches = [d for d in sdk_root.rglob(dirname) if d.is_dir()]
        if matches:
            # Prefer paths under Firmware/
            fw_matches = [m for m in matches if "/Firmware/" in m.as_posix()]
            return (fw_matches or matches)[0]
        return None

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

        # Copy device include headers (gd32f10x.h, system_gd32f10x.h)
        device_path = cmsis["device_path"]
        sdk_dev_inc = self._find_dir(sdk_base, f"{device_path}/Include")
        dest_dev_inc = dest_dir / "CMSIS" / device_path / "Include"
        dest_dev_inc.mkdir(parents=True, exist_ok=True)
        if sdk_dev_inc:
            for h_file in sdk_dev_inc.glob("*.h"):
                (dest_dev_inc / h_file.name).write_bytes(h_file.read_bytes())

        # Copy system source
        system_file = cmsis["system_source"]
        system_src = self.find_file(sdk_base, f"{device_path}/Source/{system_file}")
        if system_src:
            dest = dest_dir / "CMSIS" / device_path / "Source" / system_file
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(system_src.read_bytes())

        # Copy startup file(s) — find the ARM startup directory, copy all .s files
        startup_rel = cmsis["startup_path"]
        startup_dir = dest_dir / "CMSIS" / startup_rel
        startup_dir.mkdir(parents=True, exist_ok=True)

        sdk_startup = self._find_dir(sdk_base, startup_rel)
        if sdk_startup:
            for s_file in sdk_startup.glob("*.s"):
                (startup_dir / s_file.name).write_bytes(s_file.read_bytes())
        else:
            # Fallback: rglob for .s files, exclude IAR
            for s_file in sdk_base.rglob("*.s"):
                if s_file.name.startswith("startup_") and "/IAR/" not in s_file.as_posix():
                    (startup_dir / s_file.name).write_bytes(s_file.read_bytes())

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
