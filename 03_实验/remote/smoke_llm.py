"""端到端冒烟：HF 镜像下载小模型 -> GPU bf16 推理 -> 写 JSON 结果。
远程用法：python /root/autodl-tmp/code/smoke_llm.py
"""
import json, os, time, platform
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL = os.environ.get("SMOKE_MODEL", "Qwen/Qwen2.5-0.5B")
OUT = "/root/autodl-tmp/results/smoke_llm.json"

t0 = time.time()
tok = AutoTokenizer.from_pretrained(MODEL)
model = AutoModelForCausalLM.from_pretrained(MODEL, dtype=torch.bfloat16).cuda().eval()
t_load = time.time() - t0

prompt = "The capital of France is"
ids = tok(prompt, return_tensors="pt").to("cuda")
torch.cuda.synchronize(); t1 = time.time()
with torch.no_grad():
    out = model.generate(**ids, max_new_tokens=32, do_sample=False)
torch.cuda.synchronize(); t_gen = time.time() - t1
text = tok.decode(out[0][ids["input_ids"].shape[1]:], skip_special_tokens=True)

res = {
    "model": MODEL,
    "n_params_M": round(sum(p.numel() for p in model.parameters()) / 1e6, 1),
    "load_s": round(t_load, 2),
    "gen_32tok_s": round(t_gen, 3),
    "tok_per_s": round(32 / t_gen, 1),
    "peak_mem_GB": round(torch.cuda.max_memory_allocated() / 1e9, 2),
    "output": text,
    "env": {
        "gpu": torch.cuda.get_device_name(0),
        "torch": torch.__version__,
        "cuda": torch.version.cuda,
        "python": platform.python_version(),
        "hf_endpoint": os.environ.get("HF_ENDPOINT"),
    },
}
os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(res, open(OUT, "w"), indent=2, ensure_ascii=False)
print(json.dumps(res, indent=2, ensure_ascii=False))
