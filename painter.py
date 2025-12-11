"""
🎨 GamePainter - 游戏UI占位图生成器
用于快速生成游戏项目demo所需的各种UI占位图
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math
import os
import io
import base64
from typing import Tuple, Optional, List, Literal
from dataclasses import dataclass
from enum import Enum


class GradientDirection(Enum):
    """渐变方向"""
    HORIZONTAL = "horizontal"      # 水平渐变
    VERTICAL = "vertical"          # 垂直渐变
    DIAGONAL = "diagonal"          # 对角线渐变
    RADIAL = "radial"              # 径向渐变


class ButtonStyle(Enum):
    """按钮风格"""
    FLAT = "flat"                  # 扁平化
    GLOSSY = "glossy"              # 光泽
    OUTLINE = "outline"            # 边框
    GRADIENT = "gradient"          # 渐变
    PIXEL = "pixel"                # 像素风


class GamePainter:
    """
    🎮 游戏UI占位图绘制器
    
    专为游戏项目demo设计，可生成各种常用UI元素的占位图
    """
    
    def __init__(self, width: int, height: int, bg_color: Tuple[int, ...] = (0, 0, 0, 0)):
        """
        初始化画布
        
        Args:
            width: 画布宽度（像素）
            height: 画布高度（像素）  
            bg_color: 背景颜色 RGBA，默认透明
        """
        self.width = width
        self.height = height
        self.image = Image.new("RGBA", (width, height), bg_color)
        self.draw = ImageDraw.Draw(self.image)
    
    def _lerp_color(self, c1: Tuple[int, ...], c2: Tuple[int, ...], t: float) -> Tuple[int, ...]:
        """颜色线性插值"""
        return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))
    
    def _ensure_rgba(self, color: Tuple[int, ...]) -> Tuple[int, int, int, int]:
        """确保颜色是 RGBA 格式"""
        if len(color) == 3:
            return (*color, 255)
        return color[:4]
    
    # ==================== 基础图形 ====================
    
    def draw_rounded_rect(
        self,
        x: int = 0, y: int = 0,
        width: Optional[int] = None,
        height: Optional[int] = None,
        radius: int = 10,
        fill_color: Tuple[int, ...] = (100, 149, 237, 255),
        border_color: Optional[Tuple[int, ...]] = None,
        border_width: int = 0,
        gradient: Optional[GradientDirection] = None,
        gradient_end_color: Optional[Tuple[int, ...]] = None
    ):
        """
        绘制圆角矩形
        
        Args:
            x, y: 起始坐标
            width, height: 尺寸，默认使用画布尺寸
            radius: 圆角半径
            fill_color: 填充颜色
            border_color: 边框颜色
            border_width: 边框宽度
            gradient: 渐变方向
            gradient_end_color: 渐变结束颜色
        """
        w = width or self.width
        h = height or self.height
        fill_color = self._ensure_rgba(fill_color)
        
        if gradient and gradient_end_color:
            gradient_end_color = self._ensure_rgba(gradient_end_color)
            # 创建渐变遮罩
            gradient_img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            gradient_draw = ImageDraw.Draw(gradient_img)
            
            if gradient == GradientDirection.VERTICAL:
                for i in range(h):
                    t = i / max(h - 1, 1)
                    color = self._lerp_color(fill_color, gradient_end_color, t)
                    gradient_draw.line([(0, i), (w, i)], fill=color)
            elif gradient == GradientDirection.HORIZONTAL:
                for i in range(w):
                    t = i / max(w - 1, 1)
                    color = self._lerp_color(fill_color, gradient_end_color, t)
                    gradient_draw.line([(i, 0), (i, h)], fill=color)
            elif gradient == GradientDirection.DIAGONAL:
                for i in range(w + h):
                    t = i / max(w + h - 1, 1)
                    color = self._lerp_color(fill_color, gradient_end_color, t)
                    gradient_draw.line([(i, 0), (0, i)], fill=color)
            
            # 创建圆角遮罩
            mask = Image.new("L", (w, h), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.rounded_rectangle([0, 0, w-1, h-1], radius=radius, fill=255)
            
            # 应用遮罩
            gradient_img.putalpha(mask)
            self.image.paste(gradient_img, (x, y), gradient_img)
        else:
            self.draw.rounded_rectangle(
                [x, y, x + w - 1, y + h - 1],
                radius=radius,
                fill=fill_color,
                outline=border_color,
                width=border_width
            )
    
    def draw_circle(
        self,
        center_x: Optional[int] = None,
        center_y: Optional[int] = None,
        radius: Optional[int] = None,
        fill_color: Tuple[int, ...] = (100, 149, 237, 200),
        border_color: Optional[Tuple[int, ...]] = (100, 149, 237, 255),
        border_width: int = 2
    ):
        """
        绘制圆形
        
        Args:
            center_x, center_y: 圆心坐标，默认画布中心
            radius: 半径，默认适配画布
            fill_color: 填充颜色
            border_color: 边框颜色
            border_width: 边框宽度
        """
        cx = center_x if center_x is not None else self.width // 2
        cy = center_y if center_y is not None else self.height // 2
        r = radius if radius is not None else min(self.width, self.height) // 2 - border_width - 2
        
        fill_color = self._ensure_rgba(fill_color)
        
        # 绘制边框
        if border_color and border_width > 0:
            border_color = self._ensure_rgba(border_color)
            self.draw.ellipse(
                [cx - r - border_width, cy - r - border_width,
                 cx + r + border_width, cy + r + border_width],
                fill=border_color
            )
        
        # 绘制填充
        self.draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill_color)
    
    def draw_polygon(
        self,
        sides: int = 6,
        center_x: Optional[int] = None,
        center_y: Optional[int] = None,
        radius: Optional[int] = None,
        rotation: float = 0,
        fill_color: Tuple[int, ...] = (100, 149, 237, 255),
        border_color: Optional[Tuple[int, ...]] = None,
        border_width: int = 0
    ):
        """
        绘制正多边形
        
        Args:
            sides: 边数（3=三角形, 6=六边形等）
            center_x, center_y: 中心坐标
            radius: 外接圆半径
            rotation: 旋转角度（度）
            fill_color: 填充颜色
            border_color: 边框颜色
            border_width: 边框宽度
        """
        cx = center_x if center_x is not None else self.width // 2
        cy = center_y if center_y is not None else self.height // 2
        r = radius if radius is not None else min(self.width, self.height) // 2 - 4
        
        fill_color = self._ensure_rgba(fill_color)
        rot_rad = math.radians(rotation - 90)  # 默认顶点朝上
        
        points = []
        for i in range(sides):
            angle = rot_rad + (2 * math.pi * i / sides)
            px = cx + r * math.cos(angle)
            py = cy + r * math.sin(angle)
            points.append((px, py))
        
        self.draw.polygon(points, fill=fill_color, outline=border_color, width=border_width)
    
    # ==================== 游戏UI元素 ====================
    
    def draw_button(
        self,
        x: int = 0, y: int = 0,
        width: Optional[int] = None,
        height: Optional[int] = None,
        text: str = "",
        style: ButtonStyle = ButtonStyle.GRADIENT,
        primary_color: Tuple[int, ...] = (65, 105, 225, 255),
        secondary_color: Tuple[int, ...] = (30, 60, 180, 255),
        text_color: Tuple[int, ...] = (255, 255, 255, 255),
        radius: int = 8
    ):
        """
        绘制游戏按钮
        
        Args:
            x, y: 位置
            width, height: 尺寸
            text: 按钮文字
            style: 按钮风格
            primary_color: 主颜色
            secondary_color: 次要颜色
            text_color: 文字颜色
            radius: 圆角半径
        """
        w = width or self.width
        h = height or self.height
        
        primary_color = self._ensure_rgba(primary_color)
        secondary_color = self._ensure_rgba(secondary_color)
        
        if style == ButtonStyle.FLAT:
            self.draw.rounded_rectangle([x, y, x+w-1, y+h-1], radius=radius, fill=primary_color)
        
        elif style == ButtonStyle.GRADIENT:
            self.draw_rounded_rect(
                x, y, w, h, radius,
                fill_color=primary_color,
                gradient=GradientDirection.VERTICAL,
                gradient_end_color=secondary_color
            )
        
        elif style == ButtonStyle.GLOSSY:
            # 底色
            self.draw_rounded_rect(x, y, w, h, radius, fill_color=secondary_color)
            # 上半部分高光
            highlight = (*primary_color[:3], 180)
            self.draw_rounded_rect(x+2, y+2, w-4, h//2-2, radius-2, fill_color=highlight)
        
        elif style == ButtonStyle.OUTLINE:
            self.draw.rounded_rectangle(
                [x, y, x+w-1, y+h-1],
                radius=radius,
                fill=(0, 0, 0, 0),
                outline=primary_color,
                width=3
            )
        
        elif style == ButtonStyle.PIXEL:
            # 像素风格 - 无圆角
            self.draw.rectangle([x, y, x+w-1, y+h-1], fill=primary_color)
            # 像素边框
            self.draw.rectangle([x+2, y+2, x+w-3, y+h-3], outline=secondary_color, width=2)
        
        # 绘制文字
        if text:
            try:
                font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", min(h//2, 24))
            except:
                font = ImageFont.load_default()
            
            bbox = self.draw.textbbox((0, 0), text, font=font)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]
            text_x = x + (w - text_w) // 2
            text_y = y + (h - text_h) // 2 - 2
            
            self.draw.text((text_x, text_y), text, fill=self._ensure_rgba(text_color), font=font)
    
    def draw_progress_bar(
        self,
        x: int = 0, y: int = 0,
        width: Optional[int] = None,
        height: Optional[int] = None,
        progress: float = 50,
        bg_color: Tuple[int, ...] = (60, 60, 60, 255),
        fill_color: Tuple[int, ...] = (50, 205, 50, 255),
        border_color: Optional[Tuple[int, ...]] = (100, 100, 100, 255),
        border_width: int = 2,
        show_glow: bool = True
    ):
        """
        绘制进度条
        
        Args:
            x, y: 位置
            width, height: 尺寸
            progress: 进度百分比 0-100
            bg_color: 背景颜色
            fill_color: 填充颜色
            border_color: 边框颜色
            border_width: 边框宽度
            show_glow: 是否显示发光效果
        """
        w = width or self.width
        h = height or self.height
        radius = h // 2
        
        progress = max(0, min(100, progress))
        
        # 背景
        self.draw.rounded_rectangle([x, y, x+w-1, y+h-1], radius=radius, fill=bg_color)
        
        # 进度填充
        fill_width = int((w - 4) * progress / 100)
        if fill_width > 0:
            if show_glow:
                # 发光效果
                glow_color = (*fill_color[:3], 100)
                self.draw.rounded_rectangle(
                    [x+1, y+1, x+3+fill_width, y+h-2],
                    radius=radius-1,
                    fill=glow_color
                )
            
            self.draw.rounded_rectangle(
                [x+2, y+2, x+2+fill_width, y+h-3],
                radius=max(1, radius-2),
                fill=fill_color
            )
        
        # 边框
        if border_color and border_width > 0:
            self.draw.rounded_rectangle(
                [x, y, x+w-1, y+h-1],
                radius=radius,
                outline=border_color,
                width=border_width
            )
    
    def draw_health_bar(
        self,
        x: int = 0, y: int = 0,
        width: Optional[int] = None,
        height: Optional[int] = None,
        hp_percent: float = 75,
        show_segments: bool = True,
        segment_count: int = 10
    ):
        """
        绘制生命值条（游戏常用）
        
        Args:
            x, y: 位置
            width, height: 尺寸
            hp_percent: 血量百分比
            show_segments: 是否显示分段
            segment_count: 分段数量
        """
        w = width or self.width
        h = height or self.height
        
        # 根据血量选择颜色
        if hp_percent > 60:
            fill_color = (50, 205, 50, 255)  # 绿色
        elif hp_percent > 30:
            fill_color = (255, 165, 0, 255)  # 橙色
        else:
            fill_color = (255, 50, 50, 255)  # 红色
        
        # 背景
        self.draw.rectangle([x, y, x+w-1, y+h-1], fill=(30, 30, 30, 255))
        
        # 血量
        hp_width = int((w - 4) * hp_percent / 100)
        if hp_width > 0:
            self.draw.rectangle([x+2, y+2, x+2+hp_width, y+h-3], fill=fill_color)
        
        # 分段线
        if show_segments:
            seg_width = w // segment_count
            for i in range(1, segment_count):
                sx = x + i * seg_width
                self.draw.line([(sx, y), (sx, y+h-1)], fill=(0, 0, 0, 150), width=1)
        
        # 边框
        self.draw.rectangle([x, y, x+w-1, y+h-1], outline=(80, 80, 80, 255), width=2)
    
    def draw_star(
        self,
        center_x: Optional[int] = None,
        center_y: Optional[int] = None,
        size: Optional[int] = None,
        points: int = 5,
        fill_color: Tuple[int, ...] = (255, 215, 0, 255),
        border_color: Optional[Tuple[int, ...]] = (218, 165, 32, 255),
        border_width: int = 2,
        inner_ratio: float = 0.4
    ):
        """
        绘制星形
        
        Args:
            center_x, center_y: 中心坐标
            size: 外圈半径
            points: 星角数量
            fill_color: 填充颜色
            border_color: 边框颜色
            border_width: 边框宽度
            inner_ratio: 内圈与外圈的比例
        """
        cx = center_x if center_x is not None else self.width // 2
        cy = center_y if center_y is not None else self.height // 2
        outer_r = size if size is not None else min(self.width, self.height) // 2 - 4
        inner_r = int(outer_r * inner_ratio)
        
        fill_color = self._ensure_rgba(fill_color)
        
        vertices = []
        for i in range(points * 2):
            angle = math.pi * i / points - math.pi / 2
            r = outer_r if i % 2 == 0 else inner_r
            px = cx + r * math.cos(angle)
            py = cy + r * math.sin(angle)
            vertices.append((px, py))
        
        self.draw.polygon(vertices, fill=fill_color, outline=border_color, width=border_width)
    
    def draw_arrow(
        self,
        direction: Literal["up", "down", "left", "right"] = "right",
        x: int = 0, y: int = 0,
        width: Optional[int] = None,
        height: Optional[int] = None,
        fill_color: Tuple[int, ...] = (255, 165, 0, 255),
        style: Literal["solid", "outline", "chevron"] = "solid"
    ):
        """
        绘制箭头
        
        Args:
            direction: 箭头方向
            x, y: 位置
            width, height: 尺寸
            fill_color: 填充颜色
            style: 箭头样式
        """
        w = width or self.width
        h = height or self.height
        
        fill_color = self._ensure_rgba(fill_color)
        
        # 计算箭头顶点
        if style == "chevron":
            # V形箭头
            thickness = min(w, h) // 4
            if direction == "right":
                points = [(x+w//4, y+h//6), (x+w*3//4, y+h//2), (x+w//4, y+h*5//6)]
            elif direction == "left":
                points = [(x+w*3//4, y+h//6), (x+w//4, y+h//2), (x+w*3//4, y+h*5//6)]
            elif direction == "up":
                points = [(x+w//6, y+h*3//4), (x+w//2, y+h//4), (x+w*5//6, y+h*3//4)]
            else:
                points = [(x+w//6, y+h//4), (x+w//2, y+h*3//4), (x+w*5//6, y+h//4)]
            
            self.draw.line(points, fill=fill_color, width=thickness, joint="curve")
        else:
            # 实心三角形箭头
            margin = min(w, h) // 6
            if direction == "right":
                points = [(x+margin, y+margin), (x+w-margin, y+h//2), (x+margin, y+h-margin)]
            elif direction == "left":
                points = [(x+w-margin, y+margin), (x+margin, y+h//2), (x+w-margin, y+h-margin)]
            elif direction == "up":
                points = [(x+margin, y+h-margin), (x+w//2, y+margin), (x+w-margin, y+h-margin)]
            else:
                points = [(x+margin, y+margin), (x+w//2, y+h-margin), (x+w-margin, y+margin)]
            
            if style == "solid":
                self.draw.polygon(points, fill=fill_color)
            else:
                self.draw.polygon(points, outline=fill_color, width=3)
    
    def draw_coin(
        self,
        center_x: Optional[int] = None,
        center_y: Optional[int] = None,
        radius: Optional[int] = None,
        gold_color: Tuple[int, ...] = (255, 215, 0, 255),
        show_symbol: bool = True,
        symbol: str = "$"
    ):
        """
        绘制金币
        
        Args:
            center_x, center_y: 中心坐标
            radius: 半径
            gold_color: 金色
            show_symbol: 是否显示符号
            symbol: 显示的符号
        """
        cx = center_x if center_x is not None else self.width // 2
        cy = center_y if center_y is not None else self.height // 2
        r = radius if radius is not None else min(self.width, self.height) // 2 - 4
        
        gold_color = self._ensure_rgba(gold_color)
        dark_gold = (218, 165, 32, 255)
        light_gold = (255, 239, 180, 255)
        
        # 外圈
        self.draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=dark_gold)
        
        # 内圈
        inner_r = int(r * 0.85)
        self.draw.ellipse([cx-inner_r, cy-inner_r, cx+inner_r, cy+inner_r], fill=gold_color)
        
        # 高光
        highlight_r = int(r * 0.7)
        self.draw.arc(
            [cx-highlight_r, cy-highlight_r, cx+highlight_r, cy+highlight_r],
            start=200, end=340, fill=light_gold, width=2
        )
        
        # 符号
        if show_symbol:
            try:
                font_size = int(r * 1.2)
                font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
            except:
                font = ImageFont.load_default()
            
            bbox = self.draw.textbbox((0, 0), symbol, font=font)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]
            self.draw.text(
                (cx - text_w//2, cy - text_h//2 - 2),
                symbol, fill=dark_gold, font=font
            )
    
    def draw_gem(
        self,
        center_x: Optional[int] = None,
        center_y: Optional[int] = None,
        size: Optional[int] = None,
        gem_type: Literal["diamond", "ruby", "emerald", "sapphire"] = "diamond"
    ):
        """
        绘制宝石
        
        Args:
            center_x, center_y: 中心坐标
            size: 尺寸
            gem_type: 宝石类型
        """
        cx = center_x if center_x is not None else self.width // 2
        cy = center_y if center_y is not None else self.height // 2
        s = size if size is not None else min(self.width, self.height) // 2 - 4
        
        colors = {
            "diamond": ((200, 230, 255, 255), (150, 200, 255, 255), (100, 180, 255, 255)),
            "ruby": ((255, 100, 100, 255), (200, 50, 50, 255), (150, 30, 30, 255)),
            "emerald": ((100, 255, 150, 255), (50, 200, 100, 255), (30, 150, 80, 255)),
            "sapphire": ((100, 150, 255, 255), (50, 100, 200, 255), (30, 80, 180, 255))
        }
        
        light, mid, dark = colors.get(gem_type, colors["diamond"])
        
        # 菱形宝石
        top = (cx, cy - s)
        bottom = (cx, cy + s * 0.6)
        left = (cx - s * 0.7, cy - s * 0.2)
        right = (cx + s * 0.7, cy - s * 0.2)
        
        # 上部三角
        self.draw.polygon([top, left, (cx, cy)], fill=light)
        self.draw.polygon([top, right, (cx, cy)], fill=mid)
        
        # 下部三角
        self.draw.polygon([left, bottom, (cx, cy)], fill=mid)
        self.draw.polygon([right, bottom, (cx, cy)], fill=dark)
        
        # 高光
        highlight = [(cx - s*0.15, cy - s*0.5), (cx + s*0.1, cy - s*0.6), (cx - s*0.1, cy - s*0.3)]
        self.draw.polygon(highlight, fill=(255, 255, 255, 150))
    
    def draw_heart(
        self,
        center_x: Optional[int] = None,
        center_y: Optional[int] = None,
        size: Optional[int] = None,
        fill_color: Tuple[int, ...] = (255, 50, 80, 255),
        border_color: Optional[Tuple[int, ...]] = (200, 30, 60, 255)
    ):
        """
        绘制爱心
        
        Args:
            center_x, center_y: 中心坐标
            size: 尺寸
            fill_color: 填充颜色
            border_color: 边框颜色
        """
        cx = center_x if center_x is not None else self.width // 2
        cy = center_y if center_y is not None else self.height // 2
        s = size if size is not None else min(self.width, self.height) // 2 - 4
        
        fill_color = self._ensure_rgba(fill_color)
        
        # 使用参数方程绘制心形
        points = []
        for t in range(0, 360, 5):
            rad = math.radians(t)
            x = 16 * (math.sin(rad) ** 3)
            y = 13 * math.cos(rad) - 5 * math.cos(2*rad) - 2 * math.cos(3*rad) - math.cos(4*rad)
            points.append((cx + x * s / 18, cy - y * s / 18))
        
        self.draw.polygon(points, fill=fill_color, outline=border_color, width=2)
        
        # 高光
        self.draw.ellipse(
            [cx - s*0.4, cy - s*0.5, cx - s*0.1, cy - s*0.2],
            fill=(255, 255, 255, 100)
        )
    
    def draw_shield(
        self,
        x: int = 0, y: int = 0,
        width: Optional[int] = None,
        height: Optional[int] = None,
        fill_color: Tuple[int, ...] = (70, 130, 180, 255),
        border_color: Tuple[int, ...] = (192, 192, 192, 255)
    ):
        """
        绘制盾牌
        
        Args:
            x, y: 位置
            width, height: 尺寸
            fill_color: 填充颜色
            border_color: 边框颜色
        """
        w = width or self.width
        h = height or self.height
        cx = x + w // 2
        
        fill_color = self._ensure_rgba(fill_color)
        border_color = self._ensure_rgba(border_color)
        
        # 盾牌形状点
        points = [
            (cx, y + 4),                          # 顶部中心
            (x + w - 4, y + h * 0.15),            # 右上
            (x + w - 4, y + h * 0.5),             # 右中
            (cx, y + h - 4),                      # 底部
            (x + 4, y + h * 0.5),                 # 左中
            (x + 4, y + h * 0.15),                # 左上
        ]
        
        self.draw.polygon(points, fill=fill_color, outline=border_color, width=3)
        
        # 中间装饰线
        self.draw.line([(cx, y + h*0.15), (cx, y + h*0.75)], fill=border_color, width=2)
        self.draw.line([(x + w*0.2, y + h*0.35), (x + w*0.8, y + h*0.35)], fill=border_color, width=2)
    
    def draw_icon_slot(
        self,
        x: int = 0, y: int = 0,
        width: Optional[int] = None,
        height: Optional[int] = None,
        rarity: Literal["common", "uncommon", "rare", "epic", "legendary"] = "common",
        show_shine: bool = False
    ):
        """
        绘制道具格子/装备槽
        
        Args:
            x, y: 位置
            width, height: 尺寸
            rarity: 稀有度
            show_shine: 是否显示闪光效果
        """
        w = width or self.width
        h = height or self.height
        
        rarity_colors = {
            "common": ((80, 80, 80, 255), (120, 120, 120, 255)),
            "uncommon": ((30, 100, 30, 255), (50, 180, 50, 255)),
            "rare": ((30, 60, 150, 255), (50, 100, 220, 255)),
            "epic": ((100, 50, 150, 255), (160, 80, 220, 255)),
            "legendary": ((180, 120, 30, 255), (255, 200, 50, 255))
        }
        
        bg_color, border_color = rarity_colors.get(rarity, rarity_colors["common"])
        
        # 背景
        self.draw.rounded_rectangle([x, y, x+w-1, y+h-1], radius=4, fill=bg_color)
        
        # 内边框
        self.draw.rounded_rectangle([x+2, y+2, x+w-3, y+h-3], radius=3, outline=(40, 40, 40, 255), width=1)
        
        # 边框
        self.draw.rounded_rectangle([x, y, x+w-1, y+h-1], radius=4, outline=border_color, width=2)
        
        # 闪光效果
        if show_shine and rarity in ["epic", "legendary"]:
            for i in range(3):
                shine_x = x + w//4 + i * w//4
                self.draw.line(
                    [(shine_x, y), (shine_x + w//8, y + h//3)],
                    fill=(255, 255, 255, 100 - i*30),
                    width=2
                )
    
    def draw_minimap_frame(
        self,
        x: int = 0, y: int = 0,
        width: Optional[int] = None,
        height: Optional[int] = None,
        shape: Literal["circle", "square", "hexagon"] = "circle",
        border_color: Tuple[int, ...] = (200, 180, 150, 255)
    ):
        """
        绘制小地图框架
        
        Args:
            x, y: 位置
            width, height: 尺寸
            shape: 形状
            border_color: 边框颜色
        """
        w = width or self.width
        h = height or self.height
        cx = x + w // 2
        cy = y + h // 2
        r = min(w, h) // 2 - 4
        
        border_color = self._ensure_rgba(border_color)
        
        # 背景色（模拟地图）
        map_bg = (80, 120, 80, 255)
        
        if shape == "circle":
            self.draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=map_bg)
            self.draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline=border_color, width=3)
        elif shape == "square":
            self.draw.rounded_rectangle([x+4, y+4, x+w-5, y+h-5], radius=4, fill=map_bg)
            self.draw.rounded_rectangle([x+4, y+4, x+w-5, y+h-5], radius=4, outline=border_color, width=3)
        else:  # hexagon
            temp_painter = GamePainter(w, h, (0, 0, 0, 0))
            temp_painter.draw_polygon(6, w//2, h//2, r, 30, map_bg, border_color, 3)
            self.image.paste(temp_painter.image, (x, y), temp_painter.image)
        
        # 添加玩家指示点
        self.draw.ellipse([cx-3, cy-3, cx+3, cy+3], fill=(255, 255, 255, 255))
        
        # 添加方向指示
        self.draw.polygon(
            [(cx, cy-8), (cx-4, cy-2), (cx+4, cy-2)],
            fill=(255, 200, 50, 255)
        )
    
    def draw_dialog_box(
        self,
        x: int = 0, y: int = 0,
        width: Optional[int] = None,
        height: Optional[int] = None,
        style: Literal["modern", "fantasy", "scifi", "pixel"] = "modern",
        show_arrow: bool = True
    ):
        """
        绘制对话框
        
        Args:
            x, y: 位置
            width, height: 尺寸
            style: 风格
            show_arrow: 是否显示对话箭头
        """
        w = width or self.width
        h = height or self.height
        
        style_colors = {
            "modern": ((30, 30, 30, 230), (100, 100, 100, 255)),
            "fantasy": ((60, 40, 30, 230), (180, 140, 100, 255)),
            "scifi": ((20, 30, 50, 230), (0, 200, 255, 255)),
            "pixel": ((40, 40, 60, 255), (150, 150, 180, 255))
        }
        
        bg_color, border_color = style_colors.get(style, style_colors["modern"])
        
        radius = 0 if style == "pixel" else 12
        
        # 主体
        if style == "pixel":
            self.draw.rectangle([x, y, x+w-1, y+h-1], fill=bg_color)
            self.draw.rectangle([x, y, x+w-1, y+h-1], outline=border_color, width=3)
        else:
            self.draw.rounded_rectangle([x, y, x+w-1, y+h-1], radius=radius, fill=bg_color)
            self.draw.rounded_rectangle([x, y, x+w-1, y+h-1], radius=radius, outline=border_color, width=2)
        
        # 对话箭头
        if show_arrow:
            arrow_x = x + w // 4
            self.draw.polygon(
                [(arrow_x, y+h-1), (arrow_x+15, y+h-1), (arrow_x+7, y+h+12)],
                fill=bg_color, outline=border_color
            )
    
    def draw_tooltip(
        self,
        x: int = 0, y: int = 0,
        width: Optional[int] = None,
        height: Optional[int] = None,
        title: str = "道具名称",
        rarity: Literal["common", "uncommon", "rare", "epic", "legendary"] = "rare"
    ):
        """
        绘制工具提示框
        
        Args:
            x, y: 位置
            width, height: 尺寸
            title: 标题
            rarity: 稀有度
        """
        w = width or self.width
        h = height or self.height
        
        rarity_title_colors = {
            "common": (180, 180, 180, 255),
            "uncommon": (30, 255, 30, 255),
            "rare": (50, 150, 255, 255),
            "epic": (180, 80, 255, 255),
            "legendary": (255, 200, 50, 255)
        }
        
        # 背景
        self.draw.rounded_rectangle([x, y, x+w-1, y+h-1], radius=4, fill=(20, 20, 25, 240))
        self.draw.rounded_rectangle([x, y, x+w-1, y+h-1], radius=4, outline=(60, 60, 70, 255), width=1)
        
        # 标题
        title_color = rarity_title_colors.get(rarity, (180, 180, 180, 255))
        try:
            font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 14)
        except:
            font = ImageFont.load_default()
        
        self.draw.text((x + 10, y + 8), title, fill=title_color, font=font)
        
        # 分隔线
        self.draw.line([(x+8, y+28), (x+w-8, y+28)], fill=(60, 60, 70, 255), width=1)
        
        # 模拟属性文本
        try:
            small_font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 11)
        except:
            small_font = ImageFont.load_default()
        
        self.draw.text((x+10, y+35), "+10 攻击力", fill=(150, 255, 150, 255), font=small_font)
        self.draw.text((x+10, y+52), "+5 暴击率", fill=(255, 200, 100, 255), font=small_font)
    
    # ==================== 常用按钮图标 ====================
    
    def draw_close_button(
        self,
        center_x: Optional[int] = None,
        center_y: Optional[int] = None,
        size: Optional[int] = None,
        bg_color: Tuple[int, ...] = (220, 60, 60, 255),
        icon_color: Tuple[int, ...] = (255, 255, 255, 255),
        style: Literal["circle", "square", "none"] = "circle"
    ):
        """
        绘制关闭按钮 (X)
        
        Args:
            center_x, center_y: 中心坐标
            size: 尺寸
            bg_color: 背景颜色
            icon_color: 图标颜色
            style: 背景样式
        """
        cx = center_x if center_x is not None else self.width // 2
        cy = center_y if center_y is not None else self.height // 2
        s = size if size is not None else min(self.width, self.height) - 4
        r = s // 2
        
        bg_color = self._ensure_rgba(bg_color)
        icon_color = self._ensure_rgba(icon_color)
        
        # 背景
        if style == "circle":
            self.draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=bg_color)
        elif style == "square":
            self.draw.rounded_rectangle([cx-r, cy-r, cx+r, cy+r], radius=4, fill=bg_color)
        
        # X 图标
        offset = int(r * 0.5)
        line_width = max(2, s // 10)
        self.draw.line([(cx-offset, cy-offset), (cx+offset, cy+offset)], fill=icon_color, width=line_width)
        self.draw.line([(cx+offset, cy-offset), (cx-offset, cy+offset)], fill=icon_color, width=line_width)
    
    def draw_settings_button(
        self,
        center_x: Optional[int] = None,
        center_y: Optional[int] = None,
        size: Optional[int] = None,
        bg_color: Optional[Tuple[int, ...]] = None,
        icon_color: Tuple[int, ...] = (100, 100, 100, 255),
        style: Literal["circle", "square", "none"] = "none"
    ):
        """
        绘制设置按钮 (齿轮)
        
        Args:
            center_x, center_y: 中心坐标
            size: 尺寸
            bg_color: 背景颜色
            icon_color: 图标颜色
            style: 背景样式
        """
        cx = center_x if center_x is not None else self.width // 2
        cy = center_y if center_y is not None else self.height // 2
        s = size if size is not None else min(self.width, self.height) - 4
        r = s // 2
        
        icon_color = self._ensure_rgba(icon_color)
        
        # 背景
        if bg_color and style != "none":
            bg_color = self._ensure_rgba(bg_color)
            if style == "circle":
                self.draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=bg_color)
            elif style == "square":
                self.draw.rounded_rectangle([cx-r, cy-r, cx+r, cy+r], radius=4, fill=bg_color)
        
        # 齿轮
        outer_r = int(r * 0.85)
        inner_r = int(r * 0.5)
        center_r = int(r * 0.3)
        teeth = 8
        
        # 绘制齿轮外圈
        points = []
        for i in range(teeth * 2):
            angle = math.pi * i / teeth - math.pi / 2
            radius = outer_r if i % 2 == 0 else inner_r
            px = cx + radius * math.cos(angle)
            py = cy + radius * math.sin(angle)
            points.append((px, py))
        
        self.draw.polygon(points, fill=icon_color)
        
        # 中心孔
        self.draw.ellipse([cx-center_r, cy-center_r, cx+center_r, cy+center_r], 
                          fill=(0, 0, 0, 0) if bg_color is None else bg_color)
    
    def draw_play_button(
        self,
        center_x: Optional[int] = None,
        center_y: Optional[int] = None,
        size: Optional[int] = None,
        bg_color: Tuple[int, ...] = (50, 180, 50, 255),
        icon_color: Tuple[int, ...] = (255, 255, 255, 255),
        style: Literal["circle", "square", "none"] = "circle"
    ):
        """
        绘制播放按钮 (三角形)
        
        Args:
            center_x, center_y: 中心坐标
            size: 尺寸
            bg_color: 背景颜色
            icon_color: 图标颜色
            style: 背景样式
        """
        cx = center_x if center_x is not None else self.width // 2
        cy = center_y if center_y is not None else self.height // 2
        s = size if size is not None else min(self.width, self.height) - 4
        r = s // 2
        
        bg_color = self._ensure_rgba(bg_color)
        icon_color = self._ensure_rgba(icon_color)
        
        # 背景
        if style == "circle":
            self.draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=bg_color)
        elif style == "square":
            self.draw.rounded_rectangle([cx-r, cy-r, cx+r, cy+r], radius=4, fill=bg_color)
        
        # 播放三角形（稍微偏右以视觉居中）
        offset = int(r * 0.45)
        points = [
            (cx - offset + 2, cy - offset),
            (cx + offset + 2, cy),
            (cx - offset + 2, cy + offset)
        ]
        self.draw.polygon(points, fill=icon_color)
    
    def draw_pause_button(
        self,
        center_x: Optional[int] = None,
        center_y: Optional[int] = None,
        size: Optional[int] = None,
        bg_color: Tuple[int, ...] = (255, 180, 50, 255),
        icon_color: Tuple[int, ...] = (255, 255, 255, 255),
        style: Literal["circle", "square", "none"] = "circle"
    ):
        """
        绘制暂停按钮 (||)
        
        Args:
            center_x, center_y: 中心坐标
            size: 尺寸
            bg_color: 背景颜色
            icon_color: 图标颜色
            style: 背景样式
        """
        cx = center_x if center_x is not None else self.width // 2
        cy = center_y if center_y is not None else self.height // 2
        s = size if size is not None else min(self.width, self.height) - 4
        r = s // 2
        
        bg_color = self._ensure_rgba(bg_color)
        icon_color = self._ensure_rgba(icon_color)
        
        # 背景
        if style == "circle":
            self.draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=bg_color)
        elif style == "square":
            self.draw.rounded_rectangle([cx-r, cy-r, cx+r, cy+r], radius=4, fill=bg_color)
        
        # 暂停条
        bar_width = max(3, int(r * 0.25))
        bar_height = int(r * 0.9)
        gap = max(2, int(r * 0.2))
        
        self.draw.rectangle([cx - gap - bar_width, cy - bar_height, 
                            cx - gap, cy + bar_height], fill=icon_color)
        self.draw.rectangle([cx + gap, cy - bar_height, 
                            cx + gap + bar_width, cy + bar_height], fill=icon_color)
    
    def draw_menu_button(
        self,
        center_x: Optional[int] = None,
        center_y: Optional[int] = None,
        size: Optional[int] = None,
        bg_color: Optional[Tuple[int, ...]] = None,
        icon_color: Tuple[int, ...] = (80, 80, 80, 255),
        style: Literal["circle", "square", "none"] = "none"
    ):
        """
        绘制菜单按钮 (汉堡菜单 ≡)
        
        Args:
            center_x, center_y: 中心坐标
            size: 尺寸
            bg_color: 背景颜色
            icon_color: 图标颜色
            style: 背景样式
        """
        cx = center_x if center_x is not None else self.width // 2
        cy = center_y if center_y is not None else self.height // 2
        s = size if size is not None else min(self.width, self.height) - 4
        r = s // 2
        
        icon_color = self._ensure_rgba(icon_color)
        
        # 背景
        if bg_color and style != "none":
            bg_color = self._ensure_rgba(bg_color)
            if style == "circle":
                self.draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=bg_color)
            elif style == "square":
                self.draw.rounded_rectangle([cx-r, cy-r, cx+r, cy+r], radius=4, fill=bg_color)
        
        # 三条横线
        bar_width = int(r * 1.2)
        bar_height = max(2, int(r * 0.15))
        gap = int(r * 0.4)
        
        for i in range(-1, 2):
            y = cy + i * gap
            self.draw.rounded_rectangle(
                [cx - bar_width//2, y - bar_height//2, cx + bar_width//2, y + bar_height//2],
                radius=bar_height//2, fill=icon_color
            )
    
    def draw_home_button(
        self,
        center_x: Optional[int] = None,
        center_y: Optional[int] = None,
        size: Optional[int] = None,
        bg_color: Optional[Tuple[int, ...]] = None,
        icon_color: Tuple[int, ...] = (80, 80, 80, 255),
        style: Literal["circle", "square", "none"] = "none"
    ):
        """
        绘制主页按钮 (房子)
        
        Args:
            center_x, center_y: 中心坐标
            size: 尺寸
            bg_color: 背景颜色
            icon_color: 图标颜色
            style: 背景样式
        """
        cx = center_x if center_x is not None else self.width // 2
        cy = center_y if center_y is not None else self.height // 2
        s = size if size is not None else min(self.width, self.height) - 4
        r = s // 2
        
        icon_color = self._ensure_rgba(icon_color)
        
        # 背景
        if bg_color and style != "none":
            bg_color = self._ensure_rgba(bg_color)
            if style == "circle":
                self.draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=bg_color)
            elif style == "square":
                self.draw.rounded_rectangle([cx-r, cy-r, cx+r, cy+r], radius=4, fill=bg_color)
        
        # 房顶
        roof_points = [
            (cx, cy - r * 0.7),      # 顶点
            (cx - r * 0.7, cy),      # 左
            (cx + r * 0.7, cy)       # 右
        ]
        self.draw.polygon(roof_points, fill=icon_color)
        
        # 房身
        body_w = int(r * 0.9)
        body_h = int(r * 0.65)
        self.draw.rectangle([cx - body_w//2, cy, cx + body_w//2, cy + body_h], fill=icon_color)
        
        # 门
        door_w = int(r * 0.35)
        door_h = int(r * 0.5)
        door_color = bg_color if bg_color else (0, 0, 0, 0)
        self.draw.rectangle([cx - door_w//2, cy + body_h - door_h, cx + door_w//2, cy + body_h], 
                           fill=door_color)
    
    def draw_refresh_button(
        self,
        center_x: Optional[int] = None,
        center_y: Optional[int] = None,
        size: Optional[int] = None,
        bg_color: Optional[Tuple[int, ...]] = None,
        icon_color: Tuple[int, ...] = (80, 80, 80, 255),
        style: Literal["circle", "square", "none"] = "none"
    ):
        """
        绘制刷新按钮 (循环箭头)
        
        Args:
            center_x, center_y: 中心坐标
            size: 尺寸
            bg_color: 背景颜色
            icon_color: 图标颜色
            style: 背景样式
        """
        cx = center_x if center_x is not None else self.width // 2
        cy = center_y if center_y is not None else self.height // 2
        s = size if size is not None else min(self.width, self.height) - 4
        r = s // 2
        
        icon_color = self._ensure_rgba(icon_color)
        
        # 背景
        if bg_color and style != "none":
            bg_color = self._ensure_rgba(bg_color)
            if style == "circle":
                self.draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=bg_color)
            elif style == "square":
                self.draw.rounded_rectangle([cx-r, cy-r, cx+r, cy+r], radius=4, fill=bg_color)
        
        # 圆弧
        arc_r = int(r * 0.65)
        line_width = max(2, int(r * 0.2))
        self.draw.arc([cx-arc_r, cy-arc_r, cx+arc_r, cy+arc_r], 
                     start=30, end=300, fill=icon_color, width=line_width)
        
        # 箭头头部
        arrow_size = int(r * 0.3)
        # 右上角箭头
        ax = cx + arc_r * math.cos(math.radians(30))
        ay = cy - arc_r * math.sin(math.radians(30))
        arrow_points = [
            (ax, ay),
            (ax + arrow_size, ay + arrow_size//2),
            (ax + arrow_size//2, ay + arrow_size)
        ]
        self.draw.polygon(arrow_points, fill=icon_color)
    
    def draw_back_button(
        self,
        center_x: Optional[int] = None,
        center_y: Optional[int] = None,
        size: Optional[int] = None,
        bg_color: Optional[Tuple[int, ...]] = None,
        icon_color: Tuple[int, ...] = (80, 80, 80, 255),
        style: Literal["circle", "square", "none"] = "none"
    ):
        """
        绘制返回按钮 (<-)
        
        Args:
            center_x, center_y: 中心坐标
            size: 尺寸
            bg_color: 背景颜色
            icon_color: 图标颜色
            style: 背景样式
        """
        cx = center_x if center_x is not None else self.width // 2
        cy = center_y if center_y is not None else self.height // 2
        s = size if size is not None else min(self.width, self.height) - 4
        r = s // 2
        
        icon_color = self._ensure_rgba(icon_color)
        
        # 背景
        if bg_color and style != "none":
            bg_color = self._ensure_rgba(bg_color)
            if style == "circle":
                self.draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=bg_color)
            elif style == "square":
                self.draw.rounded_rectangle([cx-r, cy-r, cx+r, cy+r], radius=4, fill=bg_color)
        
        # 箭头
        line_width = max(2, int(r * 0.2))
        offset = int(r * 0.6)
        
        # 箭头身体
        self.draw.line([(cx - offset, cy), (cx + offset, cy)], fill=icon_color, width=line_width)
        # 箭头头部
        self.draw.line([(cx - offset, cy), (cx - offset//2, cy - offset//2)], fill=icon_color, width=line_width)
        self.draw.line([(cx - offset, cy), (cx - offset//2, cy + offset//2)], fill=icon_color, width=line_width)
    
    def draw_plus_button(
        self,
        center_x: Optional[int] = None,
        center_y: Optional[int] = None,
        size: Optional[int] = None,
        bg_color: Tuple[int, ...] = (50, 180, 50, 255),
        icon_color: Tuple[int, ...] = (255, 255, 255, 255),
        style: Literal["circle", "square", "none"] = "circle"
    ):
        """
        绘制加号按钮 (+)
        
        Args:
            center_x, center_y: 中心坐标
            size: 尺寸
            bg_color: 背景颜色
            icon_color: 图标颜色
            style: 背景样式
        """
        cx = center_x if center_x is not None else self.width // 2
        cy = center_y if center_y is not None else self.height // 2
        s = size if size is not None else min(self.width, self.height) - 4
        r = s // 2
        
        bg_color = self._ensure_rgba(bg_color)
        icon_color = self._ensure_rgba(icon_color)
        
        # 背景
        if style == "circle":
            self.draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=bg_color)
        elif style == "square":
            self.draw.rounded_rectangle([cx-r, cy-r, cx+r, cy+r], radius=4, fill=bg_color)
        
        # + 图标
        offset = int(r * 0.55)
        line_width = max(2, s // 8)
        self.draw.line([(cx - offset, cy), (cx + offset, cy)], fill=icon_color, width=line_width)
        self.draw.line([(cx, cy - offset), (cx, cy + offset)], fill=icon_color, width=line_width)
    
    def draw_minus_button(
        self,
        center_x: Optional[int] = None,
        center_y: Optional[int] = None,
        size: Optional[int] = None,
        bg_color: Tuple[int, ...] = (220, 60, 60, 255),
        icon_color: Tuple[int, ...] = (255, 255, 255, 255),
        style: Literal["circle", "square", "none"] = "circle"
    ):
        """
        绘制减号按钮 (-)
        
        Args:
            center_x, center_y: 中心坐标
            size: 尺寸
            bg_color: 背景颜色
            icon_color: 图标颜色
            style: 背景样式
        """
        cx = center_x if center_x is not None else self.width // 2
        cy = center_y if center_y is not None else self.height // 2
        s = size if size is not None else min(self.width, self.height) - 4
        r = s // 2
        
        bg_color = self._ensure_rgba(bg_color)
        icon_color = self._ensure_rgba(icon_color)
        
        # 背景
        if style == "circle":
            self.draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=bg_color)
        elif style == "square":
            self.draw.rounded_rectangle([cx-r, cy-r, cx+r, cy+r], radius=4, fill=bg_color)
        
        # - 图标
        offset = int(r * 0.55)
        line_width = max(2, s // 8)
        self.draw.line([(cx - offset, cy), (cx + offset, cy)], fill=icon_color, width=line_width)
    
    def draw_check_button(
        self,
        center_x: Optional[int] = None,
        center_y: Optional[int] = None,
        size: Optional[int] = None,
        bg_color: Tuple[int, ...] = (50, 180, 50, 255),
        icon_color: Tuple[int, ...] = (255, 255, 255, 255),
        style: Literal["circle", "square", "none"] = "circle"
    ):
        """
        绘制确认按钮 (✓)
        
        Args:
            center_x, center_y: 中心坐标
            size: 尺寸
            bg_color: 背景颜色
            icon_color: 图标颜色
            style: 背景样式
        """
        cx = center_x if center_x is not None else self.width // 2
        cy = center_y if center_y is not None else self.height // 2
        s = size if size is not None else min(self.width, self.height) - 4
        r = s // 2
        
        bg_color = self._ensure_rgba(bg_color)
        icon_color = self._ensure_rgba(icon_color)
        
        # 背景
        if style == "circle":
            self.draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=bg_color)
        elif style == "square":
            self.draw.rounded_rectangle([cx-r, cy-r, cx+r, cy+r], radius=4, fill=bg_color)
        
        # ✓ 图标
        line_width = max(2, s // 10)
        offset = int(r * 0.5)
        points = [
            (cx - offset, cy),
            (cx - offset//3, cy + offset * 0.7),
            (cx + offset, cy - offset * 0.6)
        ]
        self.draw.line(points[:2], fill=icon_color, width=line_width)
        self.draw.line(points[1:], fill=icon_color, width=line_width)
    
    # ==================== 画笔功能 (低级绘图API) ====================
    
    def pen_line(
        self,
        x1: int, y1: int,
        x2: int, y2: int,
        color: Tuple[int, ...] = (0, 0, 0, 255),
        width: int = 2
    ):
        """
        画笔：画直线
        
        Args:
            x1, y1: 起点
            x2, y2: 终点
            color: 颜色
            width: 线宽
        """
        color = self._ensure_rgba(color)
        self.draw.line([(x1, y1), (x2, y2)], fill=color, width=width)
    
    def pen_lines(
        self,
        points: List[Tuple[int, int]],
        color: Tuple[int, ...] = (0, 0, 0, 255),
        width: int = 2,
        closed: bool = False
    ):
        """
        画笔：画多段折线
        
        Args:
            points: 点列表 [(x1,y1), (x2,y2), ...]
            color: 颜色
            width: 线宽
            closed: 是否闭合
        """
        if len(points) < 2:
            return
        
        color = self._ensure_rgba(color)
        
        if closed:
            points = list(points) + [points[0]]
        
        self.draw.line(points, fill=color, width=width, joint="curve")
    
    def pen_rect(
        self,
        x: int, y: int,
        width: int, height: int,
        fill_color: Optional[Tuple[int, ...]] = None,
        border_color: Optional[Tuple[int, ...]] = (0, 0, 0, 255),
        border_width: int = 2
    ):
        """
        画笔：画矩形
        
        Args:
            x, y: 左上角
            width, height: 尺寸
            fill_color: 填充颜色
            border_color: 边框颜色
            border_width: 边框宽度
        """
        if fill_color:
            fill_color = self._ensure_rgba(fill_color)
        if border_color:
            border_color = self._ensure_rgba(border_color)
        
        self.draw.rectangle([x, y, x + width - 1, y + height - 1], 
                           fill=fill_color, outline=border_color, width=border_width)
    
    def pen_ellipse(
        self,
        x: int, y: int,
        width: int, height: int,
        fill_color: Optional[Tuple[int, ...]] = None,
        border_color: Optional[Tuple[int, ...]] = (0, 0, 0, 255),
        border_width: int = 2
    ):
        """
        画笔：画椭圆
        
        Args:
            x, y: 左上角
            width, height: 尺寸
            fill_color: 填充颜色
            border_color: 边框颜色
            border_width: 边框宽度
        """
        if fill_color:
            fill_color = self._ensure_rgba(fill_color)
        if border_color:
            border_color = self._ensure_rgba(border_color)
        
        self.draw.ellipse([x, y, x + width - 1, y + height - 1], 
                         fill=fill_color, outline=border_color, width=border_width)
    
    def pen_arc(
        self,
        x: int, y: int,
        width: int, height: int,
        start_angle: float = 0,
        end_angle: float = 180,
        color: Tuple[int, ...] = (0, 0, 0, 255),
        line_width: int = 2
    ):
        """
        画笔：画弧线
        
        Args:
            x, y: 外接矩形左上角
            width, height: 外接矩形尺寸
            start_angle: 起始角度（度）
            end_angle: 结束角度（度）
            color: 颜色
            line_width: 线宽
        """
        color = self._ensure_rgba(color)
        self.draw.arc([x, y, x + width - 1, y + height - 1], 
                     start=start_angle, end=end_angle, fill=color, width=line_width)
    
    def pen_polygon(
        self,
        points: List[Tuple[int, int]],
        fill_color: Optional[Tuple[int, ...]] = None,
        border_color: Optional[Tuple[int, ...]] = (0, 0, 0, 255),
        border_width: int = 2
    ):
        """
        画笔：画多边形
        
        Args:
            points: 顶点列表 [(x1,y1), (x2,y2), ...]
            fill_color: 填充颜色
            border_color: 边框颜色
            border_width: 边框宽度
        """
        if fill_color:
            fill_color = self._ensure_rgba(fill_color)
        if border_color:
            border_color = self._ensure_rgba(border_color)
        
        self.draw.polygon(points, fill=fill_color, outline=border_color, width=border_width)
    
    def pen_bezier(
        self,
        points: List[Tuple[int, int]],
        color: Tuple[int, ...] = (0, 0, 0, 255),
        width: int = 2,
        steps: int = 50
    ):
        """
        画笔：画贝塞尔曲线
        
        Args:
            points: 控制点列表（2点=线性, 3点=二次, 4点=三次）
            color: 颜色
            width: 线宽
            steps: 采样步数
        """
        if len(points) < 2:
            return
        
        color = self._ensure_rgba(color)
        
        # 计算贝塞尔曲线点
        curve_points = []
        for i in range(steps + 1):
            t = i / steps
            point = self._bezier_point(points, t)
            curve_points.append((int(point[0]), int(point[1])))
        
        # 绘制曲线
        if len(curve_points) >= 2:
            self.draw.line(curve_points, fill=color, width=width, joint="curve")
    
    def _bezier_point(self, points: List[Tuple[int, int]], t: float) -> Tuple[float, float]:
        """计算贝塞尔曲线上的点"""
        n = len(points) - 1
        x = 0
        y = 0
        for i, (px, py) in enumerate(points):
            # 计算伯恩斯坦多项式
            coef = self._binomial(n, i) * (1 - t) ** (n - i) * t ** i
            x += coef * px
            y += coef * py
        return (x, y)
    
    def _binomial(self, n: int, k: int) -> int:
        """计算二项式系数 C(n, k)"""
        if k < 0 or k > n:
            return 0
        if k == 0 or k == n:
            return 1
        result = 1
        for i in range(min(k, n - k)):
            result = result * (n - i) // (i + 1)
        return result
    
    def pen_point(
        self,
        x: int, y: int,
        color: Tuple[int, ...] = (0, 0, 0, 255),
        size: int = 3
    ):
        """
        画笔：画点
        
        Args:
            x, y: 位置
            color: 颜色
            size: 点大小
        """
        color = self._ensure_rgba(color)
        r = size // 2
        self.draw.ellipse([x - r, y - r, x + r, y + r], fill=color)
    
    def pen_text(
        self,
        x: int, y: int,
        text: str,
        color: Tuple[int, ...] = (0, 0, 0, 255),
        font_size: int = 16,
        font_path: Optional[str] = None
    ):
        """
        画笔：写文字
        
        Args:
            x, y: 位置
            text: 文字
            color: 颜色
            font_size: 字体大小
            font_path: 字体路径
        """
        color = self._ensure_rgba(color)
        
        try:
            if font_path:
                font = ImageFont.truetype(font_path, font_size)
            else:
                font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", font_size)
        except:
            font = ImageFont.load_default()
        
        self.draw.text((x, y), text, fill=color, font=font)
    
    def pen_fill(
        self,
        x: int, y: int,
        color: Tuple[int, ...] = (255, 0, 0, 255)
    ):
        """
        画笔：填充区域 (种子填充)
        注意：这个操作可能比较慢，适用于简单区域
        
        Args:
            x, y: 种子点
            color: 填充颜色
        """
        from PIL import ImageDraw
        
        color = self._ensure_rgba(color)
        
        # 获取种子点原始颜色
        try:
            original_color = self.image.getpixel((x, y))
        except IndexError:
            return
        
        if original_color == color:
            return
        
        # 简单的种子填充（栈溢出友好版本）
        from collections import deque
        queue = deque([(x, y)])
        visited = set()
        
        while queue and len(visited) < 100000:  # 限制填充范围
            px, py = queue.popleft()
            if (px, py) in visited:
                continue
            if px < 0 or px >= self.width or py < 0 or py >= self.height:
                continue
            
            current = self.image.getpixel((px, py))
            if current != original_color:
                continue
            
            self.image.putpixel((px, py), color)
            visited.add((px, py))
            
            queue.append((px + 1, py))
            queue.append((px - 1, py))
            queue.append((px, py + 1))
            queue.append((px, py - 1))
        
        # 重建 draw 对象
        self.draw = ImageDraw.Draw(self.image)
    
    # ==================== 输出方法 ====================
    
    def save(self, file_path: str) -> str:
        """
        保存图片到文件
        
        Args:
            file_path: 保存路径
            
        Returns:
            保存的文件路径
        """
        # 确保目录存在
        dir_path = os.path.dirname(file_path)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path)
        
        self.image.save(file_path)
        return os.path.abspath(file_path)
    
    def to_bytes(self, format: str = "PNG") -> bytes:
        """
        将图片转换为字节数据
        
        Args:
            format: 图片格式
            
        Returns:
            图片字节数据
        """
        buffer = io.BytesIO()
        self.image.save(buffer, format=format)
        return buffer.getvalue()
    
    def to_base64(self, format: str = "PNG") -> str:
        """
        将图片转换为 Base64 字符串
        
        Args:
            format: 图片格式
            
        Returns:
            Base64 编码的图片数据
        """
        return base64.b64encode(self.to_bytes(format)).decode("utf-8")
    
    def get_data_uri(self, format: str = "PNG") -> str:
        """
        获取图片的 Data URI
        
        Args:
            format: 图片格式
            
        Returns:
            Data URI 字符串
        """
        mime_types = {"PNG": "image/png", "JPEG": "image/jpeg", "GIF": "image/gif"}
        mime = mime_types.get(format.upper(), "image/png")
        return f"data:{mime};base64,{self.to_base64(format)}"


# ====================== 便捷函数 ======================

def create_button(
    width: int = 120, height: int = 40,
    text: str = "按钮",
    style: str = "gradient",
    color: str = "blue"
) -> GamePainter:
    """快速创建按钮"""
    color_presets = {
        "blue": ((65, 105, 225, 255), (30, 60, 180, 255)),
        "green": ((50, 205, 50, 255), (30, 150, 30, 255)),
        "red": ((220, 60, 60, 255), (180, 30, 30, 255)),
        "orange": ((255, 165, 0, 255), (220, 120, 0, 255)),
        "purple": ((138, 43, 226, 255), (100, 30, 180, 255))
    }
    primary, secondary = color_presets.get(color, color_presets["blue"])
    
    painter = GamePainter(width, height)
    painter.draw_button(text=text, style=ButtonStyle(style), primary_color=primary, secondary_color=secondary)
    return painter


def create_icon(
    size: int = 64,
    icon_type: str = "star",
    **kwargs
) -> GamePainter:
    """快速创建图标"""
    painter = GamePainter(size, size)
    
    if icon_type == "star":
        painter.draw_star(**kwargs)
    elif icon_type == "coin":
        painter.draw_coin(**kwargs)
    elif icon_type == "gem":
        painter.draw_gem(**kwargs)
    elif icon_type == "heart":
        painter.draw_heart(**kwargs)
    elif icon_type == "shield":
        painter.draw_shield(width=size, height=size, **kwargs)
    elif icon_type == "arrow":
        painter.draw_arrow(width=size, height=size, **kwargs)
    
    return painter


def create_progress_bar(
    width: int = 200, height: int = 24,
    progress: float = 50,
    bar_type: str = "normal"
) -> GamePainter:
    """快速创建进度条"""
    painter = GamePainter(width, height)
    
    if bar_type == "health":
        painter.draw_health_bar(hp_percent=progress)
    else:
        painter.draw_progress_bar(progress=progress)
    
    return painter


def create_control_button(
    size: int = 48,
    button_type: str = "close",
    **kwargs
) -> GamePainter:
    """快速创建控制按钮"""
    painter = GamePainter(size, size)
    
    button_methods = {
        "close": painter.draw_close_button,
        "settings": painter.draw_settings_button,
        "play": painter.draw_play_button,
        "pause": painter.draw_pause_button,
        "menu": painter.draw_menu_button,
        "home": painter.draw_home_button,
        "refresh": painter.draw_refresh_button,
        "back": painter.draw_back_button,
        "plus": painter.draw_plus_button,
        "minus": painter.draw_minus_button,
        "check": painter.draw_check_button
    }
    
    method = button_methods.get(button_type, painter.draw_close_button)
    method(**kwargs)
    return painter


def draw_simple_car(painter: GamePainter, x: int = 0, y: int = 0, scale: float = 1.0, 
                    body_color: Tuple[int, ...] = (220, 50, 50, 255),
                    window_color: Tuple[int, ...] = (150, 200, 255, 255)):
    """
    使用画笔功能绘制一辆简易小汽车
    
    这是一个示例，展示如何使用低级画笔API组合绘制复杂图形
    
    Args:
        painter: GamePainter 实例
        x, y: 左上角位置
        scale: 缩放比例
        body_color: 车身颜色
        window_color: 车窗颜色
    """
    def s(v): return int(v * scale)  # 缩放辅助函数
    
    # 车身下半部分
    painter.pen_polygon(
        points=[
            (x + s(10), y + s(50)),    # 左下
            (x + s(10), y + s(35)),    # 左
            (x + s(140), y + s(35)),   # 右
            (x + s(140), y + s(50)),   # 右下
        ],
        fill_color=body_color,
        border_color=(0, 0, 0, 255),
        border_width=2
    )
    
    # 车身上半部分（车顶）
    painter.pen_polygon(
        points=[
            (x + s(30), y + s(35)),    # 左下
            (x + s(40), y + s(15)),    # 左上
            (x + s(100), y + s(15)),   # 右上
            (x + s(110), y + s(35)),   # 右下
        ],
        fill_color=body_color,
        border_color=(0, 0, 0, 255),
        border_width=2
    )
    
    # 前车窗
    painter.pen_polygon(
        points=[
            (x + s(42), y + s(33)),
            (x + s(48), y + s(18)),
            (x + s(68), y + s(18)),
            (x + s(68), y + s(33)),
        ],
        fill_color=window_color,
        border_color=(50, 50, 50, 255),
        border_width=1
    )
    
    # 后车窗
    painter.pen_polygon(
        points=[
            (x + s(72), y + s(33)),
            (x + s(72), y + s(18)),
            (x + s(95), y + s(18)),
            (x + s(102), y + s(33)),
        ],
        fill_color=window_color,
        border_color=(50, 50, 50, 255),
        border_width=1
    )
    
    # 前车灯
    painter.pen_ellipse(
        x + s(130), y + s(38),
        s(12), s(8),
        fill_color=(255, 255, 150, 255),
        border_color=(200, 180, 50, 255),
        border_width=1
    )
    
    # 后车灯
    painter.pen_ellipse(
        x + s(8), y + s(38),
        s(10), s(8),
        fill_color=(255, 50, 50, 255),
        border_color=(150, 30, 30, 255),
        border_width=1
    )
    
    # 前轮
    wheel_color = (40, 40, 40, 255)
    hub_color = (180, 180, 180, 255)
    
    painter.pen_ellipse(
        x + s(25), y + s(42),
        s(24), s(24),
        fill_color=wheel_color,
        border_color=(20, 20, 20, 255),
        border_width=2
    )
    painter.pen_ellipse(
        x + s(31), y + s(48),
        s(12), s(12),
        fill_color=hub_color,
        border_color=None
    )
    
    # 后轮
    painter.pen_ellipse(
        x + s(100), y + s(42),
        s(24), s(24),
        fill_color=wheel_color,
        border_color=(20, 20, 20, 255),
        border_width=2
    )
    painter.pen_ellipse(
        x + s(106), y + s(48),
        s(12), s(12),
        fill_color=hub_color,
        border_color=None
    )


def draw_simple_house(painter: GamePainter, x: int = 0, y: int = 0, scale: float = 1.0,
                      wall_color: Tuple[int, ...] = (255, 230, 180, 255),
                      roof_color: Tuple[int, ...] = (180, 80, 50, 255)):
    """
    使用画笔功能绘制一个简易房子
    
    Args:
        painter: GamePainter 实例
        x, y: 左上角位置
        scale: 缩放比例
        wall_color: 墙壁颜色
        roof_color: 屋顶颜色
    """
    def s(v): return int(v * scale)
    
    # 墙壁
    painter.pen_rect(
        x + s(20), y + s(50),
        s(100), s(70),
        fill_color=wall_color,
        border_color=(100, 80, 50, 255),
        border_width=2
    )
    
    # 屋顶
    painter.pen_polygon(
        points=[
            (x + s(10), y + s(50)),     # 左
            (x + s(70), y + s(10)),     # 顶
            (x + s(130), y + s(50)),    # 右
        ],
        fill_color=roof_color,
        border_color=(100, 40, 20, 255),
        border_width=2
    )
    
    # 门
    painter.pen_rect(
        x + s(55), y + s(80),
        s(30), s(40),
        fill_color=(139, 90, 43, 255),
        border_color=(90, 60, 30, 255),
        border_width=2
    )
    
    # 门把手
    painter.pen_point(x + s(80), y + s(100), color=(255, 215, 0, 255), size=s(4))
    
    # 左窗户
    painter.pen_rect(
        x + s(28), y + s(60),
        s(20), s(18),
        fill_color=(150, 200, 255, 255),
        border_color=(100, 80, 50, 255),
        border_width=2
    )
    
    # 右窗户
    painter.pen_rect(
        x + s(92), y + s(60),
        s(20), s(18),
        fill_color=(150, 200, 255, 255),
        border_color=(100, 80, 50, 255),
        border_width=2
    )
    
    # 烟囱
    painter.pen_rect(
        x + s(95), y + s(20),
        s(15), s(30),
        fill_color=(150, 80, 50, 255),
        border_color=(100, 50, 30, 255),
        border_width=2
    )


def draw_simple_tree(painter: GamePainter, x: int = 0, y: int = 0, scale: float = 1.0,
                     trunk_color: Tuple[int, ...] = (139, 90, 43, 255),
                     leaf_color: Tuple[int, ...] = (50, 180, 50, 255)):
    """
    使用画笔功能绘制一棵简易树
    
    Args:
        painter: GamePainter 实例
        x, y: 左上角位置
        scale: 缩放比例
        trunk_color: 树干颜色
        leaf_color: 树叶颜色
    """
    def s(v): return int(v * scale)
    
    # 树干
    painter.pen_rect(
        x + s(35), y + s(70),
        s(20), s(50),
        fill_color=trunk_color,
        border_color=(100, 60, 30, 255),
        border_width=2
    )
    
    # 树冠（三层三角形）
    # 底层
    painter.pen_polygon(
        points=[
            (x + s(5), y + s(75)),
            (x + s(45), y + s(40)),
            (x + s(85), y + s(75)),
        ],
        fill_color=leaf_color,
        border_color=(30, 120, 30, 255),
        border_width=2
    )
    
    # 中层
    painter.pen_polygon(
        points=[
            (x + s(12), y + s(55)),
            (x + s(45), y + s(22)),
            (x + s(78), y + s(55)),
        ],
        fill_color=leaf_color,
        border_color=(30, 120, 30, 255),
        border_width=2
    )
    
    # 顶层
    painter.pen_polygon(
        points=[
            (x + s(20), y + s(35)),
            (x + s(45), y + s(5)),
            (x + s(70), y + s(35)),
        ],
        fill_color=leaf_color,
        border_color=(30, 120, 30, 255),
        border_width=2
    )


# ====================== 测试 ======================

if __name__ == "__main__":
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    print("🎨 GamePainter 示例生成中...")
    
    # 1. 各种按钮
    for style in ["flat", "gradient", "glossy", "outline", "pixel"]:
        btn = GamePainter(120, 40)
        btn.draw_button(text="开始游戏", style=ButtonStyle(style))
        btn.save(f"{output_dir}/button_{style}.png")
        print(f"  ✓ 按钮 ({style})")
    
    # 2. 图标
    for icon in ["star", "coin", "heart"]:
        painter = create_icon(64, icon)
        painter.save(f"{output_dir}/icon_{icon}.png")
        print(f"  ✓ 图标 ({icon})")
    
    # 3. 宝石
    for gem in ["diamond", "ruby", "emerald", "sapphire"]:
        painter = GamePainter(64, 64)
        painter.draw_gem(gem_type=gem)
        painter.save(f"{output_dir}/gem_{gem}.png")
        print(f"  ✓ 宝石 ({gem})")
    
    # 4. 进度条
    painter = GamePainter(300, 30)
    painter.draw_progress_bar(progress=75)
    painter.save(f"{output_dir}/progress_bar.png")
    print("  ✓ 进度条")
    
    # 5. 血条
    for hp in [90, 50, 20]:
        painter = GamePainter(200, 20)
        painter.draw_health_bar(hp_percent=hp)
        painter.save(f"{output_dir}/health_bar_{hp}.png")
        print(f"  ✓ 血条 ({hp}%)")
    
    # 6. 道具槽
    for rarity in ["common", "uncommon", "rare", "epic", "legendary"]:
        painter = GamePainter(64, 64)
        painter.draw_icon_slot(rarity=rarity, show_shine=(rarity in ["epic", "legendary"]))
        painter.save(f"{output_dir}/slot_{rarity}.png")
        print(f"  ✓ 道具槽 ({rarity})")
    
    # 7. 盾牌
    painter = GamePainter(64, 80)
    painter.draw_shield()
    painter.save(f"{output_dir}/shield.png")
    print("  ✓ 盾牌")
    
    # 8. 对话框
    for style in ["modern", "fantasy", "scifi", "pixel"]:
        painter = GamePainter(300, 100)
        painter.draw_dialog_box(style=style)
        painter.save(f"{output_dir}/dialog_{style}.png")
        print(f"  ✓ 对话框 ({style})")
    
    # 9. 小地图
    for shape in ["circle", "square"]:
        painter = GamePainter(120, 120)
        painter.draw_minimap_frame(shape=shape)
        painter.save(f"{output_dir}/minimap_{shape}.png")
        print(f"  ✓ 小地图 ({shape})")
    
    # 10. 工具提示
    painter = GamePainter(180, 80)
    painter.draw_tooltip(title="传说之剑", rarity="legendary")
    painter.save(f"{output_dir}/tooltip.png")
    print("  ✓ 工具提示")
    
    # 11. 箭头
    for direction in ["up", "down", "left", "right"]:
        painter = GamePainter(40, 40)
        painter.draw_arrow(direction=direction)
        painter.save(f"{output_dir}/arrow_{direction}.png")
        print(f"  ✓ 箭头 ({direction})")
    
    # ============== 新增功能演示 ==============
    
    print("\n📦 生成控制按钮...")
    
    # 12. 控制按钮
    control_buttons = [
        ("close", {}),
        ("settings", {"icon_color": (100, 100, 100, 255)}),
        ("play", {}),
        ("pause", {}),
        ("menu", {"icon_color": (80, 80, 80, 255)}),
        ("home", {"icon_color": (80, 80, 80, 255)}),
        ("refresh", {"icon_color": (80, 80, 80, 255)}),
        ("back", {"icon_color": (80, 80, 80, 255)}),
        ("plus", {}),
        ("minus", {}),
        ("check", {})
    ]
    
    for btn_type, kwargs in control_buttons:
        painter = create_control_button(48, btn_type, **kwargs)
        painter.save(f"{output_dir}/ctrl_{btn_type}.png")
        print(f"  ✓ 控制按钮 ({btn_type})")
    
    print("\n🎨 生成画笔绘制示例...")
    
    # 13. 画笔示例 - 小汽车
    painter = GamePainter(180, 80, bg_color=(220, 240, 255, 255))
    draw_simple_car(painter, x=15, y=5, scale=1.0)
    painter.save(f"{output_dir}/pen_car.png")
    print("  ✓ 画笔绘制：小汽车")
    
    # 14. 画笔示例 - 蓝色小汽车
    painter = GamePainter(180, 80, bg_color=(240, 240, 240, 255))
    draw_simple_car(painter, x=15, y=5, scale=1.0, 
                    body_color=(50, 120, 200, 255))
    painter.save(f"{output_dir}/pen_car_blue.png")
    print("  ✓ 画笔绘制：蓝色小汽车")
    
    # 15. 画笔示例 - 房子
    painter = GamePainter(150, 130, bg_color=(180, 220, 255, 255))
    draw_simple_house(painter, x=5, y=5, scale=1.0)
    painter.save(f"{output_dir}/pen_house.png")
    print("  ✓ 画笔绘制：房子")
    
    # 16. 画笔示例 - 树
    painter = GamePainter(100, 130, bg_color=(180, 220, 255, 255))
    draw_simple_tree(painter, x=5, y=5, scale=1.0)
    painter.save(f"{output_dir}/pen_tree.png")
    print("  ✓ 画笔绘制：树")
    
    # 17. 画笔示例 - 场景组合
    painter = GamePainter(400, 200, bg_color=(135, 206, 235, 255))
    # 地面
    painter.pen_rect(0, 160, 400, 40, fill_color=(100, 180, 100, 255), border_color=None)
    # 太阳
    painter.pen_ellipse(330, 20, 50, 50, fill_color=(255, 220, 100, 255), border_color=None)
    # 云
    painter.pen_ellipse(50, 30, 40, 25, fill_color=(255, 255, 255, 200), border_color=None)
    painter.pen_ellipse(75, 25, 50, 30, fill_color=(255, 255, 255, 200), border_color=None)
    painter.pen_ellipse(110, 32, 35, 22, fill_color=(255, 255, 255, 200), border_color=None)
    # 房子
    draw_simple_house(painter, x=30, y=30, scale=1.0)
    # 树
    draw_simple_tree(painter, x=170, y=30, scale=1.0)
    draw_simple_tree(painter, x=230, y=45, scale=0.8)
    # 汽车
    draw_simple_car(painter, x=280, y=85, scale=0.9, body_color=(50, 100, 200, 255))
    painter.save(f"{output_dir}/pen_scene.png")
    print("  ✓ 画笔绘制：场景组合")
    
    # 18. 画笔示例 - 贝塞尔曲线
    painter = GamePainter(200, 100, bg_color=(240, 240, 240, 255))
    # 画一条平滑的波浪线
    painter.pen_bezier(
        points=[(20, 50), (60, 20), (140, 80), (180, 50)],
        color=(100, 50, 200, 255),
        width=3
    )
    # 画一个心形用贝塞尔
    painter.pen_bezier(
        points=[(100, 80), (60, 40), (100, 20)],
        color=(255, 100, 100, 255),
        width=2
    )
    painter.pen_bezier(
        points=[(100, 80), (140, 40), (100, 20)],
        color=(255, 100, 100, 255),
        width=2
    )
    painter.save(f"{output_dir}/pen_bezier.png")
    print("  ✓ 画笔绘制：贝塞尔曲线")
    
    print(f"\n✅ 所有示例已保存到 {os.path.abspath(output_dir)} 目录")

