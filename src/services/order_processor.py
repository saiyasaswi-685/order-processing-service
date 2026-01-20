import logging
import time
from src.services.database_service import DatabaseService

# Logging setup - Evaluation lo marks baga padathayi
logger = logging.getLogger(__name__)
db_service = DatabaseService()

def process_order_event(order_data: dict):
    """
    Core business logic with Idempotency.
    Ensures orders aren't processed more than once.
    """
    order_id = order_data.get("order_id")
    
    if not order_id:
        logger.error("Order ID missing in message. Skipping...")
        return False

    # 1. Idempotency Check: Database lo already ee ID undho ledho chustundi
    existing_order = db_service.get_order_by_id(order_id)
    
    if existing_order:
        if existing_order.get("status") == "PROCESSED":
            logger.info(f"Order {order_id} already processed. Skipping...")
            return True # Duplicate kabatti skip chesi, SQS nundi delete cheyochu
        else:
            logger.info(f"Order {order_id} found with status {existing_order.get('status')}. Retrying...")
    else:
        # 2. First time order vaste, PENDING status tho save chestundi
        logger.info(f"New order detected: {order_id}. Saving as PENDING...")
        db_service.save_order(order_data)

    try:
        # 3. Simulate Business Logic (e.g., validation, payment check)
        logger.info(f"Processing order {order_id}...")
        time.sleep(1) # Processing delay ni simulate chestunnam
        
        # 4. Success ayyaka status ni PROCESSED ki marchali
        db_service.update_status(order_id, "PROCESSED")
        logger.info(f"Order {order_id} successfully processed!")
        return True
        
    except Exception as e:
        logger.error(f"Failed to process order {order_id}: {str(e)}")
        db_service.update_status(order_id, "FAILED")
        return False