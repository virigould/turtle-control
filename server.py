import asyncio
import websockets
import json
import uuid

current_commands = {}
current_id = 0
clients = {}


async def send_command(websocket, command):
    id = str(uuid.uuid4())
    await websocket.send(json.dumps({'id': id, 'type': 'eval', 'command': 'return ' + command}))
    current_commands[id] = asyncio.get_event_loop().create_future()
    response = await current_commands[id]
    return response


async def send_gps(websocket):
    id = str(uuid.uuid4())
    await websocket.send(json.dumps({'id': id, 'type': 'gps'}))
    current_commands[id] = asyncio.get_event_loop().create_future()
    response = await current_commands[id]
    return response

async def send_inspect(websocket, direction):
    print("in send inspect")
    id = str(uuid.uuid4())
    await websocket.send(json.dumps({'id': id,'type': 'inspect', 'direction': direction}))
    current_commands[id] = asyncio.get_event_loop().create_future()
    response = await current_commands[id]
    return response

async def send_dig(websocket, direction):
    id = str(uuid.uuid4())
    await websocket.send(json.dumps({'id': id,'type': 'dig', 'direction': direction}))
    current_commands[id] = asyncio.get_event_loop().create_future()
    response = await current_commands[id]
    return response

async def check_inventory(websocket):
    id = str(uuid.uuid4())
    await websocket.send(json.dumps({'id': id,'type': 'inventory'}))
    current_commands[id] = asyncio.get_event_loop().create_future()
    response = await current_commands[id]
    return response

async def send_place(websocket, direction):
    id = str(uuid.uuid4())
    await websocket.send(json.dumps({'id': id,'type': 'place', 'direction': direction}))
    current_commands[id] = asyncio.get_event_loop().create_future()
    response = await current_commands[id]
    return response

async def send_move(websocket, direction):
    id = str(uuid.uuid4())
    await websocket.send(json.dumps({'id': id,'type': 'move', 'direction': direction}))
    current_commands[id] = asyncio.get_event_loop().create_future()
    response = await current_commands[id]
    return response

async def send_suck(websocket, direction, count=None):
    if count is not None:
        id = str(uuid.uuid4())
        await websocket.send(json.dumps({'id': id,'type': 'move', 'direction': direction, 'count': count}))
        current_commands[id] = asyncio.get_event_loop().create_future()
        response = await current_commands[id]
        return response
    else:
        id = str(uuid.uuid4())
        await websocket.send(json.dumps({'id': id,'type': 'move', 'direction': direction}))
        current_commands[id] = asyncio.get_event_loop().create_future()
        response = await current_commands[id]
        return response

async def send_turn(websocket, direction):
    id = str(uuid.uuid4())
    await websocket.send(json.dumps({'id': id,'type': 'turn', 'direction': direction}))
    current_commands[id] = asyncio.get_event_loop().create_future()
    response = await current_commands[id]
    #print("after send turn response await")
    #print(response)
    return response

async def send_refuel(websocket, slot=None):
    if slot is not None:
        id = str(uuid.uuid4())
        await websocket.send(json.dumps({'id': id,'type': 'refuel', 'slot': slot}))
        current_commands[id] = asyncio.get_event_loop().create_future()
        response = await current_commands[id]
        return response
    else:
        id = str(uuid.uuid4())
        await websocket.send(json.dumps({'id': id,'type': 'refuel'}))
        current_commands[id] = asyncio.get_event_loop().create_future()
        response = await current_commands[id]
        return response
    
"""
Effectively a test method to try working on if the commands work and return what we need

Eventually we will make a async queue that gets propigated with commands to send to the turtle based off of user input we provide it from a turtle admin control
"""
async def go_mining(websocket):
    await send_gps(websocket)
    for i in range(20):
        print("iteration " + str(i))
        print(await send_move(websocket, "down"))
    # refueled = await send_refuel(websocket, 1)
    # print(f"Refueled: {refueled}")
    print("in go mining")
    await send_turn(websocket, 'left')
    print("after turn left in go mining")
    #print(location)
    await send_inspect(websocket, 'down')
    print("after the send inspect")
    # for i in range(20):
    #     print("iteration " + str(i))
    #     print(await send_move(websocket, "up"))
    #print("after the up movement")
    #print(block)
    location = await send_gps(websocket)
    print(location)


# async def keep_alive(websocket, interval=30):
#     while True:
#         try:
#             await websocket.ping()
#             #await websocket.recv()
#             await asyncio.sleep(interval)
#         except websockets.ConnectionClosed:
#             break

async def handle_message(websocket):
    async for message in websocket:
        print("Message: " + message)
        mssg = json.loads(message)
        if "computer_name" in mssg:
            client_id = mssg["computer_name"]
            print(client_id)
            if client_id not in clients:
                    clients[client_id] = websocket
            if "job" in mssg:
                print(mssg['job'])
                if mssg["job"] == "miner":
                    #this has to be in the background and can not be awaited as it will block all the threads
                    asyncio.get_event_loop().create_task(go_mining(websocket))
        elif "command_id" in mssg:
            if mssg["command_id"] in current_commands:
                command = current_commands.pop(mssg["command_id"])
                command.set_result(mssg)
    




async def handle_client(websocket):

    #asyncio.create_task(keep_alive(websocket))
    

    try:
        
        

        await handle_message(websocket)
        #while True:
            

            #await websocket.send(json.dumps({'type': 'eval', 'command': 'turtle.turnLeft()'}))
        #await go_mining(websocket)
        print("Just sent the test message")
        

    except websockets.exceptions.ConnectionClosed as e:
        print("The websocket closed unexpectedly: " + e)
        pass
    # finally:
    #     del clients[client_id]


async def main():
    async with websockets.serve(handle_client, "localhost", 7788):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())