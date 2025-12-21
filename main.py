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
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4",
        "outtmpl": output,
        "quiet": True,
        "merge_output_format": "mp4",

        # 🔥 CONTORNO REAL DO BLOQUEIO
        "extractor_args": {
            "youtube": {
                "player_client": ["android", "ios"],
                "skip": ["dash", "hls"]
            }
        },

        # 🔥 SIMULA APP MÓVEL
        "user_agent": (
            "Mozilla/5.0 (Linux; Android 11; Pixel 5) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Mobile Safari/537.36"
        ),

        # 🔥 ESSENCIAL EM DATACENTER
        "force_ipv4": True,

        # estabilidade
        "noplaylist": True,
        "retries": 5,
        "fragment_retries": 5,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        msg = str(e)
        if "Sign in to confirm you’re not a bot" in msg:
            return jsonify(
                success=False,
                error="❌ Este vídeo exige login no YouTube e não pode ser baixado."
            )
        return jsonify(success=False, error=msg)

    return jsonify(success=True, file=f"/file/{video_id}")

@app.route("/file/<video_id>")
def file(video_id):
    path = f"{BASE_DIR}/{video_id}.mp4"
    if not os.path.exists(path):
        return "Arquivo não encontrado", 404

    return send_file(path, mimetype="video/mp4")

if __name__ == "__main__":
    app.run(debug=True)
