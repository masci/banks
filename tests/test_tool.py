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
        "type": "function",
        "function": {
            "name": "my_tool_function",
            "description": "Description of the tool.\n\nArgs:\n    myparam (str): description of the parameter",
            "parameters": {
                "type": "object",
                "properties": {"myparam": {"type": "string", "description": "description of the parameter"}},
                "required": ["myparam"],
            },
        },
        "import_path": "tests.test_tool.test_tool.<locals>.my_tool_function",
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
        "type": "function",
        "function": {
            "name": "my_tool_function",
            "description": "Description of the tool.\n\nArgs:\n    myparam (str): description of the parameter",
            "parameters": {
                "type": "object",
                "properties": {"myparam": {"type": "string", "description": "description of the parameter"}},
                "required": [],
            },
        },
        "import_path": "tests.test_tool.test_tool_with_defaults.<locals>.my_tool_function",
    }
