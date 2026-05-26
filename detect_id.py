from flask import Flask, request, jsonify
from dotenv import load_dotenv
from inference_sdk import InferenceHTTPClient
from paddleocr import PaddleOCR
import requests
import os

# -----------------------------------
# LOAD ENV
# -----------------------------------

load_dotenv()

app = Flask(__name__)

# -----------------------------------
# ROBOFLOW CLIENT
# -----------------------------------

client = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key=os.getenv("ROBOFLOW_API_KEY")
)

# -----------------------------------
# OCR MODEL
# -----------------------------------

ocr = PaddleOCR(
    use_angle_cls=True,
    lang="en"
)

# -----------------------------------
# HOME ROUTE
# -----------------------------------

@app.route("/", methods=["GET"])
def home():

    return jsonify({
        "success": True,
        "message": "Python Detection + OCR API Running"
    })

# -----------------------------------
# DETECT ROUTE
# -----------------------------------

@app.route("/detect", methods=["POST"])
def detect():

    try:

        print("\n===== DETECT API HIT =====")

        data = request.get_json()

        if not data:

            return jsonify({
                "success": False,
                "message": "No JSON data received"
            }), 400

        image_url = data.get("image_url")

        print("IMAGE URL:")
        print(image_url)

        if not image_url:

            return jsonify({
                "success": False,
                "message": "No image_url provided"
            }), 400

        # -----------------------------------
        # ROBOFLOW DETECTION
        # -----------------------------------

        result = client.run_workflow(
            workspace_name="sr-banda",
            workflow_id="detect-count-and-visualize",
            images={
                "image": image_url
            },
            use_cache=True
        )

        print("===== ROBOFLOW RESPONSE RECEIVED =====")

        has_person = False
        has_idcard = False

        predictions = []

        # -----------------------------------
        # RESULT PARSING
        # -----------------------------------

        if isinstance(result, dict):

            if isinstance(result.get("predictions"), list):

                predictions = result.get("predictions")

            elif isinstance(
                result.get("predictions"),
                dict
            ):

                predictions = result[
                    "predictions"
                ].get(
                    "predictions",
                    []
                )

        elif (
            isinstance(result, list)
            and len(result) > 0
        ):

            first = result[0]

            if isinstance(
                first.get("predictions"),
                list
            ):

                predictions = first.get(
                    "predictions"
                )

            elif isinstance(
                first.get("predictions"),
                dict
            ):

                predictions = first[
                    "predictions"
                ].get(
                    "predictions",
                    []
                )

        print("===== FINAL PREDICTIONS =====")
        print(predictions)

        # -----------------------------------
        # DETECTION LOOP
        # -----------------------------------

        for item in predictions:

            cls = str(
                item.get("class", "")
            ).strip().lower()

            print("CLASS:", cls)

            # PERSON DETECT
            if cls == "person":

                has_person = True

            # ID CARD DETECT
            if cls in [
                "idcard",
                "id card",
                "id_card"
            ]:

                has_idcard = True

        final_result = (
            has_person and has_idcard
        )

        print("PERSON:", has_person)
        print("IDCARD:", has_idcard)
        print("FINAL:", final_result)

        return jsonify({

            "success": True,

            "id_card_detected": final_result,

            "person_detected": has_person,

            "card_detected": has_idcard,

            "predictions": predictions

        })

    except Exception as e:

        print("\n===== DETECT ERROR =====")
        print(str(e))

        # Render Sleep / Timeout Handle
        if (
            "timed out" in str(e).lower()
            or "timeout" in str(e).lower()
        ):

            return jsonify({
                "success": False,
                "message":
                "Server is waking up. Please try again in few seconds."
            }), 500

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

# -----------------------------------
# OCR ROUTE
# -----------------------------------

@app.route("/ocr", methods=["POST"])
def extract_text():

    try:

        print("\n===== OCR API HIT =====")

        data = request.get_json()

        if not data:

            return jsonify({
                "success": False,
                "message": "No JSON data received"
            }), 400

        image_url = data.get("image_url")

        print("OCR IMAGE URL:")
        print(image_url)

        if not image_url:

            return jsonify({
                "success": False,
                "message": "No image_url provided"
            }), 400

        # -----------------------------------
        # DOWNLOAD IMAGE
        # -----------------------------------

        image_path = "temp_id_card.jpg"

        response = requests.get(image_url)

        with open(image_path, "wb") as f:
            f.write(response.content)

        # -----------------------------------
        # OCR RUN
        # -----------------------------------

        result = ocr.ocr(
            image_path
        )

        extracted_lines = []

        if result and result[0]:

            for line in result[0]:

                text = line[1][0]

                cleaned_text = text.strip()

                if cleaned_text:

                    extracted_lines.append(
                        cleaned_text
                    )

        print("===== OCR TEXT =====")
        print(extracted_lines)

        # -----------------------------------
        # DYNAMIC KEY VALUE EXTRACTION
        # -----------------------------------

        extracted_data = {}

        for line in extracted_lines:

            # CASE 1 -> NAME: Ravi
            if ":" in line:

                parts = line.split(":")

                if len(parts) >= 2:

                    key = parts[0].strip()

                    value = ":".join(
                        parts[1:]
                    ).strip()

                    if key and value:

                        extracted_data[key] = value

            # CASE 2 -> NAME Ravi
            else:

                words = line.split()

                if len(words) >= 2:

                    key = words[0].strip()

                    value = " ".join(
                        words[1:]
                    ).strip()

                    if (
                        key
                        and value
                        and len(key) < 30
                    ):

                        extracted_data[key] = value

        return jsonify({

            "success": True,

            "raw_text": extracted_lines,

            "data": extracted_data

        })

    except Exception as e:

        print("\n===== OCR ERROR =====")
        print(str(e))

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

# -----------------------------------
# START SERVER
# -----------------------------------

if __name__ == "__main__":

    port = int(
        os.environ.get("PORT", 10000)
    )

    app.run(
        host="0.0.0.0",
        port=port
    )