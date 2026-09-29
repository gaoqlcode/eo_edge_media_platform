"""
文件：emp_py/config.py
内容：从环境变量读取配置；缺省指向本机开发栈
"""
import os


class Settings:
    """汇总平台配置，便于各微服务共用。"""

    def __init__(self):
        # 数据库：优先 DATABASE_URL；否则拼装；再否则用 sqlite 文件便于无 Docker 自测
        self.database_url = os.getenv(
            "DATABASE_URL",
            os.getenv(
                "EMP_DATABASE_URL",
                "sqlite:////tmp/emp_platform.db",
            ),
        )
        self.redis_url = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")
        self.rabbitmq_url = os.getenv(
            "RABBITMQ_URL", "amqp://emp:emp_dev_pass@127.0.0.1:5672/"
        )
        self.api_key = os.getenv("EMP_API_KEY", "emp-dev-key")
        self.use_memory_bus = os.getenv("EMP_MEMORY_BUS", "1") == "1"


settings = Settings()
