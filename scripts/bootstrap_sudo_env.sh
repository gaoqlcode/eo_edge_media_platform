#!/usr/bin/env bash
# 文件：scripts/bootstrap_sudo_env.sh
# 内容：需本机输入一次 sudo 密码，安装 Docker 等系统包（可选企业栈）
set -euo pipefail
echo "将安装：docker.io docker-compose redis-tools curl"
sudo apt-get update
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y \
  docker.io docker-compose-plugin docker-compose \
  redis-tools curl netcat-openbsd || \
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y \
  docker.io docker-compose redis-tools curl netcat

sudo service docker start || sudo systemctl start docker || true
sudo usermod -aG docker "${USER}" || true

echo
echo "Docker 版本："
docker --version || sudo docker --version
echo
echo "拉起 Compose（可能需重新登录以使 docker 组生效，或用 sudo docker）："
cd "$(dirname "$0")/.."
sudo docker compose -f platform/infra/docker-compose.yml up -d || \
  docker compose -f platform/infra/docker-compose.yml up -d

echo "完成。若 docker 权限不足，先执行：newgrp docker 或重新打开终端。"
