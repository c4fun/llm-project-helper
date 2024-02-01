import os
import json
from dotenv import load_dotenv
from llm_project_helper.parser.python_parser import python_analyze_code
from loguru import logger
TREE_JSON = True

class RepoTraverser:
    def __init__(self):
        load_dotenv()
        self.repo_path = os.getenv("REPO_PATH")

    def traverse_repo(self, workspaces_dir):
        if not self.repo_path:
            raise ValueError("Repository path not configured in .env file")

        # get the last part of the repo path, seperated by '/' or '\'
        repo_name = self.repo_path.split(os.sep)[-1]
        if len(repo_name) == 0:
            repo_name = self.repo_path.split(os.sep)[-2]
        cur_ws_dir = os.path.join(workspaces_dir, repo_name)
        # create workspaces_dir if not exists
        if not os.path.exists(cur_ws_dir):
            logger.debug(f'Creating workspaces_dir: {cur_ws_dir}')
            os.makedirs(cur_ws_dir)

        for root, dirs, files in os.walk(self.repo_path):
            for file in files:
                # judge if the file ends with *.py, if not, continue
                if not file.endswith(".py"):
                    continue
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, self.repo_path)
                try:
                    with open(file_path, 'r', encoding='utf-8') as file_handler:
                        code = file_handler.read()
                    output = python_analyze_code(code)

                    # Output the result to a json file
                    output['relative_path'] = relative_path
                    
                    json_file = relative_path.replace(os.sep, '--').replace('.', '--') + '.json'

                    if TREE_JSON:
                        # separate the folder and *.py from relative_path by os.sep
                        py_path = relative_path.split(os.sep)[-1]
                        folder_path = relative_path.replace(py_path, '')

                        cur_file_path = os.path.join(cur_ws_dir, folder_path)
                        if not os.path.exists(cur_file_path):
                            logger.debug(f'Creating folder: {cur_file_path}')
                            os.makedirs(cur_file_path)
                        json_file = os.path.join(cur_file_path, py_path.replace('.', '--') + '.json')
                    with open(os.path.join(cur_ws_dir, json_file), 'w') as f:
                        json.dump(output, f, indent=4)

                except Exception as e:
                    logger.error(f"Error reading file {file_path}: {e}")

