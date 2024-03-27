import json
from loguru import logger
from llm_project_helper.provider import ZhipuAIAPI
from llm_project_helper.const import CODE_SECTION_PROMPT_JSON as PROMPT, CODE_CLASS_PROMPT_JSON


class CodeSectionAnalyzer:
    def __init__(self):
        self.api = ZhipuAIAPI()
        self.prompt = PROMPT

    def analyze_code_section(self, json_file_path, summary_file_path, code_file_path):
        comments = []
        # 1. replace the markdown part in the prompt with the summary
        with open(summary_file_path, 'r') as file:
            summary = file.read()
            logger.debug(f"Summary is: \n{summary}")
            self.prompt = self.prompt.replace("```markdown```", "```markdown\n" + summary + "\n```")
            class_prompt = CODE_CLASS_PROMPT_JSON.replace("```markdown```", "```markdown\n" + summary + "\n```")

        # 2. Get every section(methods, functions) of the code through the json_file_path
        with open(json_file_path, 'r') as file:
            data = json.load(file)

        if 'functions' in data:
            function_pairs = self.process_functions(data['functions'])
            # 3. open code_file_path and only read relevant lines
            for start_line, end_line in function_pairs:
                lines = self.read_specific_lines(code_file_path, start_line, end_line)
                code = "\n".join(lines)
                logger.debug(f"Code is: \n{code}")

                # 4. Add prompt to get the result
                prompt = self.prompt + "\n" + "```\n" + code + "\n```"
                logger.debug(f"Prompt is: \n{prompt}")

                # 5. request LLM to get remarks
                chat_result = self.api.predict(prompt)
                remark = chat_result.content
                logger.info(f"Remark returned from LLM is: \n{remark}")
                # 6. add remarks and line numbers to the comments
                comments.append({"line_no": start_line, "remark": remark})

        if 'classes' in data:
            for class_name, class_details in data['classes'].items():
                logger.info(f"Class: {class_name}")
                class_pesudo_code = f"Class {class_name}:\n"
                class_descendant_remarks = ""
                # 3. open code_file_path and only read relevant lines
                if 'methods' in class_details:
                    method_pairs = self.process_functions(class_details['methods'])
                    for start_line, end_line in method_pairs:
                        lines = self.read_specific_lines(code_file_path, start_line, end_line)
                        code = "\n".join(lines)
                        logger.debug(f"Code is: \n{code}")

                        # 4. Add prompt to get the result
                        prompt = self.prompt + "\n" + "```\n" + class_pesudo_code + code + "\n```"
                        logger.debug(f"Prompt is: \n{prompt}")

                        # 5. request LLM to get remarks
                        chat_result = self.api.predict(prompt)
                        remark = chat_result.content
                        logger.info(f"Remark returned from LLM is: \n{remark}")
                        # 6. add remarks and line numbers to the comments
                        comments.append({"line_no": start_line, "remark": remark})
                        
                        # 7. affliate info in class_descendant_remarks
                        class_descendant_remarks += f"从 {start_line} 开始的方法:\n{remark}\n"

                # 8. Get class summary info
                cur_class_prompt = class_prompt.replace(
                    "[|$|class_descendant_remarks|$|]", class_descendant_remarks)
                logger.debug(f"Class Prompt is: \n{cur_class_prompt}")
                class_chat_result = self.api.predict(cur_class_prompt)
                class_remark = class_chat_result.content
                logger.info(f"Class Remark returned from LLM is: \n{class_remark}")
                # 9. add class remarks and line numbers to the comments
                comments.append({"line_no": class_details["line_number"], "remark": class_remark})


        # 7. Return the comments
        return comments

    def read_specific_lines(self, filename, start_line, end_line):
        """
        Reads specific lines from a file, given the start and end line numbers.

        Parameters:
        - filename: The path to the file.
        - start_line: The starting line number (inclusive).
        - end_line: The ending line number (inclusive).

        Returns:
        - A list of strings, where each string is a line from the specified range.
        """
        # Ensure start and end lines are positive and start_line is less than end_line
        if start_line < 1 or end_line < start_line:
            raise ValueError("Start line must be >= 1 and end line must be >= start line.")

        # Adjusting line numbers to zero-based indexing
        start_line -= 1
        end_line -= 1

        lines = []  # List to store the lines
        with open(filename, 'r') as file:
            for i, line in enumerate(file):
                if i > end_line:  # Stop reading if past the end line
                    break
                if i >= start_line:
                    lines.append(line.rstrip())  # Add line to list, stripping newline characters

        return lines

    def process_functions(self, functions):
        res = []
        if functions is not None:
            for func_name, details in functions.items():
                line_number = details["line_number"]
                end_line_number = details["end_line_number"]
                # contstruct a line_no, end_line_no pair
                res.append((line_number, end_line_number))
        return res
