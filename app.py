import streamlit as st
import google.generativeai as genai

with open('env') as f:
    env_content = f.read()

API_KEY = env_content.split('=')[1].strip()
#set genai api key
genai.configure(api_key=API_KEY)

model = genai.GenerativeModel('gemini-pro')

input = model.generate_content('what is your name?')

output = input.candidates[0].content.parts[0].text

print(output) 

