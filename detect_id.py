from flask import Flask, request, jsonify
from dotenv import load_dotenv
from inference_sdk import InferenceHTTPClient
import os

# Load .env file
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
# HOME ROUTE
# -----------------------------------

@app.route("/", methods=["GET"])
def home():

    return jsonify({
        "success": True,
        "message": "Python Detection API Running"
    })

# -----------------------------------
# DETECT ROUTE
# -----------------------------------

@app.route("/detect", methods=["POST"])
def detect():

    try:

        print("\n===== API HIT =====")

        # -------------------------
        # GET JSON DATA
        # -------------------------

        data = request.get_json()

        if not data:

            return jsonify({
                "success": False,
                "message": "No JSON data received"
            }), 400

        # -------------------------
        # GET IMAGE URL
        # -------------------------

        image_url = data.get("image_url")

        print("IMAGE URL:")
        print(image_url)

        if not image_url:

            return jsonify({
                "success": False,
                "message": "No image_url provided"
            }), 400

        # -------------------------
        # RUN ROBOFLOW WORKFLOW
        # -------------------------

        result = client.run_workflow(
            workspace_name="sr-banda",
            workflow_id="detect-count-and-visualize",
            images={
                "image": image_url
            },
            use_cache=False
        )

        print("===== ROBOFLOW RESPONSE RECEIVED =====")

        # -------------------------
        # VARIABLES
        # -------------------------

        has_person = False
        has_idcard = False

        predictions = []

        # -------------------------
        # RESULT PARSING
        # -------------------------

        if isinstance(result, dict):

            # CASE 1
            if isinstance(result.get("predictions"), list):

                predictions = result.get("predictions")

            # CASE 2
            elif isinstance(result.get("predictions"), dict):

                predictions = result["predictions"].get(
                    "predictions",
                    []
                )

        elif isinstance(result, list) and len(result) > 0:

            first = result[0]

            if isinstance(first.get("predictions"), list):

                predictions = first.get("predictions")

            elif isinstance(first.get("predictions"), dict):

                predictions = first["predictions"].get(
                    "predictions",
                    []
                )

        print("===== FINAL PREDICTIONS =====")
        print(predictions)

        # -------------------------
        # DETECTION LOOP
        # -------------------------

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

        # -------------------------
        # FINAL RESULT
        # -------------------------

        final_result = has_person and has_idcard

        print("PERSON DETECTED:", has_person)
        print("ID CARD DETECTED:", has_idcard)
        print("FINAL RESULT:", final_result)

        # -------------------------
        # SUCCESS RESPONSE
        # -------------------------

        return jsonify({
            "success": True,
            "id_card_detected": final_result,
            "person_detected": has_person,
            "card_detected": has_idcard,
            "predictions": predictions
        })

    except Exception as e:

        print("\n===== ERROR =====")
        print(str(e))

        # Timeout / Sleep Handling
        if "timed out" in str(e).lower():

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
# START SERVER
# -----------------------------------

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 10000))

    app.run(
        host="0.0.0.0",
        port=port
    )