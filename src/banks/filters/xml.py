import json
import xml.etree.ElementTree as ET
from typing import Any, Optional, Union
from xml.dom.minidom import parseString

from pydantic import BaseModel


def _deserialize(string: str) -> Optional[dict]:
    try:
        return json.loads(string)
    except json.JSONDecodeError:
        return None


def _prepare_dictionary(value: Union[str, BaseModel, dict[str, Any]]):
    root_tag = "input"
    if isinstance(value, str):
        model: Optional[dict[str, Any]] = _deserialize(value)
        if model is None:
            msg = f"{value} is not deserializable"
            raise ValueError(msg)
    elif isinstance(value, BaseModel):
        model = value.model_dump()
        root_tag = value.__class__.__name__.lower()
    elif isinstance(value, dict):
        model = value.copy()
        for k in value.keys():
            if not isinstance(k, str):
                key = str(k)
                if isinstance(k, (int, float)):
                    key = "_" + key
                v = model.pop(k)
                model[key.lower()] = v
    else:
        msg = f"Input can only be of type BaseModel, dictionary or deserializable string. Got {type(value)}"
        raise ValueError(msg)
    return model, root_tag


def xml(value: Union[str, BaseModel, dict[str, Any]]) -> str:
    """
    Convert a Pydantic model, a deserializable string or a dictionary into an XML string.

    Example:
        ```jinja
        {{'{"username": "user", "email": "example@email.com"}' | to_xml}}
        "
        <input>
            <username>user</username>
            <email>example@email.com</email>
        </input>
        "
        ```
    """
    model, root_tag = _prepare_dictionary(value)
    xml_model = ET.Element(root_tag)
    for k, v in model.items():
        sub = ET.SubElement(xml_model, k)
        sub.text = str(v)
    xml_str = ET.tostring(xml_model, encoding="unicode")
    return parseString(xml_str).toprettyxml().replace('<?xml version="1.0" ?>\n', "")  # noqa: S318
