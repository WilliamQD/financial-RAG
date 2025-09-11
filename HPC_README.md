The goal of using HPC was to move the LLM part of the RAG to local, for better control of the models and more cost-efficient operations. 
There are three main Open-source libraries and inference runtimes we tried for deploying LLMs on the HPC:
1. Ollama
- Easy to use and serve, however, the runner had certain issue that could not be solved
2. Huggingface transformers
- Must have for downloading models (vllm use hf transformers inherently)
- Serving is still in the developvement phrase, expect incomplete functionalities and different output format from the server
- Diffcult to implement structured output, cases where the server simply did not adhere to the format
3. vLLM
- final choice, supports structured output with chat.completion
- no response api on their serve page

Notes related to GPT-OSS
- cu128, which is cuda 12.8 is a must have for it to run properly, this also controls the version of PyTorch
- According to their guide, with gpt-oss, response api can be used (better alignment with OpenAI's recent development direction)
- MXFP4 quantization requires triton >= 3.4.0, which requres Pytorch >= 2.8, which requires CUDA 12.6 at least (and we only had CUDA 12.4)
- With MXFP4 quantization, GPT-OSS-2Ob only requires >= 16GB VRAM, GPT-OSS-12Ob only requires >= 60GB, thus possible to fit in one single GPU (currently we default to bf16 which takes up a lot of VRAMS)
