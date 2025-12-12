# 🎨 GamePainter - 基础绘图工具

> 提供 12 个核心绘图工具，通过组合可绑制任意复杂图形！

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![PyPI](https://img.shields.io/pypi/v/game-painter.svg)](https://pypi.org/project/game-painter/)
[![MCP](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## ✨ 特性

- 🎨 **12 个基础工具** - 精简设计，功能完整
- 🔧 **MCP 工具集成** - 可被 AI 助手直接调用
- 📐 **灵活组合** - 基础图形组合成复杂图案
- 🚀 **开箱即用** - 无需复杂配置

## 🚀 快速开始

### 安装

从 PyPI 安装（推荐）：

```bash
pip install game-painter
```

或从源码安装：

```bash
# 克隆项目
git clone https://github.com/dzqdzq/game-painter.git
cd game-painter

# 创建虚拟环境并安装依赖
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .
```

### 直接使用

```python
from painter import GamePainter

# 创建画布
p = GamePainter(200, 150, bg_color=(240, 240, 240, 255))

# 画一个房子
p.pen_rect(50, 60, 100, 80, fill_color=(255, 230, 180, 255))  # 墙
p.pen_polygon([(50, 60), (100, 20), (150, 60)], fill_color=(180, 80, 50, 255))  # 屋顶
p.pen_rect(85, 100, 30, 40, fill_color=(139, 90, 43, 255))  # 门

# 保存
p.save("house.png")
```

## 🔌 MCP 工具配置

安装完成后，在 Cursor 或 Claude Desktop 中配置 MCP 服务器。

### Cursor 配置

打开 Cursor Settings，找到 MCP 设置，添加配置：

```json
{
  "mcpServers": {
    "game-painter": {
      "command": "uvx",
      "args": ["game-painter"]
    }
  }
}
```

或者如果你使用的是虚拟环境：

```json
{
  "mcpServers": {
    "game-painter": {
      "command": "python",
      "args": ["-m", "server"]
    }
  }
}
```

### Claude Desktop 配置

编辑 `~/Library/Application Support/Claude/claude_desktop_config.json`（macOS）或相应配置文件：

```json
{
  "mcpServers": {
    "game-painter": {
      "command": "uvx",
      "args": ["game-painter"]
    }
  }
}
```

或使用 Python 直接运行：

```json
{
  "mcpServers": {
    "game-painter": {
      "command": "python",
      "args": ["-m", "server"]
    }
  }
}
```

> 💡 **提示**：确保安装 game-painter 的 Python 环境在系统 PATH 中，或使用完整的 Python 路径。

## 🛠️ 工具列表 (12 个)

### 画布管理

| 工具 | 说明 |
|------|------|
| `create_canvas` | 创建画布（第一步） |
| `save` | 保存画布为图片 |

### 线条类

| 工具 | 说明 |
|------|------|
| `line` | 直线/虚线 |
| `polyline` | 折线/多段线 |
| `arc` | 弧线 |
| `bezier` | 贝塞尔曲线 |
| `wave` | 波浪线 |

### 形状类

| 工具 | 说明 |
|------|------|
| `rect` | 矩形/圆角矩形 |
| `ellipse` | 椭圆/正圆 |
| `polygon` | 多边形（三角形、六边形等） |

### 图标类

| 工具 | 说明 |
|------|------|
| `icon` | 五角星、箭头 |

### 辅助类

| 工具 | 说明 |
|------|------|
| `text` | 文字 |

## 📖 工具详情

### 1. `create_canvas` - 创建画布

```
width: 画布宽度（默认 200）
height: 画布高度（默认 200）
bg_color: 背景颜色 [R,G,B,A]（默认透明）
canvas_id: 画布 ID（默认 "default"）
```

### 2. `line` - 画直线

```
x1, y1: 起点坐标
x2, y2: 终点坐标
color: 颜色 [R,G,B,A]
width: 线宽
dash: 虚线模式 [线段长, 间隔长]，如 [10, 5]
```

### 3. `polyline` - 画折线

```
points: 点坐标列表 [[x1,y1], [x2,y2], ...]
closed: 是否闭合
dash: 虚线模式
```

### 4. `arc` - 画弧线

```
x, y: 外接矩形左上角
width, height: 外接矩形尺寸
start_angle: 起始角度（度）
end_angle: 结束角度（度）
```

### 5. `bezier` - 画贝塞尔曲线

```
points: 控制点列表
  - 2 点 = 直线
  - 3 点 = 二次曲线
  - 4 点 = 三次曲线
```

### 6. `wave` - 画波浪线

```
x1, y1: 起点
x2, y2: 终点
amplitude: 振幅（默认 10）
wavelength: 波长（默认 20）
```

### 7. `rect` - 画矩形

```
x, y: 左上角坐标
width, height: 尺寸
fill_color: 填充颜色
border_color: 边框颜色
radius: 圆角半径（0 为直角）
```

### 8. `ellipse` - 画椭圆

```
x, y: 外接矩形左上角
width, height: 尺寸（相等则为正圆）
fill_color: 填充颜色
border_color: 边框颜色
```

### 9. `polygon` - 画多边形

支持两种模式：

**模式 1：自定义顶点**
```
points: [[x1,y1], [x2,y2], ...]
```

**模式 2：正多边形**
```
cx, cy: 中心坐标
radius: 外接圆半径
sides: 边数（3=三角形, 6=六边形）
rotation: 旋转角度
```

### 10. `icon` - 画图标

```
icon_type: "star" 或 "arrow"
cx, cy: 中心坐标
size: 图标大小
direction: 箭头方向（up/down/left/right）
points: 星角数量（默认 5）
```

### 11. `text` - 写文字

```
x, y: 位置
text: 文字内容
color: 颜色
font_size: 字体大小
```

### 12. `save` - 保存画布

```
filename: 文件名
output_dir: 输出目录（可选）
```

## 🎨 使用示例

### 画小汽车

```
1. create_canvas(width=200, height=100)
2. polygon(points=车身坐标)        # 车身
3. polygon(points=车顶坐标)        # 车顶
4. polygon(points=车窗坐标)        # 车窗
5. ellipse(x, y, 30, 30)           # 轮子
6. save(filename="car.png")
```

### 画花朵

```
1. create_canvas(width=150, height=180)
2. rect(茎)
3. bezier(叶子弯曲)
4. ellipse(花瓣 x 4)
5. ellipse(花心)
6. save(filename="flower.png")
```

## 📄 License

MIT License

---

Made with ❤️ for Developers
