# QR Forge — QR Code Generator

A full-stack Python web application to generate QR codes for **Images**, **Word Documents**, **PDFs**, and **Videos**.

## 🗂️ Project Structure

```
qr_project/
├── app.py                  # Flask backend + REST API
├── requirements.txt        # Python dependencies
├── database/
│   └── qr_records.db       # SQLite database (auto-created)
├── templates/
│   └── index.html          # Frontend (HTML/CSS/JS)
└── static/
    ├── uploads/            # Uploaded files (auto-created)
    └── qrcodes/            # Saved QR images (auto-created)
```

## ⚙️ Tech Stack

| Layer      | Technology              |
|------------|-------------------------|
| Backend    | Python + Flask          |
| Database   | SQLite (via sqlite3)    |
| Frontend   | HTML5 + CSS3 + Vanilla JS |
| QR Render  | qrcodejs (client-side)  |
| Doc parse  | python-docx             |
| PDF parse  | pypdf                   |
| Images     | Pillow                  |

## 🚀 Setup & Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
python app.py

# 3. Open browser
http://localhost:5000
```

## 📡 REST API Endpoints

| Method | Endpoint              | Description                        |
|--------|-----------------------|------------------------------------|
| GET    | `/`                   | Main UI                            |
| POST   | `/api/upload`         | Upload file + generate QR data     |
| GET    | `/api/records`        | Get all records (filter: ?type=)   |
| GET    | `/api/record/<uid>`   | Get single record                  |
| DELETE | `/api/record/<uid>`   | Delete record + file               |
| GET    | `/api/stats`          | Count by type                      |

### Upload Request (POST /api/upload)
```
Content-Type: multipart/form-data
Fields:
  - file: <binary file>
  - file_type: "image" | "word" | "pdf" | "video"
```

### Upload Response
```json
{
  "success": true,
  "uid": "uuid-string",
  "file_type": "image",
  "original_name": "photo.jpg",
  "file_url": "/static/uploads/uuid.jpg",
  "qr_data": "{...json...}",
  "metadata": { "size_human": "120 KB", "dimensions": "1920x1080", ... },
  "created_at": "2024-01-01T12:00:00"
}
```

## 🗄️ Database Schema

```sql
CREATE TABLE qr_records (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  uid           TEXT    NOT NULL UNIQUE,
  file_type     TEXT    NOT NULL,          -- image|word|pdf|video
  original_name TEXT    NOT NULL,
  stored_name   TEXT    NOT NULL,
  file_size     INTEGER,
  file_path     TEXT    NOT NULL,
  qr_data       TEXT    NOT NULL,          -- JSON encoded QR content
  metadata      TEXT,                      -- JSON encoded file metadata
  created_at    TEXT    NOT NULL
);
```

## 🎯 Features

- **4 Separate Sections** — Image, Word, PDF, Video each with their own upload zone
- **Drag & Drop** — Drop files directly onto the upload zone
- **Auto Metadata Extraction** — Dimensions for images, page count for PDFs, word count for docs
- **QR Generation** — Client-side QR codes using qrcodejs
- **Download QR** — Save QR as PNG
- **History Panel** — Browse all generated QR codes with filter tabs
- **Delete Records** — Remove files and DB records
- **Stats Bar** — Live counts by file type
- **Modal Preview** — Click any history card to see QR + metadata

## 📦 Supported File Types

| Type  | Extensions                          |
|-------|-------------------------------------|
| Image | .png, .jpg, .jpeg, .gif, .webp, .bmp |
| Word  | .doc, .docx                         |
| PDF   | .pdf                                |
| Video | .mp4, .avi, .mov, .mkv, .webm, .flv |

## 📝 Notes

- Max upload size: 100 MB
- QR codes encode the file's public URL
- SQLite DB auto-created on first run
- Upload and QR folders auto-created on first run
