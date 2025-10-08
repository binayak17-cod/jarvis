import google.generativeai as genai
import user
# Gemini API key
genai.configure(api_key="AIzaSyCRw4Wax6bc0WnTFW5UWa1RKzarYV1Crjw")

model = genai.GenerativeModel("gemini-pro")  # Use "gemini-pro" or "gemini-1.5-pro"

prompt = "Can you tell me a joke?"

response = model.generate_content(prompt)

print(response.text)
