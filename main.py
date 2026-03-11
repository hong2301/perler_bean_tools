import os
import cv2
import numpy as np
from paddleocr import PaddleOCR

# 变量区################################################################################################################################################################################
ocr = PaddleOCR(
    use_doc_orientation_classify=False,  # 不使用文档方向分类模型
    use_doc_unwarping=False,  # 不使用文本图像矫正模型
    use_textline_orientation=False,  # 不使用文本行方向分类模型
)


# 函数区################################################################################################################################################################################
def split_image(image, chunk_height=1000, overlap=100):
    """
    将图片按高度分块，带重叠区域避免文字被切分
    :param image: cv2 读取的图片
    :param chunk_height: 每块的高度
    :param overlap: 重叠区域高度
    :return: 分块列表，每个元素是 (块图片, y_offset)
    """
    height, width = image.shape[:2]
    chunks = []
    start_y = 0

    while start_y < height:
        end_y = min(start_y + chunk_height, height)
        chunk = image[start_y:end_y, 0:width]
        chunks.append((chunk, start_y))

        if end_y >= height:
            break
        start_y = end_y - overlap  # 重叠区域

    return chunks


def ocr_chunk(chunk, y_offset):
    """
    对单块图片进行 OCR 识别
    :param chunk: 图片块
    :param y_offset: y 轴偏移量
    :return: 识别结果字典
    """
    # 临时保存图片块
    temp_path = "./temp_chunk.jpg"
    cv2.imwrite(temp_path, chunk)

    try:
        result = ocr.predict(temp_path)

        if isinstance(result, (list, tuple)) and len(result) > 0:
            res = result[0]
            if res is not None:
                # 调整检测框的 y 坐标
                if 'det_boxes' in res:
                    for box in res['det_boxes']:
                        box[1] += y_offset  # y_min
                        box[3] += y_offset  # y_max
                return res
    except Exception as e:
        print(f"识别块时出错 (y_offset={y_offset}): {e}")

    return None


def merge_results(results):
    """
    合并多个分块的 OCR 结果
    """
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


def ocr_with_chunks(filename, chunk_height=1000, overlap=100):
    """
    分块 OCR 主函数
    :param filename: 图片文件名
    :param chunk_height: 每块高度
    :param overlap: 重叠区域
    :return: 合并后的识别结果
    """
    # 读取图片
    image_path = f"./{filename}"
    image = cv2.imread(image_path)

    if image is None:
        print(f"无法读取图片: {image_path}")
        return None

    height, width = image.shape[:2]
    print(f"图片尺寸: {width}x{height}")

    # 如果图片高度小于分块高度，直接识别
    if height <= chunk_height:
        print("图片高度较小，直接识别")
        result = ocr.predict(image_path)
        if isinstance(result, (list, tuple)) and len(result) > 0:
            return result[0]
        return None

    # 分块处理
    print(f"开始分块处理，每块高度: {chunk_height}, 重叠: {overlap}")
    chunks = split_image(image, chunk_height, overlap)
    print(f"共分成 {len(chunks)} 块")

    results = []
    for i, (chunk, y_offset) in enumerate(chunks):
        print(f"正在识别第 {i + 1}/{len(chunks)} 块...")
        res = ocr_chunk(chunk, y_offset)
        if res:
            results.append(res)

    # 合并结果
    merged_result = merge_results(results)
    print(f"分块识别完成，共识别到 {len(merged_result['rec_texts'])} 个文本")

    return merged_result

def getColor(filname='input.jpg',chunk_height=400,overlap=2):
    # 设置分块高度和重叠区域
    ocrResult = ocr_with_chunks(filname, chunk_height, overlap)

    if ocrResult:
        rec_texts = ocrResult.get('rec_texts', [])
        rec_scores = ocrResult.get('rec_scores', [])
        filtered_texts = []
        for text, score in zip(rec_texts, rec_scores):
            if score > 0.9:
                filtered_texts.append(text)

        print(f"\n最终文本列表: {filtered_texts}")
    else:
        print("OCR 识别失败，没有返回结果")

    # 清理临时文件
    if os.path.exists("./temp_chunk.jpg"):
        os.remove("./temp_chunk.jpg")


# 主流程################################################################################################################################################################################
if __name__ == "__main__":
    getColor('input.jpg')