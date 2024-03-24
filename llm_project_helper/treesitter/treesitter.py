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
        method_variables: "list[str] | None",
        parameters: "list[str] | None",
        line_number: int,
        end_line_number: int,
        async_method_flag: bool,
        decorator_line_number: int,
    ):
        self.name = name
        self.doc_comment = doc_comment
        self.node = node
        self.source_code = source_code or (node.text.decode() if node else None)
        self.method_variables = method_variables
        self.parameters = parameters
        self.line_number = line_number
        self.end_line_number = end_line_number
        self.async_method_flag = async_method_flag
        self.decorator_line_number = decorator_line_number

class TreesitterClassNode:
    def __init__(
        self,
        name: "str | bytes | None",
        methods: "dict[str, TreesitterMethodNode]",
        class_variables: "list[str]",
        doc_comment: "str | None",
        line_number: int,
        end_line_number: int,
        node: tree_sitter.Node,
        source_code: "str | None",
    ):
        self.name = name
        self.methods = methods  # This will be a dict {method_name: TreesitterMethodNode}
        self.class_variables = class_variables
        self.doc_comment = doc_comment
        self.line_number = line_number
        self.end_line_number = end_line_number
        self.node = node
        self.source_code = source_code or (node.text.decode() if node else None)

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
        query = self.language.query("""
            (function_definition
                name: (identifier) @function_name
                parameters: (parameters) @params
                body: (block) @body
            ) @function
        """)
        captures = query.captures(node)

        for captured_node, _ in captures:
            if captured_node.type == 'function_definition':
                name = self._query_method_name(captured_node)
                doc_comment = self._extract_doc_comment(captured_node)
                method_variables = self._extract_method_variables(captured_node)
                parameters = self._extract_parameters(captured_node)
                line_number = captured_node.start_point[0] + 1
                end_line_number = captured_node.end_point[0] + 1
                async_method_flag = self._check_async_method(captured_node)
                decorator_line_number = self._extract_decorator_line_number(captured_node)

                result.append(TreesitterMethodNode(
                    name,
                    doc_comment,
                    captured_node,
                    None,
                    method_variables,
                    parameters,
                    line_number,
                    end_line_number,
                    async_method_flag,
                    decorator_line_number
                ))
        return result

    def _extract_doc_comment(self, node: tree_sitter.Node):
        if node.prev_named_sibling and node.prev_named_sibling.type == 'string':
            return node.prev_named_sibling.text.decode('utf-8')
        return None

    def _extract_method_variables(self, node: tree_sitter.Node):
        # Example: Extract variables declared at the start of a function
        variables = []
        query = self.language.query("""
            (function_definition body: (block (expression_statement (assignment) @assignment)))
        """)
        captures = query.captures(node)
        for captured_node, _ in captures:
            variable_name = captured_node.child_by_field_name('left').text.decode('utf-8')
            variables.append(variable_name)
        return variables

    def _extract_parameters(self, node: tree_sitter.Node):
        params = []
        if node.type in ['function_definition', 'method_definition']:
            params_node = node.child_by_field_name('parameters')
            if params_node:
                for param in params_node.children:
                    if param.type == 'identifier':
                        params.append(param.text.decode('utf-8'))
        return params

    def _check_async_method(self, node: tree_sitter.Node):
        # return node.type == 'async_function_definition'
        return node.text.decode().startswith('async')

    def _extract_decorator_line_number(self, node: tree_sitter.Node):
        # Start with the current node and look backwards for decorators
        first_decorator_line = None
        prev_sibling = node.prev_sibling

        # Iterate backwards through siblings until you no longer find a decorator
        while prev_sibling:
            # Check if the previous sibling is a decorator node
            # Note: The actual type name for decorator nodes may vary based on the grammar.
            # Adjust 'decorator' to match your grammar's specification.
            if prev_sibling.type == 'decorator':
                # Update the first_decorator_line with the current decorator's line number
                first_decorator_line = prev_sibling.start_point[0] + 1  # Adjust for 1-based indexing if needed
                # Move to the previous sibling
                prev_sibling = prev_sibling.prev_sibling
            else:
                # If the current sibling is not a decorator, stop iterating
                break

        return first_decorator_line

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
