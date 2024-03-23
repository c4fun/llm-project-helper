import os
import json
from dotenv import load_dotenv
from llm_project_helper.parser.python_parser import python_analyze_code
from llm_project_helper.logs import logger
from llm_project_helper.analyzer.file_summary_analyzer import FileSummaryAnalyzer
from llm_project_helper.analyzer.code_section_analyzer import CodeSectionAnalyzer
from llm_project_helper.const import TREE_JSON, FORCE_RE_ANALYZE, FORCE_RE_COMMENT, AVAILABLE_SAAS, WORKSPACE_DIR

load_dotenv()


class RepoTraverser:
    def __init__(self, repo_path):
        self.repo_path = repo_path

    def get_cur_ws_dir(self):
        if not self.repo_path:
            raise ValueError("Repository path not configured in .env file")
        workspaces_dir = WORKSPACE_DIR
        logger.info(f"workspaces_dir: {workspaces_dir}")

        # get the last part of the repo path, seperated by '/' or '\'
        repo_name = self.repo_path.split(os.sep)[-1]
        if len(repo_name) == 0:
            repo_name = self.repo_path.split(os.sep)[-2]

        # REPO_PATH="/home/richardliu/code/github.com/LargeWorldModel/LWM"
        # find if REPO_PATH contains aviailable SAAS. If so, then use the last part of the path(including the avaible saas) as the repo_name
        for saas in AVAILABLE_SAAS:
            if saas in self.repo_path:
                logger.info(f"repo_path contains saas: {saas}")
                repo_name = self.repo_path.split(saas)[-1]
                repo_name = saas + repo_name
                break

        logger.info(f"repo_name from get_cur_ws_dir: {repo_name}")

        cur_ws_dir = os.path.join(workspaces_dir, repo_name)
        # create workspaces_dir if not exists
        if not os.path.exists(cur_ws_dir):
            logger.debug(f'Creating workspaces_dir: {cur_ws_dir}')
            os.makedirs(cur_ws_dir)
        return cur_ws_dir

    def traverse_repo(self):
        """
        Traverse the whole repository and analyze the code structure of each file.

        :return: traverse the whole repo and analyze their code structure and get result
        """
        
        cur_ws_dir = self.get_cur_ws_dir()

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

                    json_file = relative_path.replace(os.sep, '--') + '.json'

                    if TREE_JSON:
                        # separate the folder and *.py from relative_path by os.sep
                        py_path = relative_path.split(os.sep)[-1]
                        folder_path = relative_path.replace(py_path, '')

                        cur_file_path = os.path.join(cur_ws_dir, folder_path)
                        # src_file_path = os.path.join(self.repo_path, folder_path)
                        if not os.path.exists(cur_file_path):
                            logger.debug(f'Creating folder: {cur_file_path}')
                            os.makedirs(cur_file_path)
                        json_file = os.path.join(cur_file_path, py_path + '.json')

                        # # 之前是临时的直接拷贝，后续需要通过规则获取源文件，或者记录在json文件中
                        # # DONE: 在sectioned_comment通过规则获取源文件
                        # src_file = os.path.join(src_file_path, py_path)
                        # # copy the src_file to cur_file_path
                        # shutil.copy2(src_file, os.path.join(cur_file_path, py_path))

                    with open(os.path.join(cur_ws_dir, json_file), 'w') as f:
                        json.dump(output, f, indent=4)

                except Exception as e:
                    logger.error(f"Error reading file {file_path}: {e}")
        return cur_ws_dir

    def analyze_repo(self, analyze_folder, force_re_anlayze):
        if not analyze_folder:
            raise ValueError("Analyze folder not found")

        for root, dirs, files in os.walk(analyze_folder):
            for file in files:
                # include *.json but exclude *.comments.json
                if not file.endswith(".json") or file.endswith(".comments.json"):
                    continue
                file_path = os.path.join(root, file)
                # save result in the folder as file_path, add only the suffix .analyze.md
                analyze_file = file_path.replace('.json', '.analyze.md')
                # if the file exists, skip the analyze and continue
                # DONE: if FORCE_RE_ANALYZE is on, then re-do the analysis
                if os.path.exists(analyze_file) and not FORCE_RE_ANALYZE and not force_re_anlayze:
                    continue
                file_summary_analyzer = FileSummaryAnalyzer()
                result = file_summary_analyzer.analyze_file_summary(file_path)
                logger.info(result)
                with open(analyze_file, 'w') as f:
                    f.write(result)

    def sectioned_comment(self, analyze_folder, force_re_comment):
        if not analyze_folder:
            raise ValueError("Analyze folder not found")

        for root, dirs, files in os.walk(analyze_folder):
            for file in files:
                if not file.endswith(".json") or file.endswith(".comments.json"):
                    continue
                file_path = os.path.join(root, file)
                # save result in the folder as file_path, add only the suffix .comments.json
                analyze_file = file_path.replace('.json', '.comments.json')
                # if the file exists, skip the analyze and continue
                # DONE: if FORCE_RE_COMMENT is on, then re-do the analysis
                if os.path.exists(analyze_file) and not FORCE_RE_COMMENT and not force_re_comment:
                    continue
                # get relevant summary file: *.py.analyze.md
                summary_file = file_path.replace('.json', '.analyze.md')
                # get relevant code file:
                code_file = file_path.replace('.json', '')
                local_repo_folder = os.getenv("LOCAL_REPO_FOLDER")
                # # if local_repo_folder does not have trailing os.sep, add it. AS WORKSPACE_DIR does not have trailing os.sep, this is not needed
                # if local_repo_folder[-1] != os.sep:
                #     local_repo_folder += os.sep
                code_file = code_file.replace(WORKSPACE_DIR, local_repo_folder)
                logger.info(f"code_file: {code_file}")

                code_section_analyzer = CodeSectionAnalyzer()
                comments = code_section_analyzer.analyze_code_section(file_path, summary_file, code_file)
                logger.info(f"Comments of file {code_file} is:\n {comments}")
                result = {
                    "file_path": code_file,  # DONE: 这里的code_file需要使用SaaS地址+群组+项目+文件名方式
                    "comments": comments
                }
                with open(analyze_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=4, ensure_ascii=False)
