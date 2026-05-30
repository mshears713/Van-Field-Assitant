# 02 — Ollama Runtime Overview

Export ready: Yes
Local agent use: Tells the librarian how the local model server runs and how to reach it via HTTP.
Notes: Explains how Ollama runs local models, exposes its API, and is managed as a long-running service.
Page type: Concept
Priority: High
Related concepts: Local LLM Harnesses: Big Picture, Local Model Catalog (Small Models), Quantization and Why It Matters, FastAPI Service Layer, Process Management and Auto-Start, Local File Search and Indexing, Local Security Posture
Section: Foundations and Runtime
Source page number: 2
Status: Draft
Tags: api, embeddings, local-models, ollama, runtime, systemd

# 02 — Ollama Runtime Overview

## Why this matters

Ollama is the runtime that decides whether models load at all, swap cleanly, and respond fast enough on a mini PC. It is the single dependency that every other component — router, dashboard, librarian, indexer — talks to for LLM calls. If Ollama behavior is opaque to you, the whole assistant is opaque.

## Mental model

Ollama is a small local HTTP server (default port `11434`) plus a model store.

- You `ollama pull` model **tags** (e.g., `llama3.2:3b-instruct-q4_K_M`).
- Models live as quantized GGUF files under `~/.ollama/models`.
- On request, Ollama loads the model into RAM (and VRAM if available), runs llama.cpp under the hood, and streams tokens back over HTTP.
- It keeps recently used models warm via a **keep-alive** window (default 5 minutes).
- It also exposes an **embeddings** endpoint, so you do not need a second server for vectors.

Mental shortcut: "Ollama is llama.cpp with a registry and an HTTP API."

## How this fits into my mini PC assistant

- **Local model runtime**: Ollama *is* the runtime. Every chat or generation call goes here.
- **FastAPI dashboard**: FastAPI backends call `POST /api/generate` or `POST /api/chat`. The dashboard never talks to Ollama directly.
- **Local file search / indexing**: use `POST /api/embeddings` with an embedding model (e.g., `nomic-embed-text`). No second server needed.
- **Notion export / offline memory**: the same embedding endpoint indexes exported Markdown.
- **Phone-accessible UI**: the dashboard speaks HTTP to Ollama over `localhost`; do **not** expose port 11434 to the LAN or the phone.
- **Process management**: Ollama should run as a long-lived service that auto-starts on boot.

## Key terms

- **Tag**: model name + variant, e.g., `qwen2.5:7b-instruct-q4_K_M`.
- **Modelfile**: a text file that defines a custom model (base + system prompt + parameters), built with `ollama create`.
- **keep_alive**: how long a model stays in RAM after last use (e.g., `"30m"`, `"0"`, `"-1"` for indefinite).
- **num_ctx**: context window allocated for a request (more tokens = more RAM via KV cache).
- **num_gpu**: number of layers offloaded to GPU (`0` for CPU-only).
- **temperature / top_p / top_k / mirostat**: sampling parameters per request.
- **Embeddings endpoint**: `POST /api/embeddings` returns a vector for a piece of text.

## Recommended v1 approach

- Run Ollama as a **systemd** service that auto-starts on boot.
- Pin a small, named set of models:
    - one small chat (3B, e.g., `llama3.2:3b-instruct-q4_K_M`)
    - one main chat (7B–8B, e.g., `qwen2.5:7b-instruct-q4_K_M`)
    - one embedding model (e.g., `nomic-embed-text`)
- Always pass `keep_alive: "30m"` for the hot model to avoid cold-load latency.
- Bind Ollama to `127.0.0.1` only. FastAPI is the only client.
- Disable auto-update; pin versions so behavior does not drift silently.
- Use **Modelfiles** to bake in system prompts for named "skill models" (e.g., `router-v1`, `librarian-v1`).

## Tools / libraries

| Tool | Role | Use now or later |
| --- | --- | --- |
| Ollama | Local LLM + embeddings server | Now |
| ollama-python | Python client; optional, curl works fine too | Now |
| curl / HTTPie | Manual API testing and debugging | Now |
| Modelfile + ollama create | Define custom skill models with baked-in prompts | Now |
| ollama ps | List loaded models and their RAM/VRAM use | Now |
| nomic-embed-text | Default embedding model | Now |
| systemd unit for ollama | Auto-start and restart on failure | Now |

## Risks / failure modes

- Two clients loading different large models at once: heavy swap to disk, severe slowdown or OOM.
- Forgetting `keep_alive`: cold-load latency on every request (5–30 s).
- Pulling a model larger than available RAM: load fails or thrashes.
- Letting Ollama auto-update: silent behavior changes between versions and quants.
- Exposing `11434` on the LAN: anyone can drain compute, leak prompts, or pull unexpected models.
- Mixing embedding models without re-indexing: vector space mismatch, garbage results.
- Long `num_ctx` requests blowing RAM via KV cache even when weights fit.

## First hands-on experiment

1. Time three requests against `llama3.2:3b-instruct-q4_K_M`:
    - request A with `keep_alive: "0"` (force unload after)
    - request B with `keep_alive: "30m"`
    - request C immediately after B
2. Run `ollama ps` between requests to see what is loaded.
3. Repeat with `num_ctx: 8192` and watch RAM jump vs the default.
4. Try `POST /api/embeddings` with `nomic-embed-text` on a paragraph of exported Notion content and inspect the vector length.

## What success looks like

- You can read `ollama ps` output and predict whether the next call will be fast or cold.
- You can write a Modelfile that pins a system prompt + sampling parameters for a named skill model.
- You can swap the assistant's default chat model by changing one config value, not code.
- Ollama is bound to [localhost](http://localhost) only, runs under systemd, and survives reboots without manual steps.

## Related pages

- 01 — Local LLM Harnesses: Big Picture
- 03 — Local Model Catalog (Small Models)
- 04 — Quantization and Why It Matters
- 04 — FastAPI Service Layer
- 06 — Process Management and Auto-Start
- 18 — Local File Search and Indexing
- 25 — Local Security Posture

## Librarian Metadata

```yaml
topic: Ollama Runtime Overview
status: draft
priority: High
page_type: Concept
tags:
  - ollama
  - runtime
  - local-models
  - api
  - embeddings
  - systemd
related_concepts:
  - Local LLM Harnesses: Big Picture
  - Local Model Catalog (Small Models)
  - Quantization and Why It Matters
  - FastAPI Service Layer
  - Process Management and Auto-Start
  - Local File Search and Indexing
  - Local Security Posture
local_agent_use: Use to answer how local models are served, how to call the Ollama HTTP API, how keep_alive and num_ctx affect latency and RAM, and how to expose embeddings.
source_section: Foundations and Runtime
good_for_questions_like:
  - How does Ollama actually serve models?
  - Why is my first request always slow?
  - How do I make a custom skill model with a baked-in system prompt?
  - Should I expose port 11434 to the LAN?
  - How do I get embeddings out of Ollama?
summary_for_librarian: Ollama is a small local HTTP server (port 11434) over llama.cpp that pulls and runs GGUF models, exposes chat/generate/embeddings endpoints, manages model lifecycle with keep_alive, and should run under systemd bound to localhost.
```