from langchain_anthropic import ChatAnthropic
import os
def get_claude_llm(model,temperature):
    print("get claude llm")
    llm = ChatAnthropic(
    model=model,
    temperature=0,
    api_key=os.getenv("ANTHROPIC_API_KEY")
    )
    return llm