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
from inference import InferenceHTTPClient
import tempfile
import os
import requests

load_dotenv()

app = Flask(__name__)

client = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key=os.getenv("ROBOFLOW_API_KEY")
)

@app.route("/detect", methods=["POST"])
def detect():

    print("API HIT")

    if "image" not in request.files:
        return jsonify({
            "success": False
        })

    image = request.files["image"]

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")

    image.save(temp_file.name)

    result = client.run_workflow(
        workspace_name="sr-banda",
        workflow_id="detect-count-and-visualize",
        images={
            "image": temp_file.name
        },
        use_cache=False
    )

    print("FULL RESULT:")
    print(result)

    has_person = False
    has_idcard = False

    try:

        predictions = []

        # CASE 1
        if isinstance(result, dict):

            predictions = result.get("predictions", [])

        # CASE 2
        elif isinstance(result, list):

            if len(result) > 0:

                first = result[0]

                if "predictions" in first:

                    if isinstance(first["predictions"], dict):

                        predictions = first["predictions"].get("predictions", [])

                    else:

                        predictions = first["predictions"]

        print("FINAL PREDICTIONS:")
        print(predictions)

        for item in predictions:

            cls = item.get("class")

            print("Detected:", cls)

            if cls == "Person":
                has_person = True

            if cls == "IDCard":
                has_idcard = True

        found = has_person and has_idcard

        print("FINAL RESULT:", found)

    except Exception as e:

        print("REAL ERROR:")
        print(e)

        found = False

    try:
        temp_file.close()
        os.unlink(temp_file.name)

    except Exception as e:
        print("DELETE ERROR:", e)

    return jsonify({
        "success": True,
        "id_card_detected": found
    })

if __name__ == "__main__":
    app.run(port=8000, debug=True)