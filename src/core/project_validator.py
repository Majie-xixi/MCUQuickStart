"""Generated project validation report."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CheckResult:
    status: str
    name: str
    detail: str = ""


class ProjectValidator:
    """Validate the files that should exist for a generated project."""

    def __init__(self):
        self._project_dir: Path | None = None

    def validate(
        self,
        project_dir: Path,
        project_name: str,
        chip_config: dict,
        optional_libs: list[str] | None = None,
        build_system: str = "keil",
    ) -> list[CheckResult]:
        optional_libs = optional_libs or []
        use_keil = build_system in ("keil", "both")
        use_gcc = build_system in ("gcc", "both")
        use_freertos = "freertos" in optional_libs
        use_rtt = "rtt_nano" in optional_libs

        self._project_dir = project_dir
        results: list[CheckResult] = []
        self._check_base_project(results, project_dir, chip_config)

        if use_keil:
            self._check_file(
                results,
                "Keil project",
                project_dir / "MDK-ARM" / f"{project_name}.uvprojx",
            )

        if use_gcc:
            self._check_file(results, "CMakeLists.txt", project_dir / "CMakeLists.txt")
            self._check_file(results, "Linker script", project_dir / f"{project_name}.ld")
            self._check_file(
                results,
                "GCC startup",
                project_dir / "STARTUP" / chip_config.get("startup", ""),
            )

        if use_freertos:
            self._check_freertos(results, project_dir, chip_config, use_gcc)

        if use_rtt:
            self._check_rtt(results, project_dir, chip_config, use_keil, use_gcc)

        return results

    def _check_base_project(self, results: list[CheckResult], project_dir: Path, chip_config: dict):
        self._check_dir(results, "Project directory", project_dir)
        self._check_file(results, "USER main.c", project_dir / "USER" / "main.c")

        firmware_include = project_dir / "FIRMWARE" / "Include"
        firmware_source = project_dir / "FIRMWARE" / "Source"
        self._check_count(results, "Firmware headers", firmware_include, "*.h")
        self._check_count(results, "Firmware sources", firmware_source, "*.c")

        device_header = chip_config.get("device_header", "")
        if device_header:
            matches = list((project_dir / "CMSIS").rglob(device_header))
            self._append(
                results,
                bool(matches),
                "Device header",
                matches[0].relative_to(project_dir).as_posix() if matches else device_header,
            )

        startup_file = chip_config.get("startup", "")
        startup_rel = chip_config.get("cmsis", {}).get("startup_path", "")
        if startup_file:
            expected = project_dir / "CMSIS" / startup_rel / startup_file
            matches = list((project_dir / "CMSIS").rglob(startup_file))
            detail = expected.relative_to(project_dir).as_posix()
            if matches and not expected.exists():
                detail = matches[0].relative_to(project_dir).as_posix()
            self._append(results, bool(matches), "Keil startup", detail)

    def _check_freertos(
        self,
        results: list[CheckResult],
        project_dir: Path,
        chip_config: dict,
        use_gcc: bool,
    ):
        freertos_cfg = chip_config.get("optional_libs", {}).get("freertos", {})
        core_name = chip_config.get("core", "Cortex-M3")
        port_rel = freertos_cfg.get("port_map", {}).get(core_name, "portable/RVDS/ARM_CM3")
        heap = freertos_cfg.get("heap", "heap_4.c")

        self._check_file(
            results,
            "FreeRTOSConfig.h",
            project_dir / "FreeRTOS" / "include" / "FreeRTOSConfig.h",
        )
        self._check_expected_files(
            results,
            "FreeRTOS kernel",
            project_dir / "FreeRTOS",
            freertos_cfg.get("core_files", []),
        )
        self._check_file(results, "FreeRTOS Keil port", project_dir / "FreeRTOS" / port_rel / "port.c")
        self._check_file(
            results,
            "FreeRTOS heap",
            project_dir / "FreeRTOS" / "portable" / "MemMang" / heap,
        )

        if use_gcc:
            gcc_port_rel = port_rel.replace("/RVDS/", "/GCC/")
            self._check_file(
                results,
                "FreeRTOS GCC port",
                project_dir / "FreeRTOS" / gcc_port_rel / "port.c",
            )

    def _check_rtt(
        self,
        results: list[CheckResult],
        project_dir: Path,
        chip_config: dict,
        use_keil: bool,
        use_gcc: bool,
    ):
        rtt_cfg = chip_config.get("optional_libs", {}).get("rtt_nano", {})
        core_name = chip_config.get("core", "Cortex-M3")
        port_rel = rtt_cfg.get("port_map", {}).get(core_name, "libcpu/arm/cortex-m3")

        self._check_file(results, "RT-Thread rtconfig.h", project_dir / "RT-Thread" / "include" / "rtconfig.h")
        self._check_file(results, "RT-Thread board.c", project_dir / "USER" / "board.c")
        self._check_expected_files(
            results,
            "RT-Thread kernel",
            project_dir / "RT-Thread",
            rtt_cfg.get("core_files", []),
        )
        self._check_file(results, "RT-Thread cpuport.c", project_dir / "RT-Thread" / port_rel / "cpuport.c")

        if use_keil:
            self._check_file(
                results,
                "RT-Thread Keil context",
                project_dir / "RT-Thread" / port_rel / "context_rvds.S",
            )
        if use_gcc:
            self._check_file(
                results,
                "RT-Thread GCC context",
                project_dir / "RT-Thread" / port_rel / "context_gcc.S",
            )

    def _check_expected_files(
        self,
        results: list[CheckResult],
        name: str,
        base_dir: Path,
        filenames: list[str],
    ):
        missing = [filename for filename in filenames if not (base_dir / filename).exists()]
        if missing:
            results.append(CheckResult("error", name, f"missing: {', '.join(missing[:5])}"))
        else:
            results.append(CheckResult("ok", name, f"{len(filenames)} files"))

    def _check_count(self, results: list[CheckResult], name: str, directory: Path, pattern: str):
        if not directory.is_dir():
            results.append(CheckResult("error", name, f"missing directory: {directory.name}"))
            return
        count = len(list(directory.glob(pattern)))
        if count == 0:
            results.append(CheckResult("error", name, f"no {pattern} files"))
        else:
            results.append(CheckResult("ok", name, f"{count} files"))

    def _check_dir(self, results: list[CheckResult], name: str, path: Path):
        self._append(results, path.is_dir(), name, self._display_path(path))

    def _check_file(self, results: list[CheckResult], name: str, path: Path):
        self._append(results, path.is_file(), name, self._display_path(path))

    def _display_path(self, path: Path) -> str:
        if self._project_dir:
            try:
                return path.relative_to(self._project_dir).as_posix()
            except ValueError:
                pass
        return path.as_posix()

    @staticmethod
    def _append(results: list[CheckResult], ok: bool, name: str, detail: str):
        results.append(CheckResult("ok" if ok else "error", name, detail))
