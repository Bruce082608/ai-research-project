#!/bin/bash
# 远程 GPU 机器环境体检。本地用法（PowerShell，项目根目录）：
#   scp 03_实验/remote/check_env.sh autodl:/root/autodl-tmp/ ; ssh autodl bash /root/autodl-tmp/check_env.sh
source /root/autodl-tmp/env.sh 2>/dev/null || export PATH=/root/miniconda3/bin:$PATH
echo "=== host ==="; hostname; grep PRETTY_NAME /etc/os-release; nproc; free -g | sed -n 2p
echo "=== gpu ==="; nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
echo "=== disk ==="; df -h / /root/autodl-tmp | tail -n +2
echo "=== python ==="; which python; python --version
python - <<'EOF'
import torch
print("torch", torch.__version__, "| cuda", torch.version.cuda, "| available", torch.cuda.is_available())
if torch.cuda.is_available():
    print("device", torch.cuda.get_device_name(0), "| bf16", torch.cuda.is_bf16_supported())
EOF
echo "=== key packages ==="
pip list 2>/dev/null | grep -iE "^(transformers|datasets|accelerate|peft|trl|numpy|pandas|scipy|matplotlib|vllm|flash[-_]attn|bitsandbytes|wandb|huggingface[-_]hub) " || echo "(none of the key packages found)"
echo "=== tools ==="; for t in tmux git nvcc htop rsync; do printf "%-6s %s\n" "$t" "$(command -v $t || echo MISSING)"; done
echo "=== HF env ==="; env | grep -E "^HF_|^http_proxy|^https_proxy" || echo "(no HF/proxy env set)"
