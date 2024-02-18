from loguru import logger
from llm_project_helper.provider import ZhipuAIAPI
from llm_project_helper.const import STRUCTURE_ANALYZE_PROMPT as PROMPT

EOS_token = "[|$|EOS|$|]"
CONTINUE_PHRASE = "继续。总结时务必输出结尾符[|$|EOS|$|]"
MAX_REQ = 3


class FileSummaryAnalyzer:
    def __init__(self):
        self.api = ZhipuAIAPI()
        self.prompt = PROMPT

    def analyze_file_summary(self, file_path):
        with open(file_path, 'r') as file:
            json_code = file.read()
        EOS_flag = False
        count = 0
        result = ""
        history = []

        while (EOS_flag is False and count < MAX_REQ):
            if (count == 0):
                self.prompt += json_code
            elif (count >= 1):
                self.prompt = CONTINUE_PHRASE

            chat_result_completion_message = self.api.predict_with_history(self.prompt, history=history)
            chat_result = chat_result_completion_message.content
            logger.debug(f"chat_result: {chat_result}")

            if EOS_token in chat_result:
                EOS_flag = True
                chat_result = chat_result.replace(EOS_token, "")
            if EOS_flag is False:
                # remove chat_result's last sentence. Solving the problem of incomplete sentence
                chat_result = chat_result.rsplit('\n', 1)[0] + '\n'
            result += chat_result
            count += 1
            history.append({"role": "assistant", "content": chat_result})
        return result
