from Utilities.config import variables
from langchain_core.prompts import PromptTemplate

prompts = {}
for prompt_name, prompt_data in variables['prompts'].items():
    prompts[prompt_name] = PromptTemplate(
        template=prompt_data['template'],
        input_variables=prompt_data['input_variables']
    )

question_category_prompt = prompts['question_category_prompt']
followup_prompt = prompts['followup_prompt']
question_for_rag = prompts['question_for_rag']
rag_prompt = prompts['rag_prompt']
grade_prompt = prompts['grade_prompt']
source_prompt = prompts['source_prompt']
