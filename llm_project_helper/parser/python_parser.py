import ast
import json
import os


class PythonParser(ast.NodeVisitor):
    def __init__(self):
        self.structure = {
            "imports": [],
            "classes": {},
            "functions": {},
            "global_variables": [],
            "main_block": []
        }
        self.current_class = None
        self.current_method = None
        self.current_function = None
        self.in_main_block = False

    def visit_If(self, node):
        # Check if this is the main block
        if (
            isinstance(node.test, ast.Compare) and
            isinstance(node.test.left, ast.Name) and
            node.test.left.id == "__name__" and
            isinstance(node.test.comparators[0], ast.Str) and
            node.test.comparators[0].s == "__main__"
        ):
            self.in_main_block = True
            for stmt in node.body:
                self.visit(stmt)
            self.in_main_block = False
        else:
            self.generic_visit(node)

    def visit_Expr(self, node):
        if self.in_main_block:
            if hasattr(node.value, 's'):
                self.structure["main_block"].append(node.value.s)
        self.generic_visit(node)

    def visit_Call(self, node):
        if self.in_main_block:
            self.structure["main_block"].append(ast.unparse(node))
        self.generic_visit(node)

    def visit_Import(self, node):
        for name in node.names:
            self.structure["imports"].append({'import': name.name, 'line_number': node.lineno})
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        for name in node.names:
            self.structure["imports"].append({
                'from': node.module,
                'import': name.name,
                'line_number': node.lineno
            })
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        self.current_class = node.name
        docstring = ast.get_docstring(node)
        end_line_number = self.find_last_line(node)
        class_info = {
            'methods': {},
            'class_variables': [],
            'docstring': docstring,
            'line_number': node.lineno,
            'end_line_number': end_line_number
        }
        if node.decorator_list:
            class_info['decorator_line_number'] = node.decorator_list[0].lineno
        self.structure["classes"][node.name] = class_info
        self.generic_visit(node)
        self.current_class = None

    def visit_FunctionDef(self, node):
        self.handle_function(node)

    def visit_AsyncFunctionDef(self, node):
        self.handle_function(node, is_async=True)

    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name):
                variable_name = target.id
                variable_info = {'name': variable_name, 'line_number': node.lineno}
                if self.current_class is not None and self.current_method is None:
                    # Class variable
                    self.structure["classes"][self.current_class]['class_variables'].append(variable_info)
                elif self.current_function is None and self.current_class is None:
                    # Global variable
                    self.structure["global_variables"].append(variable_info)
        self.generic_visit(node)

    def handle_function(self, node, is_async=False):
        docstring = ast.get_docstring(node)
        end_line_number = self.find_last_line(node)

        function_name = node.name
        method_variables = self.extract_variables(node)
        parameters = self.extract_parameters(node)

        if self.current_class is not None:
            self.current_method = function_name
            func_info = {
                'method_variables': method_variables,
                'parameters': parameters,
                'docstring': docstring,
                'line_number': node.lineno,
                'end_line_number': end_line_number,
                'type': 'async_method' if is_async else 'method'
            }
            if node.decorator_list:
                func_info['decorator_line_number'] = node.decorator_list[0].lineno
            self.structure["classes"][self.current_class]['methods'][function_name] = func_info
        else:
            self.current_function = function_name
            func_info = {
                'function_variables': method_variables,
                'parameters': parameters,
                'docstring': docstring,
                'line_number': node.lineno,
                'end_line_number': end_line_number,
                'type': 'async_function' if is_async else 'function'
            }
            if node.decorator_list:
                func_info['decorator_line_number'] = node.decorator_list[0].lineno
            self.structure["functions"][function_name] = func_info
        self.current_method = None
        self.current_function = None

    def find_last_line(self, node):
        """
        Recursively find the last line of a node.
        """
        last_line = node.lineno
        for child in ast.iter_child_nodes(node):
            child_last_line = getattr(child, 'end_lineno', getattr(child, 'lineno', last_line))
            if hasattr(child, 'body'):
                child_last_line = max(child_last_line, self.find_last_line(child))
            last_line = max(last_line, child_last_line)
        return last_line

    def extract_variables(self, node):
        variables = []
        for n in node.body:
            if isinstance(n, ast.Assign):
                for target in n.targets:
                    if isinstance(target, ast.Name):
                        variable_info = {'name': target.id, 'line_number': n.lineno}
                        variables.append(variable_info)
        return variables

    def extract_parameters(self, node):
        return [{'name': arg.arg, 'line_number': node.lineno} for arg in node.args.args]


def analyze_code_from_file(file_path):
    with open(file_path, 'r') as file:
        code = file.read()
    tree = ast.parse(code)
    analyzer = PythonParser()
    analyzer.visit(tree)
    return analyzer.structure


def python_analyze_code(code):
    tree = ast.parse(code)
    analyzer = PythonParser()
    analyzer.visit(tree)
    return analyzer.structure


if __name__ == "__main__":

    # Example usage with a file path
    # file_path = '~/code/github.com/geekan/MetaGPT/metagpt/provider/zhipuai_api.py'
    file_path = '~/code/github.com/c4fun/zhipuai-playground/samples/gradio-glm4.py'
    expanded_path = os.path.expanduser(file_path)

    result = analyze_code_from_file(expanded_path)
    json_result = json.dumps(result, indent=4)
    print(json_result)
