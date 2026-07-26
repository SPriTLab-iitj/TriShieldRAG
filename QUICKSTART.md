<a id="top"></a>

[Repo Home](README.md) · [Project Guide](PROJECT_GUIDE.md) · **Quickstart**

---

# Quickstart — RAG-Shield

Three ways to run it. **Demo** needs nothing. **Lite-Live** runs real local LLMs and is the recommended way to present. **Full-Live** is the heavy FAISS path.

## 0. One-time setup

Use **Python 3.11 or later** (3.9 breaks the install). On macOS: `brew install python@3.11`.

### macOS / Linux
```bash
cd <project-folder>
python3.11 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements-demo.txt   # demo deps (light)
```

### Windows (PowerShell)
You can run the automated script or run manual commands:
* **Automated Script:**
  ```powershell
  .\setup_project.ps1
  ```
* **Manual Commands:**
  ```powershell
  cd <project-folder>
  python -m venv .venv
  .\.venv\Scripts\python.exe -m pip install --upgrade pip
  .\.venv\Scripts\python.exe -m pip install -r requirements-demo.txt
  ```

## 1. Demo mode (instant, no keys, never crashes)

### macOS / Linux
```bash
DEMO_MODE=1 .venv/bin/python -m streamlit run frontend/app.py --server.port 8502
```

### Windows (PowerShell)
You can run the automated script or run manual commands:
* **Automated Script:**
  ```powershell
  .\run_demo.ps1
  ```
* **Manual Commands:**
  ```powershell
  $env:DEMO_MODE="1"
  .\.venv\Scripts\python.exe -m streamlit run .\frontend\app.py --server.port 8502
  ```

Open **http://localhost:8502**. Sidebar pages:
Attack Demo → Side-by-Side → Defense Demo → Forensic Explorer → Results Dashboard.

### Terminal check (CLI)
* **macOS / Linux:**
  ```bash
  DEMO_MODE=1 .venv/bin/python demo_cli.py "Who founded Tesla Motors?"
  ```
* **Windows (PowerShell):**
  ```powershell
  $env:DEMO_MODE="1"
  .\.venv\Scripts\python.exe .\demo_cli.py "Who founded Tesla Motors?"
  ```

Expected: ASR **~100% no-defense → ~0% with RAG-Shield**.

---

## 2. Lite-Live mode (real local LLMs — recommended for the live demo)

Real Ollama models answer in Ring 3, but a lightweight TF-IDF retriever is used
instead of torch/faiss — so it is **fast and does not segfault on Apple Silicon**.

```bash
# full deps (adds anthropic/openai clients; torch/faiss installed but NOT loaded in lite-live)
.venv/bin/python -m pip install -r requirements.txt

# pull 2-3 small local models for the Ring-3 panel
ollama pull llama3.2:3b && ollama pull phi4-mini && ollama pull gemma3:4b
ollama serve &            # leave running

# launch (the helper sets all Mac-safety env vars + watcher off)
./run_live.sh             # http://localhost:8502
```

`.env` for lite-live (local only, no paid API needed):
```
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=llama3.1:8b
OLLAMA_PANEL=llama3.2:3b,phi4-mini:latest,gemma3:4b
VLLM_BASE_URL=
```
No inline `#` comments on value lines — they break parsing.

Check what's live before presenting:
```bash
DEMO_MODE=0 .venv/bin/python backends_status.py
```

Watch real-time logs on a second screen:
```bash
./tail_logs.sh            # tails logs/ragshield.log
```

---

## 3. Full-Live mode (real FAISS + sentence-transformers)

Heavy path; can segfault on Apple Silicon. Only on a stable/Linux/GPU box:
```bash
DEMO_MODE=0 RETRIEVER=faiss .venv/bin/python -m streamlit run frontend/app.py --server.port 8502
```

---

## Notes

- **vLLM** needs an NVIDIA GPU; it will not run on a Mac. Use extra Ollama models for Ring 3.
- **Claude API** needs paid credits (separate from a Claude Pro subscription).
- After a restart, use the Streamlit "..." menu → **Clear cache** so old answers don't linger.

## What runs where

| Command | What it does |
|---------|--------------|
| `DEMO_MODE=1 ... streamlit run frontend/app.py` | demo mode UI (mock LLMs) |
| `./run_live.sh` | lite-live UI (real local LLMs, watcher off, port 8502) |
| `./tail_logs.sh` | live log feed for a second screen |
| `backends_status.py` | ping each backend, show LIVE/DOWN |
| `demo_cli.py "<question>"` | one-question terminal demo |
| `evaluation/run_experiments.py` | full ASR table |

---

[Repo Home](README.md) · [Project Guide](PROJECT_GUIDE.md) · **Quickstart**

[↑ Back to top](#top)
