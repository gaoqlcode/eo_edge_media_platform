# media_worker

> 状态：`[x] 已完成`

消费 RabbitMQ `emp.events`（或降级读 `/tmp/emp_outbox.jsonl`）。

```bash
export PYTHONPATH=platform/libs/emp_py
python platform/services/media_worker/worker.py          # rabbit
python platform/services/media_worker/worker.py outbox   # 本地 outbox
```
