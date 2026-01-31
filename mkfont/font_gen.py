#!/usr/bin/env python3

from PIL import Image, ImageDraw, ImageFont
import numpy as np

# 默认参数
ASCII_START = 32  # 空格
ASCII_END = 126   # ~

def get_char_bitmap(ttf_path, char, font_size, width, height):
    """渲染字符到固定尺寸画布"""
    im = Image.new("1", (width, height), 0)
    draw = ImageDraw.Draw(im)
    font = ImageFont.truetype(ttf_path, font_size)
    
    # 获取字符边界框
    bbox = font.getbbox(char)
    if not bbox:
        return np.array(im, dtype=np.uint8)
    
    # 计算字符宽高
    char_width = bbox[2] - bbox[0]
    char_height = bbox[3] - bbox[1]
    #if char =='~':
    #    print(bbox,width,height)
    #    ddd
    
    # 调整绘制位置，左对齐
    x = -bbox[0]  # 左对齐
    y = -1  
    draw.text((x, y), char, font=font, fill=1)
    
    return np.array(im, dtype=np.uint8)

def determine_dimensions(ttf_path, font_size):
    """根据 font 对象确定所有字符的最大宽高"""
    font = ImageFont.truetype(ttf_path, font_size)
    max_width = 0
    max_height = 0
    
    for char_code in range(ASCII_START, ASCII_END + 1):
        char = chr(char_code)
        bbox = font.getbbox(char)
        if bbox:
            width = bbox[2] - bbox[0]  # right - left
            height = bbox[3] - bbox[1]  # bottom - top
            max_width = max(max_width, width)
            max_height = max(max_height, height)
    
    # 如果没有有效字符，使用默认值
    if max_width == 0 or max_height == 0:
        max_width = font_size
        max_height = font_size
    else:
        # 添加余量，确保下降部和上升部完整
        max_height += 1
    
    # 限制宽度不超过 16（uint16_t）
    max_width = min(max_width, 16)
    return max_width, max_height

def bitmap_to_array(bitmap, width, height):
    """将位图转换为 16 位数组"""
    array = []
    for y in range(height):
        row_value = 0
        for x in range(width):
            if bitmap[y, x] > 0:
                row_value |= (1 << (width - 1 - x))
        array.append(row_value << (16 - width))
    return array

def generate_font_array(ttf_path, font_size):
    """根据字体大小生成字体数组"""
    width, height = determine_dimensions(ttf_path, font_size)
    
    font_array = []
    for char_code in range(ASCII_START, ASCII_END + 1):
        char = chr(char_code)
        bitmap = get_char_bitmap(ttf_path, char, font_size, width, height)
        char_data = bitmap_to_array(bitmap, width, height)
        font_array.extend(char_data)
    
    return font_array, width, height

def output_c_array(font_array, width, height, name="Font"):
    """输出 C 格式数组，使用单引号注释"""
    print(f"static const uint16_t {name}{width}x{height}[] = {{")
    for i in range(0, len(font_array), height):
        char_data = font_array[i:i + height]
        char = chr(ASCII_START + i // height)
        # 使用单引号包裹字符，避免末尾反斜杠问题
        char_display = f"'{char}'"
        values = ", ".join(f"0x{val:04X}" for val in char_data)
        print(f"    {values},  // {char_display}")
    print("};")

def main():
    ttf_path = "/usr/share/fonts/dejavu-sans-mono-fonts/DejaVuSansMono.ttf"  # 你的字体路径
    font_size = 20  # 输入的字体大小
    
    try:
        font_array, width, height = generate_font_array(ttf_path, font_size)
        output_c_array(font_array, width, height)
    except FileNotFoundError:
        print(f"Error: TTF file '{ttf_path}' not found")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
