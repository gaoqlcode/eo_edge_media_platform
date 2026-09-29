# S01 · 本地 Git 建仓与推送 GitHub

> 状态：`[~] 进行中`

## 1. 目标

本地仓库初始化，关联 GitHub 空仓并完成首次推送。

## 2. 前置

- S00 中 `ssh -T git@github.com` 已成功  

## 3. 操作

```bash
cd /home/gaoql/eo_edge_media_platform
git init
git add .
git commit -m "chore(repo): 初始化平台仓库与复刻文档骨架"
git branch -M main
git remote add origin git@github.com:gaoqlcode/eo_edge_media_platform.git
git push -u origin main
```

若 `remote` 已存在：`git remote set-url origin git@github.com:gaoqlcode/eo_edge_media_platform.git`

## 4. 关键设计

`main` 为稳定线；后续用 `phase/*`、`feat/*` 分支开发（见 `docs/ops/git_workflow.md`）。

## 5. 验收

- [ ] `git log -1` 有首提交  
- [ ] `git remote -v` 指向 `gaoqlcode/eo_edge_media_platform.git`  
- [ ] GitHub 网页能看到 README / docs / platform 等文件  
