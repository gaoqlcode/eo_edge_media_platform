# Git 本地工作流

## 日常

```bash
git status
git add <文件>
git commit -m "类型(范围): 中文简述"
git push          # 需要已配置 SSH 与 origin
```

## 分支

```bash
git checkout -b phase/1-docs
git checkout -b feat/device-service-crud
# 完成后合并回 main
git checkout main
git merge feat/device-service-crud
git push
```

## 提交类型

`feat` / `fix` / `docs` / `refactor` / `test` / `chore` / `build`

## 与复刻文档

改功能时同步改 `docs/rebuild/Sxx_*.md` 状态标记，再 commit。

## 远端

```text
origin  git@github.com:gaoqlcode/eo_edge_media_platform.git
```
