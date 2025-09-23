import json
import json5
import re
from typing import Dict, List, Any

def safe_json_parse(json_string: str) -> Dict[str, Any]:
    """Safely parse a JSON string, handling common formatting issues."""
    try:
        return json.loads(json_string)
    except json.JSONDecodeError:
        try:
            return json5.loads(json_string)
        except:
            cleaned_string = clean_json_string(json_string)
            try:
                return json.loads(cleaned_string)
            except json.JSONDecodeError:
                return {"error": "Failed to parse JSON", "raw": json_string}

def clean_json_string(json_string: str) -> str:
    """Clean common JSON formatting issues."""
    json_string = re.sub(r'```json\s*', '', json_string)
    json_string = re.sub(r'```\s*', '', json_string)
    json_string = re.sub(r',(\s*[}\]])', r'\1', json_string)
    json_string = re.sub(r"'([^']*)':", r'"\1":', json_string)
    json_string = re.sub(r":\s*'([^']*)'", r': "\1"', json_string)
    json_string = json_string.strip()
    return json_string

def validate_json(data: Dict[str, Any], required_fields: List[str]) -> bool:
    """Validate that JSON data contains required fields."""
    if not isinstance(data, dict):
        return False
    for field in required_fields:
        if field not in data:
            return False
    return True

def validate_command_data(data: Dict[str, Any]) -> bool:
    """Validate command explanation data structure"""
    required_fields = ["syntax", "description", "explanation", "examples", "options", "related_commands", "advanced_options", "performance_notes", "pitfalls", "use_cases", "internal_mechanics"]
    if not validate_json(data, required_fields):
        return False
    if not isinstance(data.get("examples", []), list):
        return False
    if not isinstance(data.get("options", []), list):
        return False
    if not isinstance(data.get("related_commands", []), list):
        return False
    if not isinstance(data.get("advanced_options", []), list):
        return False
    if not isinstance(data.get("performance_notes", []), list):
        return False
    if not isinstance(data.get("pitfalls", []), list):
        return False
    if not isinstance(data.get("use_cases", []), list):
        return False
    if not isinstance(data.get("internal_mechanics", []), list):
        return False
    return True

def validate_tutorial_data(data: Dict[str, Any]) -> bool:
    """Validate tutorial data structure"""
    required_fields = ["title", "description", "prerequisites", "steps", "summary", "next_steps"]
    if not validate_json(data, required_fields):
        return False
    if not isinstance(data.get("steps", []), list):
        return False
    for step in data.get("steps", []):
        if not isinstance(step, dict):
            return False
        if not all(key in step for key in ["title", "content", "commands", "tips"]):
            return False
    return True

def validate_conflict_data(data: Dict[str, Any]) -> bool:
    """Validate conflict resolution data structure"""
    required_fields = ["analysis", "steps", "commands", "tips", "common_mistakes"]
    if not validate_json(data, required_fields):
        return False
    for field in ["steps", "commands", "tips", "common_mistakes"]:
        if not isinstance(data.get(field, []), list):
            return False
    return True

def validate_error_data(data: Dict[str, Any]) -> bool:
    """Validate error solution data structure"""
    required_fields = ["error_type", "explanation", "solution", "commands", "prevention"]
    if not validate_json(data, required_fields):
        return False
    if not isinstance(data.get("commands", []), list):
        return False
    return True
