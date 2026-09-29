# SSH 公钥配置（GitHub）

## 本机公钥（请完整复制到 GitHub）

```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAICP+LrYKoggEmx/Ts1b5nKUxTlLvk1ksfGGR273MsMgy gaoqlcode@github
```

## 网页操作

1. 打开 https://github.com/settings/keys  
2. **New SSH key**  
3. Title 可填：`wsl-eo-edge`  
4. Key 粘贴上面整行  
5. Save  

## 验证

```bash
ssh -T git@github.com
```

成功示例：`Hi gaoqlcode! You've successfully authenticated...`

## 安全提醒

- **私钥** `~/.ssh/id_ed25519` 不要发给任何人、不要提交进 Git  
- 只分享 `.pub` 公钥  
