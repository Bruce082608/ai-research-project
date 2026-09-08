#!/bin/bash
# 远程 GPU 机器一次性初始化（可重复执行，幂等）。本地用法（PowerShell，项目根目录）：
#   scp 03_实验/remote/setup.sh autodl:/root/autodl-tmp/ ; ssh autodl bash /root/autodl-tmp/setup.sh
set -e
export PATH=/root/miniconda3/bin:$PATH   # 非交互式 ssh 不会加载 conda，需显式加入

echo "=== 1. 数据盘目录 ==="
mkdir -p /root/autodl-tmp/{code,models,data,logs,results,hf_cache}
ls /root/autodl-tmp

echo "=== 2. 环境变量（HF 镜像 + 缓存放数据盘） ==="
# 独立成 env.sh：.bashrc 在非交互式 shell（ssh 直接执行命令、tmux 内）会提前 return，
# 所以 run_bg.sh 等脚本必须能单独 source 这个文件。
cat > /root/autodl-tmp/env.sh <<'EOF'
export PATH=/root/miniconda3/bin:$PATH
export HF_ENDPOINT=https://hf-mirror.com
export HF_HOME=/root/autodl-tmp/hf_cache
export HF_XET_HIGH_PERFORMANCE=1
export TOKENIZERS_PARALLELISM=false
export PYTHONUNBUFFERED=1
alias gpu='watch -n 2 nvidia-smi'
EOF
sed -i '/# >>> research-env >>>/,/# <<< research-env <<</d' ~/.bashrc
grep -q "autodl-tmp/env.sh" ~/.bashrc || echo 'source /root/autodl-tmp/env.sh' >> ~/.bashrc
source /root/autodl-tmp/env.sh
echo "HF_ENDPOINT=$HF_ENDPOINT  HF_HOME=$HF_HOME"

echo "=== 3. 系统工具 ==="
if ! command -v tmux >/dev/null; then
  apt-get update -qq && apt-get install -y -qq tmux >/dev/null
fi
tmux -V

echo "=== 4. Python 依赖 ==="
# 该机房访问阿里云/清华镜像返回 403，pypi.org 很慢；实测腾讯云镜像正常
pip config set global.index-url https://mirrors.cloud.tencent.com/pypi/simple >/dev/null
pip config set global.trusted-host mirrors.cloud.tencent.com >/dev/null
pip install -q -U pip
pip install -q transformers datasets accelerate peft huggingface_hub \
               pandas scipy scikit-learn tqdm pyyaml jsonlines evaluate
pip list 2>/dev/null | grep -iE "^(torch|transformers|datasets|accelerate|peft|huggingface[-_]hub|pandas|scipy) "

echo "=== 5. 自动关机辅助脚本 ==="
cat > /root/autodl-tmp/shutdown_when_done.sh <<'EOF'
#!/bin/bash
# 用法：bash shutdown_when_done.sh <PID>   —— 等该进程结束后 2 分钟自动关机，停止计费
while kill -0 "$1" 2>/dev/null; do sleep 30; done
sleep 120 && shutdown
EOF
chmod +x /root/autodl-tmp/shutdown_when_done.sh

echo "=== 6. 冒烟：GPU 上跑一次 bf16 矩阵乘 ==="
python - <<'EOF'
import torch, time
x = torch.randn(8192, 8192, device="cuda", dtype=torch.bfloat16)
torch.cuda.synchronize(); t = time.time()
for _ in range(20): y = x @ x
torch.cuda.synchronize(); dt = time.time() - t
print(f"bf16 matmul: {20*2*8192**3/dt/1e12:.1f} TFLOPS | peak mem {torch.cuda.max_memory_allocated()/1e9:.2f} GB")
EOF
echo "=== SETUP DONE ==="
