import argparse
import sys
from llm_project_helper import RepoTraverser
from llm_project_helper.logs import logger

from dotenv import load_dotenv
load_dotenv()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repo-path", 
        type=str,
        help="The code repo path to analyze"
    )
    
    args = parser.parse_args()
    repo_path = args.repo_path
    print(f"Repo path: {repo_path}")
    # if the args does not have a repo_path, provide one
    if not repo_path:
        sys.exit("Please provide a repo path in --repo-path. Exiting")

    traverser = RepoTraverser(repo_path)

    # # concat current folder with workspaces; if env defined a home folder, then use that
    # workspaces_dir = os.path.join(os.getcwd(), WORKSPACE_DIR)
    # if (llm_project_helper.const.HOME_FOLDER_WORKSPACE_FLAG):
    #     workspaces_dir = llm_project_helper.const.WORKSPACE_DIR
    # logger.info(f"workspaces_dir: {workspaces_dir}")

    # 1. Doing the structure analyzation. LLM is not USED HERE
    analyze_folder = traverser.traverse_repo()
    logger.info(f"Analyze folder: {analyze_folder}")

    # 2. Traverse and output the xxx.py.analyze.md file using LLM
    traverser.analyze_repo(analyze_folder)

    # 3. Analyze code section by section and output to xxx.py.comments.json
    traverser.sectioned_comment(analyze_folder)
