import websockets
import asyncio
from websockets.exceptions import ConnectionClosed
import json
import uuid
import sys

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

                # # Send to server
                await websocket.send(json.dumps(data_dict))

                # Temporary response storage
                raw_response_chunk = ''
                full_response = ''

                print('Agent Response: ', end="")

                # Process streamed output
                while raw_response_chunk != '<EOS>':

                    raw_response_chunk = await websocket.recv()

                    # Ignore server echo response
                    if raw_response_chunk == user_input:
                        continue

                    full_response += raw_response_chunk

                    if raw_response_chunk != '<EOS>':

                        print(raw_response_chunk, end="", flush=True)
                
                # Move to new line
                print('\n')

                ## Close connection if ending message received
                if user_input.lower() == 'end chat':               
                        await websocket.close()
                        print('End of chat.')  
                        sys.exit()             

            except ConnectionClosed as e:
                print(f'Connection Closed: {e}')

if __name__ == "__main__":
    asyncio.run(basic_client())