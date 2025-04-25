import asyncio
import websockets
import json

clients = {}


async def send_command(websocket, command):
    await websocket.send(json.dumps({'type': 'eval', 'command': 'return ' + command}))
    return json.loads(await websocket.recv())


async def send_inspect(websocket, direction):
    await websocket.send(json.dumps({'type': 'inspect', 'direction': direction}))
    return json.loads(await websocket.recv())

async def send_dig(websocket, direction):
    await websocket.send(json.dumps({'type': 'dig', 'direction': direction}))
    return json.loads(await websocket.recv())

async def check_inventory(websocket):
    await websocket.send(json.dumps({'type': 'inventory'}))
    return json.loads(await websocket.recv())

async def send_place(websocket, direction):
    await websocket.send(json.dumps({'type': 'place', 'direction': direction}))
    return json.loads(await websocket.recv())

async def send_move(websocket, direction):
    await websocket.send(json.dumps({'type': 'move', 'direction': direction}))
    return json.loads(await websocket.recv())

async def send_suck(websocket, direction, count=None):
    if count is not None:
        await websocket.send(json.dumps({'type': 'move', 'direction': direction, 'count': count}))
        return json.loads(await websocket.recv())
    else:
        await websocket.send(json.dumps({'type': 'move', 'direction': direction}))
        return json.loads(await websocket.recv())

async def send_turn(websocket, direction):
    await websocket.send(json.dumps({'type': 'turn', 'direction': direction}))
    return json.loads(await websocket.recv())

async def send_refuel(websocket, slot=None):
    if slot is not None:
        await websocket.send(json.dumps({'type': 'refuel', 'slot': slot}))
        return json.loads(await websocket.recv())
    else:
        await websocket.send(json.dumps({'type': 'refuel'}))
        message = await websocket.recv()
        print(message)
        return json.loads(message)
    

async def go_mining(websocket):
    refueled = await send_refuel(websocket, 1)
    print(f"Refueled: {refueled}")
    location = await send_command(websocket, 'turtle.turnLeft()')
    block = await send_inspect(websocket, 'down')
    print(block)


async def handle_client(websocket):

    first_message = await websocket.recv()
    client_id = json.loads(first_message)['name']
    print("just got the first message")

    try:
        #async for message in websocket:

        if client_id not in clients:
            clients[client_id] = websocket


            #await websocket.send(json.dumps({'type': 'eval', 'command': 'turtle.turnLeft()'}))
        await go_mining(websocket)
        print("Just sent the test message")

    except websockets.exceptions.ConnectionClosed as e:
        print(f"Disconnected {client_id}")
    finally:
        del clients[client_id]


async def main():
    async with websockets.serve(handle_client, "localhost", 7788):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())