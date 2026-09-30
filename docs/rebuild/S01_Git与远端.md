# S01 · 本地 Git 建仓与推送 GitHub

> 状态：`[x] 已完成`

## 1. 目标

本地仓库关联 GitHub，并能持续 `commit` / `push`。

详解过程（必读）：[Git 使用全过程](../ops/git_workflow.md)

## 2. 前置

S00：`ssh -T git@github.com` 成功。

## 3. 操作

### 3.1 首次（历史已完成，新环境可对照）

```bash
cd /home/gaoql/eo_edge_media_platform
git remote -v
# origin  git@github.com:gaoqlcode/eo_edge_media_platform.git
```

若从零：

```bash
git init
git add .
git commit -m "chore(repo): 初始化平台仓库与复刻文档骨架"
git branch -M main
git remote add origin git@github.com:gaoqlcode/eo_edge_media_platform.git
git push -u origin main
```

### 3.2 日常

```bash
git status
git add <精确路径>
git commit -m "类型(范围): 中文说明"
git push origin HEAD
```

提交类型：`feat` / `fix` / `docs` / `refactor` / `test` / `chore`。  
改功能同步改 `docs/rebuild/Sxx` 状态。

## 4. 设计说明

- 主线 `main`；大改用 `feat/*` 分支。  
- **禁止**对 `main` force push。  
- 私钥与 `.env` 永不入库。

## 5. 验收

- [x] `git remote -v` 指向正确仓库  
- [x] GitHub 网页可见 README / docs / platform  
- [x] 能完成一次文档小改 push  
