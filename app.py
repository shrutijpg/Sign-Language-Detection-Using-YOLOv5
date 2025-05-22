import sys,os
from signLanguage.utils.main_utils import decodeImage, encodeImageIntoBase64
from flask import Flask, request, jsonify, render_template,Response
from flask_cors import CORS, cross_origin
import glob # Ye naya import add karein
import shutil # Ye naya import add karein

app = Flask(__name__)
CORS(app)

class ClientApp:
    def __init__(self):
        self.filename = "inputImage.jpg"
        # Ek fixed output folder naam define karein
        self.output_folder_name = "my_yolov5_output" 

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=['POST','GET'])
@cross_origin()
def predictRoute():
    try:
        image = request.json['image']
        decodeImage(image, clApp.filename)

        # 1. Purane output folder ko saaf karein agar exist karta hai
        # Har prediction ke liye naya folder banane ki bajaye, ek fixed folder ko clean kar denge
        output_dir_path = f"yolov5/runs/detect/{clApp.output_folder_name}"
        if os.path.exists(output_dir_path):
            shutil.rmtree(output_dir_path)
            print(f"Cleaned up old output directory: {output_dir_path}")

        # 2. detect.py ko run karein --name aur --exist-ok flags ke saath
        # --name: YOLOv5 ko batata hai ki results ko is specific folder mein save kare
        # --exist-ok: Agar woh folder exist karta hai, toh use overwrite kare
        os.system(f"cd yolov5/ && py detect.py --weights best.pt --img 416 --conf 0.5 --source ../data/{clApp.filename} --project runs/detect --name {clApp.output_folder_name} --exist-ok")

        # 3. Output image ko is fixed folder se read karein
        opencodedbase64 = encodeImageIntoBase64(f"{output_dir_path}/{clApp.filename}")
        result = {"image": opencodedbase64.decode('utf-8')}
        
        # 4. runs folder ko poora delete na karein. Sirf output_folder_name ko delete karein.
        # Aapne poora 'yolov5/runs' delete karne wali line ko hata diya hai, ya change kar diya hai.
        # Agar aap har baar naya result dekhna chahte hain aur disk space bachana chahte hain
        # toh upar wala shutil.rmtree(output_dir_path) hi kaafi hai.

    except ValueError as val:
        print(f"ValueError: {val}")
        return Response("Value not found inside json data", status=400)
    except KeyError:
        return Response("Key value error: incorrect key passed", status=400)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        result = "Invalid input or processing error"
        return Response(f"Server error: {e}", status=500)

    return jsonify(result)

@app.route("/live", methods=['GET'])
@cross_origin()
def predictLive():
    try:
        # Live detection mein aapko results save karne ki zaroorat nahi hoti hai
        # ya aapko uske liye alag logic likhna padega
        os.system("cd yolov5/ && py detect.py --weights best.pt --img 416 --conf 0.5 --source 0")
        # Live stream mein yahan 'runs' folder delete karna theek hai
        # agar aap output images save nahi kar rahe hain.
        os.system("rm -rf yolov5/runs") 
        return "Camera starting!!" 

    except ValueError as val:
        print(f"ValueError: {val}")
        return Response("Value not found inside json data", status=400)
    except Exception as e:
        print(f"An unexpected error occurred in live: {e}")
        return Response(f"Server error: {e}", status=500)


if __name__ == "__main__":
    clApp = ClientApp()
    app.run(host="0.0.0.0", port=8080)