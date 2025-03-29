from langchain_google_genai import ChatGoogleGenerativeAI, HarmBlockThreshold, HarmCategory
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = "AIzaSyApo8UsS6q3RutbGa0FMp01Msz5BBSrqU4"

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-pro-exp-03-25",
    safety_settings={
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    },
    verbose=True,
    api_key=GOOGLE_API_KEY,
)