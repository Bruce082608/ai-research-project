#!/bin/bash
# 在 tmux 里后台运行一条命令，日志落盘，SSH 断开不影响；可选跑完自动关机。
# 远程用法（在 /root/autodl-tmp 下）：
#   bash run_bg.sh <任务名> [--shutdown] -- <命令...>
# 例：bash run_bg.sh mve_seed0 --shutdown -- python code/train.py --seed 0
# 查看：tmux attach -t <任务名>（Ctrl+B 再按 D 退出）；日志在 logs/<任务名>_<时间>.log
set -e
NAME="$1"; shift
SHUTDOWN=0
if [ "$1" = "--shutdown" ]; then SHUTDOWN=1; shift; fi
[ "$1" = "--" ] && shift
[ -z "$NAME" ] || [ $# -eq 0 ] && { echo "usage: bash run_bg.sh <name> [--shutdown] -- <cmd...>"; exit 1; }

LOG=/root/autodl-tmp/logs/${NAME}_$(date +%m%d_%H%M).log
CMD="$*"
INNER="source /root/autodl-tmp/env.sh; cd /root/autodl-tmp; echo \"[start \$(date)] $CMD\" | tee $LOG; $CMD 2>&1 | tee -a $LOG; echo \"[end \$(date)] exit=\${PIPESTATUS[0]}\" | tee -a $LOG"
if [ $SHUTDOWN -eq 1 ]; then
  INNER="$INNER; echo '[auto-shutdown in 120s]' | tee -a $LOG; sleep 120; shutdown"
fi
tmux new -d -s "$NAME" "$INNER"
echo "started tmux session '$NAME' ; log: $LOG"
echo "attach: tmux attach -t $NAME    | tail: tail -f $LOG"
