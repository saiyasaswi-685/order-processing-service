from flask import Blueprint, jsonify
from src.services.database_service import DatabaseService
from src.config import Config
import boto3

health_bp = Blueprint('health', __name__)
db_service = DatabaseService()

@health_bp.route('/health', methods=['GET'])
def health_check():
    health_status = {
        "status": "healthy",
        "sqs_connected": False,
        "db_connected": False
    }

    if db_service.is_healthy():
        health_status["db_connected"] = True

    try:
        sqs = boto3.client(
            'sqs',
            aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
            region_name=Config.AWS_REGION,
            endpoint_url="http://localstack:4566"
        )
        sqs.list_queues()
        health_status["sqs_connected"] = True
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["error"] = str(e)

    status_code = 200 if health_status["status"] == "healthy" else 503
    return jsonify(health_status), status_code