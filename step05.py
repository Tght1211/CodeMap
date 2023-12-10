from PIL import Image

def image_to_ascii(image_path, width=None):
    # 打开图片
    img = Image.open(image_path)

    # 如果指定了宽度，按比例调整图片大小
    if width:
        aspect_ratio = img.height / img.width
        new_height = round(width * aspect_ratio)
        img = img.resize((width, new_height))

    # 定义字符集
    chars = "@%#*+=-:. "

    # 初始化结果字符串
    result = ""

    # 遍历图片像素并将其转换为字符
    for y in range(img.height):
        for x in range(img.width):
            pixel = img.getpixel((x, y))
            # 将RGB值转换为灰度值
            gray = round(0.299 * pixel[0] + 0.587 * pixel[1] + 0.114 * pixel[2])
            # 将灰度值映射到字符集中的字符
            char_index = round((gray / 255) * (len(chars) - 1))
            result += chars[char_index]
        result += "\n"  # 每行结束时添加换行符

    return result

# 图片路径
image_path = "D:\\图片\\778bfe59edc2a20e222ee627dcd124e.png"

# 转换图片为字符串，并指定宽度为100
ascii_art = image_to_ascii(image_path, width=100)

# 输出结果到txt文件
output_file_path = "D:\\Data\\Work_Python\\CodeMap\\image.txt"
with open(output_file_path, "w") as file:
    file.write(ascii_art)

print(f"ASCII art has been saved to {output_file_path}")