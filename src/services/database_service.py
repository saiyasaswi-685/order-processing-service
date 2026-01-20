import os
from pymongo import MongoClient
from datetime import datetime
from src.config import Config

class DatabaseService:
    def __init__(self):
        # Config nundi details teeskuntundi
        self.client = MongoClient(Config.MONGO_URI)
        self.db = self.client[Config.MONGO_DB_NAME]
        self.orders = self.db.orders

    def is_healthy(self):
        try:
            self.client.admin.command('ping')
            return True
        except Exception:
            return False

    def get_order_by_id(self, order_id):
        return self.orders.find_one({"_id": order_id})

    def save_order(self, order_data):
        if "order_id" in order_data:
            order_data["_id"] = order_data.pop("order_id")
        
        order_data["status"] = "PENDING"
        order_data["created_at"] = datetime.utcnow()
        return self.orders.insert_one(order_data)

    def update_status(self, order_id, status):
        return self.orders.update_one(
            {"_id": order_id},
            {"$set": {"status": status, "processed_at": datetime.utcnow()}}
        )