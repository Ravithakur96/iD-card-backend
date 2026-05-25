# from flask import Flask, request, jsonify

# app = Flask(__name__)

# @app.route("/detect", methods=["POST"])
# def detect():

#     return jsonify({
#         "success": True,
#         "id_card_detected": True
#     })

# if __name__ == "__main__":
#     app.run(port=8000)



#     # 1. Import the library
# from inference_sdk import InferenceHTTPClient

# # 2. Connect to your workflow
# client = InferenceHTTPClient(
#     api_url="https://serverless.roboflow.com",
#     api_key="mTSDCSZIfmFLMMSN2Csu"
# )

# # 3. Run your workflow on an image
# result = client.run_workflow(
#     workspace_name="sr-banda",
#     workflow_id="detect-count-and-visualize",
#     images={
#         "image": "YOUR_IMAGE.jpg" # Path to your image file
#     },
#     use_cache=True # Speeds up repeated requests
# )

# # 4. Get your results
# print(result)



# from flask import Flask, request, jsonify
# from inference_sdk import InferenceHTTPClient
# import os

# app = Flask(__name__)

# client = InferenceHTTPClient(
#     api_url="https://serverless.roboflow.com",
#     api_key="mTSDCSZIfmFLMMSN2Csu"
# )

# @app.route("/detect", methods=["POST"])
# def detect():

#     if "image" not in request.files:
#         return jsonify({
#             "success": False,
#             "message": "No image uploaded"
#         })

#     image = request.files["image"]

#     temp_path = "temp.jpg"

#     image.save(temp_path)

#     result = client.run_workflow(
#         workspace_name="sr-banda",
#         workflow_id="detect-count-and-visualize",
#         images={
#             "image": temp_path
#         },
#         use_cache=True
#     )

#     found = False

# try:
#     predictions = result["predictions"]

#     for item in predictions:

#         if item["class"] == "IDCard":
#             found = True

# except:
#     pass
#     app.run(port=8000)
    
# print(result)




# from flask import Flask, request, jsonify
# from inference_sdk import InferenceHTTPClient
# import os

# app = Flask(__name__)

# client = InferenceHTTPClient(
#     api_url="https://serverless.roboflow.com",
#     api_key="mTSDCSZIfmFLMMSN2Csu"
# )

# @app.route("/detect", methods=["POST"])
# def detect():

#     if "image" not in request.files:
#         return jsonify({
#             "success": False
#         })

#     image = request.files["image"]

#     temp_path = "temp.jpg"

#     image.save(temp_path)

#     result = client.run_workflow(
#         workspace_name="sr-banda",
#         workflow_id="detect-count-and-visualize",
#         images={
#             "image": temp_path
#         },
#         use_cache=True
#     )

#     print(result)

#     found = False

#     try:
#         predictions = result["predictions"]

#         for item in predictions:

#             if item["class"] == "IDCard":
#                 found = True

#     except:
#         pass

#     os.remove(temp_path)

#     return jsonify({
#         "success": True,
#         "id_card_detected": found,
#         "data": result
#     })

# if __name__ == "__main__":
#     app.run(port=8000)

from flask import Flask, request, jsonify
from dotenv import load_dotenv
from inference_sdk import InferenceHTTPClient
import os

load_dotenv()

app = Flask(__name__)

# Roboflow Client
client = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key=os.getenv("ROBOFLOW_API_KEY")
)

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "success": True,
        "message": "Python Detection API Running"
    })

@app.route("/detect", methods=["POST"])
def detect():

    try:

        print("===== API HIT =====")

        # JSON data receive
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

        # Run Roboflow Workflow
        result = client.run_workflow(
            workspace_name="sr-banda",
            workflow_id="detect-count-and-visualize",
            images={
                "image": image_url
            },
            use_cache=False
        )

        print("===== FULL RESULT =====")
        print(result)

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

                predictions = result["predictions"].get("predictions", [])

        elif isinstance(result, list) and len(result) > 0:

            first = result[0]

            if isinstance(first.get("predictions"), list):

                predictions = first.get("predictions")

            elif isinstance(first.get("predictions"), dict):

                predictions = first["predictions"].get("predictions", [])

        print("===== FINAL PREDICTIONS =====")
        print(predictions)

        # -------------------------
        # DETECTION LOOP
        # -------------------------

        for item in predictions:

            print("ITEM:")
            print(item)

            cls = str(item.get("class", "")).strip().lower()

            print("CLASS:")
            print(cls)

            if cls == "person":
                has_person = True

            if cls in ["idcard", "id card", "id_card"]:
                has_idcard = True

        print("PERSON:", has_person)
        print("IDCARD:", has_idcard)

        final_result = has_person and has_idcard

        print("FINAL RESULT:", final_result)

        return jsonify({
            "success": True,
            "id_card_detected": final_result,
            "person_detected": has_person,
            "card_detected": has_idcard,
            "predictions": predictions
        })

    except Exception as e:

        print("===== ERROR =====")
        print(str(e))

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)