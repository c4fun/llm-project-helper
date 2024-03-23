import sys
sys.path.append('~/code/github.com/c4fun/llm-project-helper')
import os
import json
from llm_project_helper import utils
from llm_project_helper.treesitter import Treesitter, TreesitterMethodNode


def analyze_code_from_file(file_name):
    with open(file_name, 'r') as file:
        # code = file.read()
        file_bytes = file.read().encode()

        file_extension = utils.get_file_extension(file_name)
        programming_language = utils.get_programming_language(file_extension)

        treesitter_parser = Treesitter.create_treesitter(programming_language)
        treesitterNodes: list[TreesitterMethodNode] = treesitter_parser.parse(
            file_bytes
        )

        # 只能够得到当前主函数下面的方法
        # 问题：
        # 1. 没有得到__main__方法. main方法也应该是function_definition，只是它的identifier是main
        # 2. 没有得到class
        # 3. 没有得到class下面的方法
        # 4. 没有得到imports
        for node in treesitterNodes:
            # TODO: parse it and put it in json
            method_name_for_terminal_print = utils.get_bold_text(node.name)
            print(f'Method name: {method_name_for_terminal_print}')
            
            method_source_code = node.method_source_code
            print(f'Method source code: {method_source_code}')


if __name__ == "__main__":

    # Example usage with a file path
    # file_name = '~/code/github.com/c4fun/zhipuai-playground/samples/gradio-glm4.py'
    file_name = '~/code/github.com/geekan/MetaGPT/metagpt/provider/zhipuai_api.py'
    expanded_path = os.path.expanduser(file_name)

    result = analyze_code_from_file(expanded_path)
    json_result = json.dumps(result, indent=4)
    print(json_result)
