from flask import Flask, request, jsonify
from dotenv import load_dotenv
from inference_sdk import InferenceHTTPClient
import easyocr
import requests
import os
import logging

logging.disable(logging.CRITICAL)

# =========================
# LOAD ENV
# =========================

load_dotenv()

app = Flask(__name__)

# =========================
# ROBOFLOW
# =========================

client = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key=os.getenv("ROBOFLOW_API_KEY")
)

# =========================
# EASY OCR
# =========================

reader = easyocr.Reader(
    ['en'],
    gpu=False
)

# =========================
# HOME
# =========================

@app.route("/")
def home():

    return jsonify({
        "success": True,
        "message": "API Running"
    })

# =========================
# DETECT
# =========================

@app.route("/detect", methods=["POST"])
def detect():

    try:

        data = request.get_json()

        image_url = data.get("image_url")

        result = client.run_workflow(
            workspace_name="sr-banda",
            workflow_id="detect-count-and-visualize",
            images={
                "image": image_url
            },
            use_cache=True
        )

        has_person = False
        has_idcard = False

        predictions = []

        if isinstance(result, dict):

            if isinstance(result.get("predictions"), list):

                predictions = result.get("predictions")

            elif isinstance(result.get("predictions"), dict):

                predictions = result["predictions"].get(
                    "predictions",
                    []
                )

        for item in predictions:

            cls = str(
                item.get("class", "")
            ).lower().strip()

            if cls == "person":

                has_person = True

            if cls in [
                "idcard",
                "id card",
                "id_card"
            ]:

                has_idcard = True

        return jsonify({

            "success": True,

            "id_card_detected":
            has_person and has_idcard,

            "person_detected":
            has_person,

            "card_detected":
            has_idcard,

            "predictions":
            predictions

        })

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

# =========================
# OCR
# =========================

@app.route("/ocr", methods=["POST"])
def ocr_route():

    try:

        data = request.get_json()

        image_url = data.get("image_url")

        if not image_url:

            return jsonify({
                "success": False,
                "message": "No image"
            }), 400

        # DOWNLOAD IMAGE

        image_path = "temp.jpg"

        response = requests.get(image_url)

        with open(image_path, "wb") as f:

            f.write(response.content)

        # OCR

        result = reader.readtext(image_path)

        raw_text = []

        for item in result:

            text = item[1]

            raw_text.append(text)

        # DYNAMIC DATA

        extracted_data = {}

        for line in raw_text:

            if ":" in line:

                parts = line.split(":")

                key = parts[0].strip()

                value = ":".join(parts[1:]).strip()

                if key and value:

                    extracted_data[key] = value

        return jsonify({

            "success": True,

            "raw_text": raw_text,

            "data": extracted_data

        })

    except Exception as e:

        print(str(e))

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

# =========================
# START
# =========================

if __name__ == "__main__":

    port = int(
        os.environ.get("PORT", 10000)
    )

    app.run(
        host="0.0.0.0",
        port=port
    )