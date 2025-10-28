from typing import Any

from pydantic import BaseModel


def build_form_data(data: BaseModel | dict[str, Any], root_key: str) -> dict[str, Any]:
    """
    Converts a Pydantic model or a dictionary into a flat dictionary suitable
    for multipart/form-data, mimicking Rails' nested attributes format.

    For example, a dictionary `{'name': 'Test', 'details': {'a': 1}}` with a
    `root_key` of 'item' would produce:
    {
        'item[name]': 'Test',
        'item[details][a]': 1
    }

    Args:
        data: The Pydantic model instance or dictionary to convert.
        root_key: The top-level key for the form data, e.g., 'course' or 'submission'.

    Returns:
        A flat dictionary representing the nested form data.
    """
    form_data: dict[str, Any] = {}

    if isinstance(data, BaseModel):
        model_dict = data.model_dump(by_alias=True, exclude_none=True)
    else:
        model_dict = data

    def recurse(current_data: Any, prefix: str) -> None:
        if isinstance(current_data, dict):
            for key, value in current_data.items():
                recurse(value, f"{prefix}[{key}]")
        elif isinstance(current_data, list):
            if not current_data:
                # Match TypeScript behavior for empty arrays
                form_data[f"{prefix}[]"] = ""
            else:
                for i, item in enumerate(current_data):
                    recurse(item, f"{prefix}[{i}]")
        elif isinstance(current_data, BaseModel):
            # Handle Pydantic models in the data structure
            model_data = current_data.model_dump(by_alias=True, exclude_none=True)
            recurse(model_data, prefix)
        elif isinstance(current_data, bool):
            form_data[prefix] = str(current_data).lower()
        elif current_data is not None:
            form_data[prefix] = str(current_data)

    recurse(model_dict, root_key)
    return form_data