#!/usr/bin/env python3
"""
🎨 GamePainter MCP Server
游戏UI占位图生成器 - MCP 工具服务

提供游戏项目demo所需的各种UI占位图生成能力
"""

import os
import json
from typing import Optional, Literal
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ImageContent

from painter import (
    GamePainter,
    ButtonStyle,
    GradientDirection,
    create_button,
    create_icon,
    create_progress_bar,
    create_control_button,
    draw_simple_car,
    draw_simple_house,
    draw_simple_tree
)


# 创建 MCP 服务器
server = Server("game-painter")

# 默认输出目录
DEFAULT_OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(DEFAULT_OUTPUT_DIR, exist_ok=True)

# 画布存储（用于画笔功能）
canvas_storage: dict[str, GamePainter] = {}


def get_output_path(filename: str, output_dir: Optional[str] = None) -> str:
    """获取输出文件路径"""
    dir_path = output_dir or DEFAULT_OUTPUT_DIR
    os.makedirs(dir_path, exist_ok=True)
    return os.path.join(dir_path, filename)


@server.list_tools()
async def list_tools():
    """列出所有可用的绘图工具"""
    return [
        # ========== 按钮类 ==========
        Tool(
            name="draw_button",
            description="绘制游戏按钮。支持多种风格：flat(扁平)、gradient(渐变)、glossy(光泽)、outline(边框)、pixel(像素风)。适用于游戏UI中的各种按钮。",
            inputSchema={
                "type": "object",
                "properties": {
                    "width": {"type": "integer", "description": "按钮宽度(像素)", "default": 120},
                    "height": {"type": "integer", "description": "按钮高度(像素)", "default": 40},
                    "text": {"type": "string", "description": "按钮文字", "default": ""},
                    "style": {
                        "type": "string",
                        "enum": ["flat", "gradient", "glossy", "outline", "pixel"],
                        "description": "按钮风格",
                        "default": "gradient"
                    },
                    "color": {
                        "type": "string",
                        "enum": ["blue", "green", "red", "orange", "purple"],
                        "description": "按钮颜色",
                        "default": "blue"
                    },
                    "filename": {"type": "string", "description": "保存的文件名", "default": "button.png"},
                    "output_dir": {"type": "string", "description": "输出目录路径(可选)"}
                }
            }
        ),
        
        # ========== 图标类 ==========
        Tool(
            name="draw_icon",
            description="绘制游戏图标。支持：star(星星)、coin(金币)、gem(宝石)、heart(爱心)、shield(盾牌)、arrow(箭头)。适用于道具、货币、装饰等。",
            inputSchema={
                "type": "object",
                "properties": {
                    "icon_type": {
                        "type": "string",
                        "enum": ["star", "coin", "gem", "heart", "shield", "arrow"],
                        "description": "图标类型"
                    },
                    "size": {"type": "integer", "description": "图标尺寸(像素)", "default": 64},
                    "gem_type": {
                        "type": "string",
                        "enum": ["diamond", "ruby", "emerald", "sapphire"],
                        "description": "宝石类型(仅当icon_type为gem时有效)",
                        "default": "diamond"
                    },
                    "direction": {
                        "type": "string",
                        "enum": ["up", "down", "left", "right"],
                        "description": "箭头方向(仅当icon_type为arrow时有效)",
                        "default": "right"
                    },
                    "filename": {"type": "string", "description": "保存的文件名", "default": "icon.png"},
                    "output_dir": {"type": "string", "description": "输出目录路径(可选)"}
                },
                "required": ["icon_type"]
            }
        ),
        
        # ========== 进度条类 ==========
        Tool(
            name="draw_progress_bar",
            description="绘制进度条或血条。适用于游戏中的HP、MP、经验值、加载进度等UI。",
            inputSchema={
                "type": "object",
                "properties": {
                    "width": {"type": "integer", "description": "进度条宽度(像素)", "default": 200},
                    "height": {"type": "integer", "description": "进度条高度(像素)", "default": 24},
                    "progress": {"type": "number", "description": "进度百分比(0-100)", "default": 50},
                    "bar_type": {
                        "type": "string",
                        "enum": ["normal", "health"],
                        "description": "进度条类型：normal(普通)、health(血条，会根据百分比变色)",
                        "default": "normal"
                    },
                    "filename": {"type": "string", "description": "保存的文件名", "default": "progress_bar.png"},
                    "output_dir": {"type": "string", "description": "输出目录路径(可选)"}
                }
            }
        ),
        
        # ========== 道具槽 ==========
        Tool(
            name="draw_item_slot",
            description="绘制道具格子/装备槽。支持不同稀有度的边框颜色：common(普通灰)、uncommon(优秀绿)、rare(稀有蓝)、epic(史诗紫)、legendary(传说金)。",
            inputSchema={
                "type": "object",
                "properties": {
                    "width": {"type": "integer", "description": "槽位宽度(像素)", "default": 64},
                    "height": {"type": "integer", "description": "槽位高度(像素)", "default": 64},
                    "rarity": {
                        "type": "string",
                        "enum": ["common", "uncommon", "rare", "epic", "legendary"],
                        "description": "稀有度",
                        "default": "common"
                    },
                    "show_shine": {"type": "boolean", "description": "是否显示闪光效果", "default": False},
                    "filename": {"type": "string", "description": "保存的文件名", "default": "slot.png"},
                    "output_dir": {"type": "string", "description": "输出目录路径(可选)"}
                }
            }
        ),
        
        # ========== 对话框 ==========
        Tool(
            name="draw_dialog_box",
            description="绘制对话框/气泡框。支持多种风格：modern(现代)、fantasy(奇幻)、scifi(科幻)、pixel(像素)。适用于NPC对话、系统提示等。",
            inputSchema={
                "type": "object",
                "properties": {
                    "width": {"type": "integer", "description": "对话框宽度(像素)", "default": 300},
                    "height": {"type": "integer", "description": "对话框高度(像素)", "default": 100},
                    "style": {
                        "type": "string",
                        "enum": ["modern", "fantasy", "scifi", "pixel"],
                        "description": "对话框风格",
                        "default": "modern"
                    },
                    "show_arrow": {"type": "boolean", "description": "是否显示对话箭头", "default": True},
                    "filename": {"type": "string", "description": "保存的文件名", "default": "dialog.png"},
                    "output_dir": {"type": "string", "description": "输出目录路径(可选)"}
                }
            }
        ),
        
        # ========== 小地图 ==========
        Tool(
            name="draw_minimap",
            description="绘制小地图框架。支持不同形状：circle(圆形)、square(方形)、hexagon(六边形)。包含玩家指示点和方向标记。",
            inputSchema={
                "type": "object",
                "properties": {
                    "width": {"type": "integer", "description": "小地图宽度(像素)", "default": 120},
                    "height": {"type": "integer", "description": "小地图高度(像素)", "default": 120},
                    "shape": {
                        "type": "string",
                        "enum": ["circle", "square", "hexagon"],
                        "description": "小地图形状",
                        "default": "circle"
                    },
                    "filename": {"type": "string", "description": "保存的文件名", "default": "minimap.png"},
                    "output_dir": {"type": "string", "description": "输出目录路径(可选)"}
                }
            }
        ),
        
        # ========== 提示框 ==========
        Tool(
            name="draw_tooltip",
            description="绘制道具/技能提示框。显示物品名称和属性，支持不同稀有度的标题颜色。适用于悬停提示、物品详情等。",
            inputSchema={
                "type": "object",
                "properties": {
                    "width": {"type": "integer", "description": "提示框宽度(像素)", "default": 180},
                    "height": {"type": "integer", "description": "提示框高度(像素)", "default": 80},
                    "title": {"type": "string", "description": "道具/技能名称", "default": "道具名称"},
                    "rarity": {
                        "type": "string",
                        "enum": ["common", "uncommon", "rare", "epic", "legendary"],
                        "description": "稀有度",
                        "default": "rare"
                    },
                    "filename": {"type": "string", "description": "保存的文件名", "default": "tooltip.png"},
                    "output_dir": {"type": "string", "description": "输出目录路径(可选)"}
                }
            }
        ),
        
        # ========== 基础图形 ==========
        Tool(
            name="draw_shape",
            description="绘制基础图形。支持：rounded_rect(圆角矩形)、circle(圆形)、polygon(多边形)。可用于自定义UI元素。",
            inputSchema={
                "type": "object",
                "properties": {
                    "shape_type": {
                        "type": "string",
                        "enum": ["rounded_rect", "circle", "polygon"],
                        "description": "图形类型"
                    },
                    "width": {"type": "integer", "description": "画布宽度(像素)", "default": 100},
                    "height": {"type": "integer", "description": "画布高度(像素)", "default": 100},
                    "fill_color": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "填充颜色 [R,G,B,A]",
                        "default": [100, 149, 237, 255]
                    },
                    "border_color": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "边框颜色 [R,G,B,A](可选)"
                    },
                    "border_width": {"type": "integer", "description": "边框宽度", "default": 0},
                    "radius": {"type": "integer", "description": "圆角半径(圆角矩形)或外接圆半径", "default": 10},
                    "sides": {"type": "integer", "description": "多边形边数", "default": 6},
                    "gradient": {
                        "type": "string",
                        "enum": ["none", "horizontal", "vertical", "diagonal"],
                        "description": "渐变方向",
                        "default": "none"
                    },
                    "gradient_end_color": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "渐变结束颜色 [R,G,B,A]"
                    },
                    "filename": {"type": "string", "description": "保存的文件名", "default": "shape.png"},
                    "output_dir": {"type": "string", "description": "输出目录路径(可选)"}
                },
                "required": ["shape_type"]
            }
        ),
        
        # ========== 控制按钮 ==========
        Tool(
            name="draw_control_button",
            description="绘制常用控制按钮图标。支持：close(关闭X)、settings(齿轮)、play(播放)、pause(暂停)、menu(菜单≡)、home(主页)、refresh(刷新)、back(返回)、plus(加号)、minus(减号)、check(确认√)。",
            inputSchema={
                "type": "object",
                "properties": {
                    "button_type": {
                        "type": "string",
                        "enum": ["close", "settings", "play", "pause", "menu", "home", "refresh", "back", "plus", "minus", "check"],
                        "description": "按钮类型"
                    },
                    "size": {"type": "integer", "description": "按钮尺寸(像素)", "default": 48},
                    "style": {
                        "type": "string",
                        "enum": ["circle", "square", "none"],
                        "description": "背景样式",
                        "default": "circle"
                    },
                    "bg_color": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "背景颜色 [R,G,B,A]"
                    },
                    "icon_color": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "图标颜色 [R,G,B,A]"
                    },
                    "filename": {"type": "string", "description": "保存的文件名"},
                    "output_dir": {"type": "string", "description": "输出目录路径(可选)"}
                },
                "required": ["button_type"]
            }
        ),
        
        # ========== 画笔工具 - 创建画布 ==========
        Tool(
            name="pen_create_canvas",
            description="创建一个新的画布用于自由绘制。返回画布ID，后续画笔操作需要使用此ID。这是使用画笔功能的第一步。",
            inputSchema={
                "type": "object",
                "properties": {
                    "width": {"type": "integer", "description": "画布宽度(像素)", "default": 200},
                    "height": {"type": "integer", "description": "画布高度(像素)", "default": 200},
                    "bg_color": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "背景颜色 [R,G,B,A]，默认透明",
                        "default": [0, 0, 0, 0]
                    },
                    "canvas_id": {"type": "string", "description": "画布ID标识符", "default": "default"}
                }
            }
        ),
        
        # ========== 画笔工具 - 画直线 ==========
        Tool(
            name="pen_line",
            description="在画布上画一条直线。",
            inputSchema={
                "type": "object",
                "properties": {
                    "canvas_id": {"type": "string", "description": "画布ID", "default": "default"},
                    "x1": {"type": "integer", "description": "起点X坐标"},
                    "y1": {"type": "integer", "description": "起点Y坐标"},
                    "x2": {"type": "integer", "description": "终点X坐标"},
                    "y2": {"type": "integer", "description": "终点Y坐标"},
                    "color": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "线条颜色 [R,G,B,A]",
                        "default": [0, 0, 0, 255]
                    },
                    "width": {"type": "integer", "description": "线条宽度", "default": 2}
                },
                "required": ["x1", "y1", "x2", "y2"]
            }
        ),
        
        # ========== 画笔工具 - 画折线 ==========
        Tool(
            name="pen_lines",
            description="在画布上画多段折线或闭合多边形轮廓。",
            inputSchema={
                "type": "object",
                "properties": {
                    "canvas_id": {"type": "string", "description": "画布ID", "default": "default"},
                    "points": {
                        "type": "array",
                        "items": {
                            "type": "array",
                            "items": {"type": "integer"}
                        },
                        "description": "点坐标列表 [[x1,y1], [x2,y2], ...]"
                    },
                    "color": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "线条颜色 [R,G,B,A]",
                        "default": [0, 0, 0, 255]
                    },
                    "width": {"type": "integer", "description": "线条宽度", "default": 2},
                    "closed": {"type": "boolean", "description": "是否闭合", "default": False}
                },
                "required": ["points"]
            }
        ),
        
        # ========== 画笔工具 - 画矩形 ==========
        Tool(
            name="pen_rect",
            description="在画布上画一个矩形。",
            inputSchema={
                "type": "object",
                "properties": {
                    "canvas_id": {"type": "string", "description": "画布ID", "default": "default"},
                    "x": {"type": "integer", "description": "左上角X坐标"},
                    "y": {"type": "integer", "description": "左上角Y坐标"},
                    "width": {"type": "integer", "description": "矩形宽度"},
                    "height": {"type": "integer", "description": "矩形高度"},
                    "fill_color": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "填充颜色 [R,G,B,A](可选)"
                    },
                    "border_color": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "边框颜色 [R,G,B,A]",
                        "default": [0, 0, 0, 255]
                    },
                    "border_width": {"type": "integer", "description": "边框宽度", "default": 2}
                },
                "required": ["x", "y", "width", "height"]
            }
        ),
        
        # ========== 画笔工具 - 画椭圆 ==========
        Tool(
            name="pen_ellipse",
            description="在画布上画一个椭圆或圆形。",
            inputSchema={
                "type": "object",
                "properties": {
                    "canvas_id": {"type": "string", "description": "画布ID", "default": "default"},
                    "x": {"type": "integer", "description": "外接矩形左上角X坐标"},
                    "y": {"type": "integer", "description": "外接矩形左上角Y坐标"},
                    "width": {"type": "integer", "description": "椭圆宽度"},
                    "height": {"type": "integer", "description": "椭圆高度"},
                    "fill_color": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "填充颜色 [R,G,B,A](可选)"
                    },
                    "border_color": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "边框颜色 [R,G,B,A]",
                        "default": [0, 0, 0, 255]
                    },
                    "border_width": {"type": "integer", "description": "边框宽度", "default": 2}
                },
                "required": ["x", "y", "width", "height"]
            }
        ),
        
        # ========== 画笔工具 - 画多边形 ==========
        Tool(
            name="pen_polygon",
            description="在画布上画一个填充多边形。",
            inputSchema={
                "type": "object",
                "properties": {
                    "canvas_id": {"type": "string", "description": "画布ID", "default": "default"},
                    "points": {
                        "type": "array",
                        "items": {
                            "type": "array",
                            "items": {"type": "integer"}
                        },
                        "description": "顶点坐标列表 [[x1,y1], [x2,y2], ...]"
                    },
                    "fill_color": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "填充颜色 [R,G,B,A](可选)"
                    },
                    "border_color": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "边框颜色 [R,G,B,A]",
                        "default": [0, 0, 0, 255]
                    },
                    "border_width": {"type": "integer", "description": "边框宽度", "default": 2}
                },
                "required": ["points"]
            }
        ),
        
        # ========== 画笔工具 - 画弧线 ==========
        Tool(
            name="pen_arc",
            description="在画布上画一条弧线。",
            inputSchema={
                "type": "object",
                "properties": {
                    "canvas_id": {"type": "string", "description": "画布ID", "default": "default"},
                    "x": {"type": "integer", "description": "外接矩形左上角X坐标"},
                    "y": {"type": "integer", "description": "外接矩形左上角Y坐标"},
                    "width": {"type": "integer", "description": "外接矩形宽度"},
                    "height": {"type": "integer", "description": "外接矩形高度"},
                    "start_angle": {"type": "number", "description": "起始角度(度)", "default": 0},
                    "end_angle": {"type": "number", "description": "结束角度(度)", "default": 180},
                    "color": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "弧线颜色 [R,G,B,A]",
                        "default": [0, 0, 0, 255]
                    },
                    "line_width": {"type": "integer", "description": "线条宽度", "default": 2}
                },
                "required": ["x", "y", "width", "height"]
            }
        ),
        
        # ========== 画笔工具 - 画贝塞尔曲线 ==========
        Tool(
            name="pen_bezier",
            description="在画布上画一条贝塞尔曲线。控制点数量：2=直线，3=二次曲线，4=三次曲线。",
            inputSchema={
                "type": "object",
                "properties": {
                    "canvas_id": {"type": "string", "description": "画布ID", "default": "default"},
                    "points": {
                        "type": "array",
                        "items": {
                            "type": "array",
                            "items": {"type": "integer"}
                        },
                        "description": "控制点坐标列表 [[x1,y1], [x2,y2], ...]"
                    },
                    "color": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "曲线颜色 [R,G,B,A]",
                        "default": [0, 0, 0, 255]
                    },
                    "width": {"type": "integer", "description": "线条宽度", "default": 2}
                },
                "required": ["points"]
            }
        ),
        
        # ========== 画笔工具 - 画点 ==========
        Tool(
            name="pen_point",
            description="在画布上画一个点。",
            inputSchema={
                "type": "object",
                "properties": {
                    "canvas_id": {"type": "string", "description": "画布ID", "default": "default"},
                    "x": {"type": "integer", "description": "X坐标"},
                    "y": {"type": "integer", "description": "Y坐标"},
                    "color": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "点颜色 [R,G,B,A]",
                        "default": [0, 0, 0, 255]
                    },
                    "size": {"type": "integer", "description": "点大小", "default": 3}
                },
                "required": ["x", "y"]
            }
        ),
        
        # ========== 画笔工具 - 写文字 ==========
        Tool(
            name="pen_text",
            description="在画布上写文字。",
            inputSchema={
                "type": "object",
                "properties": {
                    "canvas_id": {"type": "string", "description": "画布ID", "default": "default"},
                    "x": {"type": "integer", "description": "X坐标"},
                    "y": {"type": "integer", "description": "Y坐标"},
                    "text": {"type": "string", "description": "文字内容"},
                    "color": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "文字颜色 [R,G,B,A]",
                        "default": [0, 0, 0, 255]
                    },
                    "font_size": {"type": "integer", "description": "字体大小", "default": 16}
                },
                "required": ["x", "y", "text"]
            }
        ),
        
        # ========== 画笔工具 - 保存画布 ==========
        Tool(
            name="pen_save",
            description="保存画布为图片文件。这是完成绘制后必须调用的步骤。",
            inputSchema={
                "type": "object",
                "properties": {
                    "canvas_id": {"type": "string", "description": "画布ID", "default": "default"},
                    "filename": {"type": "string", "description": "保存的文件名", "default": "canvas.png"},
                    "output_dir": {"type": "string", "description": "输出目录路径(可选)"}
                }
            }
        ),
        
        # ========== 画笔工具 - 画预设图形 ==========
        Tool(
            name="pen_draw_preset",
            description="使用画笔绘制预设的复杂图形：car(小汽车)、house(房子)、tree(树)。这些是使用基础画笔API组合而成的示例。",
            inputSchema={
                "type": "object",
                "properties": {
                    "canvas_id": {"type": "string", "description": "画布ID", "default": "default"},
                    "preset": {
                        "type": "string",
                        "enum": ["car", "house", "tree"],
                        "description": "预设图形类型"
                    },
                    "x": {"type": "integer", "description": "绘制位置X", "default": 0},
                    "y": {"type": "integer", "description": "绘制位置Y", "default": 0},
                    "scale": {"type": "number", "description": "缩放比例", "default": 1.0},
                    "primary_color": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "主颜色 [R,G,B,A](可选)"
                    }
                },
                "required": ["preset"]
            }
        ),
        
        # ========== 批量生成 ==========
        Tool(
            name="generate_ui_kit",
            description="批量生成一套游戏UI素材。包含常用的按钮、图标、进度条、道具槽等。适合快速搭建游戏demo。",
            inputSchema={
                "type": "object",
                "properties": {
                    "theme": {
                        "type": "string",
                        "enum": ["default", "rpg", "scifi", "cartoon", "pixel"],
                        "description": "UI风格主题",
                        "default": "default"
                    },
                    "output_dir": {"type": "string", "description": "输出目录路径", "default": "ui_kit"}
                }
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict):
    """处理工具调用"""
    
    try:
        if name == "draw_button":
            width = arguments.get("width", 120)
            height = arguments.get("height", 40)
            text = arguments.get("text", "")
            style = arguments.get("style", "gradient")
            color = arguments.get("color", "blue")
            filename = arguments.get("filename", "button.png")
            output_dir = arguments.get("output_dir")
            
            painter = create_button(width, height, text, style, color)
            file_path = get_output_path(filename, output_dir)
            painter.save(file_path)
            
            return [
                TextContent(type="text", text=f"✅ 按钮已生成: {file_path}\n尺寸: {width}x{height}, 风格: {style}, 颜色: {color}"),
                ImageContent(type="image", data=painter.to_base64(), mimeType="image/png")
            ]
        
        elif name == "draw_icon":
            icon_type = arguments.get("icon_type", "star")
            size = arguments.get("size", 64)
            filename = arguments.get("filename", f"icon_{icon_type}.png")
            output_dir = arguments.get("output_dir")
            
            painter = GamePainter(size, size)
            
            if icon_type == "star":
                painter.draw_star()
            elif icon_type == "coin":
                painter.draw_coin()
            elif icon_type == "gem":
                gem_type = arguments.get("gem_type", "diamond")
                painter.draw_gem(gem_type=gem_type)
            elif icon_type == "heart":
                painter.draw_heart()
            elif icon_type == "shield":
                painter.draw_shield(width=size, height=size)
            elif icon_type == "arrow":
                direction = arguments.get("direction", "right")
                painter.draw_arrow(direction=direction, width=size, height=size)
            
            file_path = get_output_path(filename, output_dir)
            painter.save(file_path)
            
            return [
                TextContent(type="text", text=f"✅ 图标已生成: {file_path}\n类型: {icon_type}, 尺寸: {size}x{size}"),
                ImageContent(type="image", data=painter.to_base64(), mimeType="image/png")
            ]
        
        elif name == "draw_progress_bar":
            width = arguments.get("width", 200)
            height = arguments.get("height", 24)
            progress = arguments.get("progress", 50)
            bar_type = arguments.get("bar_type", "normal")
            filename = arguments.get("filename", "progress_bar.png")
            output_dir = arguments.get("output_dir")
            
            painter = create_progress_bar(width, height, progress, bar_type)
            file_path = get_output_path(filename, output_dir)
            painter.save(file_path)
            
            return [
                TextContent(type="text", text=f"✅ 进度条已生成: {file_path}\n尺寸: {width}x{height}, 进度: {progress}%, 类型: {bar_type}"),
                ImageContent(type="image", data=painter.to_base64(), mimeType="image/png")
            ]
        
        elif name == "draw_item_slot":
            width = arguments.get("width", 64)
            height = arguments.get("height", 64)
            rarity = arguments.get("rarity", "common")
            show_shine = arguments.get("show_shine", False)
            filename = arguments.get("filename", f"slot_{rarity}.png")
            output_dir = arguments.get("output_dir")
            
            painter = GamePainter(width, height)
            painter.draw_icon_slot(rarity=rarity, show_shine=show_shine)
            file_path = get_output_path(filename, output_dir)
            painter.save(file_path)
            
            return [
                TextContent(type="text", text=f"✅ 道具槽已生成: {file_path}\n尺寸: {width}x{height}, 稀有度: {rarity}"),
                ImageContent(type="image", data=painter.to_base64(), mimeType="image/png")
            ]
        
        elif name == "draw_dialog_box":
            width = arguments.get("width", 300)
            height = arguments.get("height", 100)
            style = arguments.get("style", "modern")
            show_arrow = arguments.get("show_arrow", True)
            filename = arguments.get("filename", f"dialog_{style}.png")
            output_dir = arguments.get("output_dir")
            
            painter = GamePainter(width, height)
            painter.draw_dialog_box(style=style, show_arrow=show_arrow)
            file_path = get_output_path(filename, output_dir)
            painter.save(file_path)
            
            return [
                TextContent(type="text", text=f"✅ 对话框已生成: {file_path}\n尺寸: {width}x{height}, 风格: {style}"),
                ImageContent(type="image", data=painter.to_base64(), mimeType="image/png")
            ]
        
        elif name == "draw_minimap":
            width = arguments.get("width", 120)
            height = arguments.get("height", 120)
            shape = arguments.get("shape", "circle")
            filename = arguments.get("filename", f"minimap_{shape}.png")
            output_dir = arguments.get("output_dir")
            
            painter = GamePainter(width, height)
            painter.draw_minimap_frame(shape=shape)
            file_path = get_output_path(filename, output_dir)
            painter.save(file_path)
            
            return [
                TextContent(type="text", text=f"✅ 小地图已生成: {file_path}\n尺寸: {width}x{height}, 形状: {shape}"),
                ImageContent(type="image", data=painter.to_base64(), mimeType="image/png")
            ]
        
        elif name == "draw_tooltip":
            width = arguments.get("width", 180)
            height = arguments.get("height", 80)
            title = arguments.get("title", "道具名称")
            rarity = arguments.get("rarity", "rare")
            filename = arguments.get("filename", "tooltip.png")
            output_dir = arguments.get("output_dir")
            
            painter = GamePainter(width, height)
            painter.draw_tooltip(title=title, rarity=rarity)
            file_path = get_output_path(filename, output_dir)
            painter.save(file_path)
            
            return [
                TextContent(type="text", text=f"✅ 提示框已生成: {file_path}\n标题: {title}, 稀有度: {rarity}"),
                ImageContent(type="image", data=painter.to_base64(), mimeType="image/png")
            ]
        
        elif name == "draw_shape":
            shape_type = arguments.get("shape_type", "rounded_rect")
            width = arguments.get("width", 100)
            height = arguments.get("height", 100)
            fill_color = tuple(arguments.get("fill_color", [100, 149, 237, 255]))
            border_color = tuple(arguments.get("border_color")) if arguments.get("border_color") else None
            border_width = arguments.get("border_width", 0)
            radius = arguments.get("radius", 10)
            filename = arguments.get("filename", f"{shape_type}.png")
            output_dir = arguments.get("output_dir")
            
            painter = GamePainter(width, height)
            
            if shape_type == "rounded_rect":
                gradient = arguments.get("gradient", "none")
                gradient_dir = None
                if gradient != "none":
                    gradient_dir = GradientDirection(gradient)
                gradient_end = tuple(arguments.get("gradient_end_color")) if arguments.get("gradient_end_color") else None
                
                painter.draw_rounded_rect(
                    width=width, height=height, radius=radius,
                    fill_color=fill_color, border_color=border_color, border_width=border_width,
                    gradient=gradient_dir, gradient_end_color=gradient_end
                )
            elif shape_type == "circle":
                painter.draw_circle(fill_color=fill_color, border_color=border_color, border_width=border_width)
            elif shape_type == "polygon":
                sides = arguments.get("sides", 6)
                painter.draw_polygon(sides=sides, fill_color=fill_color, border_color=border_color, border_width=border_width)
            
            file_path = get_output_path(filename, output_dir)
            painter.save(file_path)
            
            return [
                TextContent(type="text", text=f"✅ 图形已生成: {file_path}\n类型: {shape_type}, 尺寸: {width}x{height}"),
                ImageContent(type="image", data=painter.to_base64(), mimeType="image/png")
            ]
        
        elif name == "draw_control_button":
            button_type = arguments.get("button_type", "close")
            size = arguments.get("size", 48)
            style = arguments.get("style", "circle")
            filename = arguments.get("filename", f"ctrl_{button_type}.png")
            output_dir = arguments.get("output_dir")
            
            # 构建参数
            kwargs = {"style": style}
            if arguments.get("bg_color"):
                kwargs["bg_color"] = tuple(arguments.get("bg_color"))
            if arguments.get("icon_color"):
                kwargs["icon_color"] = tuple(arguments.get("icon_color"))
            
            painter = create_control_button(size, button_type, **kwargs)
            file_path = get_output_path(filename, output_dir)
            painter.save(file_path)
            
            return [
                TextContent(type="text", text=f"✅ 控制按钮已生成: {file_path}\n类型: {button_type}, 尺寸: {size}x{size}"),
                ImageContent(type="image", data=painter.to_base64(), mimeType="image/png")
            ]
        
        # ========== 画笔工具处理 ==========
        
        elif name == "pen_create_canvas":
            width = arguments.get("width", 200)
            height = arguments.get("height", 200)
            bg_color = tuple(arguments.get("bg_color", [0, 0, 0, 0]))
            canvas_id = arguments.get("canvas_id", "default")
            
            painter = GamePainter(width, height, bg_color)
            canvas_storage[canvas_id] = painter
            
            return [
                TextContent(type="text", text=f"✅ 画布已创建\nID: {canvas_id}\n尺寸: {width}x{height}\n背景色: {bg_color}\n\n现在可以使用 pen_line, pen_rect 等工具在此画布上绘制。完成后使用 pen_save 保存。")
            ]
        
        elif name == "pen_line":
            canvas_id = arguments.get("canvas_id", "default")
            if canvas_id not in canvas_storage:
                return [TextContent(type="text", text=f"❌ 画布 '{canvas_id}' 不存在，请先使用 pen_create_canvas 创建画布")]
            
            painter = canvas_storage[canvas_id]
            x1 = arguments.get("x1")
            y1 = arguments.get("y1")
            x2 = arguments.get("x2")
            y2 = arguments.get("y2")
            color = tuple(arguments.get("color", [0, 0, 0, 255]))
            width = arguments.get("width", 2)
            
            painter.pen_line(x1, y1, x2, y2, color, width)
            
            return [
                TextContent(type="text", text=f"✅ 直线已绘制: ({x1},{y1}) → ({x2},{y2})"),
                ImageContent(type="image", data=painter.to_base64(), mimeType="image/png")
            ]
        
        elif name == "pen_lines":
            canvas_id = arguments.get("canvas_id", "default")
            if canvas_id not in canvas_storage:
                return [TextContent(type="text", text=f"❌ 画布 '{canvas_id}' 不存在，请先使用 pen_create_canvas 创建画布")]
            
            painter = canvas_storage[canvas_id]
            points = [tuple(p) for p in arguments.get("points", [])]
            color = tuple(arguments.get("color", [0, 0, 0, 255]))
            width = arguments.get("width", 2)
            closed = arguments.get("closed", False)
            
            painter.pen_lines(points, color, width, closed)
            
            return [
                TextContent(type="text", text=f"✅ 折线已绘制: {len(points)} 个点" + ("(闭合)" if closed else "")),
                ImageContent(type="image", data=painter.to_base64(), mimeType="image/png")
            ]
        
        elif name == "pen_rect":
            canvas_id = arguments.get("canvas_id", "default")
            if canvas_id not in canvas_storage:
                return [TextContent(type="text", text=f"❌ 画布 '{canvas_id}' 不存在，请先使用 pen_create_canvas 创建画布")]
            
            painter = canvas_storage[canvas_id]
            x = arguments.get("x")
            y = arguments.get("y")
            width = arguments.get("width")
            height = arguments.get("height")
            fill_color = tuple(arguments.get("fill_color")) if arguments.get("fill_color") else None
            border_color = tuple(arguments.get("border_color")) if arguments.get("border_color") else (0, 0, 0, 255)
            border_width = arguments.get("border_width", 2)
            
            painter.pen_rect(x, y, width, height, fill_color, border_color, border_width)
            
            return [
                TextContent(type="text", text=f"✅ 矩形已绘制: 位置({x},{y}) 尺寸{width}x{height}"),
                ImageContent(type="image", data=painter.to_base64(), mimeType="image/png")
            ]
        
        elif name == "pen_ellipse":
            canvas_id = arguments.get("canvas_id", "default")
            if canvas_id not in canvas_storage:
                return [TextContent(type="text", text=f"❌ 画布 '{canvas_id}' 不存在，请先使用 pen_create_canvas 创建画布")]
            
            painter = canvas_storage[canvas_id]
            x = arguments.get("x")
            y = arguments.get("y")
            width = arguments.get("width")
            height = arguments.get("height")
            fill_color = tuple(arguments.get("fill_color")) if arguments.get("fill_color") else None
            border_color = tuple(arguments.get("border_color")) if arguments.get("border_color") else (0, 0, 0, 255)
            border_width = arguments.get("border_width", 2)
            
            painter.pen_ellipse(x, y, width, height, fill_color, border_color, border_width)
            
            return [
                TextContent(type="text", text=f"✅ 椭圆已绘制: 位置({x},{y}) 尺寸{width}x{height}"),
                ImageContent(type="image", data=painter.to_base64(), mimeType="image/png")
            ]
        
        elif name == "pen_polygon":
            canvas_id = arguments.get("canvas_id", "default")
            if canvas_id not in canvas_storage:
                return [TextContent(type="text", text=f"❌ 画布 '{canvas_id}' 不存在，请先使用 pen_create_canvas 创建画布")]
            
            painter = canvas_storage[canvas_id]
            points = [tuple(p) for p in arguments.get("points", [])]
            fill_color = tuple(arguments.get("fill_color")) if arguments.get("fill_color") else None
            border_color = tuple(arguments.get("border_color")) if arguments.get("border_color") else (0, 0, 0, 255)
            border_width = arguments.get("border_width", 2)
            
            painter.pen_polygon(points, fill_color, border_color, border_width)
            
            return [
                TextContent(type="text", text=f"✅ 多边形已绘制: {len(points)} 个顶点"),
                ImageContent(type="image", data=painter.to_base64(), mimeType="image/png")
            ]
        
        elif name == "pen_arc":
            canvas_id = arguments.get("canvas_id", "default")
            if canvas_id not in canvas_storage:
                return [TextContent(type="text", text=f"❌ 画布 '{canvas_id}' 不存在，请先使用 pen_create_canvas 创建画布")]
            
            painter = canvas_storage[canvas_id]
            x = arguments.get("x")
            y = arguments.get("y")
            width = arguments.get("width")
            height = arguments.get("height")
            start_angle = arguments.get("start_angle", 0)
            end_angle = arguments.get("end_angle", 180)
            color = tuple(arguments.get("color", [0, 0, 0, 255]))
            line_width = arguments.get("line_width", 2)
            
            painter.pen_arc(x, y, width, height, start_angle, end_angle, color, line_width)
            
            return [
                TextContent(type="text", text=f"✅ 弧线已绘制: 角度 {start_angle}° → {end_angle}°"),
                ImageContent(type="image", data=painter.to_base64(), mimeType="image/png")
            ]
        
        elif name == "pen_bezier":
            canvas_id = arguments.get("canvas_id", "default")
            if canvas_id not in canvas_storage:
                return [TextContent(type="text", text=f"❌ 画布 '{canvas_id}' 不存在，请先使用 pen_create_canvas 创建画布")]
            
            painter = canvas_storage[canvas_id]
            points = [tuple(p) for p in arguments.get("points", [])]
            color = tuple(arguments.get("color", [0, 0, 0, 255]))
            width = arguments.get("width", 2)
            
            painter.pen_bezier(points, color, width)
            
            curve_type = {2: "直线", 3: "二次曲线", 4: "三次曲线"}.get(len(points), f"{len(points)}点曲线")
            
            return [
                TextContent(type="text", text=f"✅ 贝塞尔曲线已绘制: {curve_type}"),
                ImageContent(type="image", data=painter.to_base64(), mimeType="image/png")
            ]
        
        elif name == "pen_point":
            canvas_id = arguments.get("canvas_id", "default")
            if canvas_id not in canvas_storage:
                return [TextContent(type="text", text=f"❌ 画布 '{canvas_id}' 不存在，请先使用 pen_create_canvas 创建画布")]
            
            painter = canvas_storage[canvas_id]
            x = arguments.get("x")
            y = arguments.get("y")
            color = tuple(arguments.get("color", [0, 0, 0, 255]))
            size = arguments.get("size", 3)
            
            painter.pen_point(x, y, color, size)
            
            return [
                TextContent(type="text", text=f"✅ 点已绘制: ({x},{y})"),
                ImageContent(type="image", data=painter.to_base64(), mimeType="image/png")
            ]
        
        elif name == "pen_text":
            canvas_id = arguments.get("canvas_id", "default")
            if canvas_id not in canvas_storage:
                return [TextContent(type="text", text=f"❌ 画布 '{canvas_id}' 不存在，请先使用 pen_create_canvas 创建画布")]
            
            painter = canvas_storage[canvas_id]
            x = arguments.get("x")
            y = arguments.get("y")
            text = arguments.get("text", "")
            color = tuple(arguments.get("color", [0, 0, 0, 255]))
            font_size = arguments.get("font_size", 16)
            
            painter.pen_text(x, y, text, color, font_size)
            
            return [
                TextContent(type="text", text=f"✅ 文字已绘制: \"{text}\" 位置({x},{y})"),
                ImageContent(type="image", data=painter.to_base64(), mimeType="image/png")
            ]
        
        elif name == "pen_save":
            canvas_id = arguments.get("canvas_id", "default")
            if canvas_id not in canvas_storage:
                return [TextContent(type="text", text=f"❌ 画布 '{canvas_id}' 不存在")]
            
            painter = canvas_storage[canvas_id]
            filename = arguments.get("filename", "canvas.png")
            output_dir = arguments.get("output_dir")
            
            file_path = get_output_path(filename, output_dir)
            painter.save(file_path)
            
            return [
                TextContent(type="text", text=f"✅ 画布已保存: {file_path}\n尺寸: {painter.width}x{painter.height}"),
                ImageContent(type="image", data=painter.to_base64(), mimeType="image/png")
            ]
        
        elif name == "pen_draw_preset":
            canvas_id = arguments.get("canvas_id", "default")
            if canvas_id not in canvas_storage:
                return [TextContent(type="text", text=f"❌ 画布 '{canvas_id}' 不存在，请先使用 pen_create_canvas 创建画布")]
            
            painter = canvas_storage[canvas_id]
            preset = arguments.get("preset", "car")
            x = arguments.get("x", 0)
            y = arguments.get("y", 0)
            scale = arguments.get("scale", 1.0)
            primary_color = tuple(arguments.get("primary_color")) if arguments.get("primary_color") else None
            
            if preset == "car":
                kwargs = {"x": x, "y": y, "scale": scale}
                if primary_color:
                    kwargs["body_color"] = primary_color
                draw_simple_car(painter, **kwargs)
            elif preset == "house":
                kwargs = {"x": x, "y": y, "scale": scale}
                if primary_color:
                    kwargs["wall_color"] = primary_color
                draw_simple_house(painter, **kwargs)
            elif preset == "tree":
                kwargs = {"x": x, "y": y, "scale": scale}
                if primary_color:
                    kwargs["leaf_color"] = primary_color
                draw_simple_tree(painter, **kwargs)
            
            return [
                TextContent(type="text", text=f"✅ 预设图形已绘制: {preset} 位置({x},{y}) 缩放{scale}"),
                ImageContent(type="image", data=painter.to_base64(), mimeType="image/png")
            ]
        
        elif name == "generate_ui_kit":
            theme = arguments.get("theme", "default")
            output_dir = arguments.get("output_dir", "ui_kit")
            
            output_path = os.path.join(DEFAULT_OUTPUT_DIR, output_dir)
            os.makedirs(output_path, exist_ok=True)
            
            generated_files = []
            
            # 按钮
            for style in ["flat", "gradient", "glossy"]:
                painter = GamePainter(120, 40)
                painter.draw_button(text="按钮", style=ButtonStyle(style))
                file_path = os.path.join(output_path, f"button_{style}.png")
                painter.save(file_path)
                generated_files.append(f"button_{style}.png")
            
            # 控制按钮
            for btn_type in ["close", "settings", "play", "pause", "menu"]:
                painter = create_control_button(48, btn_type)
                file_path = os.path.join(output_path, f"ctrl_{btn_type}.png")
                painter.save(file_path)
                generated_files.append(f"ctrl_{btn_type}.png")
            
            # 图标
            for icon in ["star", "coin", "heart"]:
                painter = create_icon(64, icon)
                file_path = os.path.join(output_path, f"icon_{icon}.png")
                painter.save(file_path)
                generated_files.append(f"icon_{icon}.png")
            
            # 宝石
            for gem in ["diamond", "ruby", "emerald"]:
                painter = GamePainter(64, 64)
                painter.draw_gem(gem_type=gem)
                file_path = os.path.join(output_path, f"gem_{gem}.png")
                painter.save(file_path)
                generated_files.append(f"gem_{gem}.png")
            
            # 进度条
            painter = GamePainter(200, 24)
            painter.draw_progress_bar(progress=75)
            file_path = os.path.join(output_path, "progress_bar.png")
            painter.save(file_path)
            generated_files.append("progress_bar.png")
            
            # 血条
            for hp in [100, 50, 25]:
                painter = GamePainter(150, 16)
                painter.draw_health_bar(hp_percent=hp)
                file_path = os.path.join(output_path, f"health_{hp}.png")
                painter.save(file_path)
                generated_files.append(f"health_{hp}.png")
            
            # 道具槽
            for rarity in ["common", "rare", "epic", "legendary"]:
                painter = GamePainter(64, 64)
                painter.draw_icon_slot(rarity=rarity)
                file_path = os.path.join(output_path, f"slot_{rarity}.png")
                painter.save(file_path)
                generated_files.append(f"slot_{rarity}.png")
            
            # 对话框
            painter = GamePainter(300, 100)
            painter.draw_dialog_box(style="modern" if theme == "default" else theme)
            file_path = os.path.join(output_path, "dialog_box.png")
            painter.save(file_path)
            generated_files.append("dialog_box.png")
            
            # 箭头
            for direction in ["up", "down", "left", "right"]:
                painter = GamePainter(40, 40)
                painter.draw_arrow(direction=direction)
                file_path = os.path.join(output_path, f"arrow_{direction}.png")
                painter.save(file_path)
                generated_files.append(f"arrow_{direction}.png")
            
            return [
                TextContent(
                    type="text",
                    text=f"✅ UI套件已生成完成!\n\n📁 输出目录: {output_path}\n🎨 主题: {theme}\n📦 生成文件数: {len(generated_files)}\n\n文件列表:\n" + "\n".join(f"  • {f}" for f in generated_files)
                )
            ]
        
        else:
            return [TextContent(type="text", text=f"❌ 未知工具: {name}")]
    
    except Exception as e:
        return [TextContent(type="text", text=f"❌ 执行错误: {str(e)}")]


async def main():
    """启动 MCP 服务器"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

