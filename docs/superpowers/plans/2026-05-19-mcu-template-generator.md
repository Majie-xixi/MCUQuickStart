# MCU Template Generator — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Desktop GUI tool that generates Keil5-ready project templates for GD32F10x chips, with selectable code templates (empty / LED / UART).

**Architecture:** PyQt6 desktop app with 4 backend modules — chip database (JSON), SDK manager (file discovery & copy), template engine (placeholder replacement), project generator (orchestrator). GUI is a single-window layout with SDK config, chip selection, template choice, and a generate button.

**Tech Stack:** Python 3, PyQt6, xml.etree.ElementTree (stdlib), pathlib (stdlib)

---

## File Structure

```
Project_Tool/
├── main.py                          # Entry point
├── requirements.txt                 # pyqt6
├── src/
│   ├── __init__.py                  # (empty)
│   ├── core/
│   │   ├── __init__.py              # (empty)
│   │   ├── chip_db.py               # Chip database: load chips from JSON, return chip info
│   │   ├── sdk_manager.py           # SDK manager: persist SDK paths, find & copy library files
│   │   ├── template_engine.py       # Template engine: read file, replace {{PLACEHOLDER}}, write file
│   │   └── project_generator.py     # Project generator: orchestrate full project creation
│   ├── gui/
│   │   ├── __init__.py              # (empty)
│   │   └── main_window.py           # PyQt6 main window
│   └── resources/
│       ├── chips/
│       │   └── gd32f10x.json        # GD32F10x chip definitions
│       └── templates/
│           ├── common/              # Shared code templates
│           │   ├── main.h
│           │   ├── gd32f10x_it.c
│           │   ├── gd32f10x_it.h
│           │   ├── gd32f10x_libopt.h
│           │   ├── systick.c
│           │   ├── systick.h
│           │   ├── debug_print.h
│           │   └── retarget_printf.c
│           ├── gd32f10x/
│           │   ├── empty/main.c
│           │   ├── led/main.c
│           │   ├── uart/main.c
│           │   └── uvprojx_template.xml
│           └── system/
│               ├── delay.c
│               ├── delay.h
│               ├── sysconfig.c
│               └── sysconfig.h
```

---

### Task 1: Project scaffolding

**Files:**
- Create: `requirements.txt`
- Create: `src/__init__.py`
- Create: `src/core/__init__.py`
- Create: `src/gui/__init__.py`
- Create: `src/resources/chips/` (empty dir)
- Create: `src/resources/templates/common/` (empty dir)
- Create: `src/resources/templates/gd32f10x/` (empty dir)
- Create: `src/resources/templates/system/` (empty dir)

- [ ] **Step 1: Create directory structure**

Run:
```bash
mkdir -p "E:\MJ_Demo\Project_Tool\src\core"
mkdir -p "E:\MJ_Demo\Project_Tool\src\gui"
mkdir -p "E:\MJ_Demo\Project_Tool\src\resources\chips"
mkdir -p "E:\MJ_Demo\Project_Tool\src\resources\templates\common"
mkdir -p "E:\MJ_Demo\Project_Tool\src\resources\templates\gd32f10x"
mkdir -p "E:\MJ_Demo\Project_Tool\src\resources\templates\system"
```

- [ ] **Step 2: Create requirements.txt**

```text
pyqt6>=6.6
```

- [ ] **Step 3: Create `__init__.py` files (empty)**

Write empty files:
- `src/__init__.py`
- `src/core/__init__.py`
- `src/gui/__init__.py`

- [ ] **Step 4: Commit**

```bash
git init
git add -A
git commit -m "chore: project scaffolding with directory structure and requirements"
```

---

### Task 2: Chip database module

**Files:**
- Create: `src/resources/chips/gd32f10x.json`
- Create: `src/core/chip_db.py`

- [ ] **Step 1: Create GD32F10x chip database JSON**

`src/resources/chips/gd32f10x.json`:

```json
{
  "GD32F10x": {
    "family": "GD32F10x",
    "core": "Cortex-M3",
    "vendor": "GigaDevice",
    "pack_id": "GigaDevice.GD32F10x_DFP.2.0.3",
    "device_header": "gd32f10x.h",
    "device_define": "GD32F10X_MD",
    "use_stdperiph_driver": true,
    "sdk_subdir": "GD32F10x_Firmware_Library",
    "cmsis": {
      "core_headers": ["core_cm3.h", "core_cmFunc.h", "core_cmInstr.h"],
      "device_path": "GD/GD32F10x",
      "system_source": "system_gd32f10x.c",
      "startup_path": "GD/GD32F10x/Source/ARM",
      "firmware_include": "Include",
      "firmware_source": "Source"
    },
    "config": {
      "ram_start": "0x20000000",
      "ram_size": "0x5000",
      "rom_start": "0x08000000",
      "rom_size": "0x20000",
      "cpu_type": "Cortex-M3",
      "clock": "12000000",
      "sim_dll": "SARMCM3.DLL",
      "target_dll": "SARMCM3.DLL",
      "sim_dlg_dll": "DCM.DLL",
      "target_dlg_dll": "TCM.DLL",
      "dlg_arguments": "-pCM3",
      "flash_driver": "UL2CM3(-S0 -C0 -P0 -FD20000000 -FC1000 -FN1 -FF0GD32F10x_MD -FS08000000 -FL020000 -FP0($$Device:{{CHIP}}$$Flash\\GD32F10x_MD.FLM))",
      "svd_file": "$$Device:{{CHIP}}$$SVD\\GD32F10x\\GD32F10x_MD.svd"
    },
    "chips": {
      "GD32F103C8T6": {
        "ram_kb": 20,
        "flash_kb": 64,
        "startup": "startup_gd32f10x_md.s"
      },
      "GD32F103CBT6": {
        "ram_kb": 20,
        "flash_kb": 128,
        "startup": "startup_gd32f10x_md.s"
      },
      "GD32F103RCT6": {
        "ram_kb": 48,
        "flash_kb": 256,
        "startup": "startup_gd32f10x_hd.s"
      },
      "GD32F103RET6": {
        "ram_kb": 64,
        "flash_kb": 512,
        "startup": "startup_gd32f10x_hd.s"
      },
      "GD32F103VCT6": {
        "ram_kb": 48,
        "flash_kb": 256,
        "startup": "startup_gd32f10x_hd.s"
      },
      "GD32F103VET6": {
        "ram_kb": 64,
        "flash_kb": 512,
        "startup": "startup_gd32f10x_hd.s"
      },
      "GD32F103RBT6": {
        "ram_kb": 20,
        "flash_kb": 128,
        "startup": "startup_gd32f10x_md.s"
      },
      "GD32F103VBT6": {
        "ram_kb": 20,
        "flash_kb": 128,
        "startup": "startup_gd32f10x_md.s"
      }
    },
    "library_files": {
      "required": [
        "adc", "bkp", "crc", "dac", "dbg", "dma", "exti", "fmc",
        "fwdgt", "gpio", "i2c", "misc", "pmu", "rcu", "rtc",
        "sdio", "spi", "timer", "usart", "wwdgt"
      ],
      "optional": ["can", "enet", "exmc"]
    }
  }
}
```

- [ ] **Step 2: Create chip_db.py**

`src/core/chip_db.py`:

```python
"""Chip database: load chip definitions from JSON files."""
import json
from pathlib import Path


class ChipDatabase:
    def __init__(self, chips_dir: Path):
        self._chips_dir = chips_dir
        self._families: dict = {}

    def load(self):
        """Load all chip JSON files from chips directory."""
        for json_file in self._chips_dir.glob("*.json"):
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            for family_name, family_data in data.items():
                self._families[family_name] = family_data

    def get_families(self) -> list[str]:
        """Return list of chip family names."""
        return list(self._families.keys())

    def get_family(self, family_name: str) -> dict:
        """Return full family definition."""
        return self._families.get(family_name, {})

    def get_chip(self, family_name: str, chip_name: str) -> dict | None:
        """Return chip config merged with family defaults."""
        family = self._families.get(family_name)
        if not family:
            return None
        chip = family.get("chips", {}).get(chip_name)
        if not chip:
            return None
        result = {k: v for k, v in family.items() if k not in ("chips",)}
        result.update(chip)
        result["name"] = chip_name
        return result

    def get_chips_for_family(self, family_name: str) -> list[str]:
        """Return list of chip names for a family."""
        family = self._families.get(family_name, {})
        return list(family.get("chips", {}).keys())
```

- [ ] **Step 3: Write test and verify**

```python
# test_chip_db.py (run inline, no pytest yet)
from pathlib import Path
from src.core.chip_db import ChipDatabase

db = ChipDatabase(Path("src/resources/chips"))
db.load()
assert "GD32F10x" in db.get_families()
assert "GD32F103C8T6" in db.get_chips_for_family("GD32F10x")
chip = db.get_chip("GD32F10x", "GD32F103C8T6")
assert chip["name"] == "GD32F103C8T6"
assert chip["core"] == "Cortex-M3"
assert chip["ram_kb"] == 20
print("All chip DB tests passed")
```

Run: `python -c "..."` (inline test above)

- [ ] **Step 4: Commit**

```bash
git add src/resources/chips/gd32f10x.json src/core/chip_db.py
git commit -m "feat: add chip database module with GD32F10x definitions"
```

---

### Task 3: Template engine

**Files:**
- Create: `src/core/template_engine.py`

- [ ] **Step 1: Create template_engine.py**

`src/core/template_engine.py`:

```python
"""Template engine: replace {{PLACEHOLDER}} tokens in template files."""
from pathlib import Path


def render(template_path: Path, output_path: Path, variables: dict):
    """Read template file, replace {{VAR}} tokens with values, write output."""
    content = template_path.read_text(encoding="utf-8")
    for key, value in variables.items():
        content = content.replace("{{" + key + "}}", str(value))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")


def render_directory(template_dir: Path, output_dir: Path, variables: dict):
    """Render all files in a directory recursively."""
    for file_path in template_dir.rglob("*"):
        if file_path.is_file():
            rel_path = file_path.relative_to(template_dir)
            out_path = output_dir / rel_path
            render(file_path, out_path, variables)


def copy_file(src: Path, dst: Path):
    """Copy a file, creating parent dirs as needed."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(src.read_bytes())
```

- [ ] **Step 2: Verify with inline test**

```python
import tempfile, os
from pathlib import Path
from src.core.template_engine import render

tmp = Path(tempfile.mkdtemp())
tmpl = tmp / "template.c"
tmpl.write_text('#include "{{DEVICE_HEADER}}"\nint main(void) { while(1); }')
out = tmp / "output.c"
render(tmpl, out, {"DEVICE_HEADER": "gd32f10x.h"})
result = out.read_text()
assert 'gd32f10x.h' in result
print("Template engine test passed")
```

Run inline and verify.

- [ ] **Step 3: Commit**

```bash
git add src/core/template_engine.py
git commit -m "feat: add template engine with placeholder replacement"
```

---

### Task 4: SDK manager

**Files:**
- Create: `src/core/sdk_manager.py`

- [ ] **Step 1: Create sdk_manager.py**

`src/core/sdk_manager.py`:

```python
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
        """Search for a file by relative path. Returns None if not found."""
        target = sdk_root / relative_path
        if target.exists():
            return target
        # Fallback: recursive search by filename
        filename = Path(relative_path).name
        matches = list(sdk_root.rglob(filename))
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

        # Copy system source and device headers
        device_path = cmsis["device_path"]
        system_file = cmsis["system_source"]
        system_src = self.find_file(sdk_base, f"{device_path}/Source/{system_file}")
        if system_src:
            dest = dest_dir / "CMSIS" / device_path / "Source" / system_file
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(system_src.read_bytes())

        # Copy startup file
        startup_path = cmsis["startup_path"]
        startup_dir = dest_dir / "CMSIS" / startup_path
        startup_dir.mkdir(parents=True, exist_ok=True)

        # Copy all .s files from startup dir
        sdk_startup = sdk_base / startup_path
        if sdk_startup.exists():
            for s_file in sdk_startup.glob("*.s"):
                dest = startup_dir / s_file.name
                dest.write_bytes(s_file.read_bytes())

        # Copy firmware include files
        fw_include = cmsis["firmware_include"]
        sdk_fw_inc = sdk_base / fw_include
        dest_fw_inc = dest_dir / "FIRMWARE" / "Include"
        dest_fw_inc.mkdir(parents=True, exist_ok=True)
        if sdk_fw_inc.exists():
            for h_file in sdk_fw_inc.glob("*.h"):
                (dest_fw_inc / h_file.name).write_bytes(h_file.read_bytes())

        # Copy firmware source files
        fw_source = cmsis["firmware_source"]
        sdk_fw_src = sdk_base / fw_source
        dest_fw_src = dest_dir / "FIRMWARE" / "Source"
        dest_fw_src.mkdir(parents=True, exist_ok=True)
        if sdk_fw_src.exists():
            for c_file in sdk_fw_src.glob("*.c"):
                (dest_fw_src / c_file.name).write_bytes(c_file.read_bytes())
```

- [ ] **Step 2: Verify by pointing at reference project SDK**

```python
from pathlib import Path
from src.core.sdk_manager import SDKManager

mgr = SDKManager()
mgr.set_path("GD32", "E:/IAXX_PMT/OptoCounter")
assert mgr.get_path("GD32") == "E:/IAXX_PMT/OptoCounter"
# Test find_file
result = mgr.find_file(Path("E:/IAXX_PMT/OptoCounter"), "CMSIS/core_cm3.h")
assert result is not None
print("SDK manager tests passed")
```

Run inline.

- [ ] **Step 3: Commit**

```bash
git add src/core/sdk_manager.py
git commit -m "feat: add SDK manager for path config and library file copying"
```

---

### Task 5: Project generator

**Files:**
- Create: `src/core/project_generator.py`

- [ ] **Step 1: Create project_generator.py**

`src/core/project_generator.py`:

```python
"""Project generator: orchestrate directory creation, file copying, and template rendering."""
from pathlib import Path
from src.core.template_engine import render, render_directory, copy_file
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
        sdk_root = Path(self._sdk.get_path(chip_config["vendor"]))
        self._sdk.copy_firmware(sdk_root, chip_config, output_dir)

        # 2. Create empty user directories
        for d in ["APP", "DRIVER", "HARDWARE"]:
            (output_dir / d).mkdir(exist_ok=True)

        # 3. Render system templates
        render_directory(
            self._templates_dir / "system",
            output_dir / "SYSTEM",
            {"DEVICE_HEADER": chip_config["device_header"]}
        )

        # 4. Render common USER templates
        render_directory(
            self._templates_dir / "common",
            output_dir / "USER",
            {
                "DEVICE_HEADER": chip_config["device_header"],
                "CHIP_FAMILY": family_name,
                "DEVICE_DEFINE": chip_config.get("device_define", ""),
            }
        )

        # 5. Render the selected main.c template
        template_family_dir = self._templates_dir / family_name.lower()
        main_template = template_family_dir / template_type / "main.c"
        if main_template.exists():
            render(
                main_template,
                output_dir / "USER" / "main.c",
                {"DEVICE_HEADER": chip_config["device_header"]}
            )

        # 6. Generate .uvprojx from template
        uvprojx_template = template_family_dir / "uvprojx_template.xml"
        if uvprojx_template.exists():
            variables = {
                "PROJECT_NAME": project_name,
                "CHIP": chip_name,
                "DEVICE_HEADER_BARE": chip_config["device_header"].replace(".h", ""),
                "DEVICE_DEFINE": chip_config.get("device_define", ""),
                "CPU_TYPE": chip_config["config"]["cpu_type"],
                "RAM_START": chip_config["config"]["ram_start"],
                "RAM_SIZE": chip_config["config"]["ram_size"],
                "ROM_START": chip_config["config"]["rom_start"],
                "ROM_SIZE": chip_config["config"]["rom_size"],
                "CLOCK": chip_config["config"]["clock"],
                "SIM_DLL": chip_config["config"]["sim_dll"],
                "TARGET_DLL": chip_config["config"]["target_dll"],
                "SIM_DLG_DLL": chip_config["config"]["sim_dlg_dll"],
                "TARGET_DLG_DLL": chip_config["config"]["target_dlg_dll"],
                "DLG_ARGUMENTS": chip_config["config"]["dlg_arguments"],
                "VENDOR": chip_config["vendor"],
                "PACK_ID": chip_config["pack_id"],
                "STARTUP_FILE": chip_config["startup"],
            }
            render(
                uvprojx_template,
                output_dir / "MDK-ARM" / f"{project_name}.uvprojx",
                variables,
            )

        # 7. Copy .uvoptx and .uvguix files if available
        for ext_file in template_family_dir.glob("*.uvoptx"):
            copy_file(ext_file, output_dir / "MDK-ARM" / f"{project_name}.uvoptx")
```

- [ ] **Step 2: Commit**

```bash
git add src/core/project_generator.py
git commit -m "feat: add project generator orchestrator"
```

---

### Task 6: Create code templates from reference project

**Files:**
- Create: `src/resources/templates/system/delay.c`
- Create: `src/resources/templates/system/delay.h`
- Create: `src/resources/templates/system/sysconfig.c`
- Create: `src/resources/templates/system/sysconfig.h`
- Create: `src/resources/templates/common/main.h`
- Create: `src/resources/templates/common/gd32f10x_it.c`
- Create: `src/resources/templates/common/gd32f10x_it.h`
- Create: `src/resources/templates/common/gd32f10x_libopt.h`
- Create: `src/resources/templates/common/systick.c`
- Create: `src/resources/templates/common/systick.h`
- Create: `src/resources/templates/common/debug_print.h`
- Create: `src/resources/templates/common/retarget_printf.c`
- Create: `src/resources/templates/gd32f10x/empty/main.c`
- Create: `src/resources/templates/gd32f10x/led/main.c`
- Create: `src/resources/templates/gd32f10x/uart/main.c`

- [ ] **Step 1: Copy system templates from reference project**

Copy the following files from `E:\IAXX_PMT\OptoCounter\SYSTEM\` to `src/resources/templates/system/` (flattening the delay/ and sys/ subdirs):

```bash
cp "E:\IAXX_PMT\OptoCounter\SYSTEM\delay\delay.c" "src\resources\templates\system\delay.c"
cp "E:\IAXX_PMT\OptoCounter\SYSTEM\delay\delay.h" "src\resources\templates\system\delay.h"
cp "E:\IAXX_PMT\OptoCounter\SYSTEM\sys\sysconfig.c" "src\resources\templates\system\sysconfig.c"
cp "E:\IAXX_PMT\OptoCounter\SYSTEM\sys\sysconfig.h" "src\resources\templates\system\sysconfig.h"
```

Then in `sysconfig.h`, replace `#include "gd32f10x.h"` with `#include "{{DEVICE_HEADER}}"` at line 3.
In `delay.h`, replace `#include "gd32f10x.h"` with `#include "{{DEVICE_HEADER}}"` at line 4.

- [ ] **Step 2: Create common USER templates from reference project**

Copy from `E:\IAXX_PMT\OptoCounter\USER\`:

```bash
cp "E:\IAXX_PMT\OptoCounter\USER\main.h" "src\resources\templates\common\main.h"
cp "E:\IAXX_PMT\OptoCounter\USER\gd32f10x_it.c" "src\resources\templates\common\gd32f10x_it.c"
cp "E:\IAXX_PMT\OptoCounter\USER\gd32f10x_it.h" "src\resources\templates\common\gd32f10x_it.h"
cp "E:\IAXX_PMT\OptoCounter\USER\gd32f10x_libopt.h" "src\resources\templates\common\gd32f10x_libopt.h"
cp "E:\IAXX_PMT\OptoCounter\USER\systick.c" "src\resources\templates\common\systick.c"
cp "E:\IAXX_PMT\OptoCounter\USER\systick.h" "src\resources\templates\common\systick.h"
cp "E:\IAXX_PMT\OptoCounter\USER\debug_print.h" "src\resources\templates\common\debug_print.h"
cp "E:\IAXX_PMT\OptoCounter\USER\retarget_printf.c" "src\resources\templates\common\retarget_printf.c"
```

Replace `#include "gd32f10x.h"` with `#include "{{DEVICE_HEADER}}"` in all .c and .h files that reference it.

- [ ] **Step 3: Create code template variants (empty / led / uart)**

`src/resources/templates/gd32f10x/empty/main.c`:
```c
#include "{{DEVICE_HEADER}}"
#include "main.h"
#include "systick.h"

int main(void)
{
    systick_config();
    while (1) {
    }
}
```

`src/resources/templates/gd32f10x/led/main.c`:
```c
#include "{{DEVICE_HEADER}}"
#include "main.h"
#include "systick.h"

void led_init(void)
{
    rcu_periph_clock_enable(RCU_GPIOA);
    gpio_init(GPIOA, GPIO_MODE_OUT_PP, GPIO_OSPEED_50MHZ, GPIO_PIN_0);
}

int main(void)
{
    systick_config();
    led_init();
    while (1) {
        gpio_bit_set(GPIOA, GPIO_PIN_0);
        delay_ms(500);
        gpio_bit_reset(GPIOA, GPIO_PIN_0);
        delay_ms(500);
    }
}
```

`src/resources/templates/gd32f10x/uart/main.c`:
```c
#include "{{DEVICE_HEADER}}"
#include "main.h"
#include "systick.h"
#include "debug_print.h"
#include <stdio.h>

void uart_init(void)
{
    rcu_periph_clock_enable(RCU_GPIOA);
    rcu_periph_clock_enable(RCU_USART0);
    gpio_init(GPIOA, GPIO_MODE_AF_PP, GPIO_OSPEED_50MHZ, GPIO_PIN_9);
    gpio_init(GPIOA, GPIO_MODE_IN_FLOATING, GPIO_OSPEED_50MHZ, GPIO_PIN_10);
    usart_deinit(USART0);
    usart_baudrate_set(USART0, 115200);
    usart_word_length_set(USART0, USART_WL_8BIT);
    usart_stop_bit_set(USART0, USART_STB_1BIT);
    usart_parity_config(USART0, USART_PM_NONE);
    usart_hardware_flow_rts_config(USART0, USART_RTS_DISABLE);
    usart_hardware_flow_cts_config(USART0, USART_CTS_DISABLE);
    usart_transmit_config(USART0, USART_TRANSMIT_ENABLE);
    usart_receive_config(USART0, USART_RECEIVE_ENABLE);
    usart_enable(USART0);
}

int main(void)
{
    systick_config();
    uart_init();
    printf("Hello from {{DEVICE_HEADER}}\r\n");
    while (1) {
        delay_ms(1000);
        printf("tick\r\n");
    }
}
```

- [ ] **Step 4: Commit**

```bash
git add src/resources/templates/
git commit -m "feat: add code templates (empty, LED, UART) and system files"
```

---

### Task 7: Keil5 uvprojx template

**Files:**
- Create: `src/resources/templates/gd32f10x/uvprojx_template.xml`

- [ ] **Step 1: Create uvprojx template from reference project**

Copy `E:\IAXX_PMT\OptoCounter\MDK-ARM\OptoCounter.uvprojx` and replace dynamic values with placeholders. Key replacements:

| Original value | Placeholder |
|---|---|
| `OptoCounter` (TargetName, OutputName) | `{{PROJECT_NAME}}` |
| `GD32F103RB` (Device) | `{{CHIP}}` |
| `GD32F10X_MD` (Define) | `{{DEVICE_DEFINE}}` |
| `Cortex-M3` (CPUTYPE) | `{{CPU_TYPE}}` |
| IRAM size `0x00005000` | `{{RAM_SIZE}}` |
| IROM size `0x00020000` | `{{ROM_SIZE}}` |
| `GigaDevice` (Vendor) | `{{VENDOR}}` |
| `GigaDevice.GD32F10x_DFP.2.0.3` (PackID) | `{{PACK_ID}}` |
| `SARMCM3.DLL` | `{{SIM_DLL}}` |
| `TCM.DLL` | `{{TARGET_DLG_DLL}}` |
| `-pCM3` | `{{DLG_ARGUMENTS}}` |

Remove the HARDWARE and DRIVER groups (they're empty in the template). Keep the APP group but with no files.

- [ ] **Step 2: Commit**

```bash
git add src/resources/templates/gd32f10x/uvprojx_template.xml
git commit -m "feat: add Keil5 uvprojx template for GD32F10x"
```

---

### Task 8: GUI main window

**Files:**
- Create: `src/gui/main_window.py`
- Create: `main.py`

- [ ] **Step 1: Create main_window.py**

`src/gui/main_window.py`:

```python
"""Main window for MCU Template Generator."""
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QComboBox, QPushButton,
    QTextEdit, QGroupBox, QRadioButton, QFileDialog, QMessageBox,
)
from PyQt6.QtCore import Qt
from src.core.chip_db import ChipDatabase
from src.core.sdk_manager import SDKManager
from src.core.project_generator import ProjectGenerator


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MCU Template Generator")
        self.setMinimumSize(650, 550)

        self._sdk = SDKManager()
        self._sdk.load_config()
        self._chip_db = ChipDatabase(Path(__file__).parent.parent / "resources" / "chips")
        self._chip_db.load()
        self._gen = ProjectGenerator(
            Path(__file__).parent.parent / "resources" / "templates",
            self._sdk,
        )

        self._build_ui()
        self._populate_families()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # --- SDK Config ---
        sdk_group = QGroupBox("SDK Paths")
        sdk_layout = QVBoxLayout(sdk_group)

        gd_row = QHBoxLayout()
        gd_row.addWidget(QLabel("GD32 SDK:"))
        self._gd_path = QLineEdit(self._sdk.get_path("GD32"))
        gd_row.addWidget(self._gd_path)
        gd_btn = QPushButton("Browse...")
        gd_btn.clicked.connect(lambda: self._browse_sdk("GD32", self._gd_path))
        gd_row.addWidget(gd_btn)
        sdk_layout.addLayout(gd_row)

        st_row = QHBoxLayout()
        st_row.addWidget(QLabel("STM32 SDK:"))
        self._st_path = QLineEdit(self._sdk.get_path("STM32"))
        st_row.addWidget(self._st_path)
        st_btn = QPushButton("Browse...")
        st_btn.clicked.connect(lambda: self._browse_sdk("STM32", self._st_path))
        st_btn.setEnabled(False)  # STM32 not implemented yet
        st_row.addWidget(st_btn)
        sdk_layout.addLayout(st_row)

        layout.addWidget(sdk_group)

        # --- Project Settings ---
        proj_group = QGroupBox("Project Settings")
        proj_layout = QVBoxLayout(proj_group)

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Chip Family:"))
        self._family_combo = QComboBox()
        self._family_combo.currentTextChanged.connect(self._on_family_changed)
        row1.addWidget(self._family_combo)
        row1.addWidget(QLabel("Chip Model:"))
        self._chip_combo = QComboBox()
        row1.addWidget(self._chip_combo)
        proj_layout.addLayout(row1)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Project Name:"))
        self._proj_name = QLineEdit("MyProject")
        row2.addWidget(self._proj_name)
        proj_layout.addLayout(row2)

        row3 = QHBoxLayout()
        row3.addWidget(QLabel("Output Dir:"))
        self._output_dir = QLineEdit(str(Path.home() / "Desktop"))
        row3.addWidget(self._output_dir)
        out_btn = QPushButton("Browse...")
        out_btn.clicked.connect(self._browse_output)
        row3.addWidget(out_btn)
        proj_layout.addLayout(row3)

        layout.addWidget(proj_group)

        # --- Template Choice ---
        tmpl_group = QGroupBox("Code Template")
        tmpl_layout = QVBoxLayout(tmpl_group)
        self._tmpl_empty = QRadioButton("Empty (main loop only)")
        self._tmpl_empty.setChecked(True)
        self._tmpl_led = QRadioButton("LED Blink")
        self._tmpl_uart = QRadioButton("UART Printf")
        tmpl_layout.addWidget(self._tmpl_empty)
        tmpl_layout.addWidget(self._tmpl_led)
        tmpl_layout.addWidget(self._tmpl_uart)
        layout.addWidget(tmpl_group)

        # --- Generate Button ---
        gen_btn = QPushButton("Generate Project")
        gen_btn.setMinimumHeight(36)
        gen_btn.clicked.connect(self._on_generate)
        layout.addWidget(gen_btn)

        # --- Log Output ---
        log_group = QGroupBox("Log")
        log_layout = QVBoxLayout(log_group)
        self._log = QTextEdit()
        self._log.setReadOnly(True)
        log_layout.addWidget(self._log)
        layout.addWidget(log_group)

    def _browse_sdk(self, vendor: str, line_edit: QLineEdit):
        path = QFileDialog.getExistingDirectory(self, f"Select {vendor} SDK Root")
        if path:
            line_edit.setText(path)
            self._sdk.set_path(vendor, path)

    def _browse_output(self):
        path = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if path:
            self._output_dir.setText(path)

    def _populate_families(self):
        families = self._chip_db.get_families()
        self._family_combo.addItems(families)

    def _on_family_changed(self, family: str):
        self._chip_combo.clear()
        chips = self._chip_db.get_chips_for_family(family)
        self._chip_combo.addItems(chips)

    def _log_msg(self, msg: str):
        self._log.append(msg)

    def _on_generate(self):
        family = self._family_combo.currentText()
        chip = self._chip_combo.currentText()
        proj_name = self._proj_name.text().strip()
        output_dir = Path(self._output_dir.text().strip())

        if not family or not chip:
            QMessageBox.warning(self, "Error", "Please select a chip.")
            return
        if not proj_name:
            QMessageBox.warning(self, "Error", "Please enter a project name.")
            return
        if not self._sdk.get_path("GD32"):
            QMessageBox.warning(self, "Error", "Please set the GD32 SDK path.")
            return

        chip_config = self._chip_db.get_chip(family, chip)
        if not chip_config:
            QMessageBox.warning(self, "Error", f"Chip {chip} not found in database.")
            return

        tmpl_type = "empty"
        if self._tmpl_led.isChecked():
            tmpl_type = "led"
        elif self._tmpl_uart.isChecked():
            tmpl_type = "uart"

        try:
            output_path = output_dir / proj_name
            self._log_msg(f"Generating {proj_name} for {chip} ({tmpl_type})...")
            self._gen.generate(family, chip, chip_config, proj_name, output_path, tmpl_type)
            self._log_msg("Done! Project created at: " + str(output_path))
            QMessageBox.information(self, "Success", f"Project generated at:\n{output_path}")
        except Exception as e:
            self._log_msg(f"Error: {e}")
            QMessageBox.critical(self, "Error", str(e))
```

- [ ] **Step 2: Create main.py entry point**

`main.py`:

```python
import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication

sys.path.insert(0, str(Path(__file__).parent))

from src.gui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Commit**

```bash
git add src/gui/main_window.py main.py
git commit -m "feat: add PyQt6 GUI main window with chip selection and generation"
```

---

### Task 9: Integration test and smoke test

- [ ] **Step 1: Install dependencies**

```bash
pip install pyqt6
```

- [ ] **Step 2: Run unit smoke test on all modules**

```bash
python -c "
from pathlib import Path
from src.core.chip_db import ChipDatabase
from src.core.sdk_manager import SDKManager
from src.core.template_engine import render, copy_file
from src.core.project_generator import ProjectGenerator

# Chip DB
db = ChipDatabase(Path('src/resources/chips'))
db.load()
chip = db.get_chip('GD32F10x', 'GD32F103C8T6')
assert chip is not None
assert chip['core'] == 'Cortex-M3'
print('Chip DB: OK')

# SDK Manager
sdk = SDKManager()
sdk.set_path('GD32', 'E:/IAXX_PMT/OptoCounter')
assert sdk.get_path('GD32')
print('SDK Manager: OK')

# Template Engine
import tempfile
tmp = Path(tempfile.mkdtemp())
tmpl = tmp / 't.c'
tmpl.write_text('x={{VAR}}')
render(tmpl, tmp / 'o.c', {'VAR': 'hello'})
assert 'x=hello' in (tmp / 'o.c').read_text()
print('Template Engine: OK')

# Project Generator
gen = ProjectGenerator(Path('src/resources/templates'), sdk)
gen.generate(
    'GD32F10x', 'GD32F103C8T6', chip,
    'TestProject', tmp / 'test_out', 'empty'
)
assert (tmp / 'test_out' / 'USER' / 'main.c').exists()
assert (tmp / 'test_out' / 'MDK-ARM' / 'TestProject.uvprojx').exists()
assert (tmp / 'test_out' / 'APP').is_dir()
print('Project Generator: OK')
print('ALL TESTS PASSED')
"
```

- [ ] **Step 3: Test GUI launch**

```bash
python main.py
```

Verify the window opens with:
- GD32 SDK path pre-filled (from config)
- Chip family dropdown shows "GD32F10x"
- Sub-chip dropdown populated with chips
- Radio buttons for empty/LED/UART present
- Generate button functional

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "test: add integration smoke test, all modules pass"
```

---

## Self-Review

1. **Spec coverage**: Each spec requirement maps to a task — chip DB (Task 2), SDK manager (Task 4), template engine (Task 3), project generator (Task 5), GUI (Task 8), templates (Task 6+7), code variants (Task 6 Step 3).

2. **Placeholder scan**: No TBD/TODO. All code is complete. All file paths are exact.

3. **Type consistency**: `ChipDatabase.get_chip()` returns dict with same schema used by `ProjectGenerator.generate()`. SDK paths flow through `SDKManager` consistently. Template variables match across `template_engine.py` and `project_generator.py`.
