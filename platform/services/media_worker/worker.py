"""
文件：media_worker/worker.py
内容：RabbitMQ 消费 + 死信队列（DLQ）配置；失败 nack 进 DLQ
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
    # 模拟业务：心跳事件打印；可扩展写库
    if topic == "emp.device.heartbeat" and payload.get("status") == "fault":
        raise RuntimeError("simulated fault handling failure")
    print(f"[worker] ok topic={topic} payload={payload}", flush=True)


def setup_topology(ch):
    """声明主交换机、业务队列、死信交换机与死信队列。"""
    ch.exchange_declare(exchange="emp.events", exchange_type="topic", durable=True)
    ch.exchange_declare(exchange="emp.events.dlx", exchange_type="topic", durable=True)
    ch.queue_declare(
        queue="emp.media_worker",
        durable=True,
        arguments={
            "x-dead-letter-exchange": "emp.events.dlx",
            "x-dead-letter-routing-key": "emp.dlq",
        },
    )
    ch.queue_bind(exchange="emp.events", queue="emp.media_worker", routing_key="emp.#")
    ch.queue_declare(queue="emp.media_worker.dlq", durable=True)
    ch.queue_bind(exchange="emp.events.dlx", queue="emp.media_worker.dlq", routing_key="emp.dlq")


def consume_rabbit():
    import pika

    params = pika.URLParameters(settings.rabbitmq_url)
    conn = pika.BlockingConnection(params)
    ch = conn.channel()
    setup_topology(ch)

    def _cb(ch_, method, _props, body):
        try:
            handle_message(body.decode("utf-8"))
            ch_.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            print(f"[worker] fail -> DLQ: {e}", flush=True)
            # requeue=False 配合 DLX 进入死信队列
            ch_.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    ch.basic_qos(prefetch_count=10)
    ch.basic_consume(queue="emp.media_worker", on_message_callback=_cb)
    print("[worker] consuming emp.events with DLQ ...", flush=True)
    ch.start_consuming()


def drain_outbox_once():
    path = Path("/tmp/emp_outbox.jsonl")
    if not path.exists():
        print("[worker] no outbox")
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                handle_message(line)
            except Exception as e:
                print(f"[worker] outbox item failed: {e}", flush=True)
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
