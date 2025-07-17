import pytest
import xml.etree.ElementTree as ET
from xml.dom.minidom import parseString
from pydantic import BaseModel
from typing import Tuple, Dict, Any

from banks.filters.xml import xml

@pytest.fixture
def xml_string_from_basemodel() -> str:
    model = ET.Element("person")
    age = ET.SubElement(model, "age")
    age.text = "30"
    name = ET.SubElement(model, "name")
    name.text = "John Doe"
    xml_str = ET.tostring(model, encoding='unicode')
    return parseString(xml_str).toprettyxml().replace('<?xml version="1.0" ?>\n', '')

@pytest.fixture
def xml_string_from_other() -> str:
    model = ET.Element("input")
    age = ET.SubElement(model, "age")
    age.text = "30"
    name = ET.SubElement(model, "name")
    name.text = "John Doe"
    xml_str = ET.tostring(model, encoding='unicode')
    return parseString(xml_str).toprettyxml().replace('<?xml version="1.0" ?>\n', '')

@pytest.fixture
def starting_value() -> Tuple[BaseModel, Dict[str, Any], str]:
    class Person(BaseModel):
        age: int
        name: str
    
    p = Person(age=30, name="John Doe")
    return p, p.model_dump(), p.model_dump_json()

def test_xml_filter(xml_string_from_basemodel: str, xml_string_from_other: str, starting_value: Tuple[BaseModel, Dict[str, Any], str]) -> None:
    model, dictionary, string = starting_value
    assert xml(model) == xml_string_from_basemodel
    assert xml(dictionary) == xml_string_from_other
    assert xml(string) == xml_string_from_other

    