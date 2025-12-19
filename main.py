from flask import Flask, request, jsonify, send_file
import yt_dlp
import uuid
import os

app = Flask(__name__)

BASE_DIR = "files"
os.makedirs(BASE_DIR, exist_ok=True)

@app.route("/download", methods=["POST"])
def download():
    data = request.json
    url = data.get("url")

    if not url:
        return jsonify(success=False, error="URL não fornecida")

    video_id = str(uuid.uuid4())
    output = f"{BASE_DIR}/{video_id}.mp4"

    ydl_opts = {
        "format": "mp4",
        "outtmpl": output,
        "quiet": True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        return jsonify(success=False, error=str(e))

    return jsonify(
        success=True,
        file=f"/file/{video_id}"
    )

@app.route("/file/<video_id>")
def file(video_id):
    path = f"{BASE_DIR}/{video_id}.mp4"
    if not os.path.exists(path):
        return "Arquivo não encontrado", 404

    return send_file(path, mimetype="video/mp4")

if __name__ == "__main__":
    app.run()
