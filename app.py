import os
import json
import csv
import cv2
import numpy as np
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
from paddleocr import PaddleOCR
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
import uuid

# 创建 Flask 应用
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB 最大文件大小

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 全局变量：OCR 引擎和颜色映射
ocr = None
color_mapping = {}

# 配置参数
recognitionThreshold = 0.7
overlapValue = 10
heightValue = 400


def init_ocr():
    """初始化 OCR 引擎"""
    global ocr
    print("正在加载 PaddleOCR 模型，请稍候...")
    ocr = PaddleOCR(
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False,
    )
    print("PaddleOCR 模型加载完成！")


def load_color_mapping(json_path='color.json'):
    """加载颜色映射表"""
    global color_mapping
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        color_plates = data.get('color_plates', {})
        for plate_number, colors in color_plates.items():
            for color_info in colors:
                code = color_info.get('code')
                name = color_info.get('name')
                if code:
                    color_mapping[code] = (plate_number, name)
        print(f"颜色映射表加载完成，共 {len(color_mapping)} 个颜色")
    except Exception as e:
        print(f"读取颜色配置文件出错: {e}")


def split_image(image, chunk_height=1000, overlap=100):
    """将图片按高度分块"""
    height, width = image.shape[:2]
    chunks = []
    start_y = 0

    while start_y < height:
        end_y = min(start_y + chunk_height, height)
        chunk = image[start_y:end_y, 0:width]
        chunks.append((chunk, start_y))

        if end_y >= height:
            break
        start_y = end_y - overlap

    return chunks


def ocr_chunk(chunk, y_offset, index):
    """对单块图片进行 OCR 识别"""
    temp_path = f"./temp_chunk{index}.jpg"
    cv2.imwrite(temp_path, chunk)

    try:
        result = ocr.predict(temp_path)
        if isinstance(result, (list, tuple)) and len(result) > 0:
            res = result[0]
            if res is not None:
                if 'det_boxes' in res:
                    for box in res['det_boxes']:
                        box[1] += y_offset
                        box[3] += y_offset
                return res
    except Exception as e:
        print(f"识别块时出错 (y_offset={y_offset}): {e}")

    return None


def merge_results(results):
    """合并多个分块的 OCR 结果"""
    merged = {
        'input_path': [],
        'page_index': [],
        'det_polygons': [],
        'det_boxes': [],
        'rec_texts': [],
        'rec_scores': [],
        'rec_boxes': []
    }

    for res in results:
        if res is None:
            continue
        for key in merged.keys():
            if key in res:
                if isinstance(res[key], list):
                    merged[key].extend(res[key])
                else:
                    merged[key].append(res[key])

    return merged


def ocr_with_chunks(image_path, chunk_height=1000, overlap=100):
    """分块 OCR 主函数"""
    image = cv2.imread(image_path)

    if image is None:
        return None, "无法读取图片"

    height, width = image.shape[:2]

    if height <= chunk_height:
        result = ocr.predict(image_path)
        if isinstance(result, (list, tuple)) and len(result) > 0:
            return result[0], None
        return None, "OCR 识别失败"

    chunks = split_image(image, chunk_height, overlap)
    results = []

    for i, (chunk, y_offset) in enumerate(chunks):
        res = ocr_chunk(chunk, y_offset, i + 1)
        if res:
            results.append(res)

    merged_result = merge_results(results)
    return merged_result, None


def process_image(image_path, chunk_height=heightValue, overlap=overlapValue):
    """处理图片并返回颜色统计结果"""
    ocrResult, error = ocr_with_chunks(image_path, chunk_height, overlap)

    if error:
        return None, error

    color_count = {}

    if ocrResult:
        rec_texts = ocrResult.get('rec_texts', [])
        rec_scores = ocrResult.get('rec_scores', [])
        filtered_texts = []

        for text, score in zip(rec_texts, rec_scores):
            if score > recognitionThreshold:
                filtered_texts.append(text)

        # 处理 filtered_texts
        for item in filtered_texts:
            if not item or not item[0].isupper():
                continue

            parts = item.split()

            for part in parts:
                if not part or not part[0].isupper():
                    continue

                letter_part = ''
                number_part = ''
                for char in part:
                    if char.isalpha():
                        letter_part += char
                    elif char.isdigit():
                        number_part += char
                    else:
                        break

                if letter_part and number_part:
                    try:
                        number = int(number_part)
                        if 1 <= number <= 32:
                            color_code = f"{letter_part}{number}"
                            color_count[color_code] = color_count.get(color_code, 0) + 1
                    except ValueError:
                        continue

    return color_count, None


def generate_csv_data(color_count):
    """生成 CSV 数据"""
    data = []
    for color_code in color_count.keys():
        count = color_count[color_code]
        plate_info = color_mapping.get(color_code, ('未知', '未知'))
        plate_number = plate_info[0]
        color_name = plate_info[1]
        data.append((color_code, plate_number, count, color_name))

    # 按色盘排序
    def sort_key(item):
        plate = item[1]
        try:
            plate_int = int(plate)
        except ValueError:
            plate_int = 999
        return (plate_int, item[0])

    data.sort(key=sort_key)
    return data


def generate_excel(data, output_path):
    """生成 Excel 文件"""
    wb = Workbook()
    ws = wb.active
    ws.title = "颜色统计"

    # 设置表头样式
    header_fill = PatternFill(start_color="1976D2", end_color="1976D2", fill_type="solid")
    header_font = Font(color="FFFFFF", bold=True, size=12)
    header_alignment = Alignment(horizontal="center", vertical="center")

    # 写入表头
    headers = ['序号', '颜色编号', '色盘', '数量', '颜色名称']
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = header_alignment

    # 设置边框
    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

    # 写入数据
    for idx, row_data in enumerate(data, start=1):
        ws.cell(row=idx+1, column=1, value=idx)
        ws.cell(row=idx+1, column=2, value=row_data[0])
        ws.cell(row=idx+1, column=3, value=row_data[1])
        ws.cell(row=idx+1, column=4, value=row_data[2])
        ws.cell(row=idx+1, column=5, value=row_data[3])

    # 设置所有单元格边框和对齐
    for row in ws.iter_rows(min_row=1, max_row=len(data)+1, min_col=1, max_col=5):
        for cell in row:
            cell.border = thin_border
            cell.alignment = Alignment(horizontal="center", vertical="center")

    # 调整列宽
    ws.column_dimensions['A'].width = 8
    ws.column_dimensions['B'].width = 12
    ws.column_dimensions['C'].width = 8
    ws.column_dimensions['D'].width = 8
    ws.column_dimensions['E'].width = 15

    wb.save(output_path)


@app.route('/')
def index():
    """首页"""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    """处理图片上传"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': '没有文件'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': '没有选择文件'})

    if file:
        filename = str(uuid.uuid4()) + '.jpg'
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # 处理图片
        color_count, error = process_image(filepath)

        if error:
            return jsonify({'success': False, 'error': error})

        # 生成 CSV 数据
        csv_data = generate_csv_data(color_count)

        # 保存 CSV 文件
        csv_filename = filename.replace('.jpg', '.csv')
        csv_path = os.path.join(app.config['UPLOAD_FOLDER'], csv_filename)

        with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(['序号', '颜色编号', '色盘', '数量', '颜色名称'])
            for idx, row in enumerate(csv_data, start=1):
                writer.writerow([idx] + list(row))

        # 生成 Excel 文件
        xlsx_filename = filename.replace('.jpg', '.xlsx')
        xlsx_path = os.path.join(app.config['UPLOAD_FOLDER'], xlsx_filename)
        generate_excel(csv_data, xlsx_path)

        return jsonify({
            'success': True,
            'data': csv_data,
            'csv_url': f'/download/{csv_filename}',
            'xlsx_url': f'/download/{xlsx_filename}'
        })


@app.route('/query', methods=['POST'])
def query():
    """查询颜色编号对应的色盘"""
    input_text = request.json.get('colors', '').strip()

    if not input_text:
        return jsonify({'success': False, 'error': '输入为空'})

    color_codes = input_text.split()
    results = []

    for code in color_codes:
        code_upper = code.upper()
        plate = color_mapping.get(code_upper, '未找到')
        results.append({'color': code, 'plate': plate})

    return jsonify({'success': True, 'results': results})


@app.route('/download/<filename>')
def download(filename):
    """下载 CSV 文件"""
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    return send_file(filepath, as_attachment=True)


if __name__ == '__main__':
    # 启动时加载 OCR 和颜色映射
    init_ocr()
    load_color_mapping()

    # 启动 Flask 应用（使用 8080 端口避免冲突）
    app.run(debug=True, host='0.0.0.0', port=8080)
