# Git 使用全过程（企业学习版）

> 对应复刻：[S01_Git与远端](../rebuild/S01_Git与远端.md)  
> 远端：`git@github.com:gaoqlcode/eo_edge_media_platform.git`  
> 前置：SSH 已配好（见 [05 环境章 · SSH](../learning/05_环境软件下载与工具链.md) 与 [ssh_setup](./ssh_setup.md)）

## 1. 学习目标

- 理解工作区 / 暂存区 / 本地仓库 / 远端 四层  
- 独立完成：改文件 → 查看差异 → 暂存 → 提交 → SSH 推送  
- 遵守企业习惯：清晰 commit、同步文档、**不对 main 强推**

---

## 2. 概念详解

```text
你的编辑器改动的文件          = 工作区 (working tree)
git add 选中的快照            = 暂存区 (index / staging)
git commit 形成的历史节点     = 本地仓库 (local repo)
git push 同步到 GitHub        = 远端 (remote: origin)
```

- **commit**：不可变快照 + 说明文字 + 作者/时间。  
- **branch**：可移动的指针；本仓主线叫 `main`。  
- **SSH URL**：`git@github.com:OWNER/REPO.git`（本仓固定此方式，不用 HTTPS 密码）。

---

## 3. 安装 Git

```bash
sudo apt update
sudo apt install -y git
git --version
```

验收：打印出版本号即可。

---

## 4. 首次：克隆或绑定远端

### 4.1 已有本地目录（本项目常见）

```bash
cd /home/gaoql/eo_edge_media_platform
git remote -v
# 应看到 origin → git@github.com:gaoqlcode/eo_edge_media_platform.git
```

若没有 origin：

```bash
git remote add origin git@github.com:gaoqlcode/eo_edge_media_platform.git
# 或纠正 URL：
git remote set-url origin git@github.com:gaoqlcode/eo_edge_media_platform.git
```

### 4.2 空机器从零克隆

```bash
cd ~
git clone git@github.com:gaoqlcode/eo_edge_media_platform.git
cd eo_edge_media_platform
```

### 4.3 作者信息说明

企业机可能未配 `user.name`。本项目历史作者为 `gaoqlcode`。  
**不要擅自改全局 git config**（团队规范）；单次提交可用环境变量：

```bash
GIT_AUTHOR_NAME='gaoqlcode' GIT_AUTHOR_EMAIL='gaoqlcode@users.noreply.github.com' \
GIT_COMMITTER_NAME='gaoqlcode' GIT_COMMITTER_EMAIL='gaoqlcode@users.noreply.github.com' \
git commit -m "docs: 示例"
```

---

## 5. 日常闭环（必会）

```bash
cd /home/gaoql/eo_edge_media_platform

# 1) 看状态：改了哪些文件
git status

# 2) 看内容差异
git diff                 # 未暂存
git diff --staged        # 已暂存

# 3) 挑选文件进入暂存区（不要 git add . 盲目一把梭）
git add docs/learning/05_环境软件下载与工具链.md
# 切勿 add：.env、密码、大体积数据、密钥

# 4) 提交（信息要说清「为什么」）
git commit -m "$(cat <<'EOF'
docs(learning): 补充环境下载与工具链详解

便于新人按文档独立安装 apt/mamba/pip/docker。
EOF
)"

# 5) 推送到 GitHub
git push origin HEAD
# 或：git push -u origin main   （首次跟踪）
```

### 提交类型（约定）

| 前缀 | 含义 |
|------|------|
| `feat` | 新能力 |
| `fix` | 修缺陷 |
| `docs` | 仅文档 |
| `refactor` | 重构无行为变化 |
| `test` | 测试 |
| `chore` / `build` | 杂务 / 构建 |

示例：`feat(auth): 写接口支持 JWT 与 API Key 双模`

---

## 6. 分支工作流

```bash
# 从最新 main 拉功能分支
git checkout main
git pull origin main
git checkout -b docs/learning-05-toolchain

# ... 开发、commit ...

# 合并回 main（本仓小团队可用本地 merge）
git checkout main
git merge docs/learning-05-toolchain
git push origin main
```

说明：

- 学习期也可用直接在 `main` 上小步提交（本仓当前习惯），但**大改建议分支**。  
- **禁止**对 `main` 使用 `push --force`（除非负责人明确要求且知悉后果）。  
- `rebase -i` 需要交互，自动化环境易失败；教学默认 **merge**。

---

## 7. 与复刻文档联动（企业要求）

改功能时同步：

1. 改代码  
2. 改 `docs/rebuild/Sxx_*.md` 状态与验收勾选  
3. 必要时改 `docs/architecture/企业级成熟度.md`  
4. **同一个或紧挨着的 commit** 推送  

这样 GitHub 历史 = 可复刻说明书。

---

## 8. 常用只读命令

```bash
git log --oneline -10          # 最近提交
git log -1 --format='%h %an %s'
git show HEAD                  # 看某次改动
git branch -vv                 # 本地分支与跟踪
git status -sb                 # 短状态
```

---

## 9. 排错手册

| 现象 | 原因与处理 |
|------|------------|
| `Permission denied (publickey)` | SSH 未配置或未 `ssh-add`；先 `ssh -T git@github.com` |
| `rejected (non-fast-forward)` | 远端有你没有的提交：先 `git pull --rebase origin main` 或 `git pull` 再 push；冲突要手动解决 |
| `unknown option trailer` | 旧版 git 被包装器注入不支持参数；可用 `/usr/bin/git commit -F msgfile` |
| 误暂存大文件/密钥 | `git reset HEAD -- path`；若已 commit 未 push：用新 commit 删除文件，**勿把密钥留在历史** |
| 工作区很脏 | `git status` 分类处理；数据目录应在 `.gitignore` |

---

## 10. 两个实操剧本

### 剧本 A：只改文档（练手）

```bash
echo "" >> docs/learning/00_入学与复刻入口.md   # 或做有意义小改
git add docs/learning/00_入学与复刻入口.md
git commit -m "docs: 入学入口微调"
git push origin HEAD
# 打开 GitHub 网页确认文件已更新
```

### 剧本 B：改服务 + 文档 + 验证

```bash
# 改 platform/services/... 与 docs/rebuild/Sxx
bash scripts/e2e_test.sh          # 必须绿
git status
git add -p                        # 或精确 git add 路径
git commit -m "feat(service): ...\n\n同步 Sxx 验收。"
git push origin HEAD
```

---

## 11. 自测题

1. `git add` 与 `git commit` 各把数据推进哪一层？  
2. 为什么本仓坚持 SSH 而不是把 PAT 写进远程 URL？  
3. 改了 `device_service` 却不改 S08/成熟度文档，违反了哪条企业约定？  
4. `main` 被别人抢先推送后，你本地直接 `push` 失败，正确下一步是什么？  

答案要点：1）工作区→暂存；暂存→本地历史；2）密钥不进 URL/日志；3）文档与代码同演进；4）先 pull/合并再 push，禁 force。
