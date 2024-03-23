from abc import ABC

import tree_sitter
from tree_sitter_languages import get_language, get_parser

from llm_project_helper.const import Language
from llm_project_helper.treesitter.treesitter_registry import TreesitterRegistry


class TreesitterMethodNode:
    def __init__(
        self,
        name: "str | bytes | None",
        doc_comment: "str | None",
        node: tree_sitter.Node,
        source_code: "str | None",
    ):
        self.name = name
        self.doc_comment = doc_comment
        self.node = node
        self.source_code = source_code or node.text.decode()

class TreesitterImportNode:
    def __init__(
        self,
        import_identifier: str,
        line_number: int,
        from_module: "str | None",
        node: tree_sitter.Node,
        source_code: "str | None",
    ):
        self.import_identifier = import_identifier
        self.line_number = line_number
        self.from_module = from_module
        self.node = node
        self.source_code = source_code or node.text.decode()

class TreesitterResultNode:
    def __init__(
        self,
        imports: list[TreesitterImportNode],
        classes: dict[str, dict],
        functions: list[TreesitterMethodNode]
    ):
        self.imports = imports
        self.classes = classes
        self.functions = functions


class Treesitter(ABC):
    def __init__(
        self,
        language: Language,
        method_declaration_identifier: str,
        name_identifier: str,
        doc_comment_identifier: str,
    ):
        self.parser = get_parser(language.value)
        self.language = get_language(language.value)
        self.method_declaration_identifier = method_declaration_identifier
        self.method_name_identifier = name_identifier
        self.doc_comment_identifier = doc_comment_identifier
        self.import_identifier = 'import_statement'
        self.class_identifier = 'class_definition'

    @staticmethod
    def create_treesitter(language: Language) -> "Treesitter":
        return TreesitterRegistry.create_treesitter(language)

    def parse(self, file_bytes: bytes) -> list[TreesitterMethodNode]:
        self.tree = self.parser.parse(file_bytes)
        # all_result = {
        #     "imports": self._query_imports(self.tree.root_node),
        #     "classes": self._query_classes(self.tree.root_node),
        #     "functions": self._query_functions(self.tree.root_node),
        # }
        all_result = TreesitterResultNode(
            imports=self._query_imports(self.tree.root_node),
            classes=self._query_classes(self.tree.root_node),
            functions=self._query_functions(self.tree.root_node)
        )
        print(f'all_result: {all_result}')
        return all_result
    
    def _query_functions(self, node: tree_sitter.Node) -> list:
        result = []
        methods = self._query_all_methods(self.tree.root_node)
        for method in methods:
            method_name = self._query_method_name(method["method"])
            doc_comment = method["doc_comment"]
            result.append(
                TreesitterMethodNode(method_name, doc_comment, method["method"], None)
            )
        return result

    def _query_all_methods(
        self,
        node: tree_sitter.Node,
    ):
        methods = []
        if node.type == self.method_declaration_identifier:
            doc_comment_node = None
            if (
                node.prev_named_sibling
                and node.prev_named_sibling.type == self.doc_comment_identifier
            ):
                doc_comment_node = node.prev_named_sibling.text.decode()
            methods.append({"method": node, "doc_comment": doc_comment_node})
        else:
            for child in node.children:
                methods.extend(self._query_all_methods(child))
        return methods

    def _query_method_name(self, node: tree_sitter.Node):
        if node.type == self.method_declaration_identifier:
            for child in node.children:
                if child.type == self.method_name_identifier:
                    return child.text.decode()
        return None

    def _query_imports(self, node: tree_sitter.Node) -> list:
        # TODO: This is a simplified example; actual parsing may require more detailed handling
        imports = []
        query = self.language.query(f"(import_statement) @import")
        for captured_node, _ in query.captures(node):
            imports.append(TreesitterImportNode(
                import_identifier=captured_node.text.decode(),
                line_number=captured_node.start_point[0]+1,
                from_module=None,
                node=captured_node,
                source_code=None
            ))

        query = self.language.query(f"(import_from_statement) @import_from")
        for captured_node, _ in query.captures(node):
            if isinstance(captured_node, tree_sitter.Node):
                from_module = None
                # Attempt to find the module_name child node for from_module
                module_name_node = captured_node.child_by_field_name('module_name')
                if module_name_node:
                    from_module = module_name_node.text.decode()
                imports.append(TreesitterImportNode(
                    import_identifier=captured_node.text.decode(),  # This might need adjustment
                    line_number=captured_node.start_point[0]+1,
                    from_module=from_module,
                    node=captured_node,
                    source_code=None
                ))

        return imports

    def _query_classes(self, node: tree_sitter.Node) -> dict:
        classes = {}
        query = self.language.query("(class_definition) @class")
        captures = query.captures(node)  # Get all captures from the query

        for capture in captures:
            captured_node, _ = capture  # Unpack the tuple into the node and its capture index
            name_node = captured_node.child_by_field_name('name')  # Access 'name' field directly from the node
            if name_node:  # Ensure the name_node is not None
                class_name = name_node.text.decode('utf-8')  # Decode the name_node's text
                classes[class_name] = {
                    # Initialization or processing related to the class
                    # You may need to adjust this part based on your requirements
                }
        return classes
