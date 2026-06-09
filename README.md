# MCUQuickStart

## One Click, Ready to Compile — Stop Wasting Time Setting Up MCU Projects

Every embedded developer knows the pain: you get a new board, fire up Keil, and then spend the next **one to two hours** just scaffolding the project:

- Hunt through SDK folders for firmware libraries, startup files, and CMSIS headers
- Manually create a Keil project, add file groups, configure include paths
- Look up the chip reference manual for RAM/ROM addresses and flash algorithms
- Fill in preprocessor defines, fix compilation errors from mismatched macros
- Repeat the entire process every time you switch to a different MCU

And if you want **FreeRTOS** or **RT-Thread Nano**? Multiply the pain by ten:

- Dig through FreeRTOS.org to find the right kernel version that matches your chip
- Scroll through forum posts and tutorials to figure out which port files you need (RVDS? GCC? IAR?)
- Manually copy `tasks.c`, `queue.c`, `list.c`... did you forget `timers.c`? That's another compile error
- Hunt down the right `port.c` and `portmacro.h` for Cortex-M3 vs Cortex-M4F — get it wrong and the scheduler silently crashes
- Write `FreeRTOSConfig.h` from scratch: interrupt priorities, tick rate, heap size — one wrong `#define` and your HardFault_Handler becomes your new best friend
- SysTick collision: your bare-metal delay uses SysTick, FreeRTOS needs SysTick — now both are fighting over the same timer
- Endless linker errors: missing `xPortSysTickHandler`, undefined `vTaskDelay`, implicit `printf` in `configASSERT`
- Finally get it to compile, flash it, and... nothing. The scheduler never starts because you didn't call `NVIC_PriorityGroupConfig`
- Two days later you're still reading forum posts from 2016 trying to figure out why `vTaskDelay(500)` takes 3 seconds


And if you want to use **GCC + CMake** with CLion or VS Code? Brace yourself for another round of toolchain hell:

- Create a CMakeLists.txt from scratch, learning arm-none-eabi-gcc flags the hard way — -mcpu, -mthumb, -mfpu, -mfloat-abi — get one wrong and nothing compiles
- Write a linker script (.ld) by hand — misplace a single memory address digit and your board hard-faults on boot with zero compiler warnings
- You think you can just tweak a template? GD32 uses .vectors section + __gVectors, STM32 uses .isr_vector + g_pfnVectors — copy the wrong one and your startup file jumps into the void
- Where do the GCC startup files come from? The SDK was designed for Keil/ARMCC. Dig through subdirectories for gcc_ride7, TrueSTUDIO, Source/GCC — some SDKs have none, you're off hunting through Embedded Builder plugin folders
- CMSIS headers vomiting hundreds of warnings: misleading-indentation, strict-aliasing, pointer-sign — not your code, but you have to read every single one
- It finally compiles, then linking fails: undefined reference to __libc_init_array, _exit, _sbrk — missing system call stubs, time to hand-write syscalls.c
- STM32F10x still ships with CMSIS v1.30 from 2009 — the DWT struct doesn't even exist, so FreeRTOS DWT delays won't compile
- Keil's __asm void __set_MSP becomes __attribute__((naked)) + __asm volatile in GCC; ARMCC's #pragma import(__use_no_semihosting) means nothing to GCC
- After three days the GCC project finally works — then someone changes a source file in the Keil project, and your two build systems drift out of sync
- Two weeks later your CMakeLists.txt has ballooned from 50 lines to 200, and you have to redo everything for a different chip — you start questioning your life choices

**Why spend days porting to GCC when a checkbox can do it for you?**

**RT-Thread Nano** is another beast entirely — the official examples target GCC/ARMCC V6, but your Keil project likely compiles with ARMCC V5 C90. C99 variable declarations, FinSH command macros with spaces in parameters, `$Sub$$main` linker tricks that don't work under Microlib — every C99-ism becomes a compile error. Then there's `board.c`: you don't just copy it — you have to rewrite it from HAL to Standard Peripheral Library for your specific chip family. And when it finally compiles, the scheduler hangs on first context switch because FPU, NVIC priorities, Microlib, or heap settings are wrong. **Three full days of debugging for a blinking LED.**


**MCUQuickStart automates all of this. Bare-metal, FreeRTOS, RT-Thread Nano, GCC + CMake — pick your芯片, pick a template, check a box, click generate. A compilable Keil5 or CLion/VS Code project in under a minute.**

---

## Why This Saves You Hours

### Before vs After

| Manual Setup | MCUQuickStart |
|--------------|---------------|
| Dig through SDK folders for the right files | Auto-locates and copies everything you need |
| Manually create `.uvprojx`, add files one by one | Auto-generates the complete Keil project |
| Look up memory map and flash algorithm in the datasheet | Chip JSON has all config pre-loaded |
| Guess the wrong `#define` and debug compile errors | Per-chip defines, verified correct |
| Spend days porting GCC: write CMake + linker script + hunt startup files | Check a box \u2014 dual-build project, Keil + GCC |
| Spend 2 days porting FreeRTOS, fighting SysTick conflicts | Check a box — kernel, port, heap, config all done |
| Spend 3 days porting RT-Thread Nano, rewriting board.c from HAL to SPL, debugging C90 compile errors and PendSV crashes | Check a box — board.c, rtconfig.h, interrupt stubs, kernel all done |

### Real-World Scenarios

- You just got a new board (e.g. STM32F407VET6) and want to blink an LED to verify hardware — **done in 1 minute**
- You need to compare peripheral driver APIs between STM32F1 and GD32F1 — **generate two projects with two clicks**
- A new team member joins and has never set up a Keil project — **give them the exe, zero ramp-up**
- You want to try FreeRTOS on a new chip — instead of spending days finding port files, writing config, debugging SysTick conflicts, and hunting linker errors — **check a box, done in seconds**
- You want to try RT-Thread Nano — instead of rewriting board.c from HAL to SPL, fighting C90 compile errors, and debugging PendSV crashes — **check a box, done in seconds**
- Your board has a different crystal than the SDK default — instead of reading the datasheet to recalculate PLL parameters — **pick 8MHz or 25MHz from a dropdown\n- You prefer coding in CLion or VS Code, but the new chip only has Keil project templates \u2014 **check \"GCC + CMake\" and open the project in your favorite IDE instantly****

---

## What's New in v1.3.0

| Feature | What it does |
|---------|--------------|
| **RT-Thread Nano One-Click** | Check a box to generate an RT-Thread Nano project. Auto-generates `board.c` (HAL→Standard Peripheral Library adapted), `rtconfig.h`, interrupt stubs, and 3 application templates. Kernel, FinSH, mem/slab/memheap — all wired up. Mutually exclusive with FreeRTOS |
| **ARMCC V5 C90 Battle-Tested** | RT-Thread source targets GCC/ARMCC V6. 10+ C90 compatibility fixes baked into templates: `RT_USING_LIBC`, FinSH disabled for C90, `$Sub$$main`/Microlib awareness, C99 mode, static heap, FPU/NVIC config — every trap we hit is now handled |
| **SDK Auto-Extract** | `.zip` and `.7z` archives in the SDK directory are auto-extracted on first run. No manual unzipping |
| **About Dialog** | About button with project intro + GitHub/Gitee links, bilingual |

## What's New in v1.1.0

| Feature | What it does |
|---------|--------------|
| **FreeRTOS One-Click** | Check a box to generate an RTOS project. V10.x kernel, Cortex-M3/M4F ports, heap_4, pre-configured config — all wrapped up. No forum diving, no SysTick debugging |
| **Crystal Selector** | Pick 8 MHz or 25 MHz external crystal. Tool auto-corrects PLL macros, `PLL_M`, `HSE_VALUE` — no datasheet diving |
| **GD32F470 Support** | 5 new models added (VGT6/ZET6/ZGT6/ZIT6/IIH6), GD32F4xx family now 14 chips |
| **Built-in Help** | Click the help button for a step-by-step usage guide in English and Chinese |
| **English UI Default** | Switchable to Chinese |
| **Bug Fixes** | `printf` warnings, UART retargeting, crystal clock mismatch, and more — all ironed out |

## What's New in v1.2.0
| Feature | What it does |
|---------|--------------|
| **GCC + CMake One-Click** | Check a box to generate CMakeLists.txt + linker script + GCC startup files. Open in CLion or VS Code, hit build \u2014 it just works. 4 families, 37 chips, all verified with both compilers |
| **GD32 vs STM32 Auto Linker** | No more .vectors vs .isr_vector confusion. The tool picks the correct linker template for each vendor. CCM/TCM RAM auto-included for Cortex-M4 |
| **Smart GCC Startup Resolution** | SDK has a GCC folder? Uses it directly. No? Recursively searches GD32 Embedded Builder plugin folder. Still nothing? Prompts the official download URL |
| **Zero-Warning Clean Build** | SDK source code is the vendor's, not yours. CMSIS/FIRMWARE headers marked as SYSTEM includes, SDK sources compiled with -w. Your code gets -Wall \u2014 clean, actionable output |
| **Triple-Compiler Compatible** | sysconfig.c MSR_MSP auto-adapts to ARMCC / GCC / IAR. retarget_printf.c semihosting pragma guarded with #ifndef __GNUC__. Zero errors when moving to GCC |
| **Legacy CMSIS Fix** | STM32F10x SPL ships CMSIS v1.30 without DWT struct \u2014 delay.h auto-adds the missing definition. Old SDKs can now use FreeRTOS DWT delays |
| **FreeRTOS Heap Tuned** | configTOTAL_HEAP_SIZE reduced from 15KB to 5KB \u2014 small-RAM chips like C8T6 (20KB SRAM) can now run FreeRTOS |
| **UI Redesign** | Fusion theme + card-style layout with rounded corners + monospace log font \u2014 looks clean, works clean |

## Supported Chips (37 Models)

| Series | Core | Vendor | Models |
|--------|------|--------|--------|
| STM32F10x | Cortex-M3 | STMicro | 9 |
| STM32F4xx | Cortex-M4 | STMicro | 6 |
| GD32F10x | Cortex-M3 | GigaDevice | 8 |
| GD32F4xx | Cortex-M4 | GigaDevice | 14 |

> 37 chip models across 4 families — all verified to compile out of the box.

---

## Project Templates

- **Empty** — Minimal `main()`, clean starting point
- **LED Blink** — GPIO init + delay, verify your hardware works
- **UART Printf** — USART printf redirection, your debug console

---

## System Requirements

- Windows 10 or later
- Keil MDK V5 (to compile generated projects)
- The corresponding chip SDK package (see below)

---

## SDK Preparation

Place these official SDK packages in a single folder:

| Package | Required For |
|---------|-------------|
| STM32F10x_StdPeriph_Lib | STM32F1 series |
| STM32F4xx_DSP_StdPeriph_Lib | STM32F4 series |
| GD32F10x_Firmware_Library | GD32F1 series |
| GD32F4xx_Firmware_Library | GD32F4 series |
| FreeRTOS Kernel V10.x | RTOS projects *(optional)* |
| RT-Thread Nano V3.x | RT-Thread projects *(optional)* |

The tool auto-detects the correct subfolder — no renaming needed.

---

## How to Use

1. **Prepare SDK** — Put your chip SDK packages under a single directory
2. **Launch** — Double-click `MCUQuickStart.exe` (no installation needed)
3. **Set SDK Root** — Browse and select the SDK directory
4. **Pick a Chip** — Select series on the left, specific model on the right
5. **Pick a Template** — Empty / LED Blink / UART Printf
6. **Optional** — Check FreeRTOS or RT-Thread Nano (mutually exclusive), select external crystal frequency, check GCC+CMake for CLion/VS Code
7. **Generate** — Name your project, choose output directory, click "Generate Project"
8. **Compile** — Open `MDK-ARM/<project>.uvprojx` in Keil5, hit build — it just works

---

## Download

Get the latest `MCUQuickStart.exe` from the [Releases](https://github.com/Majie-xixi/MCUQuickStart/releases) page.

---

## License

Free for personal, educational, and non-commercial use. Commercial use (including but not limited to selling, bundling with paid products, or providing as a paid service) requires explicit permission from the author. If you are unsure whether your use case qualifies, please contact the author.

---

中文用户请查看 [中文说明](README_CN.md)

---

:star: **If this tool saves you time, please star this repo — it helps others discover it too!**
