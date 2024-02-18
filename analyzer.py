import os
from llm_project_helper.analyzer.file_summary_analyzer import FileSummaryAnalyzer

from llm_project_helper.logs import logger

if __name__ == '__main__':
    # Single GLM request
    # file_path = '~/code/github.com/c4fun/llm-project-helper/workspaces/MetaGPT/metagpt/provider/zhipuai_api.py.json'
    # file_path = '~/code/github.com/c4fun/llm-project-helper/workspaces/Rope/rope/VideoManager.py.json'
    # file_path = '~/code/github.com/c4fun/llm-project-helper/workspaces/Rope/Rope.py.son'

    # Multiple GLM request to test cases that needs manual continue
    file_path = '~/code/github.com/c4fun/llm-project-helper/workspaces/Rope/rope/GUI.py.json'

    expanded_path = os.path.expanduser(file_path)
    file_summary_analyzer = FileSummaryAnalyzer()
    result = file_summary_analyzer.analyze_file_summary(expanded_path)
    logger.info(result)
