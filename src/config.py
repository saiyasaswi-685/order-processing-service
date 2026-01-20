import os
class Config:
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "test")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "test")
    AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
    SQS_QUEUE_URL = os.getenv("SQS_QUEUE_URL")
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://db:27017/order_db")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "order_db")
    SQS_POLLING_INTERVAL = int(os.getenv("SQS_POLLING_INTERVAL_SECONDS", 5))
    APP_PORT = 8000