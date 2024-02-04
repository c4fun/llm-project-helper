from zhipuai import ZhipuAI

import os
from dotenv import load_dotenv
from llm_project_helper.logs import logger

class ZhipuAIAPI:
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
        # Get the value of the API key from the environment variable
        api_key = os.getenv("ZHIPUAI_API_KEY")
        self.client = ZhipuAI(api_key=api_key)

    def format_history(self, history):
        """
        Format the history for ZhipuAI API
        """
        history_zhipuai_format = []
        for human, assistant in history:
            history_zhipuai_format.append({"role": "user", "content": human })
            history_zhipuai_format.append({"role": "assistant", "content":assistant})
        return history_zhipuai_format
    
    def record_usage(self, response):
        """
        Record the usage of the response
        """
        usage = response.usage
        logger.info(f"prompt_tokens usage: {usage.prompt_tokens}")
        logger.info(f"completion_tokens usage: {usage.completion_tokens}")
        logger.info(f"total_tokens usage: {usage.total_tokens}")

    def predict_with_history(self, message, history=[]):
        """
        Predict using sse and stream is true
        """
        history.append({"role": "user", "content": message})
        logger.debug(f"history: {history}")

        response = self.client.chat.completions.create(
            model='glm-4',
            messages= history,
            stream=False
        )

        self.record_usage(response=response)
        return response.choices[0].message

    def predict(self, message, history=[]):
        """
        Predict using sse and stream is true
        """
        history_zhipuai_format = self.format_history(history)
        history_zhipuai_format.append({"role": "user", "content": message})

        response = self.client.chat.completions.create(
            model='glm-4',
            messages= history_zhipuai_format,
            stream=False
        )

        self.record_usage(response=response)
        return response.choices[0].message

    def predict_sse(self, message, history=[]):
        """
        Predict using sse and stream is true
        """
        history_zhipuai_format = self.format_history(history)
        history_zhipuai_format.append({"role": "user", "content": message})

        response = self.client.chat.completions.create(
            model='glm-4',
            messages= history_zhipuai_format,
            stream=True
        )

        partial_message = ""
        for chunk in response:
            if len(chunk.choices[0].delta.content) != 0:
                partial_message = partial_message + chunk.choices[0].delta.content
                yield partial_message

        self.record_usage(response=response)
        return partial_message
