### docs-comments-ai如何用treesitter分析的docstring

1. 涉及到的代码如下

```python
    def traverse_repo(self):
        """
        Traverse the whole repository and analyze the code structure of each file.

        :return: traverse the whole repo and analyze their code structure and get result
        """
        
        cur_ws_dir = self.get_cur_ws_dir()

        for root, dirs, files in os.walk(self.repo_path):
            for file in files:
                blah blah blah...
```

2. 然后，在treesitter.py的代码中，可以看到用了query_code来实现查询
```python
    def _query_doc_comment(self, node: tree_sitter.Node):
        query_code = """
            (function_definition
                body: (block . (expression_statement (string)) @function_doc_str))
        """
        doc_str_query = self.language.query(query_code)
        doc_strs = doc_str_query.captures(node)

        if doc_strs:
            return doc_strs[0][0].text.decode()
        else:
            return None
```

3. 我们再去实际打印出的treesitter元素表去查看，可以看到对应的`function_definition`的block中确实有一段string，对应的正好是第一段代码的注释的范围

```
function_definition 1836 4284
def 1836 1839
identifier 1840 1853
parameters 1853 1859
( 1853 1854
identifier 1854 1858
) 1858 1859
: 1859 1860
block 1869 4284
expression_statement 1869 2057
string 1869 2057
string_start 1869 1872
string_content 1872 2054
string_end 2054 2057
```