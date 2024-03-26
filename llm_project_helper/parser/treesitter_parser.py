import sys
sys.path.append('~/code/github.com/c4fun/llm-project-helper')
import os
import json
from pydantic import BaseModel
from llm_project_helper import utils
from llm_project_helper.treesitter import Treesitter, TreesitterMethodNode, TreesitterResultNode
from llm_project_helper.logs import logger


def analyze_code_from_file(file_name):
    with open(file_name, 'r') as file:
        # code = file.read()
        file_bytes = file.read().encode()

        file_extension = utils.get_file_extension(file_name)
        programming_language = utils.get_programming_language(file_extension)

        treesitter_parser = Treesitter.create_treesitter(programming_language)
        
        treesitter_result_nodes: TreesitterResultNode = treesitter_parser.parse(file_bytes)
        # logger.debug(f'treesitter_result_nodes: {treesitter_result_nodes}')

        imports = treesitter_result_nodes.imports
        for import_item in imports:
            logger.debug(f'Import: {import_item.import_identifier, import_item.line_number, import_item.from_module}')
            # logger.debug(f'Import source code: {import_item.source_code}')
        
        classes = treesitter_result_nodes.classes
        for class_name, class_info in classes.items():
            logger.debug(f'Class name: {class_name}')
            # logger.debug(f'Class info: {class_info}')
            # logger.debug(f'Class source code: {class_info.source_code}')
            logger.debug(f'Class line number: {class_info.line_number}')
            logger.debug(f'Class end line number: {class_info.end_line_number}')
            # logger.debug(f'Class methods: {class_info.methods}')
            logger.debug('Class methods:')
            for method_name, method in class_info.methods.items():
                logger.debug(f'Class Method name: {method.name}')
                # logger.debug(f'Class Method line number: {method.line_number}')
                # logger.debug(f'Class Method end line number: {method.end_line_number}')
                # logger.debug(f'Class Method decorator_line_number: {method.decorator_line_number}')
                # logger.debug(f'Class Method async: {method.async_method_flag}')
                # logger.debug(f'Class Method parameters: {method.parameters}')
                # logger.debug(f'Class Method variables: {method.method_variables}')
            logger.debug(f'Class variables: {class_info.class_variables}')

        functions = treesitter_result_nodes.functions
        for function_name, function in functions.items():
            method_name_for_terminal_print = utils.get_bold_text(function.name)
            logger.debug(f'Method name: {method_name_for_terminal_print}')
            # logger.debug(f'Method source code: {function.source_code}')
            logger.debug(f'Method variables: {function.method_variables}')
            logger.debug(f'Method parameters: {function.parameters}')

            logger.debug(f'Method line number: {function.line_number}')
            logger.debug(f'Method end line number: {function.end_line_number}')
            logger.debug(f'Method decorator_line_number: {function.decorator_line_number}')

            logger.debug(f'Method async: {function.async_method_flag}')

        # In java, the global_variables is N/A; and the main_block is not implemented
        global_variables = treesitter_result_nodes.global_variables
        if global_variables is not None:
            for global_variable in global_variables:
                logger.debug(f'Global variable: {global_variable.name}')
                logger.debug(f'Global variable line number: {global_variable.line_number}')

        main_block = treesitter_result_nodes.main_block
        if main_block is not None:
            logger.debug(f'Main block: {main_block}')
            logger.debug(f'Main block source code: {main_block.source_code}')

        # result = {
        #     "imports": imports,
        #     "classes": classes,
        #     "functions": functions,
        #     "global_variables": global_variables,
        #     "main_block": main_block
        # }
        # return result
        return treesitter_result_nodes


if __name__ == "__main__":

    # Example usage with a file path
    # file_name = '~/code/github.com/c4fun/zhipuai-playground/samples/gradio-glm4.py'
    # file_name = '~/code/github.com/geekan/MetaGPT/metagpt/provider/zhipuai_api.py'
    # file_name = '~/code/github.com/geekan/MetaGPT/setup.py'
    # file_name = '~/code/github.com/geekan/MetaGPT/tests/metagpttools/test_azure_tts.py'

    file_name = '~/code/github.com/rvesse/airline/airline-prompts/src/main/java/com/github/rvesse/airline/prompts/Prompt.java'
    expanded_path = os.path.expanduser(file_name)

    result = analyze_code_from_file(expanded_path)
    # json_representation = import_node.json(exclude={'node'})
    # json_result = json.dumps(result, indent=4)
    # json_result = result.model_dump()  # a dictionary representation
    # json_result =result.model_dump_json(exclude={'node'})
    # exclude_structure = {
    #     'node': ...,
    #     'source_code': ...,
    #     'methods': {'__root__': {'node': ..., 'source_code': ...}},
    # }
    # result_dict = custom_serializer(result, exclude=exclude_structure)
    # json_result = json.dumps(result_dict, indent=4, default=str)
    result_dict = result.model_dump()
    logger.info(result_dict)
    json_result = json.dumps(result_dict, indent=4, default=str)
    logger.debug(json_result)

