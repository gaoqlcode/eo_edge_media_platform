"""
文件：media_worker/worker.py
内容：消费 RabbitMQ emp.events（心跳等），写告警或刷新逻辑；无 MQ 时读 outbox 文件
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "libs" / "emp_py"))

from emp_py.config import settings  # noqa: E402


def handle_message(body: str) -> None:
    data = json.loads(body)
    topic = data.get("topic", "")
    payload = data.get("payload", {})
    print(f"[worker] topic={topic} payload={payload}", flush=True)


def consume_rabbit():
    import pika

    params = pika.URLParameters(settings.rabbitmq_url)
    conn = pika.BlockingConnection(params)
    ch = conn.channel()
    ch.exchange_declare(exchange="emp.events", exchange_type="topic", durable=True)
    q = ch.queue_declare(queue="emp.media_worker", durable=True)
    ch.queue_bind(exchange="emp.events", queue="emp.media_worker", routing_key="emp.#")

    def _cb(ch_, method, _props, body):
        handle_message(body.decode("utf-8"))
        ch_.basic_ack(delivery_tag=method.delivery_tag)

    ch.basic_consume(queue="emp.media_worker", on_message_callback=_cb)
    print("[worker] consuming emp.events ...", flush=True)
    ch.start_consuming()


def drain_outbox_once():
    path = Path("/tmp/emp_outbox.jsonl")
    if not path.exists():
        print("[worker] no outbox")
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            handle_message(line)
    print("[worker] outbox drained")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "rabbit"
    if mode == "outbox":
        drain_outbox_once()
    else:
        try:
            consume_rabbit()
        except Exception as e:
            print(f"[worker] rabbit failed: {e}; fallback outbox", flush=True)
            drain_outbox_once()
            time.sleep(1)
