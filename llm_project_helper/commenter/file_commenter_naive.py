from llm_project_helper.provider import ZhipuAIAPI

PROMPT = """
作为一个经验丰富的Python程序员，你需要对以下的代码加上docstring的注释。
注意需要把类的注释放在类的上面，方法的注释放在方法上面，函数的注释放在函数的上面。请在注释中大致描述代码的功能，以及函数的输入和输出。
不要替换掉原来的任何注释。
你需要使用中文注释。
不要做任何解释，直接返回源代码即可，并且返回消息中前后都不允许使用```来包裹代码。

"""

class FileCommenterNaive:
    def __init__(self):
        self.api = ZhipuAIAPI()
        self.prompt = PROMPT

    def comment(self, file_path):
        with open(file_path, 'r') as file:
            code = file.read()
        self.prompt += code
        return self.api.predict(self.prompt)

