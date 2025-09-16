import os
import cv2
import numpy as np
import base64
from flask import Flask, request, jsonify, render_template
from PIL import Image
import pytesseract

# --- ▼▼▼ Tesseractパス設定 ▼▼▼ ---
# Heroku環境ではTesseractは/usr/bin/tesseractに配置される
if os.environ.get('DYNO'):  # Heroku環境の検出
    pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
    print("Tesseract path set for Heroku environment.")
else:
    # ローカル環境用
    try:
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        print("Tesseract path set for local environment.")
    except Exception as e:
        print(f"!!! TESSERACT PATH ERROR: {e} !!!")
# --- ▲▲▲ Tesseractパス設定 ▲▲▲ ---

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ocr', methods=['POST'])
def ocr_endpoint():
    data = request.json
    if not data or 'image' not in data:
        return jsonify({"error": "No image data provided"}), 400

    image_data_base64 = data['image'].split(',')[1]
    missing_padding = len(image_data_base64) % 4
    if missing_padding:
        image_data_base64 += '=' * (4 - missing_padding)

    try:
        image_bytes = base64.b64decode(image_data_base64)
    except Exception as e:
        return jsonify({"error": f"Base64 decode error: {e}"}), 400

    np_array = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

    if image is None:
        return jsonify({"error": "Could not decode image"}), 400
   # ==============================
    # 画像前処理 (精度改善のため追加)
    # ==============================

    # 1. グレースケール
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 2. ノイズ除去（GaussianBlur）
    gray = cv2.GaussianBlur(gray, (3, 3), 0)

    # 3. ヒストグラム均一化（全体コントラスト改善）
    gray = cv2.equalizeHist(gray)

    # 4. コントラスト強調（CLAHE）
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)

    # 5. ガンマ補正（暗い部分をより暗く / 明るい部分をより明るく）
    gamma = 1.5  # 1.0より大きくするとコントラスト強調
    gray = np.array(255 * (gray / 255) ** (1/gamma), dtype=np.uint8)

    # 6. 二値化（大津の手法）
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # 7. 白黒反転（文字を黒、背景を白にする）
    binary = cv2.bitwise_not(binary)

    # 8. モルフォロジー処理（細かいゴミを除去）
    kernel = np.ones((1, 1), np.uint8)
    binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

    try:
        print("Performing OCR with Tesseract...")

        custom_config = r'--oem 3 --psm 6'
        data = pytesseract.image_to_data(
            binary, lang='jpn', config=custom_config, output_type=pytesseract.Output.DICT
        )
        print("OCR complete.")

        n_boxes = len(data['level'])
        text_results = []
        boxes_serializable = []

        for i in range(n_boxes):
            if int(data['conf'][i]) > 60:  # 信頼度60%以上
                text = data['text'][i]
                if text.strip():
                    text_results.append(text)
                    (x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
                    boxes_serializable.append([[x, y], [x+w, y], [x+w, y+h], [x, y+h]])

        return jsonify({
            "text": text_results,
            "boxes": boxes_serializable
        })
    except Exception as e:
        return jsonify({"error": f"Tesseract processing error: {e}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)