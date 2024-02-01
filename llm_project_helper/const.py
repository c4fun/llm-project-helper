import contextvars
import os
from pathlib import Path

from loguru import logger

import llm_project_helper

def get_llm_project_helper_package_root():
    """Get the root directory of the installed package."""
    package_root = Path(llm_project_helper.__file__).parent.parent
    for i in (".git", ".project_root", ".gitignore"):
        if (package_root / i).exists():
            break
    else:
        package_root = Path.cwd()

    logger.info(f"Package root set to {str(package_root)}")
    return package_root



def get_llm_project_helper_root():
    """Get the project root directory."""
    # Check if a project root is specified in the environment variable
    project_root_env = os.getenv("LLM_PROJECT_HELPER_PROJECT_ROOT")
    if project_root_env:
        project_root = Path(project_root_env)
        logger.info(f"PROJECT_ROOT set from environment variable to {str(project_root)}")
    else:
        # Fallback to package root if no environment variable is set
        project_root = get_llm_project_helper_package_root()
    return project_root


# LLM_PROJECT_HELPER PROJECT ROOT AND VARS

LLM_PROJECT_HELPER_ROOT = get_llm_project_helper_root()  # Dependent on LLM_PROJECT_HELPER_PROJECT_ROOT
