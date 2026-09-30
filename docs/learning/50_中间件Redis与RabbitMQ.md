# 50 · 中间件 Redis 与 RabbitMQ

## 1. 学习目标

- 说清 Redis 与 RabbitMQ 各自解决什么问题（勿混用）  
- 看懂本仓：心跳缓存、事件发布、DLQ、幂等 SETNX、outbox 降级  
- 会查 Redis key、会看 RabbitMQ 管理台  

对应 S03、S08、worker。库客户端见 [05b](./05b_依赖库总览与用法.md)。

---

## 2. 概念详解

### 2.1 何时用谁

| 需求 | 选 | 原因 |
|------|-----|------|
| 「设备现在在不在线」秒级答案 | Redis | 内存快、TTL 自动过期 |
| 「设备上线了，通知一堆下游」 | RabbitMQ | 发布订阅、解耦、可持久 |
| 权威档案、对账 | PostgreSQL | 事务与约束 |

### 2.2 Redis 要点

- 数据结构：String、Hash、List、Set、ZSet…  
- 本仓主要用 **String + TTL**：`SET key value EX 30`  
- 幂等：`SET emp:idem:<id> 1 NX EX 86400` —— 只有第一次成功  

本仓封装：`emp_py/redis_client.py`、`idempotency.py`。  
连不上 Redis 时降级进程内 dict——**单机可测，多进程不共享**。

### 2.3 RabbitMQ 要点

```text
生产者 publish → Exchange(emp.events, topic)
                    ↓ 路由键 emp.device.heartbeat
                 Queue(emp.media_worker)
                    ↓ 消费失败 nack requeue=false
                 DLX(emp.events.dlx) → Queue(...dlq)
```

- **ack**：处理成功  
- **nack + requeue=False**：结合队列上的 DLX 参数进死信  
- **message_id / event_id**：幂等去重  

本仓：`emp_py/mq.py` 发布；`media_worker/worker.py` 消费。  
MQ 不可用时写 `/tmp/emp_outbox.jsonl`（简易 outbox）。

### 2.4 心跳链路（端到端）

```text
edge_agent POST /heartbeat
  → device_service 写 PG
  → cache_set device:online:*
  → publish_event emp.device.heartbeat
  → worker 打印/后续写库（可扩展）
```

---

## 3. 下载与依赖

```bash
# Redis Local
bash scripts/start_infra_local.sh   # :56379

# RabbitMQ（Compose 镜像）
sudo docker start emp_rabbitmq 2>/dev/null || \
  sudo docker-compose -f platform/infra/docker-compose.yml up -d rabbitmq

# Python 客户端
pip install redis pika   # 或 -r requirements.txt
```

环境变量：

```bash
export REDIS_URL=redis://127.0.0.1:56379/0
export RABBITMQ_URL=amqp://emp:emp_dev_pass@127.0.0.1:5672/
```

---

## 4. 本项目对照

| 能力 | 文件 |
|------|------|
| 缓存 get/set | `emp_py/redis_client.py` |
| 发布事件 | `emp_py/mq.py` |
| 幂等 | `emp_py/idempotency.py` |
| 心跳使用处 | `device_service/app.py` |
| 消费+DLQ | `media_worker/worker.py` |

---

## 5. 动手实验

```bash
# Redis
redis-cli -p 56379 ping
redis-cli -p 56379 keys 'device:online:*'

# 发心跳后应有缓存
curl -s -X POST http://127.0.0.1:8101/api/devices/heartbeat \
  -H 'Content-Type: application/json' \
  -d '{"device_code":"edge-e2e-pg","status":"online","platform":"wsl"}'

# Worker 幂等单测直觉
python - <<'PY'
from emp_py.idempotency import already_processed
print(already_processed("demo-1"), already_processed("demo-1"))  # False True
PY

# 可选：前台消费
python platform/services/media_worker/worker.py
```

管理台（若起了 management 插件）：浏览器 `http://127.0.0.1:15672` 用户 `emp` / `emp_dev_pass`。

---

## 6. 自测题

1. 同一 `event_id` 被投递两次，worker 第二次应怎样？  
2. 为什么死信要用独立交换机而不是原地死循环 requeue？  
3. Redis TTL 30s 过期后，PG 里设备状态还在吗？  

答案：1）幂等跳过并 ack；2）避免毒消息堵队列，便于人工处理；3）在，Redis 只是缓存。
