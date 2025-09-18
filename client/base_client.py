import websockets
import asyncio
from websockets.exceptions import ConnectionClosed
import json
import uuid
import sys

## Define connection handler
def handler(response: dict):

    ai_message = response.get('ai_message')

    return ai_message

end_list = ['Invocation failed.', 'Thanks for chatting. Have a great day!']

## Create a unique thread id
thread_id = str(uuid.uuid4())

## Define client loop function
async def basic_client():

    # FastAPI default socket - update if changing spec in server script
    uri = f"ws://127.0.0.1:8080/ws/chat"

    async with websockets.connect(uri, ping_interval=None) as websocket:        

        while True:

            try:
                # Gather user request with terminal input
                user_input = input('Your Message: ')
                #user_input = 'what a lovely day'
                data_dict = {'human_message': user_input,
                            'thread_id': thread_id}       

                # Send to server
                await websocket.send(json.dumps(data_dict))

                # Receive response
                raw_response = await websocket.recv()

                # Convert to python dictionary
                response = json.loads(raw_response)

                # Extract text
                ai_response = handler(response) 
                print(f'AI: {ai_response}')

                ## Close connection if ending message received
                for e in end_list:
                    if e in ai_response:                    
                        await websocket.close()
                        print('Connection Closed.')  
                        sys.exit()             

            except ConnectionClosed as e:
                print(f'Connection Closed: {e}')

if __name__ == "__main__":
    asyncio.run(basic_client())