from flask import Flask, request, jsonify
from dotenv import load_dotenv
from inference_sdk import InferenceHTTPClient
from paddleocr import PaddleOCR
import requests
import logging
import traceback
import gc
import os

# =====================================
# DISABLE LOGS
# =====================================

logging.disable(logging.CRITICAL)

# =====================================
# LOAD ENV
# =====================================

load_dotenv()

# =====================================
# FLASK APP
# =====================================

app = Flask(__name__)

# =====================================
# ROBOFLOW CLIENT
# =====================================

client = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key=os.getenv("ROBOFLOW_API_KEY")
)

# =====================================
# OCR MODEL (GLOBAL)
# =====================================

ocr = None

# =====================================
# LOAD OCR ONLY WHEN NEEDED
# =====================================

def get_ocr():

    global ocr

    if ocr is None:

        print("===== LOADING OCR MODEL =====")

        ocr = PaddleOCR(
    use_angle_cls=False,
    lang="en"
)

    return ocr

# =====================================
# HOME ROUTE
# =====================================

@app.route("/", methods=["GET"])
def home():

    return jsonify({
        "success": True,
        "message": "Python OCR API Running"
    })

# =====================================
# DETECT ROUTE
# =====================================

@app.route("/detect", methods=["POST"])
def detect():

    try:

        data = request.get_json()

        if not data:

            return jsonify({
                "success": False,
                "message": "No JSON received"
            }), 400

        image_url = data.get("image_url")

        if not image_url:

            return jsonify({
                "success": False,
                "message": "No image_url"
            }), 400

        print("\n===== DETECT API =====")
        print(image_url)

        # =====================================
        # ROBOFLOW
        # =====================================

        result = client.run_workflow(
            workspace_name="sr-banda",
            workflow_id="detect-count-and-visualize",
            images={
                "image": image_url
            },
            use_cache=True
        )

        predictions = []

        # =====================================
        # RESULT PARSE
        # =====================================

        if isinstance(result, list):

            if len(result) > 0:

                first = result[0]

                if isinstance(first, dict):

                    if isinstance(
                        first.get("predictions"),
                        dict
                    ):

                        predictions = first[
                            "predictions"
                        ].get(
                            "predictions",
                            []
                        )

        elif isinstance(result, dict):

            if isinstance(
                result.get("predictions"),
                list
            ):

                predictions = result.get(
                    "predictions",
                    []
                )

        # =====================================
        # DETECTION CHECK
        # =====================================

        has_person = False
        has_idcard = False

        for item in predictions:

            cls = str(
                item.get("class", "")
            ).lower().strip()

            print("CLASS:", cls)

            if cls == "person":

                has_person = True

            if cls in [
                "idcard",
                "id card",
                "id_card"
            ]:

                has_idcard = True

        final_result = (
            has_person and has_idcard
        )

        gc.collect()

        return jsonify({

            "success": True,

            "id_card_detected":
            final_result,

            "person_detected":
            has_person,

            "card_detected":
            has_idcard,

            "predictions":
            predictions

        })

    except Exception as e:

        traceback.print_exc()

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

# =====================================
# OCR ROUTE
# =====================================

@app.route("/ocr", methods=["POST"])
def extract_text():

    image_path = "temp.jpg"

    try:

        data = request.get_json()

        if not data:

            return jsonify({
                "success": False,
                "message": "No JSON received"
            }), 400

        image_url = data.get("image_url")

        if not image_url:

            return jsonify({
                "success": False,
                "message": "No image_url"
            }), 400

        print("\n===== OCR API =====")
        print(image_url)

        # =====================================
        # DOWNLOAD IMAGE
        # =====================================

        response = requests.get(
            image_url,
            timeout=20
        )

        if response.status_code != 200:

            return jsonify({
                "success": False,
                "message": "Image download failed"
            }), 400

        with open(image_path, "wb") as f:

            f.write(response.content)

        # =====================================
        # OCR
        # =====================================

        ocr_model = get_ocr()

        result = ocr.ocr(
    image_path,
    cls=False
)

        extracted_lines = []

        if result and result[0]:

            for line in result[0]:

                try:

                    text = line[1][0]

                    cleaned = text.strip()

                    if cleaned:

                        extracted_lines.append(
                            cleaned
                        )

                except:

                    pass

        print("===== OCR TEXT =====")
        print(extracted_lines)

        # =====================================
        # KEY VALUE EXTRACTION
        # =====================================

        extracted_data = {}

        for line in extracted_lines:

            if ":" in line:

                parts = line.split(":")

                key = parts[0].strip()

                value = ":".join(
                    parts[1:]
                ).strip()

                if key and value:

                    extracted_data[key] = value

        gc.collect()

        return jsonify({

            "success": True,

            "raw_text": extracted_lines,

            "data": extracted_data

        })

    except Exception as e:

        traceback.print_exc()

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:

        # DELETE TEMP FILE

        if os.path.exists(image_path):

            try:

                os.remove(image_path)

            except:

                pass

# =====================================
# START SERVER
# =====================================

if __name__ == "__main__":
    print("Starting Flask Server...")
    
    app.run(
        host="127.0.0.1",
        port=10000,
        debug=True
    )