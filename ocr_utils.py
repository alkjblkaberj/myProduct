import os
import easyocr
import pyocr
import pyocr.builders
import cv2
import numpy as np
import uuid
from PIL import Image

# Tesseractのパス設定
tesseract_path = r"C:\Program Files\Tesseract-OCR"
if os.path.exists(tesseract_path):
    if tesseract_path not in os.environ["PATH"]:
        os.environ["PATH"] += os.pathsep + tesseract_path
else:
    print(f"警告: Tesseractのパスが見つかりません。{tesseract_path}")

try:
    tools = pyocr.get_available_tools()
    if len(tools) == 0:
        tool = None
        print("PyOCRツールが見つかりません。Tesseractをインストールしてください。")
    else:
        tool = tools[0]
        print("PyOCRツールが正常に見つかりました。")
except Exception as e:
    tool = None
    print(f"PyOCRの初期化エラー: {e}")

try:
    reader = easyocr.Reader(['ja', 'en'], gpu=False)
    print("EasyOCRリーダーが正常に初期化されました。")
except Exception as e:
    reader = None
    print(f"EasyOCRの初期化エラー: {e}")

UPLOAD_FOLDER = "static/uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# PyOCR処理関数
def run_pyocr(img_path):
    print("--- デバッグ: PyOCR処理開始 ---")
    if not tool:
        print("デバッグ: PyOCRツールが利用できません。")
        return "PyOCRは利用できません。", None
    
    try:
        print(f"デバッグ: 画像パスを確認: {img_path}")
        img = Image.open(img_path)
        print("デバッグ: PILで画像を読み込みました。")
        
        text = tool.image_to_string(
            img,
            lang="jpn+eng",
            builder=pyocr.builders.TextBuilder(tesseract_layout=6)
        )
        print("デバッグ: Tesseractでテキストを抽出しました。")

        words = tool.image_to_string(
            img,
            lang="jpn+eng",
            builder=pyocr.builders.WordBoxBuilder(tesseract_layout=6)
        )
        print("デバッグ: Tesseractで単語の座標を抽出しました。")
        
        draw_rectangle = cv2.imread(img_path)
        if draw_rectangle is None:
            raise ValueError("OpenCVが画像を読み込めませんでした。")
        print("デバッグ: OpenCVで画像を読み込みました。")

        for box in words:
            cv2.rectangle(draw_rectangle, box.position[0], box.position[1], (255, 0, 0), 2)
        print("デバッグ: 単語の周りに枠を描画しました。")
        
        out_path = os.path.join(UPLOAD_FOLDER, f"pyocr_{uuid.uuid4().hex}.png")
        cv2.imwrite(out_path, draw_rectangle)
        print(f"デバッグ: 処理済み画像を保存しました: {out_path}")
        
        return text, out_path
    except Exception as e:
        print(f"デバッグ: PyOCR処理中にエラーが発生しました: {e}")
        return f"エラー: PyOCR処理失敗。詳細: {e}", None

# EasyOCR処理関数
def run_easyocr(img_path):
    print("--- デバッグ: EasyOCR処理開始 ---")
    if not reader:
        print("デバッグ: EasyOCRリーダーが利用できません。")
        return "EasyOCRは利用できません。", None
        
    try:
        print(f"デバッグ: 画像パスを確認: {img_path}")
        results = reader.readtext(img_path)
        print("デバッグ: EasyOCRでテキストを抽出しました。")

        img = cv2.imread(img_path)
        if img is None:
            raise ValueError("OpenCVが画像を読み込めませんでした。")
        print("デバッグ: OpenCVで画像を読み込みました。")

        img_copy = img.copy()
        
        for detection in results:
            points = detection[0]
            points = np.array(points, dtype=np.int32)
            cv2.polylines(img_copy, [points], True, (0, 255, 0), 2)
        print("デバッグ: 単語の周りに枠を描画しました。")

        out_path = os.path.join(UPLOAD_FOLDER, f"easyocr_{uuid.uuid4().hex}.png")
        cv2.imwrite(out_path, img_copy)
        print(f"デバッグ: 処理済み画像を保存しました: {out_path}")

        text_results = [d[1] for d in results]
        return text_results, out_path
    except Exception as e:
        print(f"デバッグ: EasyOCR処理中にエラーが発生しました: {e}")
        return f"エラー: EasyOCR処理失敗。詳細: {e}", None
# import easyocr
# import pytesseract
# import cv2, os, uuid
# from PIL import Image
# import numpy as np
# import warnings

# # 警告を無視
# warnings.filterwarnings("ignore", category=UserWarning)

# # pytesseract 設定
# pytesseract.pytesseract.tesseract_cmd = r"C:\Users\Owner\Downloads\tesseract-ocr-w64-setup-5.5.0.20241111.exe"

# UPLOAD_FOLDER = "static/uploads"
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# # EasyOCR を一度だけ初期化（重いのでグローバルに保持）
# reader = easyocr.Reader(['ja', 'en'], gpu=False)

# def resize_image(img_path, max_size=1600):
#     img = cv2.imread(img_path)
#     h, w = img.shape[:2]
#     if max(h, w) > max_size:
#         scale = max_size / max(h, w)
#         img = cv2.resize(img, (int(w*scale), int(h*scale)))
#         cv2.imwrite(img_path, img)


# # --- OCR関数（pytesseract） ---
# def run_pyocr(img_path):
#     """Tesseract OCRでテキスト認識と枠付き画像生成"""
#     img = Image.open(img_path)
#     # 日本語 + 英語対応
#     text = pytesseract.image_to_string(img, lang="jpn+eng")

#     # 単語ごとの位置情報を取得
#     data = pytesseract.image_to_data(img, lang="jpn+eng", output_type=pytesseract.Output.DICT)

#     draw_rectangle = cv2.imread(img_path)

#     for i in range(len(data["level"])):
#         (x, y, w, h) = (data["left"][i], data["top"][i], data["width"][i], data["height"][i])
#         if data["text"][i].strip() != "":
#             cv2.rectangle(draw_rectangle, (x, y), (x + w, y + h), (255, 0, 0), 2)

#     out_path = os.path.join(UPLOAD_FOLDER, f"pytesseract_{uuid.uuid4().hex}.png")
#     cv2.imwrite(out_path, draw_rectangle)

#     return text, out_path

# # --- OCR関数（easyocr） ---
# # GPUを使わない（CPUのみ）
# reader = easyocr.Reader(['ja', 'en'], gpu=False)

# def run_easyocr(img_path):
#     resize_image(img_path)  # リサイズ追加
#     results = reader.readtext(img_path)

#     img = cv2.imread(img_path)
#     img_copy = img.copy()

#     for detection in results:
#         points = np.array(detection[0], dtype=np.int32)
#         cv2.polylines(img_copy, [points], True, (0, 255, 0), 2)

#     out_path = os.path.join(UPLOAD_FOLDER, f"easyocr_{uuid.uuid4().hex}.png")
#     cv2.imwrite(out_path, img_copy)

#     text_results = [d[1] for d in results]
#     return text_results, out_path

