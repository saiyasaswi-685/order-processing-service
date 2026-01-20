import threading
import time
import logging
import json
import boto3
from flask import Flask
from src.api.health import health_bp
from src.config import Config
from src.services.order_processor import process_order_event
from src.utils.validation import validate_order

# --- Requirement 1.18: Structured Logging (JSON Format) ---
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
        }
        if hasattr(record, 'order_id'):
            log_record['order_id'] = record.order_id
        return json.dumps(log_record)

logger = logging.getLogger("order_service")
handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)

app = Flask(__name__)
app.register_blueprint(health_bp)

def start_sqs_consumer():
    # Requirement 1.1: Connecting to SQS via Env Variables
    sqs = boto3.client('sqs', 
                       aws_access_key_id=Config.AWS_ACCESS_KEY_ID, 
                       aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY, 
                       region_name=Config.AWS_REGION, 
                       endpoint_url="http://localstack:4566")
    
    logger.info("SQS Consumer Polling started successfully.")
    
    while True:
        try:
            # Requirement 1.2 & 1.3: Continuous Polling & Batch of 10 messages
            response = sqs.receive_message(
                QueueUrl=Config.SQS_QUEUE_URL, 
                MaxNumberOfMessages=10, 
                WaitTimeSeconds=Config.SQS_POLLING_INTERVAL
            )
            
            messages = response.get('Messages', [])
            if not messages:
                continue

            for msg in messages:
                try:
                    # Requirement 1.4: Parse JSON Body
                    order_data = json.loads(msg['Body'])
                    order_id = order_data.get('order_id', 'unknown')
                    
                    # Requirement 1.5 & 2.1: Schema Validation
                    is_valid, error_msg = validate_order(order_data)
                    
                    if not is_valid:
                        logger.error(f"Validation Failed: {error_msg}", extra={'order_id': order_id})
                        # Message is NOT deleted, allowed to retry (Requirement 1.6)
                        continue 
                    
                    # Requirement 2.2: Business Logic & Idempotency
                    # process_order_event handles idempotency internally
                    if process_order_event(order_data):
                        # Requirement 1.13: Explicitly delete after success
                        sqs.delete_message(
                            QueueUrl=Config.SQS_QUEUE_URL, 
                            ReceiptHandle=msg['ReceiptHandle']
                        )
                        logger.info(f"Order processed and deleted from queue", extra={'order_id': order_id})
                
                except json.JSONDecodeError:
                    logger.error("Failed to parse raw SQS message body as JSON")
                except Exception as e:
                    # Requirement 1.14: Unhandled exceptions (message will reappear after timeout)
                    logger.error(f"Processing error: {str(e)}")
                    
        except Exception as e:
            logger.error(f"Critical SQS Connection Error: {e}")
            time.sleep(5) # Wait before retry

if __name__ == "__main__":
    # Start consumer in a separate thread
    consumer_thread = threading.Thread(target=start_sqs_consumer, daemon=True)
    consumer_thread.start()
    
    # Requirement 1.16: Health Check API
    logger.info(f"Starting Health API on port {Config.APP_PORT}")
    app.run(host='0.0.0.0', port=Config.APP_PORT)