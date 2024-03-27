INDEX_NAME = 'resumestore'
CHUNK_SIZE = 256
CHUNK_OVERLAP_SIZE = 50


SCHEMA_STR = """
{
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "User",
    "description": "Schema for User model",
    "type": "object",
    "properties": {
        "type": "string",
            "id": {
                "description": "Unique identifier for the user (UUID)"
            },
            "name": {
                "type": "string",
                "description": "Name of the user"
            },
            "type": {
                "type": "string",
                "description": "Type of user (e.g., TXT or PDF)"
            },
            "email": {
                "type": "string",
                "format": "email",
                "description": "Email address of the user"
            },
            "phone_number": {
                "type": "string",
                "description": "Phone number of the user"
            },
            "resume_content": {
                "anyOf": [
                    {"type": "string"},
                    {"type": "null"}
                ],
                "description": "Resume content of the user"
            },
            "captured_at": {
                "type": "string",
                "format": "date-time",
                "description": "Timestamp when the user data was captured"
            },
            "blob_url": {
                "anyOf": [
                    {"type": "string"},
                    {"type": "null"}
                ],
                "description": "URL to the user's blob data"
            },
            "position_applied_for": {
                "type": "string",
                "description": "Position the user applied for"
            },
            "company_name": {
                "type": "string",
                "description": "Name of the company the user applied to"
            }
        },
    "required": ["id", "name", "type", "email", "phone_number", "captured_at", "position_applied_for", "company_name"],
    "additionalProperties": true
}
"""
