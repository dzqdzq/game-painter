#!/usr/bin/env python3
"""
🎨 GamePainter MCP Server
基础绘图工具服务 - 提供核心绘图能力

通过15个基础工具可以组合绘制任意复杂图形和处理图片
"""

import os
import io
import base64
from typing import Optional, List
from urllib.request import urlopen
from urllib.parse import urlparse
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ImageContent

from PIL import Image, ImageDraw
from painter import GamePainter


# 创建 MCP 服务器
server = Server("game-painter")

# 默认输出目录
DEFAULT_OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(DEFAULT_OUTPUT_DIR, exist_ok=True)

# 画布存储
canvas_storage: dict[str, GamePainter] = {}


def get_output_path(filename: str, output_dir: Optional[str] = None) -> str:
    """获取输出文件路径"""
    dir_path = output_dir or DEFAULT_OUTPUT_DIR
    os.makedirs(dir_path, exist_ok=True)
    return os.path.join(dir_path, filename)


def load_image_from_source(image_path: Optional[str] = None, 
                           image_base64: Optional[str] = None,
                           image_url: Optional[str] = None) -> Image.Image:
    """
    从多种来源加载图片：文件路径、base64数据或https URL
    
    Args:
        image_path: 图片文件路径
        image_base64: 图片的base64编码数据
        image_url: 图片的https URL（必须包含图片后缀）
    
    Returns:
        PIL Image对象
    
    Raises:
        ValueError: 参数错误或URL格式错误
        Exception: 加载图片失败
    """
    # 检查参数：只能提供一个
    provided = [p for p in [image_path, image_base64, image_url] if p is not None]
    if len(provided) != 1:
        raise ValueError("必须提供且仅提供一个参数：image_path、image_base64 或 image_url")
    
    try:
        if image_path:
            # 从文件路径加载
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"图片文件不存在: {image_path}")
            return Image.open(image_path)
        
        elif image_base64:
            # 从 base64 加载
            base64_data = image_base64
            # 处理 data URI 格式：data:image/png;base64,xxx
            if base64_data.startswith("data:"):
                # 提取 base64 部分
                base64_data = base64_data.split(",", 1)[1]
            
            # 解码 base64
            image_bytes = base64.b64decode(base64_data)
            return Image.open(io.BytesIO(image_bytes))
        
        elif image_url:
            # 从 URL 加载
            parsed = urlparse(image_url)
            
            # 验证必须是 https
            if parsed.scheme != "https":
                raise ValueError("URL 必须使用 https 协议")
            
            # 验证必须有图片后缀
            path = parsed.path.lower()
            valid_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']
            if not any(path.endswith(ext) for ext in valid_extensions):
                raise ValueError(f"URL 必须包含图片后缀（支持: {', '.join(valid_extensions)}）")
            
            # 下载图片
            with urlopen(image_url) as response:
                image_bytes = response.read()
                return Image.open(io.BytesIO(image_bytes))
    
    except Exception as e:
        raise Exception(f"加载图片失败: {str(e)}")




@server.list_tools()
async def list_tools():
    """列出所有可用的绘图工具（16个核心工具 + 可选AI生图）"""
    tools = [
        # ========== 1. 创建画布 ==========
        Tool(
            name="create_canvas",
            description="创建一个新的画布。这是使用画笔功能的第一步。后续所有绘图操作都基于此画布。",
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
        
        # ========== 2. 直线 ==========
        Tool(
            name="line",
            description="画直线。支持实线和虚线。通过dash参数可以画虚线。",
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
                    "width": {"type": "integer", "description": "线条宽度", "default": 2},
                    "dash": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "虚线模式 [线段长, 间隔长]，例如 [10, 5]。不设置则为实线"
                    }
                },
                "required": ["x1", "y1", "x2", "y2"]
            }
        ),
        
        # ========== 3. 折线/多段线 ==========
        Tool(
            name="polyline",
            description="画折线（多段连续线）。支持闭合成多边形轮廓，支持虚线。",
            inputSchema={
                "type": "object",
                "properties": {
                    "canvas_id": {"type": "string", "description": "画布ID", "default": "default"},
                    "points": {
                        "type": "array",
                        "items": {"type": "array", "items": {"type": "integer"}},
                        "description": "点坐标列表 [[x1,y1], [x2,y2], ...]"
                    },
                    "color": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "线条颜色 [R,G,B,A]",
                        "default": [0, 0, 0, 255]
                    },
                    "width": {"type": "integer", "description": "线条宽度", "default": 2},
                    "closed": {"type": "boolean", "description": "是否闭合", "default": False},
                    "dash": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "虚线模式 [线段长, 间隔长]"
                    }
                    },
                "required": ["points"]
            }
        ),
        
        # ========== 4. 弧线 ==========
        Tool(
            name="arc",
            description="画弧线。可以画圆弧、半圆等。角度从右边(3点钟方向)为0度，逆时针增加。",
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
        
        # ========== 5. 贝塞尔曲线 ==========
        Tool(
            name="bezier",
            description="画贝塞尔曲线。2个控制点=直线，3个=二次曲线，4个=三次曲线。可用于画平滑曲线。",
            inputSchema={
                "type": "object",
                "properties": {
                    "canvas_id": {"type": "string", "description": "画布ID", "default": "default"},
                    "points": {
                        "type": "array",
                        "items": {"type": "array", "items": {"type": "integer"}},
                        "description": "控制点坐标列表 [[x1,y1], [x2,y2], [x3,y3], ...]"
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
        
        # ========== 6. 波浪线 ==========
        Tool(
            name="wave",
            description="画波浪线。可设置振幅和波长。适用于装饰线、水波效果等。",
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
                    "width": {"type": "integer", "description": "线条宽度", "default": 2},
                    "amplitude": {"type": "integer", "description": "波浪振幅（高度）", "default": 10},
                    "wavelength": {"type": "integer", "description": "波长（一个完整波浪的长度）", "default": 20}
                },
                "required": ["x1", "y1", "x2", "y2"]
            }
        ),
        
        # ========== 7. 矩形 ==========
        Tool(
            name="rect",
            description="画矩形。支持圆角（设置radius参数）。可填充颜色、设置边框。",
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
                        "description": "填充颜色 [R,G,B,A]，不设置则不填充"
                    },
                    "border_color": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "边框颜色 [R,G,B,A]",
                        "default": [0, 0, 0, 255]
                    },
                    "border_width": {"type": "integer", "description": "边框宽度", "default": 2},
                    "radius": {"type": "integer", "description": "圆角半径（0为直角）", "default": 0}
                },
                "required": ["x", "y", "width", "height"]
            }
        ),
        
        # ========== 8. 椭圆/圆 ==========
        Tool(
            name="ellipse",
            description="画椭圆或圆形。宽高相等时为正圆。可填充颜色、设置边框。",
            inputSchema={
                "type": "object",
                "properties": {
                    "canvas_id": {"type": "string", "description": "画布ID", "default": "default"},
                    "x": {"type": "integer", "description": "外接矩形左上角X坐标"},
                    "y": {"type": "integer", "description": "外接矩形左上角Y坐标"},
                    "width": {"type": "integer", "description": "椭圆宽度（宽高相等则为正圆）"},
                    "height": {"type": "integer", "description": "椭圆高度"},
                    "fill_color": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "填充颜色 [R,G,B,A]"
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
        
        # ========== 9. 多边形 ==========
        Tool(
            name="polygon",
            description="画多边形。支持两种模式：1) 自定义顶点坐标 2) 正多边形（设置sides参数）。可画三角形、五边形、六边形等。",
            inputSchema={
                "type": "object",
                "properties": {
                    "canvas_id": {"type": "string", "description": "画布ID", "default": "default"},
                    "points": {
                        "type": "array",
                        "items": {"type": "array", "items": {"type": "integer"}},
                        "description": "自定义顶点坐标 [[x1,y1], [x2,y2], ...]。如果提供此参数则忽略正多边形参数"
                    },
                    "cx": {"type": "integer", "description": "正多边形中心X坐标"},
                    "cy": {"type": "integer", "description": "正多边形中心Y坐标"},
                    "radius": {"type": "integer", "description": "正多边形外接圆半径"},
                    "sides": {"type": "integer", "description": "正多边形边数（3=三角形, 4=正方形, 5=五边形, 6=六边形）", "default": 6},
                    "rotation": {"type": "number", "description": "旋转角度（度），0度时第一个顶点朝上", "default": 0},
                    "fill_color": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "填充颜色 [R,G,B,A]"
                    },
                    "border_color": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "边框颜色 [R,G,B,A]",
                        "default": [0, 0, 0, 255]
                    },
                    "border_width": {"type": "integer", "description": "边框宽度", "default": 2}
                }
            }
        ),
        
        # ========== 10. 图标 ==========
        Tool(
            name="icon",
            description="画简单图标。支持：star(五角星)、arrow(箭头)。可自定义颜色和大小。",
            inputSchema={
                "type": "object",
                "properties": {
                    "canvas_id": {"type": "string", "description": "画布ID", "default": "default"},
                    "icon_type": {
                        "type": "string",
                        "enum": ["star", "arrow"],
                        "description": "图标类型：star(五角星), arrow(箭头)"
                    },
                    "cx": {"type": "integer", "description": "图标中心X坐标"},
                    "cy": {"type": "integer", "description": "图标中心Y坐标"},
                    "size": {"type": "integer", "description": "图标大小", "default": 40},
                    "direction": {
                        "type": "string",
                        "enum": ["up", "down", "left", "right"],
                        "description": "箭头方向（仅对arrow有效）",
                        "default": "right"
                    },
                    "points": {"type": "integer", "description": "星角数量（仅对star有效）", "default": 5},
                    "fill_color": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "填充颜色 [R,G,B,A]",
                        "default": [255, 215, 0, 255]
                    },
                    "border_color": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "边框颜色 [R,G,B,A]"
                    },
                    "border_width": {"type": "integer", "description": "边框宽度", "default": 2}
                },
                "required": ["icon_type", "cx", "cy"]
            }
        ),
        
        # ========== 11. 文字 ==========
        Tool(
            name="text",
            description="在画布上写文字。支持设置字体大小和颜色。",
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
        
        # ========== 12. 保存 ==========
        Tool(
            name="save",
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
        
        # ========== 13. 缩小图片 ==========
        Tool(
            name="resize_image",
            description="缩小图片。支持从文件路径、base64 数据或 https URL 加载图片，指定目标宽度或高度进行等比缩放。使用高质量重采样算法保持图片质量。",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_path": {
                        "type": "string",
                        "description": "图片文件路径。如果提供此参数，将从文件加载图片。不能与 image_base64 或 image_url 参数同时提供。"
                    },
                    "image_base64": {
                        "type": "string",
                        "description": "图片的 base64 编码数据。可以是纯 base64 字符串，也可以是 data URI 格式（data:image/png;base64,xxx）。不能与 image_path 或 image_url 参数同时提供。"
                    },
                    "image_url": {
                        "type": "string",
                        "description": "图片的 https URL。URL 必须包含图片后缀（.png, .jpg, .jpeg, .gif, .bmp, .webp）。不能与 image_path 或 image_base64 参数同时提供。"
                    },
                    "width": {
                        "type": "integer",
                        "description": "目标宽度（像素）。提供宽度时，高度将按比例自动缩放。不能与 height 参数同时提供。"
                    },
                    "height": {
                        "type": "integer",
                        "description": "目标高度（像素）。提供高度时，宽度将按比例自动缩放。不能与 width 参数同时提供。"
                    }
                },
                "required": []
            }
        ),
        
        # ========== 14. 自动裁切透明区域 ==========
        Tool(
            name="auto_crop_transparent",
            description="自动裁切PNG图片中的透明区域，只保留有内容的部分。可去除四周的透明边缘，减小图片尺寸。只支持PNG格式。",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_path": {
                        "type": "string",
                        "description": "图片文件路径。如果提供此参数，将从文件加载图片。不能与 image_base64 或 image_url 参数同时提供。"
                    },
                    "image_base64": {
                        "type": "string",
                        "description": "图片的 base64 编码数据。可以是纯 base64 字符串，也可以是 data URI 格式（data:image/png;base64,xxx）。不能与 image_path 或 image_url 参数同时提供。"
                    },
                    "image_url": {
                        "type": "string",
                        "description": "图片的 https URL。URL 必须是PNG格式，并包含.png后缀。不能与 image_path 或 image_base64 参数同时提供。"
                    }
                },
                "required": []
            }
        ),
        
        # ========== 15. 扩充透明区域 ==========
        Tool(
            name="crop_region",
            description="将图片扩充到指定大小，周围填充透明区域。可以通过偏移量控制原图在新画布中的位置。适用于需要统一尺寸或添加透明边距的场景。",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_path": {
                        "type": "string",
                        "description": "图片文件路径。如果提供此参数，将从文件加载图片。不能与 image_base64 或 image_url 参数同时提供。"
                    },
                    "image_base64": {
                        "type": "string",
                        "description": "图片的 base64 编码数据。可以是纯 base64 字符串，也可以是 data URI 格式（data:image/png;base64,xxx）。不能与 image_path 或 image_url 参数同时提供。"
                    },
                    "image_url": {
                        "type": "string",
                        "description": "图片的 https URL。URL 必须包含图片后缀（.png, .jpg, .jpeg, .gif, .bmp, .webp）。不能与 image_path 或 image_base64 参数同时提供。"
                    },
                    "width": {
                        "type": "integer",
                        "description": "目标宽度（像素）。必须大于原图宽度。"
                    },
                    "height": {
                        "type": "integer",
                        "description": "目标高度（像素）。必须大于原图高度。"
                    },
                    "x_offset": {
                        "type": "integer",
                        "description": "水平偏移量（像素）。正值向右偏移，负值向左偏移。默认为0（水平居中）。",
                        "default": 0
                    },
                    "y_offset": {
                        "type": "integer",
                        "description": "垂直偏移量（像素）。正值向上偏移，负值向下偏移。默认为0（垂直居中）。",
                        "default": 0
                    }
                },
                "required": ["width", "height"]
            }
        )
    ]
    
    return tools


@server.call_tool()
async def call_tool(name: str, arguments: dict):
    """处理工具调用"""
    
    try:
        # ========== 1. 创建画布 ==========
        if name == "create_canvas":
            width = arguments.get("width", 200)
            height = arguments.get("height", 200)
            bg_color = tuple(arguments.get("bg_color", [0, 0, 0, 0]))
            canvas_id = arguments.get("canvas_id", "default")
            
            painter = GamePainter(width, height, bg_color)
            canvas_storage[canvas_id] = painter
            
            return [
                TextContent(type="text", text=f"✅ 画布已创建\nID: {canvas_id}\n尺寸: {width}x{height}\n背景色: RGBA{bg_color}\n\n可用工具: line, polyline, arc, bezier, wave, rect, ellipse, polygon, icon, text\n完成后使用 save 保存。")
            ]
        
        # ========== 2. 直线 ==========
        elif name == "line":
            canvas_id = arguments.get("canvas_id", "default")
            if canvas_id not in canvas_storage:
                return [TextContent(type="text", text=f"❌ 画布 '{canvas_id}' 不存在，请先使用 create_canvas 创建画布")]
            
            painter = canvas_storage[canvas_id]
            x1 = arguments.get("x1")
            y1 = arguments.get("y1")
            x2 = arguments.get("x2")
            y2 = arguments.get("y2")
            color = tuple(arguments.get("color", [0, 0, 0, 255]))
            width = arguments.get("width", 2)
            dash = arguments.get("dash")
            
            painter.pen_line(x1, y1, x2, y2, color, width, dash)
            
            line_type = "虚线" if dash else "直线"
            return [
                TextContent(type="text", text=f"✅ {line_type}已绘制: ({x1},{y1}) → ({x2},{y2})"),
                ImageContent(type="image", data=painter.to_base64(), mimeType="image/png")
            ]
        
        # ========== 3. 折线 ==========
        elif name == "polyline":
            canvas_id = arguments.get("canvas_id", "default")
            if canvas_id not in canvas_storage:
                return [TextContent(type="text", text=f"❌ 画布 '{canvas_id}' 不存在，请先使用 create_canvas 创建画布")]
            
            painter = canvas_storage[canvas_id]
            points = [tuple(p) for p in arguments.get("points", [])]
            color = tuple(arguments.get("color", [0, 0, 0, 255]))
            width = arguments.get("width", 2)
            closed = arguments.get("closed", False)
            dash = arguments.get("dash")
            
            painter.pen_lines(points, color, width, closed, dash)
            
            desc = f"折线已绘制: {len(points)} 个点"
            if closed:
                desc += "(闭合)"
            if dash:
                desc += "(虚线)"
            
            return [
                TextContent(type="text", text=f"✅ {desc}"),
                ImageContent(type="image", data=painter.to_base64(), mimeType="image/png")
            ]
        
        # ========== 4. 弧线 ==========
        elif name == "arc":
            canvas_id = arguments.get("canvas_id", "default")
            if canvas_id not in canvas_storage:
                return [TextContent(type="text", text=f"❌ 画布 '{canvas_id}' 不存在，请先使用 create_canvas 创建画布")]
            
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
        
        # ========== 5. 贝塞尔曲线 ==========
        elif name == "bezier":
            canvas_id = arguments.get("canvas_id", "default")
            if canvas_id not in canvas_storage:
                return [TextContent(type="text", text=f"❌ 画布 '{canvas_id}' 不存在，请先使用 create_canvas 创建画布")]
            
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
        
        # ========== 6. 波浪线 ==========
        elif name == "wave":
            canvas_id = arguments.get("canvas_id", "default")
            if canvas_id not in canvas_storage:
                return [TextContent(type="text", text=f"❌ 画布 '{canvas_id}' 不存在，请先使用 create_canvas 创建画布")]
            
            painter = canvas_storage[canvas_id]
            x1 = arguments.get("x1")
            y1 = arguments.get("y1")
            x2 = arguments.get("x2")
            y2 = arguments.get("y2")
            color = tuple(arguments.get("color", [0, 0, 0, 255]))
            width = arguments.get("width", 2)
            amplitude = arguments.get("amplitude", 10)
            wavelength = arguments.get("wavelength", 20)
            
            painter.pen_wave(x1, y1, x2, y2, color, width, amplitude, wavelength)
            
            return [
                TextContent(type="text", text=f"✅ 波浪线已绘制: ({x1},{y1}) → ({x2},{y2}), 振幅={amplitude}, 波长={wavelength}"),
                ImageContent(type="image", data=painter.to_base64(), mimeType="image/png")
            ]
        
        # ========== 7. 矩形 ==========
        elif name == "rect":
            canvas_id = arguments.get("canvas_id", "default")
            if canvas_id not in canvas_storage:
                return [TextContent(type="text", text=f"❌ 画布 '{canvas_id}' 不存在，请先使用 create_canvas 创建画布")]
            
            painter = canvas_storage[canvas_id]
            x = arguments.get("x")
            y = arguments.get("y")
            width = arguments.get("width")
            height = arguments.get("height")
            fill_color = tuple(arguments.get("fill_color")) if arguments.get("fill_color") else None
            border_color = tuple(arguments.get("border_color")) if arguments.get("border_color") else (0, 0, 0, 255)
            border_width = arguments.get("border_width", 2)
            radius = arguments.get("radius", 0)
            
            painter.pen_rect(x, y, width, height, fill_color, border_color, border_width, radius)
            
            rect_type = "圆角矩形" if radius > 0 else "矩形"
            return [
                TextContent(type="text", text=f"✅ {rect_type}已绘制: 位置({x},{y}) 尺寸{width}x{height}"),
                ImageContent(type="image", data=painter.to_base64(), mimeType="image/png")
            ]
        
        # ========== 8. 椭圆/圆 ==========
        elif name == "ellipse":
            canvas_id = arguments.get("canvas_id", "default")
            if canvas_id not in canvas_storage:
                return [TextContent(type="text", text=f"❌ 画布 '{canvas_id}' 不存在，请先使用 create_canvas 创建画布")]
            
            painter = canvas_storage[canvas_id]
            x = arguments.get("x")
            y = arguments.get("y")
            width = arguments.get("width")
            height = arguments.get("height")
            fill_color = tuple(arguments.get("fill_color")) if arguments.get("fill_color") else None
            border_color = tuple(arguments.get("border_color")) if arguments.get("border_color") else (0, 0, 0, 255)
            border_width = arguments.get("border_width", 2)
            
            painter.pen_ellipse(x, y, width, height, fill_color, border_color, border_width)
            
            shape_type = "正圆" if width == height else "椭圆"
            return [
                TextContent(type="text", text=f"✅ {shape_type}已绘制: 位置({x},{y}) 尺寸{width}x{height}"),
                ImageContent(type="image", data=painter.to_base64(), mimeType="image/png")
            ]
        
        # ========== 9. 多边形 ==========
        elif name == "polygon":
            canvas_id = arguments.get("canvas_id", "default")
            if canvas_id not in canvas_storage:
                return [TextContent(type="text", text=f"❌ 画布 '{canvas_id}' 不存在，请先使用 create_canvas 创建画布")]
            
            painter = canvas_storage[canvas_id]
            fill_color = tuple(arguments.get("fill_color")) if arguments.get("fill_color") else None
            border_color = tuple(arguments.get("border_color")) if arguments.get("border_color") else (0, 0, 0, 255)
            border_width = arguments.get("border_width", 2)
            
            # 检查是自定义顶点还是正多边形
            custom_points = arguments.get("points")
            
            if custom_points:
                # 自定义顶点多边形
                points = [tuple(p) for p in custom_points]
                painter.pen_polygon(points, fill_color, border_color, border_width)
                return [
                    TextContent(type="text", text=f"✅ 多边形已绘制: {len(points)} 个顶点"),
                    ImageContent(type="image", data=painter.to_base64(), mimeType="image/png")
                ]
            else:
                # 正多边形
                cx = arguments.get("cx")
                cy = arguments.get("cy")
                radius = arguments.get("radius")
                sides = arguments.get("sides", 6)
                rotation = arguments.get("rotation", 0)
                
                if cx is None or cy is None or radius is None:
                    return [TextContent(type="text", text="❌ 正多边形需要提供 cx, cy, radius 参数")]
                
                painter.pen_regular_polygon(cx, cy, radius, sides, rotation, fill_color, border_color, border_width)
                
                side_names = {3: "三角形", 4: "正方形", 5: "五边形", 6: "六边形", 8: "八边形"}
                shape_name = side_names.get(sides, f"{sides}边形")
                
                return [
                    TextContent(type="text", text=f"✅ 正{shape_name}已绘制: 中心({cx},{cy}) 半径{radius}"),
                    ImageContent(type="image", data=painter.to_base64(), mimeType="image/png")
                ]
        
        # ========== 10. 图标 ==========
        elif name == "icon":
            canvas_id = arguments.get("canvas_id", "default")
            if canvas_id not in canvas_storage:
                return [TextContent(type="text", text=f"❌ 画布 '{canvas_id}' 不存在，请先使用 create_canvas 创建画布")]
            
            painter = canvas_storage[canvas_id]
            icon_type = arguments.get("icon_type")
            cx = arguments.get("cx")
            cy = arguments.get("cy")
            size = arguments.get("size", 40)
            fill_color = tuple(arguments.get("fill_color", [255, 215, 0, 255]))
            border_color = tuple(arguments.get("border_color")) if arguments.get("border_color") else None
            border_width = arguments.get("border_width", 2)
            
            if icon_type == "star":
                star_points = arguments.get("points", 5)
                painter.pen_star(cx, cy, size // 2, points=star_points, 
                               fill_color=fill_color, border_color=border_color, border_width=border_width)
                return [
                    TextContent(type="text", text=f"✅ 五角星已绘制: 中心({cx},{cy}) 大小{size}"),
                    ImageContent(type="image", data=painter.to_base64(), mimeType="image/png")
                ]
            
            elif icon_type == "arrow":
                direction = arguments.get("direction", "right")
                painter.pen_arrow_shape(cx, cy, size, direction, fill_color, border_color, border_width)
                dir_names = {"up": "上", "down": "下", "left": "左", "right": "右"}
                return [
                    TextContent(type="text", text=f"✅ {dir_names[direction]}箭头已绘制: 中心({cx},{cy}) 大小{size}"),
                    ImageContent(type="image", data=painter.to_base64(), mimeType="image/png")
                ]
            
            else:
                return [TextContent(type="text", text=f"❌ 未知图标类型: {icon_type}")]
        
        # ========== 11. 文字 ==========
        elif name == "text":
            canvas_id = arguments.get("canvas_id", "default")
            if canvas_id not in canvas_storage:
                return [TextContent(type="text", text=f"❌ 画布 '{canvas_id}' 不存在，请先使用 create_canvas 创建画布")]
            
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
        
        # ========== 12. 保存 ==========
        elif name == "save":
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
        
        # ========== 13. 缩小图片 ==========
        elif name == "resize_image":
            try:
                # 加载图片
                image_path = arguments.get("image_path")
                image_base64 = arguments.get("image_base64")
                image_url = arguments.get("image_url")
                width = arguments.get("width")
                height = arguments.get("height")
                
                # 检查尺寸参数：必须提供 width 或 height 其中一个，不能同时提供
                if width is not None and height is not None:
                    return [TextContent(type="text", text="❌ 不能同时提供 width 和 height 参数，只能提供其中一个以避免图片变形")]
                
                if width is None and height is None:
                    return [TextContent(type="text", text="❌ 必须提供 width 或 height 参数之一")]
                
                # 加载图片
                img = load_image_from_source(
                    image_path=image_path,
                    image_base64=image_base64,
                    image_url=image_url
                )
                
                original_width, original_height = img.size
                
                # 计算目标尺寸（等比缩放）
                if width is not None:
                    # 只提供宽度，按比例缩放高度
                    ratio = width / original_width
                    new_width = width
                    new_height = int(original_height * ratio)
                else:  # height is not None
                    # 只提供高度，按比例缩放宽度
                    ratio = height / original_height
                    new_width = int(original_width * ratio)
                    new_height = height
                
                # 缩小图片（使用高质量重采样算法）
                resized_img = img.resize((new_width, new_height), resample=Image.Resampling.LANCZOS)
                
                # 转换为 base64
                buffer = io.BytesIO()
                resized_img.save(buffer, format="PNG")
                img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
                
                return [
                    ImageContent(type="image", data=img_base64, mimeType="image/png")
                ]
            except Exception as e:
                return [TextContent(type="text", text=f"❌ 缩放图片失败: {str(e)}")]
        
        # ========== 14. 自动裁切透明区域 ==========
        elif name == "auto_crop_transparent":
            try:
                # 加载图片
                image_path = arguments.get("image_path")
                image_base64 = arguments.get("image_base64")
                image_url = arguments.get("image_url")
                
                img = load_image_from_source(
                    image_path=image_path,
                    image_base64=image_base64,
                    image_url=image_url
                )
                
                # 检查是否是PNG格式（需要有alpha通道）
                if img.mode != "RGBA":
                    # 尝试转换为RGBA
                    if img.mode == "RGB":
                        return [TextContent(type="text", text="❌ 图片没有透明通道，无法自动裁切透明区域。此工具仅支持PNG格式的透明图片。")]
                    img = img.convert("RGBA")
                
                # 获取图片的alpha通道
                alpha = img.split()[3]
                
                # 获取非透明像素的边界框
                bbox = alpha.getbbox()
                
                if bbox is None:
                    return [TextContent(type="text", text="❌ 图片完全透明，无法裁切")]
                
                # 裁切图片
                cropped_img = img.crop(bbox)
                
                # 转换为 base64
                buffer = io.BytesIO()
                cropped_img.save(buffer, format="PNG")
                img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
                
                original_size = f"{img.width}x{img.height}"
                cropped_size = f"{cropped_img.width}x{cropped_img.height}"
                
                return [
                    TextContent(type="text", text=f"✅ 透明区域已自动裁切\n原始尺寸: {original_size}\n裁切后尺寸: {cropped_size}\n裁切区域: x={bbox[0]}, y={bbox[1]}, width={bbox[2]-bbox[0]}, height={bbox[3]-bbox[1]}"),
                    ImageContent(type="image", data=img_base64, mimeType="image/png")
                ]
            except Exception as e:
                return [TextContent(type="text", text=f"❌ 自动裁切失败: {str(e)}")]
        
        # ========== 15. 扩充透明区域 ==========
        elif name == "crop_region":
            try:
                # 加载图片
                image_path = arguments.get("image_path")
                image_base64 = arguments.get("image_base64")
                image_url = arguments.get("image_url")
                target_width = arguments.get("width")
                target_height = arguments.get("height")
                x_offset = arguments.get("x_offset", 0)
                y_offset = arguments.get("y_offset", 0)
                
                # 验证必需参数
                if target_width is None or target_height is None:
                    return [TextContent(type="text", text="❌ 必须提供 width 和 height 参数")]
                
                # 加载图片
                img = load_image_from_source(
                    image_path=image_path,
                    image_base64=image_base64,
                    image_url=image_url
                )
                
                # 确保图片有透明通道
                if img.mode != "RGBA":
                    img = img.convert("RGBA")
                
                orig_width, orig_height = img.size
                
                # 验证目标尺寸必须大于原图
                if target_width < orig_width:
                    return [TextContent(type="text", text=f"❌ 目标宽度 ({target_width}px) 必须大于或等于原图宽度 ({orig_width}px)")]
                if target_height < orig_height:
                    return [TextContent(type="text", text=f"❌ 目标高度 ({target_height}px) 必须大于或等于原图高度 ({orig_height}px)")]
                
                # 创建透明背景的新图片
                new_img = Image.new("RGBA", (target_width, target_height), (0, 0, 0, 0))
                
                # 计算原图在新图中的位置（默认居中）
                # x_offset 正值向右，负值向左
                # y_offset 正值向上，负值向下（所以要用减法）
                x_pos = (target_width - orig_width) // 2 + x_offset
                y_pos = (target_height - orig_height) // 2 - y_offset
                
                # 验证位置是否合理（原图不能超出边界）
                if x_pos < 0 or x_pos + orig_width > target_width:
                    return [TextContent(type="text", text=f"❌ x_offset ({x_offset}) 导致图片超出边界。可用范围: [{-(target_width - orig_width)//2}, {(target_width - orig_width)//2}]")]
                if y_pos < 0 or y_pos + orig_height > target_height:
                    return [TextContent(type="text", text=f"❌ y_offset ({y_offset}) 导致图片超出边界。可用范围: [{-(target_height - orig_height)//2}, {(target_height - orig_height)//2}]")]
                
                # 将原图粘贴到新图的指定位置
                new_img.paste(img, (x_pos, y_pos), img)
                
                # 转换为 base64
                buffer = io.BytesIO()
                new_img.save(buffer, format="PNG")
                img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
                
                offset_info = ""
                if x_offset != 0 or y_offset != 0:
                    offset_info = f"\n偏移: x={x_offset}px, y={y_offset}px"
                
                return [
                    TextContent(type="text", text=f"✅ 图片已扩充到透明背景\n原始尺寸: {orig_width}x{orig_height}\n目标尺寸: {target_width}x{target_height}\n原图位置: ({x_pos}, {y_pos}){offset_info}"),
                    ImageContent(type="image", data=img_base64, mimeType="image/png")
                ]
            except Exception as e:
                return [TextContent(type="text", text=f"❌ 扩充透明区域失败: {str(e)}")]
        
        else:
            return [TextContent(type="text", text=f"❌ 未知工具: {name}")]
    
    except Exception as e:
        return [TextContent(type="text", text=f"❌ 执行错误: {str(e)}")]


async def main_async():
    """启动 MCP 服务器 (异步)"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def main():
    """启动 MCP 服务器 (入口点)"""
    import asyncio
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
