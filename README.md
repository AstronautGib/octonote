# VoiceDoc
 
An AI-assisted tool that turns a spoken nursing shift report into a structured clinical note. Automatically transcribing the audio, then organizing it into a reviewable, editable chart entry.
 
Inspired by how much time nurses spend on manual charting, this project explores a "human-in-the-loop" approach to AI-assisted documentation: the AI drafts a structured note from a voice recording, but a nurse always reviews and edits before anything is saved.
 
> **This is a portfolio/demo project, not a real clinical tool.** It is not HIPAA-compliant, has not been validated for clinical use, and should never be used with real patient data. All sample data in this repo is synthetic.
 
## How it works
 
1. **Record or upload audio** of a spoken shift report (e.g. "Patient in stable condition, BP 120/80, reports mild headache, given 500mg Tylenol at 2pm...")
2. **Transcription** — the audio is transcribed locally using [faster-whisper](https://github.com/SYSTRAN/faster-whisper)
3. **Structuring** — the transcript is sent to the **Claude API**, which extracts it into a structured note (vitals, subjective complaints, actions taken, plan/follow-up) via a forced tool call built directly from [`schema.json`](schema.json) — so the response is guaranteed to match the schema rather than parsed out of free text
4. **Review** — the structured draft is shown side-by-side with the original transcript so it can be corrected before saving
5. **Save** — the finalized note is stored locally in SQLite

## Tech stack
 
| Layer | Tool |
|---|---|
| Speech-to-text | faster-whisper (local, open-source) |
| Note structuring | Claude API (tool use / function calling) |
| Backend | FastAPI (Python) |
| Database | SQLite |
| Frontend | HTML / CSS / JavaScript |

Transcription runs fully locally; structuring is the one call that leaves your machine, via the Claude API.
 
## Setup
 
### Prerequisites
- Python 3.10+
- An Anthropic API key from [console.anthropic.com](https://console.anthropic.com) — structuring a single note costs a fraction of a cent
 
### Installation
```bash
git clone https://github.com/<your-username>/voicedoc.git
cd voicedoc
python -m venv venv
source venv/bin/activate  # on Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# then edit .env and paste in your ANTHROPIC_API_KEY
```
 
### Running
```bash
# start the backend
uvicorn backend.main:app --reload

# open frontend/index.html in your browser
```
 
## Demo
 
*(I will add a screenshot or short GIF here once the UI is working)*
 
## Project scope
 
**In scope (v1):**
- Upload or record audio → transcript
- Transcript → structured JSON note via Claude tool use
- Editable review screen before saving
- Local SQLite storage of past entries

**Out of scope / future work:**
- Real EHR integration
- Multi-user authentication/roles
- Real-time/streaming transcription

## Why this project

Built to explore practical AI applications in healthcare documentation, with a deliberate focus on responsible design — the AI drafts, but a human always verifies before anything is finalized. It's also a small showcase of the Claude API's tool-use feature: `schema.json` is the single source of truth for the note's shape, reused directly as the tool's `input_schema` so structuring stays reliable as the schema evolves.
 
## License
 
MIT — see [LICENSE](LICENSE).