# MCUQuickStart

One-click MCU project generator for STM32/GD32.

Pick a chip, choose a template, enable FreeRTOS / RT-Thread Nano / GCC+CMake if needed, then generate a ready-to-build Keil or CMake project in under a minute.

[中文说明](README_CN.md)

| Light | Dark |
| --- | --- |
| ![MCUQuickStart light UI](docs/images/ui-light.png) | ![MCUQuickStart dark UI](docs/images/ui-dark.png) |

## Why This Exists

Setting up an MCU project is boring work that still goes wrong too often:

- Find the right SDK folders, CMSIS headers, startup files, and firmware sources
- Create a Keil project and add file groups one by one
- Configure include paths, preprocessor macros, RAM/ROM ranges, and flash algorithms
- Port FreeRTOS or RT-Thread Nano without breaking SysTick, PendSV, heap, or ARMCC V5 compatibility
- Build a parallel GCC/CMake project without hand-writing linker scripts and startup glue

MCUQuickStart turns that setup work into a few selections in a GUI.

## Highlights

| Feature | What You Get |
| --- | --- |
| Chip-aware project generation | Correct startup file, device define, memory map, flash algorithm, and include paths |
| Keil MDK project output | Complete `.uvprojx` project with generated file groups |
| GCC + CMake output | `CMakeLists.txt`, linker script, GCC startup file lookup, CLion / VS Code friendly layout |
| FreeRTOS integration | Kernel files, Cortex-M3/M4F port, heap_4, `FreeRTOSConfig.h`, SysTick-aware templates |
| RT-Thread Nano integration | `rtconfig.h`, `board.c`, interrupt stubs, ARMCC V5/C90 compatibility fixes |
| SDK auto-detection | Finds SDK folders automatically and can extract `.zip` / `.7z` packages |
| Crystal selector | 8 MHz / 25 MHz HXTAL selection with generated clock macro fixes |
| Light / dark UI | Clean PyQt6 interface with switchable themes |

## Supported Chips

37 models across 4 families:

| Series | Core | Vendor | Models |
| --- | --- | --- | --- |
| STM32F10x | Cortex-M3 | STMicroelectronics | 9 |
| STM32F4xx | Cortex-M4 | STMicroelectronics | 6 |
| GD32F10x | Cortex-M3 | GigaDevice | 8 |
| GD32F4xx | Cortex-M4 | GigaDevice | 14 |

## Project Templates

- **Empty**: minimal `main()` and clean startup point
- **LED Blink**: GPIO initialization plus delay, useful for board bring-up
- **UART Printf**: USART printf retargeting for debug output

Each template can be generated as bare-metal, FreeRTOS, or RT-Thread Nano. GCC+CMake can also be generated alongside Keil.

## Quick Start

1. Download `MCUQuickStart.exe` from [Releases](https://github.com/Majie-xixi/MCUQuickStart/releases).
2. Put the required SDK packages in one directory.
3. Start MCUQuickStart and set that directory as **SDK Root**.
4. Select chip family, chip model, project name, output directory, and code template.
5. Optionally enable FreeRTOS, RT-Thread Nano, and/or GCC+CMake.
6. Click **Generate Project**.
7. Build with Keil MDK V5, or open the generated CMake project in CLion / VS Code.

## SDK Packages

Place these official SDK packages under the same SDK root directory:

| Package | Used For |
| --- | --- |
| `STM32F10x_StdPeriph_Lib` | STM32F1 projects |
| `STM32F4xx_DSP_StdPeriph_Lib` | STM32F4 projects |
| `GD32F10x_Firmware_Library` | GD32F1 projects |
| `GD32F4xx_Firmware_Library` | GD32F4 projects |
| FreeRTOS Kernel V10.x | Optional FreeRTOS projects |
| RT-Thread Nano V3.x | Optional RT-Thread Nano projects |

The tool searches common SDK layouts automatically. Archives in the SDK root can be auto-extracted on first use.

## Real Use Cases

- Bring up a new STM32/GD32 board and blink an LED quickly
- Generate comparable STM32 and GD32 projects to compare standard peripheral APIs
- Give a new team member a ready-to-build Keil project without teaching all setup details first
- Try FreeRTOS or RT-Thread Nano on a supported chip without manually copying kernel and port files
- Use CLion or VS Code with chips whose official examples are Keil-first

## Version Highlights

### v1.3.0

- RT-Thread Nano one-click project generation
- ARMCC V5 / C90 compatibility handling for RT-Thread Nano
- SDK `.zip` / `.7z` auto-extract
- About dialog with GitHub / Gitee links

### v1.2.0

- GCC + CMake project generation
- Vendor-specific linker script selection for STM32/GD32
- GCC startup file lookup, including GD32 Embedded Builder fallback
- Cleaner GCC builds by suppressing vendor SDK warnings while keeping user code warnings useful

### v1.1.0

- FreeRTOS one-click integration
- External crystal selection
- GD32F470 support
- Built-in bilingual help

## Build From Source

```bash
pip install -r requirements.txt
python main.py
```

The GUI is built with PyQt6.

## Roadmap Ideas

- More chip families
- More board-level templates
- Optional lwIP integration for Ethernet-capable MCUs
- More generated examples for RTOS projects

## License

MCUQuickStart is released under the GNU General Public License v3.0.
See [LICENSE](LICENSE) for the full license text.

This project does not redistribute vendor SDK packages. Generated projects may include
files copied from the user's local STM32/GD32 SDK, FreeRTOS, or RT-Thread Nano
installation, and those copied files remain subject to their original licenses.

STM32 is a trademark of STMicroelectronics. GD32 is a trademark of GigaDevice.
Keil and Arm are trademarks of Arm Limited. All trademarks are the property of
their respective owners. MCUQuickStart is not affiliated with or endorsed by
these companies.

## Star History

If MCUQuickStart saves you time, a GitHub star helps more embedded developers find it.
