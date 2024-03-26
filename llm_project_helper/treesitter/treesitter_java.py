import tree_sitter

from llm_project_helper.const import Language
from llm_project_helper.treesitter.treesitter import (Treesitter,
                                                      TreesitterGeneralVariableNode,
                                                      TreesitterGeneralParameterNode,
                                                      TreesitterMethodNode,
                                                      TreesitterClassNode,
                                                      TreesitterImportNode,
                                                      TreesitterGlobalVariableNode,
                                                      TreesitterMainBlockNode,
                                                      TreesitterResultNode,)
from llm_project_helper.treesitter.treesitter_registry import TreesitterRegistry
from llm_project_helper.logs import logger


class TreesitterJava(Treesitter):
    def __init__(self):
        super().__init__(
            Language.JAVA, "function_definition", "identifier", "expression_statement"
        )

    def parse(self, file_bytes: bytes) -> list[TreesitterMethodNode]:
        self.tree = self.parser.parse(file_bytes)
        
        imports=self._query_imports(self.tree.root_node)
        logger.debug(f'typeof imports: {type(imports)}')
        classes=self._query_classes(self.tree.root_node)
        logger.debug(f'typeof classes: {type(classes)}')
        functions=self._query_functions(self.tree.root_node)
        logger.debug(f'typeof functions: {type(functions)}')
        # global_variables=self._query_global_variables(self.tree.root_node)
        # logger.debug(f'typeof global_variables: {type(global_variables)}')
        # main_block=self._query_main_block(self.tree.root_node)
        # logger.debug(f'typeof main_block: {type(main_block)}')

        all_result = TreesitterResultNode(
            imports=imports,
            classes=classes,
            functions=functions,
            global_variables=None,
            main_block=None,
        )
        # logger.debug(f'all_result: {all_result}')
        return all_result

    def _query_imports(self, node: tree_sitter.Node) -> list:
        # TODO: This is a simplified example; actual parsing may require more detailed handling
        imports = []
        query = self.language.query(f"(import_declaration) @import")
        for captured_node, _ in query.captures(node):
            logger.debug(f'captured_node.text.decode(): {captured_node.text.decode()}')
            imports.append(TreesitterImportNode(
                import_identifier=captured_node.text.decode(),
                line_number=captured_node.start_point[0]+1,
                from_module=None,
                node=captured_node,
                source_code=None
            ))
        logger.debug(f'imports: {imports}')
        return imports

    def _query_classes(self, node: tree_sitter.Node) -> dict:
        classes = {}
        # Java 的类定义查询
        query = self.language.query("""
            (class_declaration
                name: (identifier) @class_name
                body: (class_body) @body
            ) @class
        """)
        captures = query.captures(node)

        for captured_node, capture_name in captures:
            if capture_name == 'class':
                name_node = captured_node.child_by_field_name('name')
                if name_node:
                    name = name_node.text.decode('utf-8')
                    methods = self._query_methods_within_class(captured_node)
                    # Java 类中的变量也可能在这里处理
                    class_variables = self._extract_class_variables(captured_node)
                    # TODO: 添加 doc_comment 的处理
                    line_number = captured_node.start_point[0] + 1
                    end_line_number = captured_node.end_point[0] + 1

                    classes[name] = TreesitterClassNode(
                        name=name,
                        methods=methods,
                        class_variables=class_variables,
                        doc_comment=None,  # Java 文档注释的处理
                        line_number=line_number,
                        end_line_number=end_line_number,
                        node=captured_node,
                        source_code=None
                    )
        return classes

    def _query_functions(self, node: tree_sitter.Node) -> dict:
        functions = {}
        # Java 的方法定义查询
        query = self.language.query("""
            (method_declaration
                name: (identifier) @method_name
                parameters: (formal_parameters) @params
                body: (block) @body
            ) @method
        """)
        captures = query.captures(node)

        for captured_node, capture_name in captures:
            if capture_name == 'method':
                name_node = captured_node.child_by_field_name('name')
                if name_node:
                    name = name_node.text.decode('utf-8')
                    parameters = self._extract_parameters(captured_node)
                    line_number = captured_node.start_point[0] + 1
                    end_line_number = captured_node.end_point[0] + 1
                    method_variables = self._extract_method_variables(captured_node)
                    # TODO: 添加 async_method_flag 和 decorator_line_number 的处理（如果在 Java 中适用）

                    functions[name] = TreesitterMethodNode(
                        name=name,
                        doc_comment=None,  # Java 文档注释的处理
                        node=captured_node,
                        source_code=None,
                        method_variables=method_variables,
                        parameters=parameters,
                        line_number=line_number,
                        end_line_number=end_line_number,
                        async_method_flag=False,  # 根据 Java 语法适当调整
                        decorator_line_number=None  # Java 注解处理
                    )
        return functions

    def _query_methods_within_class(self, class_node: tree_sitter.Node):
        result = {}
        query = self.language.query("""
            (method_declaration
                name: (identifier) @function_name
                parameters: (formal_parameters) @params
                body: (block) @body
            ) @function
        """)
        captures = query.captures(class_node)

        for captured_node, _ in captures:
            if captured_node.type == 'method_declaration':
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

    def _query_method_name(self, node: tree_sitter.Node):
        # Assuming 'method_declaration' nodes have a direct 'identifier' child for the name.
        name_node = node.child_by_field_name('name')
        if name_node is not None and name_node.type == 'identifier':
            return name_node.text.decode('utf-8')
        # Fallback or error handling if name extraction fails
        return "UnnamedMethod"  # Or handle this case as appropriate

    def _extract_decorator_line_number(self, node: tree_sitter.Node):
        query_str = """
                (annotation) @annotation
        """
        query = self.language.query(query_str)
        captures = query.captures(node)
        for captured_node, capture_name in captures:
            if capture_name == 'annotation':
                return captured_node.start_point[0] + 1
        return None



    def _extract_method_variables(self, node: tree_sitter.Node):
        # Example: Extract variables declared at the start of a function
        variables = []
        query = self.language.query("""
            (method_declaration body: (block (expression_statement (assignment_expression) @assignment)))
        """)
        captures = query.captures(node)
        for captured_node, _ in captures:
            variable_name = captured_node.child_by_field_name('left').text.decode('utf-8')
            # retrieve the line_number of the variable
            line_number = captured_node.start_point[0] + 1
            # append the variable_name and line_number to a dict
            variables.append({'name': variable_name, 'line_number': line_number})
        return variables

    def _extract_class_variables(self, class_node: tree_sitter.Node):
        class_variables = []
        # 更新了查询字符串以匹配 Java 中的字段声明
        query_str = """
            (class_declaration
                body: (class_body
                    (field_declaration
                        declarator: (variable_declarator
                            name: (identifier) @variable_name
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
                # 可以在这里添加更多逻辑，比如提取变量类型等
                class_variables.append(TreesitterGeneralVariableNode(
                    name=variable_name,
                    line_number=line_number
                ))

        return class_variables
    
    def _query_global_variables(self, class_node: tree_sitter.Node):
        # 全局变量在 Java 中一般指的是静态变量，可以在类级别定义。注意这里的node应该是class_node，而不是一般的node
        class_variables = []
        # 查询静态变量的字符串
        query_str = """
            (class_declaration
                body: (class_body
                    (field_declaration
                        (modifier) @modifier
                        declarator: (variable_declarator
                            name: (identifier) @variable_name
                        )
                    )
                )
            )
        """
        query = self.language.query(query_str)
        captures = query.captures(class_node)

        for captured_node, capture_name in captures:
            if capture_name == 'variable_name':
                # 检查是否有静态修饰符
                modifier_node = captured_node.prev_sibling
                while modifier_node is not None:
                    if modifier_node.type == 'modifier' and 'static' in modifier_node.text.decode('utf-8'):
                        variable_name = captured_node.text.decode('utf-8')
                        line_number = captured_node.start_point[0] + 1
                        class_variables.append(TreesitterGeneralVariableNode(
                            name=variable_name,
                            line_number=line_number
                        ))
                        break  # 找到静态修饰符后就不需要继续查找
                    modifier_node = modifier_node.prev_sibling

        return class_variables

    def _query_main_block(self, root_node: tree_sitter.Node):
        # 构建查询字符串以查找 main 方法
        query_str = """
            (class_declaration
                body: (class_body
                    (method_declaration
                        modifiers: (modifiers
                            (modifier) @public
                            (modifier) @static
                        )
                        type: (void_type) @return_type
                        name: (identifier) @method_name
                        parameters: (formal_parameters
                            (formal_parameter
                                type: (type_identifier) @param_type
                                name: (identifier) @param_name
                            )
                        )
                        body: (block) @body
                    ) @main_method
                    (#match? @method_name "main")
                    (#match? @param_type "String\\[\\]")
                )
            )
        """
        query = self.language.query(query_str)
        captures = query.captures(root_node)

        main_blocks = []

        for captured_node, capture_name in captures:
            if capture_name == 'body':
                # 提取 main 方法的信息
                source_code = captured_node.text.decode('utf-8')
                line_number = captured_node.start_point[0] + 1
                end_line_number = captured_node.end_point[0] + 1

                main_blocks.append(TreesitterMainBlockNode(
                    node=captured_node,
                    source_code=source_code,
                    line_number=line_number,
                    end_line_number=end_line_number
                ))

        return main_blocks



# Register the TreesitterJava class in the registry
TreesitterRegistry.register_treesitter(Language.JAVA, TreesitterJava)

