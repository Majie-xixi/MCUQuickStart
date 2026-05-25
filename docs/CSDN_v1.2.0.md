# 别再手动移植GCC了！MCUQuickStart v1.2.0发布，一键生成Keil+GCC双构建工程

## 前言

做嵌入式开发的都懂三种痛。

**第一种：搭裸机工程。**

每次换芯片、开新项目，第一件事不是写代码，而是**搭工程**。翻SDK找固件库、拷贝启动文件、建Keil工程、配头文件路径、填预定义宏、设内存映射和Flash烧录算法……一套流程走下来，一两个小时就过去了。

**第二种：移植 FreeRTOS。**

如果你还想上个 RTOS？痛苦直接翻十倍：

- 翻 FreeRTOS 官网找匹配你芯片的内核版本，纠结 V9 还是 V10
- 刷论坛帖子、搜移植教程，搞清楚到底用哪个 port 文件——RVDS？GCC？IAR？Keil 用 RVDS，但你得自己试出来
- 手动拷贝 `tasks.c`、`queue.c`、`list.c`……漏了 `timers.c`？又是一个编译错误
- 找到正确的 `port.c` 和 `portmacro.h`——Cortex-M3 和 Cortex-M4F 选错了，调度器直接崩溃
- 从头手写 `FreeRTOSConfig.h`：中断优先级、tick 频率、堆大小——一个 `#define` 写错，HardFault_Handler 就成了你的常客
- **SysTick 冲突**：裸机延时用了 SysTick，FreeRTOS 也需要 SysTick——两个抢同一个定时器
- 无尽的链接错误；晶振和 SDK 默认不一样导致 PLL 全乱；两天过去还在翻 2016 年的帖子

**第三种：移植 GCC + CMake——v1.2.0 重点解决。**

如果你想用 CLion 或 VS Code 写嵌入式代码？恭喜你，地狱难度再来一轮：

- **从零写 CMakeLists.txt**：arm-none-eabi-gcc 那堆编译参数——`-mcpu`、`-mthumb`、`-mfpu`、`-mfloat-abi`——写错一个就编译不过，连试错都不知道从哪个参数开始
- **手写链接脚本 .ld**：MEMORY 段内存地址写偏一位——编译零警告零错误，烧进去直接 HardFault，调试器都连不上，你都不知道是链接脚本的问题
- **GD32 vs STM32 的坑**：你以为找个模板改改就行？GD32 向量表叫 `.vectors` 段、符号是 `__gVectors`，STM32 叫 `.isr_vector` 段、符号是 `g_pfnVectors`——抄错了启动文件直接跳飞
- **启动文件从哪来**：SDK 是给 Keil/ARMCC 设计的，ARM 汇编 GCC 不认。翻遍子目录找 `gcc_ride7`、`TrueSTUDIO`、`Source/GCC`——有的 SDK 压根没 GCC 目录，还得去 Embedded Builder 插件目录大海捞针
- **CMSIS 头文件警告刷屏**：几百条 `misleading-indentation`、`strict-aliasing`、`pointer-sign`——不是你的代码，但每条你都得看
- **链接时缺系统调用桩**：好不容易编译过，链接报 `undefined reference to __libc_init_array`、`_exit`、`_sbrk`——又得手写 `syscalls.c`
- **ARMCC ↔ GCC 语法不兼容**：Keil 的 `__asm void __set_MSP` 到 GCC 变成 `__attribute__((naked))` + `__asm volatile`，ARMCC 的 `#pragma import(__use_no_semihosting)` GCC 压根不认识
- **老 CMSIS 缺定义**：STM32F10x SPL 还带着 2009 年的 CMSIS v1.30，连 `DWT` 结构体都没定义——FreeRTOS 的 DWT 延时直接编译报错
- **双项目同步噩梦**：GCC 项目折腾三天终于跑起来了。然后有人改了 Keil 工程里一个源文件——你的两套项目手工维护，迟早出岔子
- **换芯片重来一遍**：两周过去，CMakeLists.txt 从 50 行膨胀到 200 行。换个芯片？从头再改

**这些跟你的业务逻辑毫无关系，纯属重复体力劳动。**

MCUQuickStart v1.0.0 解决了裸机搭工程的痛，v1.1.0 解决了 FreeRTOS 移植的痛，**v1.2.0 把最后一块拼图——GCC/CMake 双构建——补上了**。

---

## v1.2.0 更新了什么

| 新功能 | 说明 |
|--------|------|
| **GCC + CMake 一键生成** | 勾个选框，自动生成 CMakeLists.txt + 链接脚本 + GCC 启动文件。CLion/VS Code 打开 `CMakeLists.txt` 直接编译。4 系列 37 芯片全部 Keil + GCC 双编译器验证通过 |
| **GD32/STM32 链接脚本自动适配** | 不用纠结 `.vectors` vs `.isr_vector`、`__gVectors` vs `g_pfnVectors`。工具根据芯片厂商自动选正确的链接脚本模板，Cortex-M4 自动加 TCMRAM 段 |
| **GCC 启动文件智能获取** | SDK 自带 GCC 目录→直接复用。没有→递归搜索 GD32 Embedded Builder 插件。都找不到→明确提示官方下载地址，不再大海捞针 |
| **零警告干净编译** | SDK 源文件加 `-w` 全压制（原厂代码不是你的锅），CMSIS/FIRMWARE 头文件标为 `SYSTEM` include，你自己的代码保持 `-Wall`——真正有问题的警告一条不漏 |
| **三编译器兼容** | `sysconfig.c` 的 MSR_MSP 自动分流 ARMCC / GCC / IAR，`retarget_printf.c` 的 semihosting pragma 加 `#ifndef __GNUC__` 守卫 |
| **老 CMSIS 兼容修复** | STM32F10x SPL 自带 CMSIS v1.30 缺 DWT 结构体——`delay.h` 自动补定义，老 SDK 也能用 FreeRTOS 的 DWT 延时 |
| **FreeRTOS 堆优化** | `configTOTAL_HEAP_SIZE` 从 15KB 降到 5KB——C8T6 那种 20KB SRAM 的小芯片也能跑 FreeRTOS |
| **UI 重新设计** | Fusion 主题 + 白底圆角卡片布局 + 等宽日志字体 |

加上 v1.0.0 的裸机工程和 v1.1.0 的 FreeRTOS 一键集成，**裸机、RTOS、Keil、GCC——全场景覆盖**。

---

## 它能做什么

一句话：**选芯片→选模板→(勾FreeRTOS)→(勾GCC+CMake)→点生成，一分钟拿到 Keil5 + CLion/VS Code 双兼容的工程，打开即编译。**

![软件主界面]

目前支持 **37 款芯片**，4 大系列，全部 Keil + GCC 双编译器验证：

| 系列 | 内核 | 厂商 | 型号数 | Keil | GCC |
|------|------|------|--------|------|-----|
| STM32F10x | Cortex-M3 | ST | 9 | ✓ | ✓ |
| STM32F4xx | Cortex-M4 | ST | 6 | ✓ | ✓ |
| GD32F10x | Cortex-M3 | GigaDevice | 8 | ✓ | ✓ |
| GD32F4xx | Cortex-M4 | GigaDevice | 14 | ✓ | ✓ |

三套代码模板：

- **空壳** — 最简 `main()`，裸机、FreeRTOS、Keil、GCC 版本都有
- **LED 闪烁** — GPIO 控制，裸机用 `delay_1ms()`，FreeRTOS 用 `vTaskDelay()`
- **串口打印** — USART printf 重定向，调试利器

可选库：

- **FreeRTOS**（v1.1.0）— 一键生成 RTOS 工程
- **GCC + CMake**（v1.2.0 新增）— 一键生成双构建系统
- **外部晶振**（v1.1.0）— 8MHz / 25MHz 下拉选定

---

## 手动搭建 vs 这个工具

### 裸机工程

| 手动操作 | MCUQuickStart |
|----------|---------------|
| 从 SDK 翻找固件库、启动文件、CMSIS 头文件 | 自动匹配路径并拷贝 |
| 手动创建 `.uvprojx`，逐文件添加到工程 | 自动生成完整 Keil 工程 |
| 对着芯片手册查 RAM/ROM 地址、Flash 算法 | 芯片 JSON 预配置，自动填入 |
| 宏定义写错导致编译报错，排查半天 | 每颗芯片独立 `define`，预设验证过 |
| 换一颗芯片，上面全重来 | 同一界面，下拉选个型号 |

### FreeRTOS 移植

| 手动移植 | MCUQuickStart |
|----------|---------------|
| 翻官网找对内核版本和 port 文件 | 自动匹配 Cortex-M3/M4F 端口 |
| 手动拷贝 7 个内核 .c 文件，漏一个报错 | 自动全量拷贝 |
| 手写 FreeRTOSConfig.h，调中断优先级 | 预配置模板，4 系列独立配置 |
| SysTick 跟裸机延时抢定时器 | DWT 做 us 延迟，不碰 SysTick |
| 两天调不通，翻 2016 年论坛帖 | **勾个框，几秒搞定** |

### GCC + CMake 移植（v1.2.0 新增）

| 手动移植 | MCUQuickStart |
|----------|---------------|
| 从零写 CMakeLists.txt，试 arm-none-eabi-gcc 参数 | 模板自动生成，所有参数预配好 |
| 手写链接脚本 .ld，GD32/STM32 段名不一样 | 自动区分厂商，选正确模板 |
| 满 SDK 找 GCC 启动文件，找不到急得跳脚 | 自动搜索 SDK → Embedded Builder → 提示下载链接 |
| CMSIS 头文件几百条警告刷屏 | SDK 头文件 SYSTEM include 隔离 + SDK 源文件 -w 压制 |
| ARMCC 和 GCC 语法不兼容，逐个文件改 | 模板文件三编译器兼容，自动分流 |
| Keil 和 GCC 两套项目分开维护，逐渐不同步 | **同一个项目文件夹**，Keil/GCC 共享源码 |
| 花三整天从零搭 GCC 工程 | **勾个框，几秒搞定** |

---

## 使用方式

无需安装 Python，一个 exe 搞定：

1. **下载** `MCUQuickStart.exe`（文末链接）
2. **准备 SDK**：芯片固件包 + FreeRTOS 源码（可选）放同一目录
3. **打开软件**：双击 exe → 设置 SDK 根目录
4. **选芯片**：左侧系列 → 右侧型号
5. **选模板**：空壳 / LED / 串口打印
6. **可选**：勾 FreeRTOS、勾 GCC+CMake、选晶振频率
7. **点生成** → Keil MDK 打开 `.uvprojx`，或 CLion/VS Code 打开 `CMakeLists.txt` → 编译 → 一把过

![GCC编译成功效果]

---

## 实际场景

**场景一：新板子验证硬件**

刚到手的 STM32F407VET6，传统做法是网上找例程改来改去。现在——打开工具，选系列→选型号→LED 模板→生成。一分钟，灯闪起来了。想用 CLion？勾上 GCC+CMake，同样直接编译。

**场景二：你习惯用 CLion/VS Code，但新项目只有 Keil 模板**

以前得花一两天手写 CMakeLists.txt、手写链接脚本、找 GCC 启动文件、解决几百条 CMSIS 警告、补系统调用桩……现在——勾选"GCC + CMake"，生成的工程 CLion 直接打开编译。以后换芯片？重新生成一次，不用从头改 CMakeLists.txt。

**场景三：团队里有人用 Keil 调试，有人用 VS Code 写代码**

以前两套工程分开维护，加个源文件两边手动改，迟早出岔子。MCUQuickStart v1.2.0 生成的工程 **Keil 和 GCC 共享同一套源码目录**，永远同步，改一次两边生效。

**场景四：新芯片上跑 FreeRTOS**

选了 GD32F103C8T6，勾选 FreeRTOS——内核源码、ARM_CM3 端口、heap_4、FreeRTOSConfig.h（堆大小已优化为 5KB 适配 20KB SRAM）全自动到位。SysTick 冲突？工具用 DWT 做 us 延时，不碰 SysTick。

**场景五：新人入职 / 学生上手**

还教怎么搭 Keil 工程、怎么配 GCC 工具链、怎么移植 FreeRTOS？把 exe 扔过去，给个 SDK 包。零学习成本，一分钟出活。

---

## 原理简述

数据驱动架构。每款芯片的参数——启动文件、Flash 驱动、内存映射、预编译宏、排除的外设文件——全部存在 JSON 里。模板文件用 `{{PLACEHOLDER}}` 占位符，生成时替换。加新芯片不改代码，只加 JSON + 模板。

GCC/CMake 也是同样的思路：芯片 JSON 配置好 MCPU、FPU 参数、TCMRAM，链接脚本按 GD32/STM32 分两套模板，CMakeLists.txt 的源文件列表由 Python 预生成自动过滤不兼容文件。GCC 启动文件从 SDK 或 Embedded Builder 实时获取，不打包在工具里。

---

## 系统要求

- Windows 10 及以上
- Keil MDK V5（Keil 编译用）
- arm-none-eabi-gcc 工具链（GCC 编译用，CLion 用户自行安装）
- 对应芯片的 SDK 固件包
- FreeRTOS Kernel V10.x 源码（可选，用于 RTOS 工程）

---

## 下载地址

GitHub Release：**[https://github.com/Majie-xixi/MCUQuickStart/releases](https://github.com/Majie-xixi/MCUQuickStart/releases)**

下载 `MCUQuickStart.exe` 直接运行，无需安装。

> 如果觉得好用，⭐ **Star** 支持一下，让更多嵌入式同行看到！

---

## 总结

v1.0.0 解决了裸机工程搭建，v1.1.0 解决了 FreeRTOS 移植，**v1.2.0 解决了 GCC/CMake 双构建**——至此，裸机、RTOS、Keil、GCC 四大场景全部覆盖。

做嵌入式的都知道，从 Keil 换到 GCC 有多折腾。手写 CMakeLists.txt + 链接脚本 + 找启动文件 + 压制警告 + 处理编译器兼容——三天起步，还不算换芯片的重复劳动。

把这些全部自动化之后，你只用做一件事：**选芯片，勾需求，点生成。** 精力花在业务代码上，而不是跟工具链斗智斗勇。

后续计划加更多芯片系列（GD32F3xx、STM32G0 等），有什么需求欢迎在 GitHub Issues 里提。

*原创文章，转载注明出处。*
