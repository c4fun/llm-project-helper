# 使用方法

## Quickstart

1. 安装`pip install -r requirements.txt`

2. 下载需要comment的仓库

3. 添加`.env`文件，其中REPO_PATH是你下载下来的代码仓库，请务必根据实际需要更改

```
REPO_PATH="/your/repo/path/"
ZHIPUAI_API_KEY="xxx.yyy"
```

4. 运行

它内部包含两个步骤：
- 4.1 使用`traverse_repo`来traverse整个代码仓库，生成对应的结构化的JSON。目前只实现了python
- 4.2 使用`analyze_repo`来分析4.1中生成的JSON，生成当前文件的概要。

```bash
python main.py
```
