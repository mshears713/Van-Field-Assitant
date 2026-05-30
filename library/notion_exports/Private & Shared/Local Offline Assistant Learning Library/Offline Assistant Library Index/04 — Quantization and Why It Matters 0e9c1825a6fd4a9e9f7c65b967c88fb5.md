# 04 — Quantization and Why It Matters

Export ready: Yes
Local agent use: Lets the librarian explain quant tags (Q4_K_M, Q5_K_M, Q8_0), predict file size and RAM, and pick the right quant per task and hardware.
Notes: Foundational source page: how quantization makes 7B-class models fit on a mini PC, and which level to use.
Page type: Concept
Priority: High
Related concepts: Local LLM Harnesses: Big Picture, Ollama Runtime Overview, Local Model Catalog (Small Models), Model Selection Rules, Experiments Log
Section: Foundations and Runtime
Source page number: 4
Status: Draft
Tags: comparisons, experiments, local-models, models, ollama

# 04 — Quantization and Why It Matters

## Why this matters

Quantization is what makes 7B-class models fit on a mini PC at all. It is the single biggest knob between "this model will not load" and "this model is fast enough to use." Get it wrong and the assistant either OOMs at load, runs too slowly to use, or quietly degrades to bad answers. Get it right and a mid-range mini PC runs a capable assistant in real time.

## Mental model

Original training weights are 16-bit floats (FP16), sometimes 32-bit (FP32). A 7B model at FP16 weighs about 14 GB. The same model at Q4 weighs around 4.5 GB. Quantization rounds those weights down to fewer bits per number.

Lower bits = smaller file, less RAM, faster on CPU — but more quality loss.

Modern **K-quants** (Q4_K_M, Q5_K_M) are not naive: they spend more bits on "important" weights (e.g., attention) and fewer on the rest. Quality holds up surprisingly well, especially at Q4_K_M and above. Below Q4, quality drops are noticeable on real tasks.

Rule of thumb on a CPU-only mini PC:

- Q8_0: near-lossless, half the size of FP16. Good for small models.
- Q5_K_M / Q6_K: quality-leaning sweet spot if RAM allows.
- Q4_K_M: balanced default.
- Q3 / Q2: emergency only. Real quality drop.

## How this fits into my mini PC assistant

- **Ollama / local model runtime**: every Ollama tag carries a quant suffix (`:q4_K_M`, `:q5_K_M`, `:q8_0`). It is how you pick quant in practice.
- **FastAPI dashboard**: irrelevant at the API surface, but quant determines per-call latency the router has to plan around.
- **Local file search / indexing**: embedding models are usually quantized less aggressively (often FP16 or Q8); they are small enough that aggressive quant is not worth the quality risk.
- **Local voice notes / STT**: Whisper has its own quant story (int8 in CTranslate2 / faster-whisper). Same idea, different ecosystem.
- **Git safety / rollback**: always log the exact quant tag alongside the model name. Different quant = different behavior. Treat (model, quant) as one identity.

## Key terms

- **FP16 / BF16 / FP32**: float precisions used during training and full-precision inference.
- **Q8_0**: 8-bit, near-lossless, roughly half the size of FP16.
- **Q5_K_M**: 5-bit "K-quant medium" — strong quality/size balance.
- **Q4_K_M**: 4-bit medium — common sweet spot on CPU.
- **Q3_K_S / Q2_K**: very aggressive quants with visible quality drop.
- **K-quant**: llama.cpp's family of mixed-bit quantizations.
- **GGUF**: container format that holds the quantized weights and metadata.
- **Perplexity (PPL)**: standard language-modeling quality measure; higher = worse.
- **AWQ / GPTQ / EXL2**: GPU-oriented quantizations from a different ecosystem (vLLM, ExLlama).

## Recommended v1 approach

- **Default: Q4_K_M** for every chat model on the mini PC.
- Step up to **Q5_K_M** or **Q6_K** if the model is the bottleneck and RAM allows.
- Use **Q8_0** only for tiny models (1B–3B), where the size cost is small and you get near-full quality.
- Avoid Q2 and Q3 for the main chat or code model.
- For embedding models, take whatever the publisher recommends; FP16 is usually fine.
- Always record the full tag (e.g., `qwen2.5:7b-instruct-q4_K_M`) when logging experiments.

## Tools / libraries

| Tool | Role | Use now or later |
| --- | --- | --- |
| GGUF format | Quantized weight container used by llama.cpp / Ollama | Now |
| Ollama tags (e.g. :q4_K_M) | How you actually select a quant in practice | Now |
| llama.cpp quantize | Build custom quants from a base model | Later |
| Hugging Face GGUFs (TheBloke, unsloth, lmstudio-community) | Sources of pre-quantized weights | Reference |
| llama-bench | Benchmark tokens/sec across quants | Optional |
| AWQ / GPTQ / EXL2 | GPU-side quant formats for vLLM / ExLlama | Later |

## Risks / failure modes

- Pulling Q8 of a 7B model thinking it is "better" and hitting OOM at load.
- Comparing two models at different quants and blaming the model for quality differences caused by the quant.
- Re-quantizing arbitrarily and losing reproducibility — always log the exact tag.
- Assuming Q4_K_M is fine for code: for code, Q5_K_M or Q6_K is usually worth the RAM if available.
- Forgetting that KV cache stacks on top of weight size; long context can blow past the headroom quantization gave you.
- Mixing quant levels between dev and prod runs.

## First hands-on experiment

1. Pull the same model at three quant levels:
    
    ```
    ollama pull qwen2.5:7b-instruct-q4_K_M
    ollama pull qwen2.5:7b-instruct-q5_K_M
    ollama pull qwen2.5:7b-instruct-q8_0
    ```
    
2. Run the same five prompts on each (summarize, classify, follow a multi-step instruction, write a small Python snippet, refuse a malformed request).
3. Record for each: file size on disk, RAM use during generation, tokens/sec, subjective quality.
4. Log results in the Experiments Log.
5. Pick a default quant for the assistant based on the table you produced.

## What success looks like

- You can predict file size and rough RAM use from a quant tag alone.
- You can explain why Q4_K_M is your default and when you would deviate.
- You can defend a step up to Q5_K_M for code or a step down for a router model.
- Every model in production is logged with its exact quant tag in the model catalog.

## Related pages

- 01 — Local LLM Harnesses: Big Picture
- 02 — Ollama Runtime Overview
- 03 — Local Model Catalog (Small Models)
- 08 — Model Selection Rules
- 29 — Experiments Log

## Librarian Metadata

```yaml
topic: Quantization and Why It Matters
status: draft
priority: High
page_type: Concept
tags:
  - quantization
  - gguf
  - q4_K_M
  - q5_K_M
  - q8_0
  - k-quant
  - models
related_concepts:
  - Local LLM Harnesses: Big Picture
  - Ollama Runtime Overview
  - Local Model Catalog (Small Models)
  - Model Selection Rules
  - Experiments Log
local_agent_use: Use to translate quant tags (Q4_K_M, Q5_K_M, Q8_0) into expected file size, RAM use, speed, and quality, and to recommend a quant per task.
source_section: Foundations and Runtime
good_for_questions_like:
  - What does Q4_K_M mean?
  - Why does my 7B model use ~4.5 GB instead of 14 GB?
  - Should I use Q4 or Q5 for code generation?
  - Why is my model OOMing at load?
  - What is GGUF and how does it relate to quantization?
summary_for_librarian: Quantization stores weights at fewer bits per number so 7B-class models fit on a mini PC. Q4_K_M is the default; Q5_K_M / Q6_K for quality-leaning use; Q8_0 only for tiny models. Always log the exact quant tag.
```