# 03 — Local Model Catalog (Small Models)

Export ready: Yes
Local agent use: Lookup table the router uses to map task class to a specific local model variant.
Notes: Catalogs small local models considered or used (e.g., Llama 3 8B, Qwen, Phi, Mistral) with size, speed, and use case.
Page type: Reference
Priority: High
Related concepts: Local LLM Harnesses: Big Picture, Ollama Runtime Overview, Quantization and Why It Matters, Model Selection Rules, Local File Search and Indexing, Speech-to-Text (Local STT), Experiments Log
Section: Foundations and Runtime
Source page number: 3
Status: Draft
Tags: embeddings, llama, local-models, mistral, models, ollama, phi, qwen

# 03 — Local Model Catalog (Small Models)

*Source title: Small Model Selection for Weak Hardware*

## Why this matters

A mini PC typically has 8–32 GB of RAM and often no discrete GPU. The wrong model gives you an unusable assistant — too slow, OOMing, or simply dumb. The right small model gives you a genuinely capable instant local assistant. Most of the perceived quality and speed of the whole system is downstream of this choice.

## Mental model

Pick by four axes, in this order:

1. **Size after quantization** (e.g., 7B at Q4 ≈ 4.5 GB weights + KV cache).
2. **Instruction-tuned vs base** — almost always want Instruct/Chat.
3. **License** — fine for personal/family use, but worth knowing.
4. **Latency on your hardware** — measured in tokens/sec on *your* CPU, not a marketing chart.

Rule of thumb on CPU-only mini PC:

- **3B at Q4** = snappy, good for routing and light tasks.
- **7–8B at Q4** = usable as the main chat model.
- **13B at Q4** = sluggish, only if patience allows.
- **30B+** = forget it on CPU.

Size the job to the model, not the other way around:

- **Tiny (1–3B)**: classification, intent detection, routing, light summarization.
- **Small (7–8B)**: main chat, RAG synthesis, code help.
- **Embedding (~100M–300M)**: just for vector index.

## How this fits into my mini PC assistant

- **Ollama / local model runtime**: the catalog is literally a list of `ollama pull` tags.
- **FastAPI router**: uses model name per skill (router classify → 3B; full answer → 7B–8B).
- **Local file search / indexing**: a dedicated embedding model (`nomic-embed-text`, `mxbai-embed-large`) — not your chat model.
- **Notion export / offline memory**: the embedding model choice locks the vector index format. Switching means re-indexing everything.
- **Local voice notes / STT**: separate, but Whisper has its own size ladder (tiny / base / small / medium) — same principle.

## Key terms

- **Parameter count** (1B, 3B, 7B, 8B): rough model capacity.
- **Instruction-tuned / Instruct / Chat**: post-training to follow instructions; default choice.
- **Base model**: raw pretrained, harder to prompt — usually not what you want.
- **Q4_K_M / Q5_K_M / Q8_0**: quantization levels in GGUF.
- **Context window**: 4K, 8K, 32K, 128K — bigger contexts use more RAM via KV cache.
- **Tokens/sec (t/s)**: throughput measured on your actual hardware.
- **MoE (mixture of experts)**: model architecture where only some parameters activate per token; can give bigger "effective" models with lower active RAM.

## Recommended v1 approach

- **Routing / classify**: `llama3.2:3b-instruct-q4_K_M` — fast, good enough at structured outputs.
- **Main chat**: `qwen2.5:7b-instruct-q4_K_M` — strong general reasoning, good tool-use behavior.
- **Tiny intent / yes-no**: `llama3.2:1b-instruct-q4_K_M` or `phi3.5:3.8b-mini-instruct-q4_K_M`.
- **Code (when needed)**: `qwen2.5-coder:7b-instruct-q4_K_M`.
- **Embeddings**: `nomic-embed-text` (768-dim) for v1. Consider `mxbai-embed-large` later if retrieval quality matters.
- Avoid 13B+ on CPU-only mini PC for v1.
- Treat the catalog as a config file, not as code. The router reads model names from config.

## Tools / libraries

| Tool | Role | Use now or later |
| --- | --- | --- |
| Llama 3.2 3B Instruct (q4_K_M) | Router / classifier model | Now |
| Qwen2.5 7B Instruct (q4_K_M) | Main chat model | Now |
| Qwen2.5-Coder 7B Instruct (q4_K_M) | Code-focused tasks | Later |
| Phi-3.5 Mini 3.8B Instruct | Alternative small model with strong reasoning | Optional |
| Llama 3.2 1B Instruct | Tiny intent / yes-no model | Optional |
| Mistral 7B Instruct v0.3 | Fallback chat model | Optional |
| Gemma 2 9B Instruct | Higher-quality option (heavier) | Later |
| nomic-embed-text | Default embedding model | Now |
| mxbai-embed-large | Higher-quality embedding model | Later |
| Whisper tiny / base / small | STT, sized similarly | Now (separate) |

## Risks / failure modes

- Picking a research-only-licensed model for a personal/family tool: usually fine, but document it.
- Mixing embedding models without re-indexing: cosine garbage and silently bad retrieval.
- Choosing a 32K-context model and always allocating it: wastes RAM you do not need.
- Using **base** (non-Instruct) variants and wondering why the model ignores instructions.
- Relying on random community fine-tunes without checking their quantization quality.
- Letting the chat model also do routing: slow, expensive, and you cannot reason about cost.
- Picking by leaderboard score rather than tokens/sec on your actual mini PC.

## First hands-on experiment

1. Pull three models:
    
    ```
    ollama pull llama3.2:3b-instruct-q4_K_M
    ollama pull qwen2.5:7b-instruct-q4_K_M
    ollama pull phi3.5:3.8b-mini-instruct-q4_K_M
    ```
    
2. Define five prompts:
    - Summarize a Markdown file.
    - Classify a query as `chat | search | voice | other`.
    - Write a small Python snippet.
    - Follow a multi-step instruction.
    - Refuse a malformed or ambiguous request.
3. Run each prompt through each model. Record tokens/sec, RAM use, and a subjective 1–5 quality score.
4. Log results in the Experiments Log and pick your default chat + router models.

## What success looks like

- You can name your default chat model, router model, and embedding model from memory.
- You can defend each pick on RAM, tokens/sec, and observed quality on *your* hardware.
- You can switch the default chat model by changing one config value.
- The router does not call the 7B model for tasks the 3B model can handle.

## Related pages

- 01 — Local LLM Harnesses: Big Picture
- 02 — Ollama Runtime Overview
- 04 — Quantization and Why It Matters
- 08 — Model Selection Rules
- 18 — Local File Search and Indexing
- 22 — Speech-to-Text (Local STT)
- 29 — Experiments Log

## Librarian Metadata

```yaml
topic: Small Model Selection for Weak Hardware
status: draft
priority: High
page_type: Reference
tags:
  - models
  - llama
  - qwen
  - phi
  - mistral
  - gemma
  - embeddings
  - local-models
related_concepts:
  - Local LLM Harnesses: Big Picture
  - Ollama Runtime Overview
  - Quantization and Why It Matters
  - Model Selection Rules
  - Local File Search and Indexing
  - Speech-to-Text (Local STT)
  - Experiments Log
local_agent_use: Use to recommend a specific model + quant for a given task (routing, chat, code, embeddings) under known RAM/CPU constraints on a mini PC.
source_section: Foundations and Runtime
good_for_questions_like:
  - Which model should I use as the main chat model on a mini PC?
  - What is a good router/classifier model?
  - Which embedding model should I use for indexing exported Notion pages?
  - Why is the assistant slow when I switched to a 13B model?
  - What is the difference between an Instruct and a base model?
summary_for_librarian: Pick by size-after-quant, Instruct vs base, license, and tokens/sec on your CPU. v1 defaults: Llama 3.2 3B Instruct for routing, Qwen2.5 7B Instruct for chat, nomic-embed-text for embeddings. Avoid 13B+ on CPU-only.
```