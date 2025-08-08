#!/bin/bash

# 清除代理设置
export http_proxy=""
export https_proxy=""
export no_proxy=""
export HTTP_PROXY=""
export HTTPS_PROXY=""
export NO_PROXY=""

BASE_PORT=${PORT:-10001}
function task_exe(){
    while [ 1 -eq 1 ]; do
        python3 "$@"
    done
}

port0=$((BASE_PORT + 0))
task_exe mcps/run_web_research.py --port $port0 &

port1=$((BASE_PORT + 1))
task_exe mcps/run_example.py --port $port1 &

wait