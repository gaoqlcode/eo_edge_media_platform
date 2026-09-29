"""
文件：emp_py/bus.py
内容：进程内消息总线（默认）+ 可选 Redis Pub/Sub 封装
说明：无 Redis/RabbitMQ 时仍可联调全链路
"""
import threading
from collections import defaultdict
from typing import Callable, Dict, List


class MemoryBus:
    """线程安全的教学型发布订阅总线。"""

    def __init__(self):
        self._subs: Dict[str, List[Callable[[str, str], None]]] = defaultdict(list)
        self._lock = threading.Lock()

    def subscribe(self, topic: str, handler: Callable[[str, str], None]) -> None:
        with self._lock:
            self._subs[topic].append(handler)

    def publish(self, topic: str, payload: str) -> None:
        with self._lock:
            handlers = list(self._subs.get(topic, []))
        for h in handlers:
            h(topic, payload)


# 全局单例，便于边端模拟与 worker 同进程测试
memory_bus = MemoryBus()
