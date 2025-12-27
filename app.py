from flask import Flask, request, send_file, jsonify
import subprocess
import os
import uuid

app = Flask(__name__)

@app.route("/api/srt")
def get_srt():
    video_id = request.args.get("id")
    if not video_id:
        return jsonify({"error": "missing id"}), 400

    temp_name = str(uuid.uuid4())
    output_file = f"{temp_name}.srt"

    cmd = [
        "yt-dlp",
        f"https://www.youtube.com/watch?v={video_id}",
        "--write-auto-subs",
        "--sub-format", "srt",
        "--skip-download",
        "-o", temp_name
    ]

    try:
        subprocess.run(cmd, check=True)
    except Exception as e:
        return jsonify({"error": "yt-dlp failed", "details": str(e)}), 500

    if not os.path.exists(output_file):
        return jsonify({"error": "no subtitles found"}), 404

    return send_file(output_file, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

