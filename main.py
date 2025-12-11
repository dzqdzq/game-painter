#!/usr/bin/env python3
"""
🎨 GamePainter - 游戏UI占位图生成器

用法:
  python main.py              # 生成示例图片
  python main.py --server     # 启动MCP服务器
  python main.py --help       # 显示帮助
"""

import sys
import os


def show_help():
    """显示帮助信息"""
    print("""
🎨 GamePainter - 游戏UI占位图生成器

用法:
  python main.py              生成示例图片到 output/ 目录
  python main.py --server     启动 MCP 服务器
  python main.py --demo       生成完整 UI 套件
  python main.py --help       显示此帮助

示例:
  # 作为 Python 库使用
  from painter import GamePainter, create_button, create_icon
  
  btn = create_button(120, 40, text="开始", style="gradient")
  btn.save("button.png")

MCP 配置 (Cursor):
  {
    "mcpServers": {
      "game-painter": {
        "command": "python",
        "args": ["{}/server.py"]
      }}
    }}
  }}
""".format(os.path.abspath(os.path.dirname(__file__))))


def generate_demo():
    """生成完整的 UI 套件演示"""
    from painter import (
        GamePainter, ButtonStyle, create_button, create_icon, create_progress_bar
    )
    
    output_dir = "demo_ui_kit"
    os.makedirs(output_dir, exist_ok=True)
    
    print("🎨 正在生成完整 UI 套件...")
    print(f"📁 输出目录: {os.path.abspath(output_dir)}\n")
    
    # 1. 按钮集合
    print("📦 生成按钮...")
    colors = ["blue", "green", "red", "orange", "purple"]
    styles = ["flat", "gradient", "glossy", "outline", "pixel"]
    
    for color in colors:
        for style in styles:
            btn = create_button(140, 44, text="按钮", style=style, color=color)
            btn.save(f"{output_dir}/btn_{color}_{style}.png")
    print(f"  ✓ {len(colors) * len(styles)} 个按钮")
    
    # 2. 图标集合
    print("📦 生成图标...")
    icons = ["star", "coin", "heart", "shield"]
    for icon in icons:
        painter = create_icon(80, icon)
        painter.save(f"{output_dir}/icon_{icon}.png")
    
    # 箭头
    for direction in ["up", "down", "left", "right"]:
        painter = GamePainter(48, 48)
        painter.draw_arrow(direction=direction)
        painter.save(f"{output_dir}/arrow_{direction}.png")
    print(f"  ✓ {len(icons) + 4} 个图标")
    
    # 3. 宝石
    print("📦 生成宝石...")
    gems = ["diamond", "ruby", "emerald", "sapphire"]
    for gem in gems:
        painter = GamePainter(80, 80)
        painter.draw_gem(gem_type=gem)
        painter.save(f"{output_dir}/gem_{gem}.png")
    print(f"  ✓ {len(gems)} 个宝石")
    
    # 4. 进度条
    print("📦 生成进度条...")
    for progress in [0, 25, 50, 75, 100]:
        painter = GamePainter(300, 32)
        painter.draw_progress_bar(progress=progress)
        painter.save(f"{output_dir}/progress_{progress}.png")
    print("  ✓ 5 个进度条")
    
    # 5. 血条
    print("📦 生成血条...")
    for hp in [100, 75, 50, 25, 10]:
        painter = GamePainter(200, 24)
        painter.draw_health_bar(hp_percent=hp)
        painter.save(f"{output_dir}/health_{hp}.png")
    print("  ✓ 5 个血条")
    
    # 6. 道具槽
    print("📦 生成道具槽...")
    rarities = ["common", "uncommon", "rare", "epic", "legendary"]
    for rarity in rarities:
        painter = GamePainter(72, 72)
        painter.draw_icon_slot(rarity=rarity, show_shine=(rarity in ["epic", "legendary"]))
        painter.save(f"{output_dir}/slot_{rarity}.png")
    print(f"  ✓ {len(rarities)} 个道具槽")
    
    # 7. 对话框
    print("📦 生成对话框...")
    dialog_styles = ["modern", "fantasy", "scifi", "pixel"]
    for style in dialog_styles:
        painter = GamePainter(400, 120)
        painter.draw_dialog_box(style=style)
        painter.save(f"{output_dir}/dialog_{style}.png")
    print(f"  ✓ {len(dialog_styles)} 个对话框")
    
    # 8. 小地图
    print("📦 生成小地图...")
    shapes = ["circle", "square"]
    for shape in shapes:
        painter = GamePainter(150, 150)
        painter.draw_minimap_frame(shape=shape)
        painter.save(f"{output_dir}/minimap_{shape}.png")
    print(f"  ✓ {len(shapes)} 个小地图")
    
    # 9. 提示框
    print("📦 生成提示框...")
    for rarity in ["common", "rare", "epic", "legendary"]:
        painter = GamePainter(220, 100)
        painter.draw_tooltip(title=f"{rarity.title()} 道具", rarity=rarity)
        painter.save(f"{output_dir}/tooltip_{rarity}.png")
    print("  ✓ 4 个提示框")
    
    # 10. 基础图形
    print("📦 生成基础图形...")
    # 圆角矩形渐变
    painter = GamePainter(200, 80)
    from painter import GradientDirection
    painter.draw_rounded_rect(
        radius=15,
        fill_color=(255, 100, 100, 255),
        gradient=GradientDirection.VERTICAL,
        gradient_end_color=(100, 50, 150, 255)
    )
    painter.save(f"{output_dir}/gradient_rect.png")
    
    # 多边形
    for sides in [3, 5, 6, 8]:
        painter = GamePainter(80, 80)
        painter.draw_polygon(sides=sides, fill_color=(100, 180, 255, 255), border_color=(50, 100, 200, 255), border_width=2)
        painter.save(f"{output_dir}/polygon_{sides}.png")
    print("  ✓ 5 个基础图形")
    
    total = (len(colors) * len(styles) + len(icons) + 4 + len(gems) + 
             5 + 5 + len(rarities) + len(dialog_styles) + len(shapes) + 4 + 5)
    
    print(f"\n✅ 生成完成! 共 {total} 个文件")
    print(f"📁 查看: {os.path.abspath(output_dir)}")


def run_examples():
    """运行示例生成"""
    # 导入并运行 painter.py 的示例
    import painter
    

def start_server():
    """启动 MCP 服务器"""
    import asyncio
    from server import main
    print("🚀 启动 GamePainter MCP 服务器...")
    asyncio.run(main())


if __name__ == "__main__":
    args = sys.argv[1:]
    
    if "--help" in args or "-h" in args:
        show_help()
    elif "--server" in args:
        start_server()
    elif "--demo" in args:
        generate_demo()
    else:
        # 默认运行 painter.py 的示例
        print("🎨 GamePainter 示例生成")
        print("=" * 40)
        exec(open("painter.py").read())
