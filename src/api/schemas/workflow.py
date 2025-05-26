from jsonschema import validate, ValidationError
from typing import Optional

WORKFLOW_SCHEMA = {
    "type": "object",
    "required": ["workflow_id", "name", "steps"],
    "properties": {
        "workflow_id": {
            "type": "string",
            "pattern": "^[a-zA-Z0-9-_]+$",
            "minLength": 3,
            "maxLength": 50
        },
        "name": {
            "type": "string",
            "minLength": 1,
            "maxLength": 200
        },
        "steps": {
            "type": "array",
            "minItems": 1,
            "maxItems": 100,
            "items": {
                "type": "object",
                "required": ["action"],
                "properties": {
                    "action": {
                        "enum": ["click", "type", "wait", "extract", "screenshot", "navigate"]
                    },
                    "target": {"type": "string"},
                    "value": {"type": "string", "maxLength": 5000},
                    "wait_time": {"type": "number", "minimum": 0, "maximum": 30000}
                }
            }
        }
    }
}


def validate_workflow(data: dict) -> tuple[bool, Optional[str]]:
    try:
        validate(instance=data, schema=WORKFLOW_SCHEMA)
        return True, None
    except ValidationError as e:
        return False, str(e)
