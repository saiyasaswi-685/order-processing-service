import unittest
import time
import json
import boto3
from src.services.database_service import DatabaseService
from src.config import Config

class TestAdvancedFlow(unittest.TestCase):
    def setUp(self):
        self.db = DatabaseService()
        self.sqs = boto3.client('sqs', 
                               endpoint_url="http://localstack:4566", 
                               region_name=Config.AWS_REGION)
        self.queue_url = Config.SQS_QUEUE_URL
        # Test start ayye mundu clean up
        self.db.orders.delete_many({"_id": {"$regex": "TEST_"}})

    def test_schema_validation_failure(self):
        """Requirement 2.1: Schema validation fails -> No DB entry"""
        # total_amount missing (Invalid Schema)
        invalid_msg = {
            "order_id": "TEST_ERR_777",
            "user_id": "USER_1",
            "items": [{"item_id": "P1", "quantity": 1, "price": 10.0}],
            "timestamp": "2024-01-01T10:00:00Z"
        }
        self.sqs.send_message(QueueUrl=self.queue_url, MessageBody=json.dumps(invalid_msg))
        
        # Consumer ki processing time ivvali
        time.sleep(5)
        
        order = self.db.get_order_by_id("TEST_ERR_777")
        self.assertIsNone(order, "Order with invalid schema should not be saved in database.")

    def test_idempotency_skip_processed(self):
        """Requirement 2.2: If PROCESSED, skip and delete"""
        order_id = "TEST_DUP_101"
        # 1. Database lo munde PROCESSED status pettu
        self.db.orders.update_one(
            {"_id": order_id},
            {"$set": {
                "status": "PROCESSED", 
                "user_id": "U1",
                "total_amount": 50.0,
                "timestamp": "2024-01-01T10:00:00Z",
                "items": []
            }},
            upsert=True
        )

        # 2. Ade order_id tho malli message pampu
        msg = {
            "order_id": order_id,
            "user_id": "U1",
            "items": [{"item_id": "P1", "quantity": 1, "price": 50.0}],
            "total_amount": 50.0,
            "timestamp": "2024-01-01T10:00:00Z"
        }
        self.sqs.send_message(QueueUrl=self.queue_url, MessageBody=json.dumps(msg))

        time.sleep(5)

        # 3. DB lo check cheyi - status 'PROCESSED' lane undali, duplicate entry rakudadu
        order = self.db.get_order_by_id(order_id)
        self.assertEqual(order['status'], 'PROCESSED', "Idempotency failed: Existing processed order was modified.")

    def test_end_to_end_success(self):
        """Requirement 3.1: Scenario 1 - Success Flow"""
        order_id = "TEST_SUCCESS_200"
        msg = {
            "order_id": order_id,
            "user_id": "U2",
            "items": [{"item_id": "P2", "quantity": 2, "price": 25.0}],
            "total_amount": 50.0,
            "timestamp": "2024-01-01T11:00:00Z"
        }
        self.sqs.send_message(QueueUrl=self.queue_url, MessageBody=json.dumps(msg))

        time.sleep(5)

        order = self.db.get_order_by_id(order_id)
        self.assertIsNotNone(order)
        self.assertEqual(order['status'], 'PROCESSED', "Order was not successfully processed.")

if __name__ == "__main__":
    unittest.main()