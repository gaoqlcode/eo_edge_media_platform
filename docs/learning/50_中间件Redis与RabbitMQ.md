# 50 · 中间件 Redis 与 RabbitMQ

## Redis
适合：在线状态、短 TTL 缓存、限流计数。  
本项目：心跳写入 `device:online:<code>`（见 `emp_py/redis_client.py`）。

## RabbitMQ
适合：服务解耦的领域事件。  
本项目：交换机 `emp.events`，路由键如 `emp.device.heartbeat`；`media_worker` 消费。

## 本机启动
```bash
# Docker（已装镜像时）
sudo docker start emp_rabbitmq emp_redis_docker
# 或 micromamba Redis
bash scripts/start_infra_local.sh
```

## 对应复刻步骤
S03、S08、以及 worker 联调
