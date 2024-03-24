import sys
sys.path.append('~/code/github.com/c4fun/llm-project-helper')
import os
import json
from llm_project_helper import utils
from llm_project_helper.treesitter import Treesitter, TreesitterMethodNode, TreesitterResultNode


def analyze_code_from_file(file_name):
    with open(file_name, 'r') as file:
        # code = file.read()
        file_bytes = file.read().encode()

        file_extension = utils.get_file_extension(file_name)
        programming_language = utils.get_programming_language(file_extension)

        treesitter_parser = Treesitter.create_treesitter(programming_language)

        # treesitterNodes: list[TreesitterMethodNode] = treesitter_parser.parse(
        #     file_bytes
        # )

        # # 只能够得到当前主函数下面的方法
        # # 问题：
        # # 1. 没有得到__main__方法. main方法也应该是function_definition，只是它的identifier是main
        # # 2. 没有得到class
        # # 3. 没有得到class下面的方法
        # # 4. 没有得到imports
        # for node in treesitterNodes:
        #     # TODO: parse it and put it in json
        #     method_name_for_terminal_print = utils.get_bold_text(node.name)
        #     print(f'Method name: {method_name_for_terminal_print}')
            
        #     source_code = node.source_code
        #     print(f'Method source code: {source_code}')
        
        treesitter_result_nodes: TreesitterResultNode = treesitter_parser.parse(file_bytes)
        print(f'treesitter_result_nodes: {treesitter_result_nodes}')

        imports = treesitter_result_nodes.imports
        # for import_item in imports:
        #     print(f'Import: {import_item.import_identifier, import_item.line_number, import_item.from_module}')
        #     print(f'Import source code: {import_item.source_code}')
        
        classes = treesitter_result_nodes.classes
        for class_name, class_info in classes.items():
            print(f'Class name: {class_name}')
            print(f'Class info: {class_info}')
            # print(f'Class source code: {class_info.source_code}')
            print(f'Class line number: {class_info.line_number}')
            print(f'Class end line number: {class_info.end_line_number}')
            print(f'Class methods: {class_info.methods}')
            print('Class methods:')
            for method in class_info.methods:
                print(f'Class Method name: {method.name}')
                # print(f'Class Method line number: {method.line_number}')
                # print(f'Class Method end line number: {method.end_line_number}')
                # print(f'Class Method decorator_line_number: {method.decorator_line_number}')
                # print(f'Class Method async: {method.async_method_flag}')
                # print(f'Class Method parameters: {method.parameters}')
                # print(f'Class Method variables: {method.method_variables}')
                print()
            print(f'Class variables: {class_info.class_variables}')

        functions = treesitter_result_nodes.functions
        for function in functions:
            method_name_for_terminal_print = utils.get_bold_text(function.name)
            print(f'Method name: {method_name_for_terminal_print}')
            # print(f'Method source code: {function.source_code}')
            # print(f'Method variables: {function.method_variables}')
            # print(f'Method parameters: {function.parameters}')

            # print(f'Method line number: {function.line_number}')
            # print(f'Method end line number: {function.end_line_number}')
            # print(f'Method decorator_line_number: {function.decorator_line_number}')

            # print(f'Method async: {function.async_method_flag}')



if __name__ == "__main__":

    # Example usage with a file path
    file_name = '~/code/github.com/c4fun/zhipuai-playground/samples/gradio-glm4.py'
    # file_name = '~/code/github.com/geekan/MetaGPT/metagpt/provider/zhipuai_api.py'
    expanded_path = os.path.expanduser(file_name)

    result = analyze_code_from_file(expanded_path)
    json_result = json.dumps(result, indent=4)
    print(json_result)

