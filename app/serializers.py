from app.models.enums import ClearanceLevel
from app.permissions import FIELD_PERMISSIONS


def is_field_visible(field_key: str, clearance: ClearanceLevel) -> bool:
    """
    Returns True if `clearance` grants access to `field_key`.
    A field is visible when the user's numeric level is <= the required level.
    Fields absent from the map are visible by default.
    """
    required = FIELD_PERMISSIONS.get(field_key)
    if required is None:
        return True
    return clearance.value <= required.value


def filter_fields_by_clearance(
    data: dict, clearance: ClearanceLevel, prefix: str = ""
) -> dict:
    """
    Recursively removes keys from `data` that `clearance` cannot see.

    - Top-level scalar fields are checked against `field_key` (no prefix).
    - Nested dicts are checked at the section level first, then each inner
      field is checked with `"section.field"` as the key.
    - Lists of dicts are filtered per-item using the list key as prefix.
    """
    result = {}
    for key, value in data.items():
        field_key = f"{prefix}.{key}" if prefix else key

        if not is_field_visible(field_key, clearance):
            continue

        if value is None:
            result[key] = None
        elif isinstance(value, dict):
            result[key] = filter_fields_by_clearance(value, clearance, prefix=key)
        elif isinstance(value, list):
            result[key] = [
                filter_fields_by_clearance(item, clearance, prefix=key)
                if isinstance(item, dict) else item
                for item in value
            ]
        else:
            result[key] = value

    return result
