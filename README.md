# VoiceDoc
 
An AI-assisted tool that turns a spoken nursing shift report into a structured clinical note — automatically transcribing the audio, then organizing it into a reviewable, editable chart entry.
 
Inspired by how much time nurses spend on manual charting, this project explores a "human-in-the-loop" approach to AI-assisted documentation: the AI drafts a structured note from a voice recording, but a nurse always reviews and edits before anything is saved.
 
> **This is a portfolio/demo project, not a real clinical tool.** It is not HIPAA-compliant, has not been validated for clinical use, and should never be used with real patient data. All sample data in this repo is synthetic.
 
## How it works
 
1. **Record or upload audio** of a spoken shift report (e.g. "Patient in stable condition, BP 120/80, reports mild headache, given 500mg Tylenol at 2pm...")
2. **Transcription** — the audio is transcribed locally using [faster-whisper](https://github.com/SYSTRAN/faster-whisper)
3. **Structuring** — the transcript is sent to a local LLM (via [Ollama](https://ollama.com)) which extracts it into a structured note (vitals, subjective complaints, actions taken, plan/follow-up)
4. **Review** — the structured draft is shown side-by-side with the original transcript so it can be corrected before saving
5. **Save** — the finalized note is stored locally in SQLite
## Tech stack
 
| Layer | Tool |
|---|---|
| Speech-to-text | faster-whisper (local, open-source) |
| Note structuring | Ollama + local LLM (e.g. llama3.1:8b) |
| Backend | FastAPI (Python) |
| Database | SQLite |
| Frontend | HTML / CSS / JavaScript |
 
Everything runs **fully locally** — no paid APIs, no data leaving your machine.
 
## Setup
 
### Prerequisites
- Python 3.10+
- [Ollama](https://ollama.com) installed, with a model pulled:
```bash
  ollama pull llama3.1:8b
```
 
### Installation
```bash
git clone https://github.com/<your-username>/voicedoc.git
cd voicedoc
python -m venv venv
source venv/bin/activate  # on Windows: venv\Scripts\activate
pip install -r requirements.txt
```
 
### Running
```bash
# start Ollama (if not already running)
ollama serve
 
# start the backend
uvicorn backend.main:app --reload
 
# open frontend/index.html in your browser
```
 
## Demo
 
*(Add a screenshot or short GIF here once the UI is working — this goes a long way for portfolio viewers who won't run the setup themselves.)*
 
## Project scope
 
**In scope (v1):**
- Upload or record audio → transcript
- Transcript → structured JSON note
- Editable review screen before saving
- Local storage of past entries
**Out of scope / future work:**
- Real EHR integration
- Multi-user authentication/roles
- Real-time/streaming transcription
## Why this project
 
Built to explore practical AI applications in healthcare documentation, with a deliberate focus on responsible design — the AI drafts, but a human always verifies before anything is finalized.
 
## License
 
MIT — see [LICENSE](LICENSE).