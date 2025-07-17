import json
from pydantic import BaseModel
from typing import Dict, Any, Union, Optional
import xml.etree.ElementTree as ET
from xml.dom.minidom import parseString

def _deserialize(string: str) -> Optional[dict]:
    try:
        return json.loads(string)
    except json.JSONDecodeError:
        return

def _prepare_dictionary(value: Union[str, BaseModel, Dict[str, Any]]):
    root_tag = "input"
    if isinstance(value, str):
        model: Optional[Dict[str, Any]] = _deserialize(value)
        if model is None:
            raise ValueError(f"{value} is not deserializable")
    elif isinstance(value, BaseModel):
        model = value.model_dump()
        root_tag = value.__class__.__name__.lower()
    elif isinstance(value, dict):
        for k in value.keys():
            if not isinstance(k, str):
                v = value.pop(k)
                value[str(k)] = v
        model = value
    else:
        raise ValueError(f"Input can only be of type BaseModel, dictionary or deserializable string. Got {type(value)}")
    return model, root_tag

def xml(value: Union[str, BaseModel, Dict[str, Any]]) -> str:
    """
    Convert a Pydatic model, a deserializable string or a dictionary into an XML string.

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
    xml_str = ET.tostring(xml_model, encoding='unicode')
    return parseString(xml_str).toprettyxml().replace('<?xml version="1.0" ?>\n', '')

