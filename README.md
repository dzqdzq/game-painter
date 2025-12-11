# 🎨 GamePainter - 游戏UI占位图生成器

> 为游戏项目Demo快速生成各种UI占位图，无需美术人员！

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![MCP](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## ✨ 特性

- 🎮 **专为游戏设计** - 涵盖常见游戏UI元素
- 🔧 **MCP工具集成** - 可被AI助手直接调用
- 🎨 **多种风格** - 支持现代、奇幻、科幻、像素等风格
- 💎 **稀有度系统** - 支持普通到传说的稀有度边框
- 📦 **开箱即用** - 快速生成完整UI套件

## 🚀 快速开始

### 安装

```bash
# 克隆项目
git clone https://github.com/dzqdzq/game-painter.git
cd game-painter

# 创建虚拟环境并安装依赖
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 直接使用

```python
from painter import GamePainter, create_button, create_icon

# 创建按钮
btn = create_button(120, 40, text="开始游戏", style="gradient", color="blue")
btn.save("start_button.png")

# 创建图标
star = create_icon(64, "star")
star.save("star_icon.png")

# 使用 GamePainter 类进行更多自定义
painter = GamePainter(200, 30)
painter.draw_progress_bar(progress=75)
painter.save("progress.png")
```

### 生成示例

```bash
python painter.py
```

这将在 `output/` 目录生成所有示例图片。

## 🔌 MCP 工具配置

### Cursor 配置

在 Cursor 的 MCP 设置中添加：

```json
{
  "mcpServers": {
    "game-painter": {
      "command": "python",
      "args": ["/path/to/game-painter/server.py"],
      "env": {}
    }
  }
}
```

或使用 uvx（需要先发布到 PyPI）：

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

### Claude Desktop 配置

编辑 `~/Library/Application Support/Claude/claude_desktop_config.json`：

```json
{
  "mcpServers": {
    "game-painter": {
      "command": "/path/to/game-painter/.venv/bin/python",
      "args": ["/path/to/game-painter/server.py"]
    }
  }
}
```

## 🛠️ 可用工具

### 预设UI组件

#### 1. `draw_button` - 绘制按钮

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| width | int | 120 | 宽度 |
| height | int | 40 | 高度 |
| text | string | "" | 按钮文字 |
| style | enum | gradient | flat/gradient/glossy/outline/pixel |
| color | enum | blue | blue/green/red/orange/purple |

#### 2. `draw_icon` - 绘制图标

| 参数 | 类型 | 说明 |
|------|------|------|
| icon_type | enum | star/coin/gem/heart/shield/arrow |
| size | int | 图标尺寸 |
| gem_type | enum | diamond/ruby/emerald/sapphire |
| direction | enum | up/down/left/right (箭头方向) |

#### 3. `draw_progress_bar` - 绘制进度条

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| width | int | 200 | 宽度 |
| height | int | 24 | 高度 |
| progress | float | 50 | 进度 0-100 |
| bar_type | enum | normal | normal/health |

#### 4. `draw_item_slot` - 绘制道具槽

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| rarity | enum | common | common/uncommon/rare/epic/legendary |
| show_shine | bool | false | 显示闪光效果 |

#### 5. `draw_dialog_box` - 绘制对话框

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| style | enum | modern | modern/fantasy/scifi/pixel |
| show_arrow | bool | true | 显示对话箭头 |

#### 6. `draw_minimap` - 绘制小地图

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| shape | enum | circle | circle/square/hexagon |

#### 7. `draw_tooltip` - 绘制提示框

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| title | string | "道具名称" | 标题 |
| rarity | enum | rare | 稀有度 |

#### 8. `draw_control_button` - 绘制控制按钮 🆕

常用的UI控制按钮图标，如关闭、设置、播放等。

| 参数 | 类型 | 说明 |
|------|------|------|
| button_type | enum | close/settings/play/pause/menu/home/refresh/back/plus/minus/check |
| size | int | 按钮尺寸 |
| style | enum | circle/square/none (背景样式) |

#### 9. `draw_shape` - 绘制基础图形

| 参数 | 类型 | 说明 |
|------|------|------|
| shape_type | enum | rounded_rect/circle/polygon |
| fill_color | [R,G,B,A] | 填充颜色 |
| gradient | enum | none/horizontal/vertical/diagonal |

#### 10. `generate_ui_kit` - 批量生成UI套件

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| theme | enum | default | default/rpg/scifi/cartoon/pixel |
| output_dir | string | ui_kit | 输出目录 |

---

### 🎨 画笔工具 (低级绘图API) 🆕

让AI像"手"一样自由控制画笔，绘制任意自定义图形！

#### 工作流程

```
1. pen_create_canvas  →  创建画布
2. pen_* bindbindbindbd操作bindbd     →bindbd  绑定图形 (可重复)
3. pen_save           →  保存图片
```

#### 画布操作

| 工具 | 说明 |
|------|------|
| `pen_create_canvas` | 创建新画布，返回canvas_id用于后续操作 |
| `pen_save` | 保存画布为图片文件 |

#### 基础绘图

| 工具 | 说明 |
|------|------|
| `pen_line` | 画直线 (x1,y1 → x2,y2) |
| `pen_lines` | 画多段折线，支持闭合 |
| `pen_rect` | 画矩形 (填充/边框) |
| `pen_ellipse` | 画椭圆/圆形 (填充/边框) |
| `pen_polygon` | 画多边形 (填充/边框) |
| `pen_arc` | 画弧线 (起始/结束角度) |
| `pen_bezier` | 画贝塞尔曲线 (2-4个控制点) |
| `pen_point` | 画点 |
| `pen_text` | 写文字 |

#### 预设图形

| 工具 | 说明 |
|------|------|
| `pen_draw_preset` | 绘制预设复杂图形：car(小汽车)、house(房子)、tree(树) |

#### 画笔使用示例

```python
# 1. 创建画布
pen_create_canvas(width=300, height=200, bg_color=[135,206,235,255])

# 2. 画地面
pen_rect(x=0, y=160, width=300, height=40, fill_color=[100,180,100,255])

# 3. 画太阳
pen_ellipse(x=240, y=20, width=40, height=40, fill_color=[255,220,100,255])

# 4. 画房子和汽车
pen_draw_preset(preset="house", x=30, y=40, scale=1.0)
pen_draw_preset(preset="car", x=180, y=90, scale=0.8)

# 5. 写文字
pen_text(x=100, y=10, text="Hello World!", font_size=20)

# 6. 保存
pen_save(filename="my_scene.png")
```

## 🎯 使用场景

- **游戏原型开发** - 快速搭建可玩Demo
- **UI/UX设计** - 占位图辅助布局设计
- **教学演示** - 游戏开发教程素材
- **独立游戏** - 小团队快速迭代

## 📄 License

MIT License - 自由使用和修改！

---

Made with ❤️ for Game Developers
