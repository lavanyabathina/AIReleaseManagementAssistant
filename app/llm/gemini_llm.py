from langchain_google_genai import ChatGoogleGenerativeAI

def get_gemini_llm(model,temperature):


    llm= ChatGoogleGenerativeAI(
        model=model
      #  temperature=temperature
    )
    return llm