import os

from llm_project_helper import RepoTraverser
from llm_project_helper.logs import logger

WORKSPACE_DIR = "workspaces"

if __name__ == '__main__':
    traverser = RepoTraverser()
    # concat current folder with workspaces 
    workspaces_dir = os.path.join(os.getcwd(), WORKSPACE_DIR)
    print(workspaces_dir)
    # 1. Doing the structure analyzation. LLM is not USED HERE
    analyze_folder = traverser.traverse_repo(workspaces_dir)
    logger.info(f"Analyze folder: {analyze_folder}")

    # 2. Traverse and output the xxx.py.analyze.md file using LLM
    traverser.analyze_repo(analyze_folder)

    # 3. Analyze code section by section