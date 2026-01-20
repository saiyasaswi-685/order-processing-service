import jsonschema
from jsonschema import validate

# Requirement lo ichina official schema
ORDER_SCHEMA = {
    "type": "object",
    "properties": {
        "order_id": {"type": "string"},
        "user_id": {"type": "string"},
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "item_id": {"type": "string"},
                    "quantity": {"type": "integer", "minimum": 1},
                    "price": {"type": "number", "exclusiveMinimum": 0}
                },
                "required": ["item_id", "quantity", "price"]
            },
            "minItems": 1
        },
        "total_amount": {"type": "number", "exclusiveMinimum": 0},
        "timestamp": {"type": "string"}
    },
    "required": ["order_id", "user_id", "items", "total_amount", "timestamp"]
}

def validate_order(data):
    try:
        validate(instance=data, schema=ORDER_SCHEMA)
        return True, None
    except jsonschema.exceptions.ValidationError as err:
        return False, err.message