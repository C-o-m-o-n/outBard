import streamlit as st
import google.generativeai as genai

# with open('env') as f:
#     env_content = f.read()

# GEMINI_API_KEY = env_content.split('GEMINI_API_KEY=')[1].strip()
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

#set genai api key
genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel('gemini-pro')

def generateOutput(prompt):
    input = model.generate_content(prompt)

    output = input.candidates[0].content.parts[0].text

    return output

