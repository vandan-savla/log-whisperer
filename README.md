## Log Whisperer

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20|%203.11%20|%203.12%20|%203.13-blue)
[![OS](https://img.shields.io/badge/OS-Windows%20|%20macOS%20|%20Linux-555)](#)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)


Log Whisperer is a CLI-first assistant that helps you explore, summarize, and reason about application logs through a conversational interface. Point it at a log file, ask questions, and iterate quickly.

This project uses LangChain under the hood and supports multiple LLM providers (OpenAI, Anthropic, Google, Groq), configurable via a simple guided setup. Conversations are optionally saved so you can resume later.

---

### Quick links

[![Configure](https://img.shields.io/badge/Step%201-Configure-blue?logo=terminal)](#-configuration) [![Start Chat](https://img.shields.io/badge/Step%202-Start%20Chat-green?logo=gnu-bash)](#-quickstart) [![Status](https://img.shields.io/badge/Status-Check-informational?logo=gnometerminal)](#-commands)

---

### Demo

> Tip: Add your own screenshots or GIFs later under `docs/assets/` and replace the placeholders below.

<iframe width="560" height="315" src="docs/assets/log-whisperer%20demo%20video.mp4" frameborder="0" ></iframe>

<!-- ![Hero placeholder]() -->

---

### Features

- Conversational log analysis over any text log
- Local vector index (FAISS) for retrieval-augmented answers
- Provider-agnostic via LangChain: OpenAI, Anthropic, Google Gemini, Groq
- Persistent conversation history per-log for continuity
- Colorful, ergonomic CLI using `rich` and `click`

---

## Installation (local, editable)

No PyPI release yet. Install locally in editable mode for fast iteration.

#### 1) Clone

```bash
git clone https://github.com/vandan-savla/log-whisperer.git
cd log-whisperer
```

#### 2) Create and activate a virtual environment

- Windows (PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip setuptools wheel
```

- macOS/Linux (bash)

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip setuptools wheel
```

#### 3) Install the project in editable mode

Core installation:

```bash
pip install -e .
```

---

## Quickstart

Once installed, the `log-whisperer` command is available.

```bash
# 1) Configure your preferred provider and model
log-whisperer configure

# 2) Check configuration
log-whisperer status

# 3) Analyze a log file interactively; optionally save the conversation
log-whisperer chat --log-file /path/to/app.log --save ~/.log-whisperer/last-session.json
```

During configuration, you’ll be prompted for provider credentials and model. Supported providers are: 
- OpenAI: `OPENAI_API_KEY`
- Anthropic: `ANTHROPIC_API_KEY`
- Google: `GOOGLE_API_KEY`
- Groq: `GROQ_API_KEY`
---

## Commands

```bash
# Guided config flow (choose provider, model, and options)
log-whisperer configure

# Show current provider configuration
log-whisperer status

# Start an interactive session on a specific log file
log-whisperer chat --log-file /path/to/logfile.log --save path/to/convo.json

# Reset configuration (removes ~/.log-whisperer/config.yaml)
log-whisperer reset
```

Configuration is stored at `~/.log-whisperer/config.yaml`.

---

## Tips

- Use natural language questions like “What errors do you see?”, “Summarize main events”, “Any anomalies around 10:32?”
- Use `--save` to capture the conversation so you can resume context later.
- The first run on a large log may build a local vector index; subsequent runs will be faster.

---

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines, a suggested workflow, and development tips.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Acknowledgements

- Built with `click`, `rich`, and `LangChain`
- FAISS for local vector search; `sentence-transformers` for embeddings

---


