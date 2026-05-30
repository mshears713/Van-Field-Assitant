# Local Offline Assistant Learning Library

# Local Offline Assistant Learning Library

A long-term knowledge library that teaches me how to build and operate a local/offline mini PC assistant. This library is designed to be exported to Markdown and later read by a small local librarian agent running on a mini PC.

## Purpose

This library teaches me how to build and operate a local/offline mini PC assistant using Ollama, small local models, FastAPI, local file search, Notion exports, voice notes, speech-to-text, Git safety, routing, and a phone-accessible dashboard.

It serves two audiences:

1. **Human reader (me)** — a readable, structured learning library.
2. **Future local librarian agent** — a machine-readable knowledge store that can search, classify, summarize, and route through the exported pages.

## Design Principles

- Keep structure simple and Markdown-export friendly.
- Prefer headings, bullets, tables, and code blocks.
- Avoid fancy Notion-only layouts that may not export cleanly.
- Each child page should read as a normal standalone document.
- Each child page must include a small **Librarian Metadata** section so a future local model can search, classify, summarize, and route.
- Do not over-condense technical details.
- Do not turn this into generic AI advice.
- Preserve implementation-specific details, model names, tool names, risks, and experiments.

## Librarian Metadata Block (template for child pages)

Every child page should end with a metadata block like this:

```yaml
---
librarian_metadata:
  page_title: "<exact page title>"
  section: "<one of: Foundations and Runtime | Routing and Control | Safety, Change Control, and Testing | Knowledge, Speech, and Interface | Security, MVP, Glossary, and Experiments>"
  page_type: "<conceptual | implementation | reference | experiment>"
  priority: "<High | Medium | Low>"
  tags: ["tag1", "tag2"]
  summary: "<one or two sentence summary>"
  related_pages: ["<title>", "<title>"]
  last_reviewed: "<YYYY-MM-DD>"
---
```

## Pilot Export v0.1 Test

A first export dry-run using four completed pages from the Foundations and Runtime section.

**Pages included**

- 01 — Local LLM Harnesses: Big Picture
- 02 — Ollama Runtime Overview
- 03 — Local Model Catalog (Small Models)
- 04 — Quantization and Why It Matters

**What this export is testing**

- Whether the four page bodies render cleanly as standalone Markdown after Notion export.
- Whether the Librarian Metadata YAML block survives the export intact as plain text inside a fenced code block.
- Whether the database CSV export captures the matching properties (Section, Priority, Page type, Status, Tags, Local agent use, Related concepts, Notes, Export ready) so the local librarian can join body and metadata.
- Whether these four pages are usable as a small seed corpus for the local mini PC librarian program.

**Known issue**

- Duplicate page numbering exists in the index: `01` and `04` are each used twice (new pilot rows vs the original `01 — Mini PC Hardware and Local Environment` and `04 — FastAPI Service Layer`). This should be reviewed and renumbered **after** the export test, not before, so the export results stay traceable.

## Library Map

The library is organized into five sections. Each child page below is planned but not yet written. Build child pages one at a time later.

---

## 1. Foundations and Runtime

Core concepts and runtime pieces that the offline assistant depends on: the mini PC, Ollama, small local models, FastAPI, and the local environment.

| Done | Page Title | Purpose (one sentence) | Priority | Librarian Tags | Page Type |
| --- | --- | --- | --- | --- | --- |
| ☐ | 01 — Mini PC Hardware and Local Environment | Defines the target mini PC, OS, disk layout, and base environment the assistant runs on. | High | hardware, mini-pc, environment, runtime | reference |
| ☐ | 02 — Ollama Runtime Overview | Explains how Ollama runs local models, exposes its API, and is managed as a long-running service. | High | ollama, runtime, local-models, api | conceptual |
| ☐ | 03 — Local Model Catalog (Small Models) | Catalogs small local models considered or used (e.g., Llama 3 8B, Qwen, Phi, Mistral) with size, speed, and use case. | High | models, llama, qwen, phi, mistral, ollama | reference |
| ☐ | 04 — FastAPI Service Layer | Defines the FastAPI app that wraps Ollama and exposes assistant endpoints to other components. | High | fastapi, api, service-layer, python | implementation |
| ☐ | 05 — Python Environment and Dependencies | Tracks the Python version, virtualenv strategy, and pinned dependencies for the assistant stack. | Medium | python, venv, dependencies, pip, uv | reference |
| ☐ | 06 — Process Management and Auto-Start | Describes how Ollama, FastAPI, and helper services start on boot and recover from crashes. | Medium | systemd, services, autostart, supervisord | implementation |

---

## 2. Routing and Control

How requests are routed across models, tools, and skills; how the assistant decides what to do.

| Done | Page Title | Purpose (one sentence) | Priority | Librarian Tags | Page Type |
| --- | --- | --- | --- | --- | --- |
| ☐ | 07 — Router Architecture Overview | Explains the top-level router that classifies an incoming request and dispatches it to a model or skill. | High | router, architecture, dispatch, control | conceptual |
| ☐ | 08 — Model Selection Rules | Defines deterministic rules for picking which local model handles which kind of task. | High | routing, model-selection, rules, heuristics | implementation |
| ☐ | 09 — Tool and Skill Registry | Catalogs callable tools/skills (file search, notes, voice, dashboard actions) and their input/output contracts. | High | tools, skills, registry, contracts | reference |
| ☐ | 10 — Prompt and System Message Library | Stores reusable system prompts for the router, librarian, and specialized skills. | Medium | prompts, system-messages, library | reference |
| ☐ | 11 — Fallback and Degraded Modes | Describes what happens when a model is unavailable, slow, or returns low-confidence output. | Medium | fallback, resilience, degraded-mode | conceptual |

---

## 3. Safety, Change Control, and Testing

Guardrails, Git hygiene, dry runs, and testing patterns that keep the local stack stable.

| Done | Page Title | Purpose (one sentence) | Priority | Librarian Tags | Page Type |
| --- | --- | --- | --- | --- | --- |
| ☐ | 12 — Git Safety and Repository Layout | Defines repo structure, branch rules, and commit hygiene for the assistant codebase. | High | git, repo, branches, safety | implementation |
| ☐ | 13 — Backups, Snapshots, and Rollback | Documents how to back up models, code, configs, and knowledge, and how to roll back safely. | High | backups, snapshots, rollback, recovery | reference |
| ☐ | 14 — Dry Run and Human-in-the-Loop Patterns | Captures patterns for previewing agent actions before they touch real state. | High | dry-run, hitl, guardrails, preview | conceptual |
| ☐ | 15 — Local Testing Strategy | Defines how to test FastAPI endpoints, routing logic, and skills locally with small fixtures. | Medium | testing, pytest, fixtures, fastapi | implementation |
| ☐ | 16 — Observability and Local Logging | Describes logs, metrics, and traces produced by the assistant and how they are stored locally. | Medium | logging, observability, metrics, traces | implementation |
| ☐ | 17 — Failure Modes and Risk Register | Tracks known failure modes (OOM, model drift, disk full, bad routes) and mitigations. | Medium | risks, failures, mitigations, register | reference |

---

## 4. Knowledge, Speech, and Interface

Where the assistant gets its knowledge, how it listens and speaks, and how I interact with it.

| Done | Page Title | Purpose (one sentence) | Priority | Librarian Tags | Page Type |
| --- | --- | --- | --- | --- | --- |
| ☐ | 18 — Local File Search and Indexing | Explains how local files are indexed and queried (e.g., embeddings, BM25, hybrid search). | High | search, indexing, embeddings, bm25, rag | implementation |
| ☐ | 19 — Notion Export Pipeline | Documents how Notion pages are exported to Markdown and imported into the local library. | High | notion, export, markdown, pipeline | implementation |
| ☐ | 20 — Librarian Agent Design | Defines the small local agent that classifies, summarizes, and routes through exported pages. | High | librarian, agent, classification, summarization | conceptual |
| ☐ | 21 — Voice Notes Capture | Describes how voice notes are captured from phone or mic and queued for processing. | Medium | voice-notes, capture, audio, queue | implementation |
| ☐ | 22 — Speech-to-Text (Local STT) | Covers local STT options (e.g., whisper.cpp, faster-whisper) with model and quality notes. | High | stt, whisper, transcription, local | reference |
| ☐ | 23 — Phone-Accessible Dashboard | Defines the small dashboard (web UI) used to interact with the assistant from a phone on the LAN. | High | dashboard, phone, ui, lan | implementation |
| ☐ | 24 — Knowledge Library Structure on Disk | Maps how exported Markdown is organized on disk so the librarian can find it predictably. | Medium | filesystem, layout, markdown, library | reference |

---

## 5. Security, MVP, Glossary, and Experiments

Local security posture, the smallest useful version, shared vocabulary, and a place to log experiments.

| Done | Page Title | Purpose (one sentence) | Priority | Librarian Tags | Page Type |
| --- | --- | --- | --- | --- | --- |
| ☐ | 25 — Local Security Posture | Defines network exposure, auth, secrets handling, and update policy for the mini PC stack. | High | security, network, secrets, auth | conceptual |
| ☐ | 26 — Secrets and Config Management | Describes how API keys, tokens, and configs are stored and rotated locally. | Medium | secrets, config, env, rotation | implementation |
| ☐ | 27 — MVP Definition (v0.1) | Defines the smallest end-to-end working assistant and the cut line for v0.1. | High | mvp, scope, v0.1, milestones | conceptual |
| ☐ | 28 — Glossary of Terms | Shared vocabulary for the project (router, skill, librarian, dashboard, etc.). | Medium | glossary, vocabulary, definitions | reference |
| ☐ | 29 — Experiments Log | Running log of experiments with models, prompts, routing rules, and quantization choices. | Medium | experiments, log, evaluation, comparisons | experiment |
| ☐ | 30 — Open Questions and Future Work | Captures unresolved questions and future directions deferred past v0.1. | Low | questions, future, backlog | reference |

---

## How to use this hub

- Build child pages **one at a time**.
- Mark the **Done** box in the table when a child page is created and reviewed.
- Every child page must include the **Librarian Metadata** block at the end.
- Keep formatting export-friendly: headings, bullets, tables, code blocks.

## Librarian Metadata (this hub)

```yaml
---
librarian_metadata:
  page_title: "Local Offline Assistant Learning Library"
  section: "Hub"
  page_type: "reference"
  priority: "High"
  tags: ["hub", "index", "offline-assistant", "mini-pc", "ollama", "librarian"]
  summary: "Parent hub and map for the Local Offline Assistant Learning Library, organized into five sections of planned child pages."
  related_pages: []
  last_reviewed: "2026-05-28"
---
```

[Offline Assistant Library Index](Local%20Offline%20Assistant%20Learning%20Library/Offline%20Assistant%20Library%20Index%20096f44fc8d9b4e26b286645f8c92d380.csv)