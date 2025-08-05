#!/bin/bash

export http_proxy=""; export https_proxy=""; export no_proxy=""; export HTTP_PROXY=""; export HTTPS_PROXY=""; export NO_PROXY=""
while [ 1 -eq 1 ];do
    python3 mcps/run_web_research.py
done

wait;
