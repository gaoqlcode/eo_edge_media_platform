# 15 · Python 语法与 FastAPI（对照本仓）

## 1. 学习目标

- 读懂控制面 `app.py`：路由、Pydantic、Depends、中间件  
- 理解 `sys.path` 引入 `emp_py`、环境变量配置  
- 能本地起一个服务并 `curl /health`  

库卡片见 [05b](./05b_依赖库总览与用法.md)。对应 S08～S13。

---

## 2. 概念详解

### 2.1 虚拟环境与解释器

永远确认：

```bash
which python
python -c "import sys; print(sys.executable)"
```

本仓推荐：`.tools/mamba_root/envs/emp/bin/python`。

### 2.2 模块导入

```python
from fastapi import Depends, HTTPException
from emp_py.auth import require_auth
```

各服务开头：

```python
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "libs" / "emp_py"))
```

教学写法；企业更大仓会用正式 package 安装（`pip install -e`）。

### 2.3 类型注解与 Pydantic

```python
class DeviceCreate(BaseModel):
    device_code: str
    name: str
    platform: str = "wsl"
```

- 注解帮助编辑器与运行时校验。  
- 本仓 **Pydantic v1**（`<2`）。

### 2.4 FastAPI 路由

```python
@app.post("/api/devices")
def create_device(body: DeviceCreate, db: Session = Depends(get_db), _auth: dict = Depends(require_auth)):
    ...
```

- `body`：自动从 JSON 解析并校验。  
- `Depends`：依赖注入——鉴权、数据库会话。  
- 失败可 `raise HTTPException(401, "...")`。

### 2.5 双模鉴权（本仓）

```python
from emp_py.auth import require_auth
# Header: X-API-Key: emp-dev-key
# 或 Authorization: Bearer <jwt>
```

返回 `{"mode":"api_key"|"jwt","sub":...,"role":...}`。

### 2.6 中间件与追踪

`create_service_app` 挂请求日志、`X-Request-Id`、`X-Trace-Id`、`/health`、`/metrics`。  
学中间件时对照 `emp_py/fastapi_app.py`。

### 2.7 SQLAlchemy Session

```python
db = next(get_db())
try:
    rows = db.query(Device).all()
finally:
    db.close()
```

或在路由里 `db: Session = Depends(get_db)`。

### 2.8 环境变量

```python
os.getenv("DATABASE_URL", "sqlite:////tmp/emp_platform.db")
```

启动脚本统一 export，避免 shell 残留错误 URL。

---

## 3. 下载与依赖

```bash
EMP_PY=/home/gaoql/eo_edge_media_platform/.tools/mamba_root/envs/emp/bin/python
"$EMP_PY" -m pip install -r requirements.txt
```

---

## 4. 本项目对照

| 概念 | 文件 |
|------|------|
| 应用工厂 | `emp_py/fastapi_app.py` |
| 鉴权 | `emp_py/auth.py`、`jwt_auth.py` |
| ORM | `emp_py/models.py`、`db.py` |
| 设备服务 | `platform/services/device_service/app.py` |
| BFF 登录 | `platform/services/control_bff/app.py` |
| 启动 | `scripts/start_python_services.sh` |

---

## 5. 动手实验

```bash
bash scripts/start_infra_local.sh
bash scripts/start_python_services.sh
curl -s http://127.0.0.1:8101/health
curl -s -o /dev/null -w '%{http_code}\n' -X POST http://127.0.0.1:8101/api/devices \
  -H 'Content-Type: application/json' -d '{"device_code":"x","name":"x"}'
# 期望 401
curl -s -X POST http://127.0.0.1:8105/api/bff/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"admin123"}'
```

---

## 6. 自测题

1. `Depends(require_auth)` 在什么时机执行？失败时客户端看到什么？  
2. 为何要把 `emp_py` 插进 `sys.path`？  
3. Pydantic 默认值 `platform: str = "wsl"` 在请求省略该字段时行为？  

答案：1）进路由前，401；2）否则 import 找不到包；3）用默认值。
