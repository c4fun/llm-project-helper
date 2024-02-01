from zhipuai import ZhipuAI

import os
from dotenv import load_dotenv

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

        return partial_message
