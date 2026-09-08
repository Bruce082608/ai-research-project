# 本地 <-> 远程 GPU 机器同步（在项目根目录执行）
#   .\03_实验\remote\sync.ps1 push     # 本地 03_实验/code 与 remote/*.sh *.py -> 远程 /root/autodl-tmp/
#   .\03_实验\remote\sync.ps1 pull     # 远程 results/ logs/ -> 本地 03_实验/results, 03_实验/logs
#   .\03_实验\remote\sync.ps1 status   # 远程 GPU / tmux / 磁盘 一览
#   .\03_实验\remote\sync.ps1 shell    # 进入远程交互终端
param([Parameter(Mandatory)][ValidateSet("push","pull","status","shell")][string]$Action)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$Remote = "autodl"
$RDir = "/root/autodl-tmp"

function ToLF($paths) {
    # Windows 的 CRLF 会让远程 bash 报 "\r: command not found"，推送前统一为 LF
    foreach ($p in $paths) {
        $b = [IO.File]::ReadAllBytes($p)
        $s = [Text.Encoding]::UTF8.GetString($b) -replace "`r`n", "`n"
        [IO.File]::WriteAllBytes($p, [Text.Encoding]::UTF8.GetBytes($s))
    }
}

switch ($Action) {
    "push" {
        $scripts = Get-ChildItem "$Root\03_实验\remote" -Include *.sh,*.py -Recurse | % FullName
        ToLF $scripts
        scp -q ($scripts | ? { $_ -like "*.sh" }) "${Remote}:$RDir/"
        scp -q ($scripts | ? { $_ -like "*.py" }) "${Remote}:$RDir/code/"
        $codeFiles = @(Get-ChildItem "$Root\03_实验\code" -File -Recurse -ErrorAction SilentlyContinue)
        if ($codeFiles.Count -gt 0) {
            ToLF ($codeFiles | ? { $_.Extension -in ".sh",".py",".yaml",".yml",".json",".txt" } | % FullName)
            scp -q -r "$Root\03_实验\code\*" "${Remote}:$RDir/code/"
        } else { "(03_实验\code 为空，跳过)" }
        ssh $Remote "ls -la $RDir/code | head -20"
        "push done"
    }
    "pull" {
        New-Item -ItemType Directory -Force "$Root\03_实验\results", "$Root\03_实验\logs" | Out-Null
        scp -q -r "${Remote}:$RDir/results/*" "$Root\03_实验\results\" 2>$null
        scp -q -r "${Remote}:$RDir/logs/*"    "$Root\03_实验\logs\"    2>$null
        Get-ChildItem "$Root\03_实验\results" | Select Name, Length, LastWriteTime
        "pull done"
    }
    "status" {
        # 注意：PowerShell 会剥掉传给 ssh 的内层双引号，这里的远程命令避免使用任何引号
        ssh $Remote 'nvidia-smi --query-gpu=name,utilization.gpu,memory.used,memory.total --format=csv; echo; echo --- tmux ---; tmux ls 2>/dev/null || echo no_tmux_sessions; echo; echo --- disk ---; df -h /root/autodl-tmp | tail -1; echo; echo --- results ---; ls -la /root/autodl-tmp/results'
    }
    "shell" { ssh $Remote }
}
