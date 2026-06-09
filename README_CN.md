# MCUQuickStart

## 一键生成，打开即编译 — 别再浪费时间搭建 MCU 工程了

每个嵌入式开发者都懂这种痛苦：拿到一块新板子，打开 Keil，然后花上一两个小时就为了搭个工程骨架：

- 在 SDK 目录里翻找固件库、启动文件、CMSIS 头文件
- 手动建 Keil 工程，一个一个加文件组，配 include 路径
- 翻数据手册查 RAM/ROM 地址和 Flash 烧录算法
- 填预处理器宏，修因宏不匹配导致的编译错误
- 换一颗芯片，以上全部重来一遍

如果你想上 **FreeRTOS** 或 **RT-Thread Nano**？痛苦翻十倍：

- 翻 FreeRTOS 官网找匹配你芯片的内核版本
- 刷论坛帖子、搜移植教程，搞清楚到底用哪个 port 文件（RVDS？GCC？IAR？）
- 手动拷贝 `tasks.c`、`queue.c`、`list.c`……是不是漏了 `timers.c`？好的，又一个编译错误
- 找到正确的 `port.c` 和 `portmacro.h` — Cortex-M3 和 Cortex-M4F 不一样，选错了调度器直接崩溃
- 从头写 `FreeRTOSConfig.h`：中断优先级、tick 频率、堆大小——一个 `#define` 写错，HardFault_Handler 就是你最好的朋友
- SysTick 冲突：你的裸机延时用了 SysTick，FreeRTOS 也需要 SysTick——两个抢同一个定时器
- 无尽的链接错误：找不到 `xPortSysTickHandler`、未定义的 `vTaskDelay`、`configASSERT` 里 `printf` 隐式声明
- 好不容易编译过了，烧进去……什么都没发生。调度器没启动，因为你忘了配 `NVIC_PriorityGroupConfig`
- 两天过去了，你还在翻 2016 年的论坛帖子，试图搞懂为什么 `vTaskDelay(500)` 延时了 3 秒

**还想用 **GCC + CMake** 配 CLion 或 VS Code？地狱难度再来一轮：

- 新建 CMakeLists.txt，从零学 arm-none-eabi-gcc 那堆编译参数 —— -mcpu、-mthumb、-mfpu、-mfloat-abi，哪个写错都编译不过
- 手写链接脚本 .ld —— MEMORY 段内存地址写偏一个数字，编译零警告零错误，烧进去直接 HardFault，调试器都连不上
- 想找个模板改改？GD32 向量表叫 .vectors 段、符号是 __gVectors，STM32 叫 .isr_vector 段、符号是 g_pfnVectors —— 抄错了启动文件直接跳飞
- 启动文件从哪来？SDK 是给 Keil 准备的，ARM 汇编 GCC 不认。翻遍子目录找 gcc_ride7、TrueSTUDIO、Source/GCC —— 有的 SDK 压根没有，还得去 Embedded Builder 插件目录大海捞针
- CMSIS 头文件哗哗哗几百条警告 —— misleading-indentation、strict-aliasing、pointer-sign —— 不是你的代码，但每条都得看
- 好不容易编译过，链接报 undefined reference to __libc_init_array、_exit、_sbrk —— 缺系统调用桩，又得手写 syscalls.c
- STM32F10x 还用着 2009 年的 CMSIS v1.30，连 DWT 结构体都没定义 —— FreeRTOS 的 DWT 延时直接编译报错
- Keil 的 __asm void __set_MSP 到 GCC 变成 __attribute__((naked)) + __asm volatile，ARMCC 的 #pragma import(__use_no_semihosting) GCC 压根不认识
- GCC 项目折腾三天终于能跑了，有人改 Keil 工程里一个源文件 —— 两套项目手工同步，迟早出岔子
- 两周过去，CMakeLists.txt 从 50 行膨胀到 200 行，换芯片又要重改一遍 —— 你开始怀疑人生

**花一整天移植 GCC 踩坑，还是勾一个框？MCUQuickStart 帮你省掉的不只是时间，是头发。**

**RT-Thread Nano** 又是另一个坑 —— 官方示例面向 GCC/ARMCC V6，你手上的 Keil 项目大概率是 ARMCC V5 C90。C99 变量声明、FinSH 命令宏参数带空格、`$Sub$$main` 链接器魔法在 Microlib 下不工作……每条 C99 写法都变成编译报错。还有 `board.c`：不是复制就行，得把 HAL 改成标准库，每个系列都不一样。好不容易编译过了，调度器第一次上下文切换就死机 —— FPU、NVIC 优先级、Microlib、heap 配置，任一不对就是 PendSV crash。**点个 LED 调试了三天。**\n\nMCUQuickStart 把这些全部自动化。裸机、FreeRTOS、RT-Thread Nano、GCC + CMake —— 选芯片，选模板，勾个选框，点生成。一分钟内拿到可直接编译的 Keil5 工程。**

---

## 为什么能省你几个小时

### 手动 vs 工具

| 手动搭建 | MCUQuickStart |
|----------|---------------|
| 翻 SDK 文件夹找对应文件 | 自动定位并拷贝固件库、启动文件、CMSIS 头文件、FreeRTOS 源码 |

## v1.3.0 新增

| 功能 | 说明 |
|------|------|
| **RT-Thread Nano 一键集成** | 勾选即生成 RT-Thread Nano 工程。自动生成 `board.c`（HAL→标准库适配）、`rtconfig.h`、中断转发桩、3 套应用模板。内核、FinSH、mem/slab/memheap 全部配置到位。与 FreeRTOS 互斥 |
| **ARMCC V5 C90 兼容全覆盖** | RT-Thread 源码面向 GCC/ARMCC V6。模板内置 10+ 项 C90 兼容修复：`RT_USING_LIBC`、FinSH 对 C90 禁用、`$Sub$$main`/Microlib 感知、C99 模式、静态堆、FPU/NVIC 配置 —— 踩过的坑全部填平 |
| **SDK 自动解压** | SDK 目录下的 .zip/.7z 压缩包首次运行时自动解压，无需手动操作 |
| **About 对话框** | 左上角新增"关于"按钮，显示软件简介 + GitHub/Gitee 项目地址，中英双语 |

## v1.2.0 新增

| 功能 | 说明 |
|------|------|
| **GCC + CMake 一键生成** | 勾选后自动生成 CMakeLists.txt + 链接脚本 + GCC 启动文件。CLion/VS Code 打开 CMakeLists.txt 直接编译。4 系列 37 个芯片全部双编译器验证通过，Keil 和 GCC 都零警告 |
| **GD32/STM32 链接脚本自动适配** | 不用纠结 .vectors vs .isr_vector、__gVectors vs g_pfnVectors。工具根据芯片厂商自动选正确的链接脚本模板，Cortex-M4 自动加 TCMRAM 段 |
| **GCC 启动文件智能获取** | SDK 自带 GCC 目录？直接复用。没有？递归搜索 GD32 Embedded Builder 插件目录。都找不到？明确提示官方下载地址 —— 不再让你大海捞针 |
| **零警告干净编译** | SDK 源码是原厂写的，不是你的锅。CMSIS/FIRMWARE 头文件标为 SYSTEM include，SDK 源文件加 -w 全压制，你自己的代码保持 -Wall，真正有问题的一条不漏 |
| **三编译器兼容** | sysconfig.c 的 MSR_MSP 自动分流 ARMCC / GCC / IAR，retarget_printf.c 的 semihosting pragma 加 GNUC 守卫。搬到 GCC 零报错 |
| **老 CMSIS 兼容** | STM32F10x SPL 自带的 CMSIS v1.30 缺 DWT 结构体 —— delay.h 自动补定义，老 SDK 也能用 FreeRTOS 的 DWT 延时 |
| **FreeRTOS 堆栈优化** | configTOTAL_HEAP_SIZE 从 15KB 降到 5KB —— C8T6 那种 20KB SRAM 的小芯片也跑得起来 |
| **UI 重新设计** | Fusion 主题 + 白底圆角卡片布局 + 等宽日志字体 —— 看着顺眼，用着顺手 |

> **37 芯片 x 4 系列 x 3 模板 x 双构建系统 x FreeRTOS 可选 —— 全部验证，编译即过。**

---

贝所需全部文件 |
| 手动建 `.uvprojx`，逐个加文件 | 自动生成完整 Keil 工程 |
| 查数据手册配内存映射和烧录算法 | 芯片 JSON 预置全部配置 |
| 猜错 `#define` 然后修编译错误 | 每颗芯片独立配置，经验证正确 |
| 换芯片就从头来 | 同一界面，换个型号即可 |
| 花两天移植 FreeRTOS，跟 SysTick 斗智斗勇 | 勾个框——内核、端口、内存管理、配置文件全搞定 |
| 花三天移植 RT-Thread Nano，从 HAL 改 SPL 写 board.c，C90 编译报错、PendSV 死机挨个排查 | 勾个框——board.c、rtconfig.h、中断转发、内核全部就绪 |

### 真实场景

- 刚到手的 STM32F407VET6 板子，想点个灯验证硬件 — **1 分钟搞定**
- 想对比 STM32F1 和 GD32F1 的外设驱动 API — **点两下生成两个工程**
- 新同事没搭过 Keil 工程 — **给他 exe，零学习成本**
- 想在新芯片上跑 FreeRTOS — 不用花几天找 port 文件、写配置、调 SysTick 冲突、修链接错误 — **勾个选框，几秒搞定**
- 想在新芯片上跑 RT-Thread Nano — 不用花三天从 HAL 改 SPL 写 board.c、跟 C90 编译错误较劲、排查 PendSV 死机 — **勾个选框，几秒搞定**
- 板子晶振跟 SDK 默认不一样 — 不用翻数据手册重算 PLL 参数 — **下拉选 8MHz / 25MHz 即可
- 你用惯了 CLion 或 VS Code 写代码，但新芯片只有 Keil 工程模板 —— **勾选 GCC + CMake，直接用你熟悉的 IDE 打开编译****

---

## v1.1.0 新增

| 功能 | 说明 |
|------|------|
| **FreeRTOS 一键集成** | 勾选即生成 RTOS 工程，V10.x 内核 + Cortex-M3/M4F 端口 + heap_4 + 预配置。不用翻论坛、不用调 SysTick |
| **外部晶振选择** | 下拉框选 8 MHz / 25 MHz，工具自动修正 PLL 宏、`PLL_M`、`HSE_VALUE`，不用翻数据手册 |
| **GD32F470 系列** | 新增 5 款型号（VGT6 / ZET6 / ZGT6 / ZIT6 / IIH6），GD32F4xx 家族 14 款 |
| **内置使用说明** | 点击帮助按钮弹出分步指南，中英双语 |
| **默认英文界面** | 可切换中文 |
| **Bug 修复** | `printf` 警告、串口重定向、晶振时钟不匹配等问题全部解决 |

---

## 支持芯片（37 款）

| 系列 | 内核 | 厂商 | 型号数 |
|------|------|------|--------|
| STM32F10x | Cortex-M3 | ST | 9 |
| STM32F4xx | Cortex-M4 | ST | 6 |
| GD32F10x | Cortex-M3 | GD | 8 |
| GD32F4xx | Cortex-M4 | GD | 14 |

> 4 大系列 37 款芯片 — 全部验证可编译通过。

---

## 工程模板

- **空壳** — 最简 `main()`，干净起点
- **LED 闪烁** — GPIO 初始化 + 延时，快速验证硬件
- **串口打印** — USART printf 重定向，调试控制台

---

## 环境要求

- Windows 10 及以上
- Keil MDK V5（用于编译生成的工程）
- 对应芯片的 SDK 包（见下方）

---

## SDK 准备

将以下官方 SDK 包放在同一目录下：

| 包名 | 用途 |
|------|------|
| STM32F10x_StdPeriph_Lib | STM32F1 系列 |
| STM32F4xx_DSP_StdPeriph_Lib | STM32F4 系列 |
| GD32F10x_Firmware_Library | GD32F1 系列 |
| GD32F4xx_Firmware_Library | GD32F4 系列 |
| FreeRTOS Kernel V10.x | RTOS 工程（可选） |
| RT-Thread Nano V3.x | RT-Thread 工程（可选） |

工具自动前缀匹配子目录，无需重命名。

---

## 使用方法

1. **准备 SDK** — 把芯片 SDK 包放在同一个目录下
2. **启动** — 双击 `MCUQuickStart.exe`（无需安装）
3. **设置 SDK 根目录** — 浏览选择 SDK 所在目录
4. **选择芯片** — 左边选系列，右边选具体型号
5. **选择模板** — 空壳 / LED 闪烁 / 串口打印
6. **可选** — 勾选 FreeRTOS 或 RT-Thread Nano（互斥），选择外部晶振频率，勾选 GCC+CMake 可适配 CLion/VS Code
7. **生成** — 填项目名称，选输出目录，点"生成工程"
8. **编译** — Keil5 打开 `MDK-ARM/<项目名>.uvprojx`，点编译 — 直接过

---

## 下载

从 [Releases](https://github.com/Majie-xixi/MCUQuickStart/releases) 页面下载 `MCUQuickStart.exe`。

---

## 许可

个人、教育及非商业用途免费使用。商业用途（包括但不限于销售、捆绑付费产品或作为付费服务提供）需经作者明确授权。如有疑问请联系作者。

---

:star: **如果这个工具帮你省了时间，请给个 Star — 让更多人发现它！**
