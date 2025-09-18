from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph
from langgraph.graph import START, END
from langgraph.graph.message import add_messages
from langgraph.types import interrupt, Command
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.messages import AnyMessage, HumanMessage
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from typing import Annotated
from typing_extensions import TypedDict, Literal
import getpass
import os

from utilities import extract_human_message, extract_AI_message

## Import OpenAI key (or whichever LLM service you prefer, simply replace the llm object definition below)
if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")
    
# Initialise OpenAI model
model_type = "gpt-4o"

class llm:
    model = ChatOpenAI(
    model=model_type,
    temperature=0,
)

## Define state - for this simple demo just a list of messages
class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]

## Define AI chat node
def AI_node(state: State) -> Command[Literal["human_node", END]]:

    ## Unpack message list
    messages = state['messages']

    ## Invoke chat
    chat_model = llm.model

    ## Define system prompt
    system = '''As an optimistic and outgoing personality, you can always find the positives in any situation.

                If the user indicates they wish to terminate the chat, return the string "END CHAT" only.'''

    # Define prompt template
    chat_prompt = ChatPromptTemplate.from_messages([
        ("system", system),
        ("human", "Messages: {messages}"),  
    ])

    # Define runnable
    chat_runner = chat_prompt | chat_model 

    # Invoke model on message list
    output = chat_runner.invoke({"messages": messages})        

    # If the user types 'end chat' send to END node
    if output.content.upper() == 'END CHAT':
        goto = END
    else:
        goto = "human_node"

    # Execute go to via Command pattern
    return Command(
        # state update
        update={"messages": [output]}, 
        # control flow
        goto=goto
    )

## Simple human node
def human_node(state: State) -> Command[Literal["AI_node", END]]:

    # Get value via interrupt
    value = interrupt( 
        {
            "messages": state["messages"] 
        }
    )     
    ## Get human feedback
    human_message = HumanMessage(content=value["human_message"])

    return {"messages": human_message}


## Create graph
graph = StateGraph(State)

# Nodes
graph.add_node("AI_node", AI_node)
graph.add_node("human_node", human_node)

# Edges
graph.add_edge(START, "AI_node")
graph.add_edge("human_node", "AI_node")

checkpointer = InMemorySaver() 
graph_app = graph.compile(checkpointer=checkpointer)

## Create application
app = FastAPI()

# Define token-verified websocket and enclosed logic
@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    
    # Accept connection
    await websocket.accept()

    ## Run AI model and return response to client
    try:
        # Receive client message
        message = await websocket.receive_text() 

        # Unpack
        content, thread_config = extract_human_message(message)

        # Invoke graph
        result = graph_app.invoke(
            {"messages": [HumanMessage(content=content)]}, 
            config=thread_config
        )

        # Extract LLM response
        response = extract_AI_message(result)

        # Send message to client
        await websocket.send_json(response)
    
    except Exception as graph_error:
        await websocket.send_json({"message": f"Error: Failed to process the graph: {graph_error}"}) 

    ## Continually converse with client
    try:
        while True:

            ## Receive user response
            message = await websocket.receive_text()

            # Unpack
            content, thread_config = extract_human_message(message)

            # Invoke graph with Commmand pattern to resume HITL node
            result = graph_app.invoke(Command(resume={"human_message": content}), 
                                        config=thread_config)

            # Extract most recent AI message
            response = extract_AI_message(result)

            # Handle simple logic to gracefully end conversation and close websocket
            if 'END CHAT' in response["ai_message"].strip(' \n'):

                message_to_send = response["ai_message"].strip(' \n').replace('END CHAT', '')

                response = {'ai_message': f'''{message_to_send} \nThanks for chatting. Have a great day!'''}
                
                await websocket.send_json(response)
                websocket.close()
                print('Connection closed.')
                break  

            # Send response to client
            await websocket.send_json(response) 

    except WebSocketDisconnect as d:
        await websocket.send_json({"message": f"WebSocket connection closed: {d}"})  