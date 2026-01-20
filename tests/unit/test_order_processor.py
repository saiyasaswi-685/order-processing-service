import unittest
from unittest.mock import MagicMock, patch
from src.services.order_processor import process_order_event

class TestOrderProcessor(unittest.TestCase):
    @patch('src.services.order_processor.db_service')
    def test_process_new_order(self, mock_db):
        # 1. New order case test
        mock_db.get_order_by_id.return_value = None
        order_data = {"order_id": "TEST_1", "amount": 100}
        
        result = process_order_event(order_data)
        
        self.assertTrue(result)
        mock_db.save_order.assert_called_once()
        mock_db.update_status.assert_called_with("TEST_1", "PROCESSED")

    @patch('src.services.order_processor.db_service')
    def test_idempotency_duplicate_order(self, mock_db):
        # 2. Duplicate order case test (Idempotency)
        mock_db.get_order_by_id.return_value = {"_id": "TEST_1", "status": "PROCESSED"}
        order_data = {"order_id": "TEST_1"}
        
        result = process_order_event(order_data)
        
        self.assertTrue(result)
        mock_db.save_order.assert_not_called() # Duplicate kabatti save avvakudadhu

if __name__ == '__main__':
    unittest.main()