from app.llm.gemini_llm import *
from app.llm.openai_llm import *
from app.llm.claude_llm import *

def get_llm(application_config):


    llm_provider = application_config["llm"]["provider"]
    model=application_config["llm"]["model"]
    temperature=application_config["llm"]["temperature"]
    print("Getting llm:")
    print(f"llm provider: {llm_provider}")
    print(f"model: {model}")
    print(f"temperature:{temperature}")

    if llm_provider == "openai":
        return get_openai_llm(model,temperature)
    elif llm_provider == "gemini":
        return get_gemini_llm(model,temperature)
    elif llm_provider == "claude":
        return get_claude_llm(model,temperature)
    else:
        print(f"{llm_provider} is not supported")
        return

    
