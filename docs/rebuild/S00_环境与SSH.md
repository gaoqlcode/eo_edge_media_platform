# S00 · 环境准备与 SSH 公钥

> 状态：`[x] 已完成`

## 1. 目标

本机（WSL）具备基础工具，并能用 SSH 访问 GitHub。

## 2. 前置

无。详解见学习章：[05_环境软件下载与工具链](../learning/05_环境软件下载与工具链.md)。

## 3. 操作

### 3.1 建议安装的工具

```bash
sudo apt update
sudo apt install -y \
  git build-essential cmake pkg-config \
  libjpeg-dev ffmpeg \
  python3 python3-venv python3-pip \
  docker.io docker-compose curl ca-certificates
```

额外：本仓可用 micromamba 起 PG（见 `scripts/start_infra_local.sh`），不必强依赖 Docker。

### 3.2 SSH 公钥

```bash
ssh-keygen -t ed25519 -C "gaoqlcode@github" -f ~/.ssh/id_ed25519 -N ""
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
cat ~/.ssh/id_ed25519.pub
```

GitHub：**Settings → SSH and GPG keys → New SSH key**。验证：`ssh -T git@github.com`。

Git 日常流程见：[Git 使用全过程](../ops/git_workflow.md)。

## 4. 设计说明

用 SSH 而非 HTTPS 密码；私钥永不入库。

## 5. 验收

- [x] `git --version` / `cmake --version` 可用  
- [x] SSH 认证 GitHub 成功  
- [x] （推荐）`libjpeg-dev` 已装，便于编 edge_agent  
