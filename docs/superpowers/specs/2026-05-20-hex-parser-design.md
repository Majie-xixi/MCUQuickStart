# HexParser — 嵌入式协议帧解析CLI工具

## 目标

粘贴 hex 字符串，依据协议 JSON 定义自动解析出每一层结构体的字段和含义，输出可读的树形结果。

## 输入

```
5A00010100080200FF010201
# 或带空格: 5A 00 01 01 00 08 02 00 FF 01 02 01
```

## 输出示例

```
=== CtrlFrame ===
head:      0x5A ✓
seq:       0x0001 (1)
add:       0x01
len:       0x0008 (8字节)
cmd:       0x02 (CMD_SEND_DATA)
sum:       0x00FF (验证: 通过 ✓)
data:      ──→ SendData

  === SendData ===
  dataType:  0x01 (DATA_TYPE_REAGENT)
  data:      ──→ SyringeCleaningTypeInfo

    === SyringeCleaningTypeInfo ===
    清洗次数:      0x02 (2)
    清洗类型:      0x01 → 内外壁清洗
```

## 架构

```
HexParser/
├── main.py                    # CLI 入口
├── protocol.json              # 协议定义（用户维护）
├── src/
│   ├── parser.py              # 核心解析引擎
│   ├── field_types.py         # uint8/uint16/int16/sum16 等类型处理
│   └── formatter.py           # 树形输出格式化
└── hexparser.spec             # PyInstaller 打包配置
```

## 协议 JSON 结构设计

```json
{
  "name": "CtrlFrame",
  "fields": [
    {"name": "head",      "type": "uint8",    "check": "0x5A"},
    {"name": "seq",       "type": "uint16"},
    {"name": "add",       "type": "uint8"},
    {"name": "len",       "type": "uint16"},
    {"name": "cmd",       "type": "uint8",    "map": {
      "0x01": "CMD_HEARTBEAT",
      "0x02": "CMD_SEND_DATA",
      "0x03": "CMD_ACK"
    }},
    {"name": "sum",       "type": "uint16",   "verify": "sum16"},
    {"name": "data",      "type": "switch",   "on": "cmd", "cases": {
      "CMD_SEND_DATA": {
        "name": "SendData",
        "fields": [
          {"name": "dataType",  "type": "uint8", "map": {
            "0x01": "DATA_TYPE_REAGENT",
            "0x07": "DATA_TYPE_TEMP",
            "0x08": "DATA_TYPE_EXCEPTION"
          }},
          {"name": "payload",   "type": "switch", "on": "dataType", "cases": {
            "DATA_TYPE_REAGENT": {
              "name": "SyringeCleaningTypeInfo",
              "fields": [
                {"name": "清洗次数", "type": "uint8"},
                {"name": "清洗类型", "type": "uint8", "map": {"0": "外壁清洗", "1": "内外壁清洗"}}
              ]
            }
          }}
        ]
      }
    }}
  ]
}
```

### 字段类型说明

| type | 说明 |
|------|------|
| `uint8` | 无符号 1 字节 |
| `uint16` | 无符号 2 字节（小端） |
| `int16` | 有符号 2 字节 |
| `switch` | 根据 `on` 字段值路由到对应 `cases` 子结构体 |
| `verify: sum16` | 对所有字节求和校验 |

## 交互流程

```
$ hexparser
> 5A00010100080200FF010201

=== CtrlFrame ===
...

> 5A00020100060300AA01

=== CtrlFrame ===
...
```

输入空行退出。支持上下箭头翻历史记录。

## 技术选型

- Python 3，纯 CLI
- 交互：`readline` 支持历史回翻
- 打包：PyInstaller → 单文件 `.exe`，约 5-10 MB（远小于 MCUQuickStart）

## 与 MCUQuickStart 的区别

- MCUQuickStart 面向**项目创建**，GUI 交互，涉及 Keil/SDK
- HexParser 面向**调试解析**，CLI 交互，纯文本处理
- 两个工具独立目录、独立打包、独立发布
