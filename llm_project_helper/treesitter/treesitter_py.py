import tree_sitter

from llm_project_helper.const import Language
from llm_project_helper.treesitter.treesitter import (Treesitter,
                                                      TreesitterMethodNode)
from llm_project_helper.treesitter.treesitter_registry import TreesitterRegistry


class TreesitterPython(Treesitter):
    def __init__(self):
        super().__init__(
            Language.PYTHON, "function_definition", "identifier", "expression_statement"
        )


# Register the TreesitterPython class in the registry
TreesitterRegistry.register_treesitter(Language.PYTHON, TreesitterPython)
