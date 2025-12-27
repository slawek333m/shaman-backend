from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import subprocess
import os
import uuid

app = Flask(__name__)
CORS(app)

@app.route("/api/srt")
def get_srt():
    video_id = request.args.get("id")
    if not video_id:
        return jsonify({"error": "missing id"}), 400

    temp_name = str(uuid.uuid4())
    output_file = f"{temp_name}.srt"

    base_cmd = [
        "yt-dlp",
        f"https://www.youtube.com/watch?v={video_id}",
        "--sub-format", "srt",
        "--skip-download",
        "-o", temp_name
    ]

    # 1️⃣ Próba auto-napisów
    cmd_auto = base_cmd + ["--write-auto-subs"]

    # 2️⃣ Próba ręcznych napisów
    cmd_manual = base_cmd + ["--write-subs"]

    # LOG
    print("▶️ START: Pobieranie napisów dla:", video_id)

    # AUTO
    try:
        print("▶️ Próbuję auto-napisy:", " ".join(cmd_auto))
        subprocess.run(cmd_auto, check=True, capture_output=True)
    except subprocess.CalledProcessError as e1:
        print("⚠️ Auto-napisy nie znalezione, próbuję ręczne:", " ".join(cmd_manual))

        # MANUAL
        try:
            subprocess.run(cmd_manual, check=True, capture_output=True)
        except subprocess.CalledProcessError as e2:
            print("❌ yt-dlp failed:", e2.stderr.decode())
            return jsonify({
                "error": "yt-dlp failed",
                "details": e2.stderr.decode()
            }), 500

    # Sprawdzenie czy plik powstał
    if not os.path.exists(output_file):
        print("❌ Nie znaleziono pliku SRT:", output_file)
        return jsonify({"error": "nie znaleziono napisów"}), 404

    print("✅ Sukces! Wysyłam plik:", output_file)
    return send_file(output_file, as_attachment=True)


# ===============================
#  URUCHOMIENIE NA RENDERZE
# ===============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
