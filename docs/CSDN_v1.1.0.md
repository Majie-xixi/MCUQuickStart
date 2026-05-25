# 别再手动移植FreeRTOS了！MCUQuickStart v1.1.0发布，一键生成Keil工程+RTOS模板

## 前言

做嵌入式开发的都懂两种痛。

**第一种：搭裸机工程。**

每次换芯片、开新项目，第一件事不是写代码，而是**搭工程**。翻SDK找固件库、拷贝启动文件、建Keil工程、配头文件路径、填预定义宏、设内存映射和Flash烧录算法……一套流程走下来，一两个小时就过去了。

**第二种：移植 FreeRTOS。**

如果你还想上个 RTOS？痛苦直接翻十倍：

- 翻 FreeRTOS 官网找匹配你芯片的内核版本，纠结 V9 还是 V10
- 刷论坛帖子、搜移植教程，搞清楚到底用哪个 port 文件——RVDS？GCC？IAR？Keil 用 RVDS，但你得自己试出来
- 手动拷贝 `tasks.c`、`queue.c`、`list.c`……漏了 `timers.c`？好的，又是一个编译错误
- 找到正确的 `port.c` 和 `portmacro.h`——Cortex-M3 和 Cortex-M4F 选错了，调度器直接崩溃
- 从头手写 `FreeRTOSConfig.h`：中断优先级、tick 频率、堆大小、是否抢占……一个 `#define` 写错，HardFault_Handler 就成了你的常客
- **SysTick 冲突**：你的裸机延时用了 SysTick，FreeRTOS 也需要 SysTick——两个抢同一个定时器，延时函数全乱
- 无尽的链接错误：`xPortSysTickHandler` 未定义、`vTaskDelay` 找不到、`configASSERT` 里 `printf` 隐式声明
- 好不容易编译过了，烧进去……灯不闪。调度器根本没启动，因为你忘了 `NVIC_PriorityGroupConfig`
- 你板子的晶振是 8MHz，SDK 默认配的 25MHz——`vTaskDelay(500)` 延时了三秒
- 两天过去了，你还在翻 2016 年的论坛帖子，试图搞懂为什么调度器不跑

**这些跟你的业务逻辑毫无关系，纯属重复体力劳动。**

于是我写了 MCUQuickStart，昨天刚发了 v1.0.0，今天直接迭代到 **v1.1.0**——最大的更新就是：**FreeRTOS 一键集成**。

---

## v1.1.0 更新了什么

| 新功能 | 说明 |
|--------|------|
| **FreeRTOS 一键集成** | 勾个选框，自动生成 RTOS 工程——内核源码、Cortex-M3/M4F 端口、heap_4 内存管理、预配置的 FreeRTOSConfig.h，全部就位 |
| **外部晶振选择** | 下拉框选 8MHz / 25MHz，工具自动修正 PLL 宏、PLL_M、HSE_VALUE——不用翻数据手册 |
| **GD32F470 系列** | 新增 5 款：VGT6、ZET6、ZGT6、ZIT6、IIH6 |
| **使用说明按钮** | 中英文双语使用指南，内置在界面上 |
| **默认英文界面** | 可切中文 |

加上 v1.0.0 已有的裸机工程生成能力，现在**裸机和 RTOS 都能一键生成**。

---

## 它能做什么

一句话：**选芯片→选模板→(勾FreeRTOS)→点生成，一分钟拿到打开即编译的 Keil5 工程。**

![主界面](https://i-blog.csdnimg.cn/img_convert/70639dc6e2641a288d79fe0f917aba72.png)

目前支持 **37 款芯片**，4 大系列：

| 系列 | 内核 | 厂商 | 型号数 |
|------|------|------|--------|
| STM32F10x | Cortex-M3 | ST | 9 |
| STM32F4xx | Cortex-M4 | ST | 6 |
| GD32F10x | Cortex-M3 | GigaDevice | 8 |
| GD32F4xx | Cortex-M4 | GigaDevice | **14**（v1.1.0 新增 F470×5） |

三套代码模板：

- **空壳** — 最简，裸机和 FreeRTOS 版本都有
- **LED 闪烁** — GPIO 控制，裸机用 `delay_1ms()`，FreeRTOS 用 `vTaskDelay()`
- **串口打印** — USART printf 重定向，调试利器

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
| 手动拷贝 7 个内核 .c 文件，漏一个报错一次 | 自动全量拷贝 |
| 手写 FreeRTOSConfig.h，调中断优先级、tick 频率 | 预配置模板，4 系列独立配置 |
| SysTick 跟裸机延时抢定时器，各种冲突 | FreeRTOS 模式用 DWT 做 us 延迟，不碰 SysTick |
| 晶振跟 SDK 默认不一样，PLL 全乱 | 下拉选 8M/25M，自动修正 |
| 两天调不通，翻 2016 年论坛帖 | **勾个框，几秒搞定** |

---

## 使用方式

无需安装 Python，一个 exe 搞定：

1. **下载** `MCUQuickStart.exe`（文末链接）
2. **准备 SDK**：芯片固件包 + FreeRTOS 源码放同一目录
3. **打开软件**：双击 exe → 设置 SDK 根目录
4. **选芯片**：左侧系列 → 右侧型号
5. **选模板**：空壳 / LED / 串口打印
6. **可选**：勾 FreeRTOS，选晶振频率（8M/25M）
7. **点生成** → Keil5 打开 → 编译 → 一把过

---

## 实际场景

**场景一：新板子验证硬件**

刚到手的 STM32F407VET6，传统做法是网上找例程改来改去。现在——打开工具，选系列→选型号→LED 模板→生成。一分钟，灯闪起来了。

**场景二：上 FreeRTOS**

想在新项目里跑 RTOS？不用翻帖子找 port 文件，不用手写 FreeRTOSConfig.h，不用跟 SysTick 斗智斗勇。勾个框，工具帮你把内核、端口、内存管理、配置文件全部搞定。移植 FreeRTOS 从"两天起步"变成"几秒钟"。

**场景三：换晶振不用改代码**

你板子是 8MHz 晶振，SDK 默认按 25MHz 配的 PLL。以前得翻数据手册重算寄存器值。现在——下拉框选 8MHz，工具自动修正 `PLL_M`、`HSE_VALUE` 和相关宏。

**场景四：新人入职**

团队来了新同事，还得教他怎么搭 Keil 工程、怎么移植 FreeRTOS？把 exe 扔给他，给个 SDK 包就行了。零学习成本。

---

## 原理简述

数据驱动架构。每款芯片的参数——启动文件、Flash 驱动、内存映射、预编译宏、排除的外设文件——全部存在 JSON 里。模板文件用 `{{PLACEHOLDER}}` 占位符，生成时替换。加新芯片不改代码，只加 JSON + 模板。

FreeRTOS 的集成也是同样思路：芯片 JSON 里配好内核文件列表、端口映射（Cortex-M3→ARM_CM3、Cortex-M4→ARM_CM4F）、SysTick 分频系数。生成时自动从 FreeRTOS SDK 源码拷贝，渲染配置文件。

---

## 系统要求

- Windows 10 及以上
- Keil MDK V5
- 对应芯片的 SDK 固件包（STM32F10x_StdPeriph_Lib、STM32F4xx_DSP_StdPeriph_Lib、GD32F10x_Firmware_Library、GD32F4xx_Firmware_Library）
- FreeRTOS Kernel V10.x 源码（可选，用于 RTOS 工程）

---

## 下载地址

GitHub Release：**[https://github.com/MJ1289856135/-MCUQuickStart/releases](https://github.com/MJ1289856135/-MCUQuickStart/releases)**

下载 `MCUQuickStart.exe` 直接运行，无需安装。

> 源码开源在 Gitee：[https://gitee.com/mj_yyfddca/mcu_quick_start](https://gitee.com/mj_yyfddca/mcu_quick_start)

> 如果觉得好用，⭐ **Star** 支持一下，让更多嵌入式同行看到！

---

## 总结

v1.0.0 解决了裸机工程搭建的痛点，v1.1.0 进一步解决了 **FreeRTOS 移植**这个更大的痛点。后续还会加 LVGL 等更多可选库。

嵌入式开发的很多效率问题不是技术问题，是流程问题。把这些自动化之后，你的时间应该花在业务代码上，而不是跟工具链斗智斗勇。

*原创文章，转载注明出处。*
