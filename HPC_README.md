# HPC README

**Goal**
Move the LLM component of the RAG pipeline onto **HPC** for better model control and lower cost.

---

## Open-source libraries & runtimes tested

1. **Ollama**

   * Easy to use and serve.
   * Blocked by unresolved runner issues on our cluster.

2. **Hugging Face Transformers**

   * Essential for downloading models (vLLM uses HF Transformers under the hood).
   * Serving is still in the development phase; expect incomplete functionality and output-format differences.
   * Structured output was difficult; the server sometimes did not adhere to the requested format.

3. **vLLM** *(final choice)*

   * Supports structured output via **chat completions**.
   * No **Responses API** exposed on the server.

---

## Notes on GPT-OSS

* **cu128 (CUDA 12.8)** is required for stable runs; this also dictates the compatible **PyTorch** version.
* Per their guide, GPT-OSS supports a **Responses API** (aligns with OpenAI’s recent direction).
* **MXFP4 quantization** needs **Triton ≥ 3.4.0 → PyTorch ≥ 2.8 → CUDA ≥ 12.6** (we only had CUDA 12.4).
* With **MXFP4**:

  * **GPT-OSS-2Ob** requires **≥16 GB VRAM**
  * **GPT-OSS-12Ob** requires **≥60 GB VRAM**
  * Both can fit on a single GPU. We currently default to **bf16**, which uses more VRAM.
