import os
from langchain_openai import ChatOpenAI

LLM_API_KEY = os.environ.get("LLM_API_KEY")

# Prompts from tech spec
INITIAL_PROMPT = (
    "You are an interrogator. The subject is accused of assassinating Mayor Elias Vance, a polarizing figure behind the Urban Renewal Project and the Truth Serum Justice System. "
    "The subject is a prominent architect whose family home was demolished by Vance's project, and who became a public critic. The subject has amnesia. "
    "Generate three vague questions for the first interview, focusing on motive and opportunity."
)
SUBSEQUENT_PROMPT = (
    "Continue the interrogation. Here is the full history of previous interview transcripts: {history}. "
    "Reference the evidence and public record from the case of Mayor Vance's assassination (see docs/crime-details.md). "
    "Generate three new, more specific questions that probe for inconsistencies or new details."
)
PRECHECK_PROMPT = (
    "Based on the interview history so far: {history}, do you have enough information to make a final judgment of 'guilty', 'innocent', or 'inconclusive'? "
    "Respond with only 'yes' or 'no'. If the subject has contradicted established facts from docs/crime-details.md, respond with 'contradiction'."
)
ENDING_PROMPT = (
    "The interrogation is over. Here is the full transcript history: {history}. "
    "Based on the evidence and narrative in docs/crime-details.md, determine if the subject is 'guilty', 'innocent', or 'inconclusive'. Respond with only one of these words. "
    "If the subject contradicted a known truth, explain which truth was violated and state that the subject is immune to the truth serum and will be executed."
)

def get_llm():
    return ChatOpenAI(api_key=LLM_API_KEY)

# Example function to generate questions
def generate_questions(history=None):
    llm = get_llm()
    if not history:
        prompt = INITIAL_PROMPT
    else:
        prompt = SUBSEQUENT_PROMPT.format(history=history)
    return llm.invoke(prompt)
