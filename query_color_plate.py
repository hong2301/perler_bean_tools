import json
import csv
import sys


def load_color_mapping(json_path='color.json'):
    """
    加载颜色映射表，返回 {颜色编码: 色盘}
    颜色编码统一转为大写
    """
    color_mapping = {}
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        color_plates = data.get('color_plates', {})
        for plate_number, colors in color_plates.items():
            for color_info in colors:
                code = color_info.get('code')
                if code:
                    # 统一转为大写，方便匹配
                    color_mapping[code.upper()] = plate_number
    except Exception as e:
        print(f"读取颜色配置文件出错: {e}")

    return color_mapping


def query_color_plates(input_text, color_mapping):
    """
    查询颜色编号对应的色盘
    :param input_text: 用户输入的字符串，如 "E4 r1 f5"
    :param color_mapping: 颜色映射字典
    :return: [(颜色编号, 色盘号), ...]
    """
    # 分割输入字符串
    color_codes = input_text.strip().split()

    results = []
    for code in color_codes:
        # 转为大写进行查询
        code_upper = code.upper()
        plate = color_mapping.get(code_upper, '未找到')
        results.append((code, plate))

    return results


def save_to_csv(results, output_path='color_plate_query.csv'):
    """
    保存查询结果到 CSV 文件
    """
    try:
        with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            # 写入表头（添加序号列）
            writer.writerow(['序号', '颜色编号', '色盘号'])
            # 写入数据（添加序号，从1开始）
            for idx, (color_code, plate) in enumerate(results, start=1):
                writer.writerow([idx, color_code, plate])

        print(f"查询结果已保存到: {output_path}")
    except Exception as e:
        print(f"保存 CSV 文件出错: {e}")


def main():
    # 加载颜色映射
    color_mapping = load_color_mapping('color.json')

    if not color_mapping:
        print("未能加载颜色映射表，请检查 color.json 文件")
        return

    # 获取用户输入
    print("请输入颜色编号（用空格分隔，如: E4 r1 f5）：")
    user_input = input().strip()

    if not user_input:
        print("输入为空，程序退出")
        return

    # 查询色盘
    results = query_color_plates(user_input, color_mapping)

    # 显示结果
    print("\n查询结果:")
    print("-" * 20)
    for color_code, plate in results:
        print(f"{color_code} -> 色盘 {plate}")
    print("-" * 20)

    # 保存到 CSV
    save_to_csv(results)


if __name__ == "__main__":
    main()
