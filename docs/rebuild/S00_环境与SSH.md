# S00 · 环境准备与 SSH 公钥

> 状态：`[x] 已完成`

## 1. 目标

本机（WSL）具备基础工具，并能用 SSH 访问 GitHub。

## 2. 前置

无。

## 3. 操作

### 3.1 建议安装的工具

```bash
sudo apt update
sudo apt install -y git build-essential cmake python3 python3-venv python3-pip docker.io docker-compose-v2 curl
```

（若包名因发行版不同略有差异，以能运行为准并在本页 `[!]` 记录。）

### 3.2 SSH 公钥（本机已生成示例）

若尚无密钥：

```bash
ssh-keygen -t ed25519 -C "gaoqlcode@github" -f ~/.ssh/id_ed25519 -N ""
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```

查看公钥：

```bash
cat ~/.ssh/id_ed25519.pub
```

到 GitHub：**Settings → SSH and GPG keys → New SSH key**，粘贴公钥并保存。

验证：

```bash
ssh -T git@github.com
```

期望看到类似：`Hi gaoqlcode! You've successfully authenticated...`

## 4. 关键设计

用 SSH 而非 HTTPS 密码，便于本地与 CI/Agent 自动化推送；私钥永不入库。

## 5. 验收

- [ ] `git --version` 有输出  
- [ ] `cat ~/.ssh/id_ed25519.pub` 有一行 `ssh-ed25519 ...`  
- [ ] `ssh -T git@github.com` 认证成功  

**你现在需要做的**：把公钥加到 GitHub 后告诉助手「SSH 已配置」，再继续 S01 的 push。
