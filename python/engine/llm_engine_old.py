import json
from http.client import responses

import ollama

class LLM_Engine:
    def __init__(self):
        self.history = [ {"role": "system", "content": "You are Sarah, a highly advanced AI. Keep answers short, witty, and helpful."}
            ]
    def chat(self,text) :
        self.history.append({"role": "user", "content": text})
        response = ollama.chat(model= 'llama3.1:8b', messages=self.history)
        reply = response['message']['content']
        self.history.append({"role": "assistant", "content": reply})
        return reply

    def process_name_info(self, user_text):
        system_prompt = """
                You are a Data Extraction AI. You will receive a sentence about a person.
                You MUST return the output in VALID JSON format with keys: 'name' and 'info'.

                Rules:
                1. Extract the name (e.g., 'Rahul', 'Amit').
                2. 'info': Summarize ALL other details regarding the person (relationship, job, facts) into a short string.
                3. Do NOT add any extra text or markdown. Return ONLY the raw JSON.

                Example Input: "This is my brother Rahul, he is a doctor."
                Example Output: {"name": "Rahul", "info": "Brother, Doctor"}

                Example Input: "Ye mera dost Pankaj hai, ye Google me kaam karta hai."
                Example Output: {"name": "Pankaj", "info": "Friend, works at Google"}
                """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text}
        ]
        try:
            response = ollama.chat(model='llama3.1:8b', messages=messages)
            content = response['message']['content']
            content = content.replace("```json", "").replace("```", "").strip()

            return json.loads(content)

        except Exception as e:
            print(f"JSON Error: {e}")
            return None


