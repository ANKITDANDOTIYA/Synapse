
import ollama

class LLM_Engine:
    def __init__(self):
        self.history = [ {"role": "system", "content": "You are Sarah, a highly advanced AI. Keep answers short, witty, and helpful."}
            ]
    def chat(self,text) :
        self.history.append({"role": "user", "content": text})
        response = ollama.chat(model= 'llama3.1', messages=self.history)
        reply = response['message']['content']
        self.history.append({"role": "assistant", "content": reply})
        return reply





