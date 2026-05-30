# 01 — Local LLM Harnesses: Big Picture

Export ready: Yes
Local agent use: Top-level mental map of how a local model actually gets executed; lets the librarian explain why Ollama exists vs vLLM, llama.cpp, LM Studio, etc.
Notes: Foundational source page: harness landscape, where Ollama sits, what GGUF is, where STT lives.
Page type: Concept
Priority: High
Related concepts: Ollama Runtime Overview, Local Model Catalog (Small Models), Quantization and Why It Matters, FastAPI Service Layer, Speech-to-Text (Local STT)
Section: Foundations and Runtime
Source page number: 1
Status: Draft
Tags: api, architecture, library, local-models, models, ollama, runtime

# 01 — Local LLM Harnesses: Big Picture

## Why this matters

A "harness" is what actually runs the model on your machine. Raw model weights are just files on disk — without a harness they do nothing. For an offline mini PC assistant, the harness decision controls latency, RAM use, whether you can swap models, what languages can call the model, whether you get streaming, embeddings, and GPU support. A bad harness choice early locks the rest of the system into a stack that may not fit later.

## Mental model

Think of a harness as the engine bay around a raw model. The model is the engine block; the harness wires it up, gives it an API, manages memory, batches requests, and serves tokens.

There are three layers, and you should be able to name what plays which role in your stack:

- **Inference engine** (lowest level, C/C++ runners): llama.cpp, ggml, ExLlamaV2, vLLM, TensorRT-LLM
- **Runtime / server** (HTTP API, model lifecycle, swapping): Ollama, LM Studio, text-generation-webui, vLLM server, llamafile
- **Application framework** (router, tools, RAG): your FastAPI app, LangChain, LlamaIndex

On a mini PC, you want a CPU-friendly inference engine (llama.cpp), wrapped by a simple HTTP runtime (Ollama), called from your own thin framework (FastAPI). That separation is the whole game.

## How this fits into my mini PC assistant

- **Ollama / local model runtime**: Ollama is the harness. It is llama.cpp underneath, plus a model registry and an HTTP API on port 11434.
- **FastAPI dashboard**: FastAPI sits *above* the harness. It calls Ollama's API and decides which model and which skill to use.
- **Local file search / indexing**: Ollama also exposes an embeddings endpoint, so you do not need a second model server just for vectors.
- **Notion export / offline memory**: The harness determines how easy it is to swap models when re-indexing exported Markdown. Ollama makes this a config change, not a code change.
- **Local voice notes / STT**: STT runs in a different harness (whisper.cpp or faster-whisper). Do not conflate it with the LLM harness.

## Key terms

- **GGUF**: file format from llama.cpp that packages quantized model weights plus metadata for CPU/GPU inference.
- **Quantization**: storing weights at fewer bits per number (Q4_K_M, Q5_K_M, Q8_0) so the model fits in RAM.
- **Inference engine**: lowest layer that runs the forward passes (llama.cpp, vLLM, ExLlamaV2).
- **Runtime / server**: layer that exposes an HTTP API and manages model loading (Ollama, LM Studio, vLLM server).
- **Context window**: how many tokens the model can hold at once (2K, 4K, 8K, 32K, 128K).
- **KV cache**: per-session memory the model accumulates during generation; often dominates RAM use after weights.
- **Batching**: combining multiple requests in one forward pass for throughput; matters more on GPU servers than on a personal mini PC.

## Recommended v1 approach

- Use **Ollama** as the LLM harness. It is the simplest path to a working HTTP-served local model.
- Do not try to run **vLLM**, **TGI**, or **text-generation-webui** on a weak mini PC for v1.
- Keep **STT** in a separate harness (whisper.cpp or faster-whisper) — different problem, different process.
- Put **FastAPI** on top of Ollama as the orchestration layer; it talks to `http://localhost:11434`.
- Treat the harness as boring and stable. Iteration happens in FastAPI and the librarian, not in the harness.

## Tools / libraries

| Tool | Role | Use now or later |
| --- | --- | --- |
| Ollama | LLM harness / server, wraps llama.cpp | Now |
| llama.cpp | Underlying CPU/GPU inference engine | Indirectly via Ollama |
| LM Studio | GUI harness, useful for browsing and comparing models | Optional side tool |
| llamafile | Single-binary harness; nice for portability tests | Optional experiment |
| vLLM | High-throughput GPU server | Later, if a GPU is added |
| ExLlamaV2 | Fast GPU inference (older ecosystem) | Later, niche |
| text-generation-webui | Multi-backend Web UI | Skip for v1 |
| faster-whisper | STT harness (CTranslate2 backend) | Now, separate process |
| whisper.cpp | CPU STT harness | Now, separate process |

## Risks / failure modes

- Picking a harness without an HTTP API forces tight Python coupling and breaks the FastAPI separation.
- Choosing a GPU-only harness on a CPU-only mini PC: it will not even load.
- Pulling huge unquantized models without checking RAM: OOM at load time.
- Running two harnesses for the same role: confusing state, hard to log, hard to debug.
- Letting the harness do too much (routing, RAG, tool calls): blurs responsibility that should live in your FastAPI router.
- Auto-updates silently changing model behavior between runs.

## First hands-on experiment

1. Install Ollama on the mini PC.
2. Pull two models:
    
    ```
    ollama pull llama3.2:3b-instruct-q4_K_M
    ollama pull qwen2.5:7b-instruct-q4_K_M
    ```
    
3. Hit the API directly with curl:
    
    ```
    curl http://localhost:11434/api/generate -d '{
      "model": "qwen2.5:7b-instruct-q4_K_M",
      "prompt": "Summarize: Ollama is a local LLM runtime.",
      "stream": false
    }'
    ```
    
4. Watch `htop` and `free -h` during generation; note RAM use and tokens/sec.
5. Repeat with both models loaded back-to-back and observe swap behavior.

## What success looks like

- You can explain in two sentences why you chose Ollama over vLLM, LM Studio, and a raw llama.cpp binary.
- You can name the three layers (engine, runtime, framework) and place every tool in your stack into one of them.
- You can swap the assistant's default model by changing one config value, without touching FastAPI code.
- You stop thinking of "the model" and start thinking of "the model + harness + config" as one unit.

## Related pages

- 02 — Ollama Runtime Overview
- 03 — Local Model Catalog (Small Models)
- 04 — Quantization and Why It Matters
- 04 — FastAPI Service Layer
- 22 — Speech-to-Text (Local STT)

## Librarian Metadata

```yaml
topic: Local LLM Harnesses: Big Picture
status: draft
priority: High
page_type: Concept
tags:
  - harness
  - runtime
  - ollama
  - llama.cpp
  - gguf
  - architecture
related_concepts:
  - Ollama Runtime Overview
  - Local Model Catalog (Small Models)
  - Quantization and Why It Matters
  - FastAPI Service Layer
  - Speech-to-Text (Local STT)
local_agent_use: Use as the top-level mental map when a user asks how local model execution works, or compares Ollama, llama.cpp, vLLM, LM Studio, and llamafile.
source_section: Foundations and Runtime
good_for_questions_like:
  - What is a local LLM harness?
  - Why are we using Ollama instead of vLLM or LM Studio?
  - What does llama.cpp do under the hood?
  - Where does whisper fit in this picture?
  - What is GGUF?
summary_for_librarian: Three-layer mental model (inference engine, runtime, application framework) for how local models actually run, with Ollama on llama.cpp as the v1 choice and FastAPI as the orchestration layer above it.
```