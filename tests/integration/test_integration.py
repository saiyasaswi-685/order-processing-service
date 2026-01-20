import unittest
import time
import boto3
from src.services.database_service import DatabaseService

class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.db = DatabaseService()
        self.sqs = boto3.client('sqs', endpoint_url='http://localhost:4566', region_name='us-east-1')
        self.queue_url = "http://localhost:4566/000000000000/order-queue"

    def test_end_to_end_flow(self):
        # 1. Clear previous data for clean test
        self.db.orders.delete_one({"_id": "INT_TEST_1"})

        # 2. Send a valid message to SQS
        order_msg = '{"order_id": "INT_TEST_1", "user_id": "U1", "total_amount": 100, "timestamp": "2024-01-01T10:00:00Z", "items": [{"item_id": "P1", "quantity": 1, "price": 100}]}'
        self.sqs.send_message(QueueUrl=self.queue_url, MessageBody=order_msg)

        # 3. Wait for app to process
        time.sleep(5)

        # 4. Assert DB has the record
        order = self.db.get_order_by_id("INT_TEST_1")
        self.assertIsNotNone(order)
        self.assertEqual(order['status'], 'PROCESSED')

if __name__ == '__main__':
    unittest.main()