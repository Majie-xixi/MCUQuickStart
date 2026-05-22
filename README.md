# MCUQuickStart

嵌入式 MCU 工程模板一键生成工具。选择芯片型号，自动生成 Keil5 打开即编译 + CLion/VS Code GCC 编译的双兼容工程模板。

## 分支说明

| 分支 | 内容 |
|------|------|
| **master** (v1.1.0) | 裸机+FreeRTOS 可选库，HXTAL 晶振配置，4 系列 37 型号 |
| **feature/gcc-cmake-support** | 新增 GCC+CMake 双构建支持（可选），模板 Keil/GCC 双兼容 |

## 支持芯片

| 系列 | 内核 | 厂商 | 型号数 |
|------|------|------|--------|
| STM32F10x | Cortex-M3 | ST | 9 (C8T6 ~ ZET6) |
| STM32F4xx | Cortex-M4 | ST | 6 (F407 / F429) |
| GD32F10x | Cortex-M3 | GigaDevice | 8 (C8T6 ~ VET6) |
| GD32F4xx | Cortex-M4 | GigaDevice | 14 (F405 / F407 / F450 / F470) |

## 代码模板

- **空壳** — 最简 main.c，可在此基础上开发
- **LED 闪烁** — GPIO 输出控制 LED
- **串口打印** — USART printf 重定向

## 功能

- 自动从 SDK 拷贝固件库、启动文件、CMSIS 头文件
- 自动生成 Keil5 `.uvprojx` 工程文件（含正确的芯片选型、内存映射、Flash 烧录算法）
- 模板占位符替换（`{{DEVICE_HEADER}}`、`{{CONF_HEADER}}`、`{{DEBUG_USART}}` 等）
- `fwlib_exclude` 机制：芯片 JSON 可配置排除不兼容的固件源文件
- 中英文界面切换
- 预留 APP / DRIVER / HARDWARE 空目录
- FreeRTOS 可选库：勾选即生成 RTOS 工程，4 系列全支持
- 外部晶振选择：8MHz / 25MHz，自动适配 PLL 配置
- 使用说明按钮（中英文双语）
- **（feature 分支）** GCC + CMake 构建：勾选后额外生成 CMakeLists.txt + 链接脚本 + GCC 启动文件，项目同时支持 Keil MDK 和 CLion/VS Code 打开编译
- **（feature 分支）** 链接脚本分 GD32/STM32 两套，向量段名/符号自动适配
- **（feature 分支）** SDK 源文件 `-w` 隔离，用户代码 `-Wall` 保留，编译零警告

## 安装

```bash
pip install PyQt6
```

## 使用

```bash
python main.py
```

1. 设置 SDK 路径（指向固件库根目录）
2. 选择芯片系列和型号
3. 选择代码模板，可勾选 FreeRTOS、GCC+CMake、外部晶振频率
4. 点击 "Generate Project"

Keil5 打开 `MDK-ARM/<项目名>.uvprojx`，CLion/VS Code 打开 `CMakeLists.txt` 即可编译。

## SDK 准备

不同芯片系列需要对应的 SDK 包，以及可选的 FreeRTOS 源码：

| 系列 | SDK |
|------|-----|
| STM32F10x | STM32F10x_StdPeriph_Lib |
| STM32F4xx | STM32F4xx_DSP_StdPeriph_Lib |
| GD32F10x | GD32F10x_Firmware_Library |
| GD32F4xx | GD32F4xx_Firmware_Library |
| FreeRTOS（可选） | FreeRTOS Kernel V10.x（解压到 SDK 根目录） |

## 目录结构

```
MCUQuickStart/
├── main.py                     # 入口
├── src/
│   ├── core/
│   │   ├── chip_db.py          # 芯片数据库
│   │   ├── sdk_manager.py      # SDK 文件管理
│   │   ├── template_engine.py  # 模板替换引擎
│   │   └── project_generator.py # 工程生成器
│   ├── gui/
│   │   └── main_window.py      # PyQt6 主窗口
│   └── resources/
│       ├── chips/              # 芯片定义 JSON（4 系列 37 型号）
│       └── templates/          # 代码和工程模板（含 freertos/）
└── requirements.txt
```
