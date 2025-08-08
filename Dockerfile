# base 阶段
FROM ubuntu:22.04 AS base
USER root
SHELL ["/bin/bash", "-c"]

# 定义构建参数以自定义构建过程
ARG NEED_MIRROR=${NEED_MIRROR}

# 设置工作目录
WORKDIR /lazyllm

ENV DEBIAN_FRONTEND=noninteractive

# 更新ubuntu apt
RUN --mount=type=cache,id=lazyllm_apt,target=/var/cache/lazyllm/apt,sharing=locked \
    if [ "$NEED_MIRROR" == "1" ]; then \
        sed -i 's|http://archive.ubuntu.com|https://mirrors.tuna.tsinghua.edu.cn|g' /etc/apt/sources.list; \
    fi; \
    rm -f /etc/apt/apt.conf.d/docker-clean && \
    echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' > /etc/apt/apt.conf.d/keep-cache && \
    chmod 1777 /tmp && \
    apt update && \
    apt --no-install-recommends install -y ca-certificates && \
    apt update

# apt-get安装应用
RUN --mount=type=cache,id=lazyllm_apt_app,target=/var/cache/lazyllm/apt_app,sharing=locked \
    apt install -y python3-pip python3.11-venv pipx nginx unzip curl wget git vim less telnet iputils-ping \
    libgl1 libglib2.0-0 libsm6 libxext6 libxrender1

# 安装uv
RUN --mount=type=cache,id=lazyllm_uv,target=/var/cache/lazyllm/uv,sharing=locked \
    if [ "$NEED_MIRROR" == "1" ]; then \
        pip3 config set global.index-url https://mirrors.aliyun.com/pypi/simple && \
        pip3 config set global.trusted-host mirrors.aliyun.com; \
        echo "[[index]]" > /etc/uv/uv.toml && \
        echo 'url = "https://mirrors.aliyun.com/pypi/simple"' >> /etc/uv/uv.toml && \
        echo "default = true" >> /etc/uv/uv.toml; \
    fi; \
    mkdir -p /etc/uv && \
    pipx install uv

ENV PYTHONDONTWRITEBYTECODE=1
ENV PATH=/root/.local/bin:$PATH

# builder 阶段
FROM base AS builder
USER root
WORKDIR /lazyllm

# uv下载python依赖包
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,id=lazyllm_uv_sync,target=/var/cache/lazyllm/uv_sync,sharing=locked \
    uv sync --python 3.11 --frozen --all-extras;

# production 阶段
FROM base AS production
USER root
WORKDIR /lazyllm

# 复制 Python 环境和包
ENV VIRTUAL_ENV=/lazyllm/.venv
COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}
ENV PATH="${VIRTUAL_ENV}/bin:${PATH}"

ENV PYTHONPATH=/lazyllm/

COPY entrypoint.sh ./entrypoint.sh
RUN chmod +x ./entrypoint.sh

COPY configs configs
COPY lazyllm lazyllm
COPY mcps mcps

ENTRYPOINT ["./entrypoint.sh"]