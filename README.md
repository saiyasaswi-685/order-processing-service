Order Processing Service (Event-Driven)
A robust, production-ready backend service that consumes order events from AWS SQS, processes them with Idempotency logic, and persists data into MongoDB.

🚀 Overview
This service is designed using an event-driven architecture to handle high-volume e-commerce order streams. It focuses on:

Reliability: Ensuring no message is lost during processing by leveraging SQS visibility timeouts.

Consistency: Using a strict idempotency mechanism to prevent duplicate orders.

Observability: Implementing structured JSON logging for professional-grade monitoring.

🛠️ Tech Stack
Framework: Flask (Python 3.11)

Message Queue: AWS SQS (Mocked via Localstack for local development)

Database: MongoDB (NoSQL)

Validation: JSON Schema (jsonschema library)

Containerization: Docker & Docker Compose

⚙️ Setup & Installation
1. Clone the Repository
Bash

git clone https://github.com/saiyasaswi-685/order-processing-service
cd order-processing-service
2. Configuration
Create a .env file based on the .env.example template:

Bash

cp .env.example .env
Ensure the SQS_QUEUE_URL and MONGO_URI are configured to point to the services defined in docker-compose.yml.

3. Run with Docker (One-Command Setup)
Start the entire stack (App, MongoDB, Localstack) with a single command:

Bash

docker-compose up --build -d
🧪 Testing
Unit Tests
Validates core message parsing, schema validation logic, and models:

Bash

docker exec -it $(docker ps -qf "name=app") python3 -m unittest discover -s tests/unit
Integration Tests
Validates end-to-end flow, SQS connectivity, and the Idempotency mechanism:

Bash

docker exec -it $(docker ps -qf "name=app") python3 tests/integration/test_advanced_flow.py
📐 Design Decisions
Idempotency: We use the order_id as the primary key (_id) in MongoDB. Before processing an event, the service checks the database state. If an order with that ID is already marked as PROCESSED, the service skips the business logic and acknowledges/deletes the SQS message to ensure exactly-once semantics.

Schema Validation: Every message is validated against a formal JSON schema (OrderEvent). Messages failing validation are logged as errors and are not deleted, allowing for retries or Dead-Letter Queue (DLQ) handling.

Error Handling: Implemented a non-blocking consumer. Exceptions during processing trigger an automatic retry via SQS visibility timeouts, ensuring no data loss.

Structured Logging: Adopted a JSON logging format (using JsonFormatter) to include contextual data like order_id, making the service compatible with modern log aggregation tools.

📡 API Endpoints
GET /health: Returns the operational status and connectivity to dependencies.

200 OK: {"status": "healthy", "sqs_connected": true, "db_connected": true}

503 Service Unavailable: If any critical dependency (SQS/DB) is disconnected.