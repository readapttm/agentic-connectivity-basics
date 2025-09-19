import json
from langchain_core.messages import AIMessage

## Function to process client messages
def extract_human_message(message: dict) -> tuple[str]:
        
    ## Unpack client supplied data
    input_data = json.loads(message)

    config_id = input_data['thread_id']
    content = input_data['human_message']
    thread_config = {"configurable": {"thread_id": config_id, "checkpoint_ns": ''}}

    return content, thread_config

## Function to process AI messages
def extract_AI_message(result: dict) -> dict:
        
    ai_message = result['messages'][-1]

    if isinstance(ai_message, AIMessage):
        response = {"ai_message": ai_message.content}
    else:
        response = {"ai_message": 'Invocation failed.'}

    return response
