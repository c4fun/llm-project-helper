from abc import ABC

import tree_sitter
from tree_sitter_languages import get_language, get_parser

from llm_project_helper.const import Language
from llm_project_helper.treesitter.treesitter_registry import TreesitterRegistry
from pydantic import BaseModel, Field
from llm_project_helper.logs import logger

# class CustomBaseModel(BaseModel):
#     class Config:
#         arbitrary_types_allowed = True
#         json_encoders = {
#             tree_sitter.Node: lambda v: str(v)  # or any other serialization you prefer
#         }

#     def model_dump(self, **kwargs):
#         exclude = kwargs.pop('exclude', set())
#         exclude.update({'node', 'source_code'})  # Automatically exclude these fields
#         return super().model_dump(**kwargs, exclude=exclude)

class TreesitterGeneralVariableNode(BaseModel):
    name: str | bytes | None
    line_number: int

class TreesitterGeneralParameterNode(BaseModel):
    name: str | bytes | None
    line_number: int

class TreesitterMethodNode(BaseModel):
    name: str | bytes | None
    doc_comment: str | None
    node: tree_sitter.Node = Field(..., exclude=True)
    source_code: str | None = Field(exclude=True)
    method_variables: list[TreesitterGeneralVariableNode] | None
    parameters: list[TreesitterGeneralParameterNode] | None
    line_number: int
    end_line_number: int
    async_method_flag: bool
    decorator_line_number: int | None
    class Config:
        arbitrary_types_allowed = True

class TreesitterClassNode(BaseModel):
    name: str | bytes | None
    methods: dict[str, TreesitterMethodNode] | None
    class_variables: list[TreesitterGeneralVariableNode] | None
    doc_comment: str | None
    line_number: int
    end_line_number: int
    node: tree_sitter.Node = Field(..., exclude=True)
    source_code: str | None = Field(exclude=True)
    class Config:
        arbitrary_types_allowed = True

class TreesitterInferfaceNode(BaseModel):
    line_number: int
    end_line_number: int
    name: str | bytes | None
    methods: dict[str, TreesitterMethodNode] | None
    node: tree_sitter.Node = Field(..., exclude=True)
    source_code: str | None = Field(exclude=True)
    interface_variables: list[TreesitterGeneralVariableNode] | None
    class Config:
        arbitrary_types_allowed = True

class TreesitterImportNode(BaseModel):
    import_identifier: str | None
    line_number: int
    from_module: str | None
    node: tree_sitter.Node = Field(..., exclude=True)
    source_code: str | None = Field(exclude=True)
    class Config:
        arbitrary_types_allowed = True

class TreesitterGlobalVariableNode(BaseModel):
    name: str | bytes | None
    line_number: int
    class Config:
        arbitrary_types_allowed = True

class TreesitterMainBlockNode(BaseModel):
    node: tree_sitter.Node = Field(..., exclude=True)
    source_code: str | None
    class Config:
        arbitrary_types_allowed = True
class TreesitterResultNode(BaseModel):
    imports: list[TreesitterImportNode] | None
    classes: dict[str, TreesitterClassNode] | None
    functions: dict[str, TreesitterMethodNode] | None
    global_variables: list[TreesitterGlobalVariableNode] | None
    main_block: TreesitterMainBlockNode | None
    interfaces: dict[str, TreesitterInferfaceNode] | None
    class Config:
        arbitrary_types_allowed = True

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
        
        imports=self._query_imports(self.tree.root_node)
        logger.debug(f'typeof imports: {type(imports)}')
        classes=self._query_classes(self.tree.root_node)
        logger.debug(f'typeof classes: {type(classes)}')
        functions=self._query_functions(self.tree.root_node)
        logger.debug(f'typeof functions: {type(functions)}')
        global_variables=self._query_global_variables(self.tree.root_node)
        logger.debug(f'typeof global_variables: {type(global_variables)}')
        main_block=self._query_main_block(self.tree.root_node)
        logger.debug(f'typeof main_block: {type(main_block)}')
        # interfaces=self._query_interfaces(self.tree.root_node)
        # logger.debug(f'typeof interfaces: {type(interfaces)}')

        all_result = TreesitterResultNode(
            imports=imports,
            classes=classes,
            functions=functions,
            global_variables=global_variables,
            main_block=main_block,
            interfaces=None,
        )
        # logger.debug(f'all_result: {all_result}')
        return all_result
    
    def _query_interfaces(self, node: tree_sitter.Node):
        return None
    
    def _query_functions(self, node: tree_sitter.Node) -> dict:
        result = {}
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
                # Traverse up the tree to check if this function is within a class
                is_within_class = False
                ancestor = captured_node.parent
                while ancestor:
                    if ancestor.type == 'class_definition':
                        is_within_class = True
                        break
                    ancestor = ancestor.parent

                if not is_within_class:
                    name = self._query_method_name(captured_node)
                    doc_comment = self._extract_doc_comment(captured_node)
                    method_variables = self._extract_method_variables(captured_node)
                    parameters = self._extract_parameters(captured_node)
                    line_number = captured_node.start_point[0] + 1
                    end_line_number = captured_node.end_point[0] + 1
                    async_method_flag = self._check_async_method(captured_node)
                    decorator_line_number = self._extract_decorator_line_number(captured_node)

                    result[name] = TreesitterMethodNode(
                        name=name,
                        doc_comment=doc_comment,
                        node=captured_node,
                        source_code=captured_node.text.decode('utf-8'),
                        method_variables=method_variables,
                        parameters=parameters,
                        line_number=line_number,
                        end_line_number=end_line_number,
                        async_method_flag=async_method_flag,
                        decorator_line_number=decorator_line_number
                    )

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
            # retrieve the line_number of the variable
            line_number = captured_node.start_point[0] + 1
            # append the variable_name and line_number to a dict
            variables.append({'name': variable_name, 'line_number': line_number})
        return variables

    def _extract_parameters(self, node: tree_sitter.Node):
        params = []
        if node.type in ['function_definition', 'method_definition']:
            params_node = node.child_by_field_name('parameters')
            if params_node:
                for param in params_node.children:
                    if param.type == 'identifier':
                        line_number = param.start_point[0] + 1
                        params.append(TreesitterGeneralParameterNode(
                            name=param.text.decode('utf-8'),
                            line_number=line_number
                        ))
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
            logger.debug(f'captured_node.text.decode(): {captured_node.text.decode()}')
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
                name = name_node.text.decode('utf-8')  # Decode the name_node's text
                methods = self._query_methods_within_class(captured_node)
                class_variables = self._extract_class_variables(captured_node)
                doc_comment = self._extract_doc_comment(captured_node)
                line_number = captured_node.start_point[0] + 1
                end_line_number = captured_node.end_point[0] + 1

                classes[name] = TreesitterClassNode(
                    name=name,
                    methods=methods,
                    class_variables=class_variables,
                    doc_comment=doc_comment,
                    line_number=line_number,
                    end_line_number=end_line_number,
                    node=captured_node,
                    source_code=captured_node.text.decode('utf-8'),
                )
        return classes

    def _query_methods_within_class(self, class_node: tree_sitter.Node):
        result = {}
        query = self.language.query("""
            (function_definition
                name: (identifier) @function_name
                parameters: (parameters) @params
                body: (block) @body
            ) @function
        """)
        captures = query.captures(class_node)

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

                result[name] = TreesitterMethodNode(
                    name=name,
                    doc_comment=doc_comment,
                    node=captured_node,
                    source_code=captured_node.text.decode('utf-8'),
                    method_variables=method_variables,
                    parameters=parameters,
                    line_number=line_number,
                    end_line_number=end_line_number,
                    async_method_flag=async_method_flag,
                    decorator_line_number=decorator_line_number
                )
        return result

    def _extract_class_variables(self, class_node: tree_sitter.Node):
        class_variables = []
        query_str = """
            (class_definition
                body: (block
                    (expression_statement
                        (assignment
                            left: (identifier) @variable_name
                            right: _ @value
                        )
                    )
                )
            )
        """
        query = self.language.query(query_str)
        captures = query.captures(class_node)

        for captured_node, capture_name in captures:
            if capture_name == 'variable_name':
                variable_name = captured_node.text.decode('utf-8')
                line_number = captured_node.start_point[0] + 1
                class_variables.append(TreesitterGeneralVariableNode(
                    name=variable_name,
                    line_number=line_number
                ))

        return class_variables

    def _query_global_variables(self, node: tree_sitter.Node):
        global_variables = []
        query_str = """
            (module
                (expression_statement
                    (assignment
                        left: (identifier) @variable_name
                        right: _ @value
                    )
                )
            )
        """
        query = self.language.query(query_str)
        captures = query.captures(node)

        for captured_node, capture_name in captures:
            if capture_name == 'variable_name':
                variable_name = captured_node.text.decode('utf-8')
                line_number = captured_node.start_point[0] + 1
                global_variables.append(TreesitterGlobalVariableNode(
                    name=variable_name,
                    line_number=line_number,
                ))

        return global_variables
    
    def _query_main_block(self, node: tree_sitter.Node):
        query_str = """
            (module
                (if_statement
                    condition: (comparison_operator) @comparison
                    consequence: (block) @block
                ) @if_stmt
            )
        """
        query = self.language.query(query_str)
        captures = query.captures(node)

        for captured_node, capture_name in captures:
            if capture_name == 'comparison':
                # Directly inspect children of the comparison_operator to find identifier and string
                identifier_node = None
                string_node = None
                for child in captured_node.children:
                    if child.type == 'identifier' and child.text.decode('utf-8') == '__name__':
                        identifier_node = child
                    elif child.type == 'string':
                        string_content = child.text.decode('utf-8').strip('"\'')
                        if string_content == '__main__':
                            string_node = child

                if identifier_node and string_node:
                    # Proceed to extract the block associated with this if_statement
                    block_node = next((n for n, n_name in captures if n_name == 'block' and n.parent == captured_node.parent), None)
                    if block_node:
                        line_number = block_node.start_point[0] + 1
                        block_code = block_node.text.decode('utf-8')
                        return TreesitterMainBlockNode(node=block_node, source_code=block_code)

        return None
