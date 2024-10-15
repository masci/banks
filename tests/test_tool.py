import inspect

from banks.filters import tool
from banks.types import Tool


def test_tool():
    def my_tool_function(myparam: str):
        """Description of the tool.

        Args:
            myparam (str): description of the parameter

        """
        pass

    tool_dump = tool(my_tool_function)
    t = Tool.model_validate_json(tool_dump)
    assert t.model_dump() == {
        "function": {
            "description": inspect.getdoc(my_tool_function),
            "name": "my_tool_function",
            "parameters": {
                "properties": {"myparam": {"description": "description " "of the " "parameter", "type": "string"}},
                "required": ["myparam"],
                "type": "object",
            },
        },
        "type": "function",
    }


def test_tool_with_defaults():
    def my_tool_function(myparam: str = ""):
        """Description of the tool.

        Args:
            myparam (str): description of the parameter

        """
        pass

    tool_dump = tool(my_tool_function)
    t = Tool.model_validate_json(tool_dump)
    assert t.model_dump() == {
        "function": {
            "description": inspect.getdoc(my_tool_function),
            "name": "my_tool_function",
            "parameters": {
                "properties": {"myparam": {"description": "description " "of the " "parameter", "type": "string"}},
                "required": [],
                "type": "object",
            },
        },
        "type": "function",
    }
