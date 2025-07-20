import os
import logging
from langchain_google_genai import ChatGoogleGenerativeAI

INITIAL_PROMPT = (
    "You are an interrogator. The subject is accused of assassinating Mayor Elias Vance, a polarizing figure behind the Urban Renewal Project and the Truth Serum Justice System. "
    "The subject is a prominent architect whose family home was demolished by Vance's project, and who became a public critic. The subject claims amnesia. "
    "Generate three questions for the first interview. Each question should be increasingly direct and accusatory, even if the logic is not fully sound. Do not be afraid to make assumptions or suggest the subject's guilt, but do not reveal any direct evidence. Give the subject opportunities to correct you, defend themselves, or argue their innocence. The questions should feel like the interrogator is trying to catch the subject in a lie or contradiction, and should provoke a defensive or clarifying response."
)
SUBSEQUENT_PROMPT = (
    "Continue the interrogation. Here is the full history of previous interview transcripts: {history}. "
    "Reference the evidence and public record from the case of Mayor Vance's assassination (see docs/crime-details.md). "
    "Generate three new, more specific questions that are even more direct and accusatory, making pointed suggestions about the subject's involvement or motives, even if the logic is not fully sound. The questions should challenge the subject's statements, point out possible inconsistencies, or suggest that the subject is hiding something. Always give the subject a chance to correct you, defend themselves, or argue their innocence. Do not reveal any direct evidence, but make the interrogator's suspicions clear."
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

import os


def get_llm():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("No Gemini API key found. Set GEMINI_API_KEY.")
    return ChatGoogleGenerativeAI(api_key=api_key, model="gemini-2.5-flash")


# Example function to generate questions
def generate_questions(history=None):
    llm = get_llm()
    if not history:
        prompt = INITIAL_PROMPT
    else:
        prompt = SUBSEQUENT_PROMPT.format(history=history)
    try:
        response = llm.invoke(prompt)
        # If response is a LangChain Message, get content
        if hasattr(response, "content"):
            text = response.content
        else:
            text = str(response)
        print(f"LLM response: {text}")
        logging.info(f"LLM response: {text}")

        # Try to split into 3 questions
        import re

        # Split by numbered list (1. 2. 3.) or newlines
        lines = re.split(r"\n+", text)
        # Filter: only keep lines that look like questions (end with ? or ?")
        questions = []
        for line in lines:
            line = line.strip()
            # Remove markdown bold/italics and leading numbering
            line = re.sub(r"^[*\d.\s:>\-]+", "", line)
            line = re.sub(r"[*_`]+", "", line)
            # Only keep lines that end with ? or ?"
            if line.endswith("?") or line.endswith('?"'):
                # Remove any trailing quotes
                line = line.rstrip('"').strip()
                questions.append(line)
        # If not enough, fallback to any line that is not rationale or intro
        if len(questions) < 3:
            for line in lines:
                line = line.strip()
                if not line or 'rationale' in line.lower() or 'here are' in line.lower():
                    continue
                if len(line) > 20 and line not in questions:
                    questions.append(line)
                if len(questions) >= 3:
                    break
        # Only return up to 3 questions, and strip leading/trailing quotes
        cleaned = []
        for q in questions[:3]:
            q = q.strip()
            # Remove leading/trailing quotes (single or double)
            q = q.lstrip('"\'').rstrip('"\'').strip()
            cleaned.append(q)
        return cleaned
    except Exception as e:
        # Log the error for debugging
        logging.error(f"LLM error in generate_questions: {e}")
        print(f"LLM error: {e}")
        return ["[LLM Error: Unable to generate questions]"]
