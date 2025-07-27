from langchain_openai import AzureChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

def get_llm():
    return AzureChatOpenAI(
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_KEY"),
        api_version=os.getenv("AZURE_OPENAI_VERSION"),
        temperature=0.7,
        model_name="gpt-4o"
    )
