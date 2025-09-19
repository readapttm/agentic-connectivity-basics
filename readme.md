# A basic conversational LLM app using websocket connection

This is a basic demonstration of using a websocket to connect a langgraph application running on a server to a client via a websocket, enabling continuous back and forth communication. The advantage of a websocket is that it supports a continuous connection during human-in-the-loop workflows. Both streaming and non-streaming modes are provided.

A basic python test client is provided, but this can be replaced by any equivalent program (in any language) that implements the websocket protocol. This method can be used to embed LLM driven applications in third party platforms.

The application demonstrated here provides a simple chat functionality only, but can be extended in many directions including:
- Connection to MCP servers and other external data sources such as web search or data bases
- Teams of agents co-ordinated by the state graph
- Retrieval of datasets from vector stores
- Structured outputs (non-streaming only)

NB This demonstration is not suitable for production use. At a minimum, token-based authentication should be added to the websocket. A connection manager class can be added to handle multiple websocket connections.

## Instructions

Firstly, it is recommended to clone the repository, create a virtual environment and install the necessary packages as set out in requirements.txt. 

# Without streaming
To initiate the server, use the following commands in a command line terminal:
```
cd server
uvicorn base_hitl_server:app --ws-ping-timeout 300 --host 0.0.0.0 --port 8080
```

You will be asked to enter your API key at this point.

To run the client, in a separate command line terminal:
```
python client/base_client.py
```
You can then communicate with the LLM via the client terminal.

# With streaming
Note, if you are using a windows machine you may need to run this in WSL2 to see streaming behaviour.

In first terminal:
```
cd server
uvicorn base_hitl_server_streaming:app --ws-ping-timeout 300 --host 0.0.0.0 --port 8080
```

In a second terminal:
```
python client/stream_client.py
```