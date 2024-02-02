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
STRUCTURE_ANALYZE_PROMPT = """
给你一个用JSON表示的python文件的结构，这个JSON文件中，imports表示导入的包，classes表示类，functions表示函数，methods表示类的方法，docstrings表示原来的注释。
另外line_number表示它们在文件中的行号。
你需要根据这个结构大致分析出这个文件的总体功能；然后再根据详细的类、类的方法、函数等结构，逐一写出它们的具体功能。
最终结尾必须输出[|$|EOS|$|]
输出可参考这个格式：
```
根据提供的JSON结构，这个Python文件（metagpt/provider/zhipuai_api.py）的主要功能是与智谱AI服务进行交互，提供异步和同步的方法来获取聊天回复。以下是详细的分析：

文件的总体功能：
该文件主要定义了一个与智谱AI模型进行交互的类ZhiPuAILLM，这个类实现了与智谱AI服务的接口调用，包括发送消息、接收回复、流式传输数据和处理成本更新。此外，还有一个枚举类ZhiPuEvent，它定义了与智谱AI交互过程中可能遇到的事件。

类和方法的详细功能：
类ZhiPuEvent：
- 功能: 定义了与智谱AI交互的事件类型。
- 类变量:
    - `ADD:` 表示添加新的事件。
    - `ERROR:` 表示发生错误的事件。
    - `INTERRUPTED:` 表示被中断的事件。
    - `FINISH:` 表示完成的事件。
类ZhiPuAILLM：
- 功能: 封装了与智谱AI服务的交互逻辑，提供同步和异步的方法来获取聊天回复。
- 方法:
    - `__init__(self):` 构造函数，初始化类实例。
    - `__init_zhipuai(self, config):` 初始化智谱AI服务的配置。
    - `_const_kwargs(self, messages, stream):` 构造请求的参数。
    - `_update_costs(self, usage):` 更新每次请求的令牌成本。
    - `completion(self, messages, timeout):` 同步方法，发送消息并获取回复。
    - `_achat_completion(self, messages, timeout):` 异步方法，发送消息并获取回复。
    - `acompletion(self, messages, timeout):` 异步方法，发送消息并获取回复。
    - `_achat_completion_stream(self, messages, timeout):` 异步方法，流式传输回复数据。
    - `acompletion_text(self, messages, stream, timeout):` 异步方法，根据是否开启流式传输返回不同格式的回复。

函数和装饰器的详细功能：
- `check_cmd_exists(command):` 检查命令是否存在于系统中。
- `require_python_version(req_version):` 检查Python版本是否满足要求。

导入的包和模块：
- `enum.Enum:` 可能用于定义枚举类。
- `openai:` 可能用于与OpenAI服务进行交互。

综上所述，该文件主要提供了一个与智谱AI服务交互的接口，通过定义的方法和类变量，用户可以方便地发送请求，获取聊天机器人的回复，并处理相关的事件和错误。[|$|EOS|$|]
```
需要解析的JSON如下：

"""