import os
import uuid
import sqlite3
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
import qrcode

app = Flask(__name__, template_folder="templates", static_folder="static")

# ================= CONFIG =================
BASE_URL = os.environ.get("BASE_URL", "")

UPLOAD_FOLDER = 'static/uploads'
QR_FOLDER = 'static/qrcodes'
DB_FOLDER = 'database'
DB_PATH = os.path.join(DB_FOLDER, 'qr_records.db')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(QR_FOLDER, exist_ok=True)
os.makedirs(DB_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['QR_FOLDER'] = QR_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# ================= DB =================
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    db = get_db()
    db.execute('''
        CREATE TABLE IF NOT EXISTS qr_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uid TEXT,
            original_name TEXT,
            stored_name TEXT,
            qr_path TEXT
        )
    ''')
    db.commit()
    db.close()

init_db()

# ================= ROUTES =================

@app.route('/')
def home():
    return render_template('index.html')


# 🔥 FILE QR
@app.route('/api/upload', methods=['POST'])
def upload():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({"error": "Empty filename"}), 400

        uid = str(uuid.uuid4())
        filename = secure_filename(file.filename)
        stored_name = uid + "_" + filename

        filepath = os.path.join(app.config['UPLOAD_FOLDER'], stored_name)
        file.save(filepath)

        base = BASE_URL if BASE_URL else request.host_url.rstrip("/")
        file_url = f"{base}/static/uploads/{stored_name}"

        qr_img = qrcode.make(file_url)
        qr_filename = uid + ".png"
        qr_path = os.path.join(app.config['QR_FOLDER'], qr_filename)
        qr_img.save(qr_path)

        db = get_db()
        db.execute(
            "INSERT INTO qr_records (uid, original_name, stored_name, qr_path) VALUES (?, ?, ?, ?)",
            (uid, filename, stored_name, qr_filename)
        )
        db.commit()
        db.close()

        return jsonify({
            "success": True,
            "qr_data": f"/static/qrcodes/{qr_filename}",
            "metadata": {
                "filename": filename,
                "url": file_url
            }
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 🔥 TEXT / LINK QR (IMPORTANT FIX)
@app.route('/api/text', methods=['POST'])
def text_qr():
    try:
        data = request.get_json()
        text = data.get("text")

        if not text:
            return jsonify({"error": "No text provided"}), 400

        uid = str(uuid.uuid4())
        qr_img = qrcode.make(text)

        qr_filename = uid + ".png"
        qr_path = os.path.join(app.config['QR_FOLDER'], qr_filename)
        qr_img.save(qr_path)

        return jsonify({
            "success": True,
            "qr_data": f"/static/qrcodes/{qr_filename}"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/history')
def history():
    db = get_db()
    rows = db.execute("SELECT * FROM qr_records ORDER BY id DESC").fetchall()
    db.close()

    data = []
    for r in rows:
        data.append({
            "filename": r["original_name"],
            "qr": f"/static/qrcodes/{r['qr_path']}"
        })

    return jsonify(data)


@app.route('/api/stats')
def stats():
    return jsonify({"status": "ok"})


# ================= RUN =================
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)