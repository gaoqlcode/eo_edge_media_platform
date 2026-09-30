#!/usr/bin/env bash
# 文件：scripts/encode_session_h264.sh
# 内容：将会话 JPEG 序列软编为 H.264（需本机 ffmpeg）；RK3588 可改为 MPP
# 用法：bash scripts/encode_session_h264.sh data/sessions/<session>/cam0
set -euo pipefail
DIR="${1:?用法: $0 <jpeg_dir>}"
OUT="${2:-${DIR%/}/preview.h264.mp4}"
if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "缺少 ffmpeg：sudo apt install -y ffmpeg"
  exit 1
fi
# %d.jpg 命名；edge_agent 写 0.jpg 1.jpg ...
ffmpeg -y -framerate 5 -i "${DIR}/%d.jpg" -c:v libx264 -pix_fmt yuv420p -an "${OUT}"
echo "OK ${OUT}"
ls -la "${OUT}"
