import os
from llm_project_helper.commenter.file_commenter_naive import FileCommenterNaive
from zhipuai.types.chat.chat_completion import CompletionMessage

from llm_project_helper.logs import logger

if __name__ == '__main__':

    file_path = '~/code/github.com/geekan/MetaGPT/metagpt/provider/zhipuai_api.py'  # 返回不全
    # file_path = '~/code/github.com/c4fun/zhipuai-playground/samples/gradio-glm4.py'
    expanded_path = os.path.expanduser(file_path)

    # test if the comment method is working
    file_commenter = FileCommenterNaive()
    result = file_commenter.comment(expanded_path)
    assert isinstance(result, CompletionMessage)
    logger.info(result.content)
