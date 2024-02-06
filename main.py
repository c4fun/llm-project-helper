import os

from llm_project_helper import RepoTraverser
from llm_project_helper.logs import logger

WORKSPACE_DIR = "workspaces"

if __name__ == '__main__':
    traverser = RepoTraverser()
    # concat current folder with workspaces 
    workspaces_dir = os.path.join(os.getcwd(), WORKSPACE_DIR)
    print(workspaces_dir)
    analyze_folder = traverser.traverse_repo(workspaces_dir)
    logger.info(f"Analyze folder: {analyze_folder}")

    # Traverse and output the xxx.py.analyze.md file
    traverser.analyze_repo(analyze_folder)

