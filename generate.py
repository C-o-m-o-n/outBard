
import google.generativeai as genai

with open('env') as f:
    env_content = f.read()

GEMINI_API_KEY = env_content.split('GEMINI_API_KEY=')[1].strip()
#set genai api key
genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel('gemini-pro')

input = model.generate_content('what is the ocean?')

output = input.candidates[0].content.parts[0].text

print(output) 

