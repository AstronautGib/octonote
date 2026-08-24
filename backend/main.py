import uuid
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend import db
from backend.structure import structure_transcript
from backend.transcribe import transcribe_audio

UPLOAD_DIR = Path(__file__).parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {"wav", "mp3", "m4a", "ogg", "webm"}

app = FastAPI(title="VoiceDoc")

# Wide-open CORS is fine for a local demo project where frontend/index.html
# is opened directly (file://) or served from a different port than the API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    db.init_db()


class SaveNoteRequest(BaseModel):
    transcript: str
    note: dict


@app.post("/api/process")
async def process_audio(audio: UploadFile = File(...)):
    ext = audio.filename.rsplit(".", 1)[-1].lower() if "." in audio.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"Unsupported file type: .{ext}")

    saved_path = UPLOAD_DIR / f"{uuid.uuid4().hex}.{ext}"
    saved_path.write_bytes(await audio.read())

    try:
        transcript = transcribe_audio(str(saved_path))
        note = structure_transcript(transcript)
    except Exception as exc:
        raise HTTPException(500, str(exc)) from exc
    finally:
        saved_path.unlink(missing_ok=True)

    return {"transcript": transcript, "note": note}


@app.post("/api/notes")
def save_note(payload: SaveNoteRequest):
    note_id = db.save_note(payload.transcript, payload.note)
    return {"id": note_id}


@app.get("/api/notes")
def list_notes():
    return db.list_notes()


@app.get("/api/notes/{note_id}")
def get_note(note_id: int):
    note = db.get_note(note_id)
    if note is None:
        raise HTTPException(404, "Note not found")
    return note
