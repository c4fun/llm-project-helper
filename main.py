import os

from llm_project_helper import RepoTraverser

WORKSPACE_DIR = "workspaces"

if __name__ == '__main__':
    traverser = RepoTraverser()
    # concat current folder with workspaces 
    workspaces_dir = os.path.join(os.getcwd(), WORKSPACE_DIR)
    print(workspaces_dir)
    traverser.traverse_repo(workspaces_dir)
