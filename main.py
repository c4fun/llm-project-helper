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
    # add an argument called forced-re-analyze, which is a boolean,
    # and default is false, but if it is set, then it is true
    parser.add_argument(
        "--force-re-analyze",
        action="store_true",
        help="Force re-analyze the whole repo"
    )
    # add an argument called forced-re-comment, which is a boolean,
    # and default is false, but if it is set, then it is true
    parser.add_argument(
        "--force-re-comment",
        action="store_true",
        help="Force re-comment the whole repo"
    )

    args = parser.parse_args()
    repo_path = args.repo_path
    logger.info(f"Repo path: {repo_path}")
    # if the args does not have a repo_path, provide one
    if not repo_path:
        sys.exit("Please provide a repo path in --repo-path. Exiting")
    force_re_analyze = args.force_re_analyze
    logger.info(f"Force re-analyze: {force_re_analyze}")
    force_re_comment = args.force_re_comment
    logger.info(f"Force re-comment: {force_re_comment}")
    traverser = RepoTraverser(repo_path)

    # # concat current folder with workspaces; if env defined a home folder, then use that
    # workspaces_dir = os.path.join(os.getcwd(), WORKSPACE_DIR)
    # if (llm_project_helper.const.HOME_FOLDER_WORKSPACE_FLAG):
    #     workspaces_dir = llm_project_helper.const.WORKSPACE_DIR
    # logger.info(f"workspaces_dir: {workspaces_dir}")

    # 1. Doing the structure analyzation. LLM is not USED HERE
    # TODO: try to parse using treesitter. change the parser from python_parser to treesitter parser
    analyze_folder = traverser.traverse_repo()
    logger.info(f"Analyze folder: {analyze_folder}")

    # 2. Traverse and output the xxx.py.analyze.md file using LLM
    traverser.analyze_repo(analyze_folder, force_re_analyze)

    # 3. Analyze code section by section and output to xxx.py.comments.json
    traverser.sectioned_comment(analyze_folder, force_re_comment)
