import xml.etree.ElementTree as ET
from typing import Any
from xml.dom.minidom import parseString

import pytest
from pydantic import BaseModel

from banks.filters.xml import xml


@pytest.fixture
def xml_string_from_basemodel() -> str:
    model = ET.Element("person")
    age = ET.SubElement(model, "age")
    age.text = "30"
    name = ET.SubElement(model, "name")
    name.text = "John Doe"
    xml_str = ET.tostring(model, encoding="unicode")
    return parseString(xml_str).toprettyxml().replace('<?xml version="1.0" ?>\n', "")  # noqa: S318


@pytest.fixture
def xml_string_from_other() -> str:
    model = ET.Element("input")
    age = ET.SubElement(model, "age")
    age.text = "30"
    name = ET.SubElement(model, "name")
    name.text = "John Doe"
    xml_str = ET.tostring(model, encoding="unicode")
    return parseString(xml_str).toprettyxml().replace('<?xml version="1.0" ?>\n', "")  # noqa: S318


@pytest.fixture
def xml_string_from_edge_case() -> str:
    model = ET.Element("input")
    hello = ET.SubElement(model, "_1")
    hello.text = "hello"
    world = ET.SubElement(model, "_2.4")
    world.text = "world"
    xml_str = ET.tostring(model, encoding="unicode")
    return parseString(xml_str).toprettyxml().replace('<?xml version="1.0" ?>\n', "")  # noqa: S318


@pytest.fixture
def starting_value() -> tuple[BaseModel, dict[str, Any], str]:
    class Person(BaseModel):
        age: int
        name: str

    p = Person(age=30, name="John Doe")
    return p, p.model_dump(), p.model_dump_json()


@pytest.fixture
def dict_edge_case() -> tuple[dict, str]:
    return {1: "hello", 2.4: "world"}


def test_xml_filter(
    xml_string_from_basemodel: str,
    xml_string_from_other: str,
    starting_value: tuple[BaseModel, dict[str, Any], str],
    dict_edge_case: dict,
    xml_string_from_edge_case: str,
) -> None:
    model, dictionary, string = starting_value
    assert xml(model) == xml_string_from_basemodel
    assert xml(dictionary) == xml_string_from_other
    assert xml(string) == xml_string_from_other
    assert xml(dict_edge_case) == xml_string_from_edge_case
