# Development Design

- [x] Record the tree structure of the data
- [x] Output the structured json data using directory?
    - In this way, for every json, we can find its parent and grandparents till root. Thus, we might know more detail information regarding the code.
    - Use a TREE_JSON to alternate between tree and list modes
- [ ] Use a public LLM to comment
    - [ ] Use ZhipuAI LLM API
    - [ ] Comment the whole file
    - [ ] Comment one section by one section
- [ ] Write prompt to comment
- [ ] Write comments back into the file
    - [ ] Write-back should occur backward
- [ ] Use a private LLM through ollama to comment
