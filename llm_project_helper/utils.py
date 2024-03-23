import os
import re

from llm_project_helper.const import Language

def get_programming_language(file_extension: str) -> Language:
    """
    Returns the programming language based on the provided file extension.

    Args:
        file_extension (str): The file extension to determine the programming language of.

    Returns:
        Language: The programming language corresponding to the file extension. If the file extension is not found
        in the language mapping, returns Language.UNKNOWN.
    """
    language_mapping = {
        ".py": Language.PYTHON,
    }
    return language_mapping.get(file_extension, Language.UNKNOWN)

def get_file_extension(file_name: str) -> str:
    """
    Returns the extension of a file from its given name.

    Parameters:
        file_name (str): The name of the file.

    Returns:
        str: The extension of the file.

    """
    return os.path.splitext(file_name)[-1]

def get_bold_text(text):
    """
    Returns the provided text formatted to appear as bold when printed in the console.

    Args:
        text (str): The text to be formatted as bold.

    Returns:
        str: The formatted text, wrapped in ANSI escape sequences to achieve bold appearance.
    """
    return f"\033[01m{text}\033[0m"

def extract_content_from_markdown_code_block(markdown_code_block) -> str:
    """
    Extracts the content from a markdown code block.

    :param markdown_code_block: A string containing a markdown code block.
    :return: The content within the code block, with leading and trailing whitespace removed if found,
             or the original markdown code block if no match is found.
    """
    pattern = r"```(?:[a-zA-Z0-9]+)?\n(.*?)```"
    match = re.search(pattern, markdown_code_block, re.DOTALL)

    if match:
        return match.group(1).strip()
    else:
        return markdown_code_block.strip()