# MCU 工程模板生成器 — 设计文档

## 目标

桌面 GUI 工具，选择芯片型号后，一键生成 Keil5 可直接编译的工程模板。

支持芯片：GD32 系列 + STM32 系列。

## 架构概览

5 个模块：

```
GUI (PyQt6) — 芯片选择 | 模版选择 | 生成按钮
   ├── SDK 管理器      — 管理 SDK 路径，从 SDK 目录拷贝文件
   ├── 芯片数据库       — JSON，定义每款芯片的参数
   ├── 模版引擎        — Keil 工程模版 + 代码模版，填充占位符
   └── 工程生成器      — 组合以上，创建目录结构，生成 .uvprojx
```

## 芯片数据库

JSON 文件，每款芯片一条记录：

```json
{
  "GD32F103C8T6": {
    "family": "GD32F10x",
    "core": "Cortex-M3",
    "ram_kb": 20,
    "flash_kb": 64,
    "sdk_dir": "GD32F10x_Firmware_Library",
    "startup": "startup_gd32f10x_md.s",
    "system_file": "system_gd32f10x.c",
    "cmsis_core": "core_cm3.h",
    "lib_required": ["gpio", "rcu", "usart", "timer", "dma", "exti", "misc", "pmu", "bkp", "rtc", "wwdgt", "fwdgt", "spi", "i2c"],
    "lib_optional": ["can", "usb", "enet", "sdio", "exmc", "dac", "adc"]
  }
}
```

库文件分必选（通用外设，默认带）和可选（不常用的，高级选项勾选）。

## 固件库来源

用户指定 SDK 目录（不打包库文件，避免版权问题 + 保持灵活）。

首次使用时配置 GD32/STM32 SDK 根路径，工具从 SDK 中拷贝所需文件到新工程。

## 目录结构

生成工程目录固定：

```
<项目名>/
├── CMSIS/           # 从 SDK 拷贝
├── FIRMWARE/        # 从 SDK 拷贝（Include/ + Source/）
├── STARTUP/         # 从 SDK 拷贝
├── SYSTEM/          # 工具自带模版（delay/ + sys/）
├── USER/            # 工具自带模版（main.c, it.c/h, systick.c/h, libopt.h）
├── APP/             # 空目录，预留
├── DRIVER/          # 空目录，预留
├── HARDWARE/        # 空目录，预留
└── MDK-ARM/         # 填充占位符后的工程文件
```

## 模版机制

工程模版：每个芯片系列准备一个干净的 `.uvprojx` 模版，生成时替换占位符。

代码模版：`main.c`、`gd32f10x_it.c` 等文件中用 `{{PLACEHOLDER}}` 标记，生成时替换，如：

- `{{DEVICE_HEADER}}` → `gd32f10x` 或 `stm32f4xx`
- `{{STARTUP_FILE}}` → `startup_gd32f10x_md.s`
- `{{CHIP_FAMILY}}` → `GD32F10x`

## GUI 布局

单窗口应用：

- SDK 路径配置区（GD32 / STM32 路径 + 浏览按钮）
- 工程设置区（芯片系列下拉 → 芯片型号级联下拉、项目名称、输出目录）
- 模版选择区（空壳 / LED闪烁 / 串口打印，单选）
- 生成按钮
- 日志输出区（展示复制和生成过程）

## 代码模版选项

- **空壳**: `int main(void) { while(1); }`
- **LED 闪烁**: 带 GPIO 初始化 + 延时循环
- **串口打印**: 带 USART 初始化 + `printf("Hello\\r\\n")` 循环输出

## 初始支持的芯片

- GD32F10x 系列（Cortex-M3）：C8T6/CBT6/RCT6/RET6/VCT6/VET6 等
- STM32F10x 系列（Cortex-M3）：同上
- STM32F4xx 系列（Cortex-M4）：后续添加

## 后期扩展点（此版本不做）

- Keil 版本选择 / GCC Makefile / CMake 项目生成
- FreeRTOS 可选集成
- 更多芯片系列（GD32F3xx/F4xx、STM32F0xx/G0xx/H7xx 等）
- 可选外设库勾选（CAN/USB/ENET 等）
- 保存/加载用户配置
