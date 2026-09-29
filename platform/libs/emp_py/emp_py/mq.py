"""
文件：emp_py/mq.py
内容：RabbitMQ 发布封装；不可用时写入本地 outbox 文件
"""
import json
from datetime import datetime
from pathlib import Path

from emp_py.config import settings

_OUTBOX = Path("/tmp/emp_outbox.jsonl")


def publish_event(topic: str, payload: dict) -> bool:
    """发布领域事件到 RabbitMQ topic exchange；失败则落本地 outbox。"""
    body = json.dumps({"topic": topic, "payload": payload, "ts": datetime.utcnow().isoformat()}, ensure_ascii=False)
    try:
        import pika

        params = pika.URLParameters(settings.rabbitmq_url)
        params.socket_timeout = 2
        conn = pika.BlockingConnection(params)
        ch = conn.channel()
        ch.exchange_declare(exchange="emp.events", exchange_type="topic", durable=True)
        ch.basic_publish(exchange="emp.events", routing_key=topic, body=body.encode("utf-8"))
        conn.close()
        return True
    except Exception:
        with _OUTBOX.open("a", encoding="utf-8") as f:
            f.write(body + "\n")
        return False
