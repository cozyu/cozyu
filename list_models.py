import google.generativeai as genai
import os
import streamlit as st
import toml

try:
    secrets = toml.load(".streamlit/secrets.toml")
    api_key = secrets["GEMINI_API_KEY"]
except:
    api_key = os.environ.get("GEMINI_API_KEY")

genai.configure(api_key=api_key)
for m in genai.list_models():
    if "generateContent" in m.supported_generation_methods:
        print(m.name)
