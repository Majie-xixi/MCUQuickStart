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
        """Find SDK directory by name prefix under the SDK root (searches up to 2 levels)."""
        base = Path(sdk_root)
        if not base.is_dir():
            return None
        # Level 1: direct children
        for entry in base.iterdir():
            if entry.is_dir() and entry.name.lower().startswith(sdk_subdir.lower()):
                return str(entry)
        # Level 2: grandchildren (e.g. stsw-stm32054/STM32F10x_StdPeriph_Lib_V3.6.0)
        for entry in base.iterdir():
            if entry.is_dir():
                for sub in entry.iterdir():
                    if sub.is_dir() and sub.name.lower().startswith(sdk_subdir.lower()):
                        return str(sub)
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

        # Copy device include headers
        device_path = cmsis["device_path"]
        sdk_dev_inc = self._find_dir(sdk_base, f"{device_path}/Include")
        if not sdk_dev_inc:
            sdk_dev_inc = self._find_dir(sdk_base, device_path)  # STM32: flat, no Include/
        dest_dev_inc = dest_dir / "CMSIS" / device_path / "Include"
        dest_dev_inc.mkdir(parents=True, exist_ok=True)
        if sdk_dev_inc:
            for h_file in sdk_dev_inc.glob("*.h"):
                (dest_dev_inc / h_file.name).write_bytes(h_file.read_bytes())

        # Copy system source (try Source/, Source/Templates/, then flat)
        system_file = cmsis["system_source"]
        system_src = self.find_file(sdk_base, f"{device_path}/Source/{system_file}")
        if not system_src:
            system_src = self.find_file(sdk_base, f"{device_path}/Source/Templates/{system_file}")
        if not system_src:
            system_src = self.find_file(sdk_base, f"{device_path}/{system_file}")
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

        # Copy GCC startup files if SDK has them (as sibling of ARM startup dir)
        self._copy_gcc_startup(sdk_base, cmsis, dest_dir, chip_config)

    def _copy_gcc_startup(self, sdk_base: Path, cmsis: dict, dest_dir: Path, chip_config: dict):
        """Copy GCC-compatible startup files from SDK (gcc_ride7/, GCC/, TrueSTUDIO/ dirs)."""
        startup_rel = cmsis["startup_path"]
        arm_startup_dir = self._find_dir(sdk_base, startup_rel)
        if not arm_startup_dir:
            return

        # Look for GCC directories as siblings of the ARM startup dir
        gcc_candidates = ["gcc_ride7", "GCC", "TrueSTUDIO"]
        gcc_dir = None
        parent = arm_startup_dir.parent
        for name in gcc_candidates:
            candidate = parent / name
            if candidate.is_dir():
                gcc_dir = candidate
                break

        if not gcc_dir:
            return

        # Copy to STARTUP/ directory for GCC use
        gcc_dest = dest_dir / "STARTUP"
        gcc_dest.mkdir(parents=True, exist_ok=True)
        for f in gcc_dir.iterdir():
            if f.is_file() and f.suffix.lower() in (".s", ".c") and f.name.startswith("startup"):
                (gcc_dest / f.name).write_bytes(f.read_bytes())

        # Also search GD32 Embedded Builder in SDK root for GCC startup files
        sdk_root = Path(self.get_path("SDK_ROOT")) if self.get_path("SDK_ROOT") else None
        if sdk_root and sdk_root.is_dir():
            startup_file = chip_config.get("startup", "")
            for ext in (startup_file, startup_file.replace(".s", ".S")):
                for eb_dir in sdk_root.glob("GD32EmbeddedBuilder*"):
                    if eb_dir.is_dir():
                        for match in eb_dir.rglob(f"gcc_startup/{ext}"):
                            (gcc_dest / startup_file).write_bytes(match.read_bytes())
                            return
