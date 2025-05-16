import asyncio
import websockets
import json
import uuid

current_commands = {}
current_id = 0
clients = {}


async def send_command(websocket, command):
    id = str(uuid.uuid4())
    await websocket.send(
        json.dumps({"id": id, "type": "eval", "command": "return " + command})
    )
    current_commands[id] = asyncio.get_event_loop().create_future()
    response = await current_commands[id]
    return response


async def send_gps(websocket):
    id = str(uuid.uuid4())
    await websocket.send(json.dumps({"id": id, "type": "gps"}))
    current_commands[id] = asyncio.get_event_loop().create_future()
    response = await current_commands[id]
    return response


async def send_inspect(websocket, direction):
    print("in send inspect")
    id = str(uuid.uuid4())
    await websocket.send(
        json.dumps({"id": id, "type": "inspect", "direction": direction})
    )
    current_commands[id] = asyncio.get_event_loop().create_future()
    response = await current_commands[id]
    return response


async def send_dig(websocket, direction):
    id = str(uuid.uuid4())
    await websocket.send(json.dumps({"id": id, "type": "dig", "direction": direction}))
    current_commands[id] = asyncio.get_event_loop().create_future()
    response = await current_commands[id]
    return response


async def check_inventory(websocket):
    id = str(uuid.uuid4())
    await websocket.send(json.dumps({"id": id, "type": "inventory"}))
    current_commands[id] = asyncio.get_event_loop().create_future()
    response = await current_commands[id]
    return response


async def send_place(websocket, direction):
    id = str(uuid.uuid4())
    await websocket.send(
        json.dumps({"id": id, "type": "place", "direction": direction})
    )
    current_commands[id] = asyncio.get_event_loop().create_future()
    response = await current_commands[id]
    return response


async def send_move(websocket, direction):
    id = str(uuid.uuid4())
    await websocket.send(json.dumps({"id": id, "type": "move", "direction": direction}))
    current_commands[id] = asyncio.get_event_loop().create_future()
    response = await current_commands[id]
    return response


async def send_suck(websocket, direction, count=None):
    if count is not None:
        id = str(uuid.uuid4())
        await websocket.send(
            json.dumps(
                {"id": id, "type": "move", "direction": direction, "count": count}
            )
        )
        current_commands[id] = asyncio.get_event_loop().create_future()
        response = await current_commands[id]
        return response
    else:
        id = str(uuid.uuid4())
        await websocket.send(
            json.dumps({"id": id, "type": "move", "direction": direction})
        )
        current_commands[id] = asyncio.get_event_loop().create_future()
        response = await current_commands[id]
        return response


async def send_turn(websocket, direction):
    id = str(uuid.uuid4())
    await websocket.send(json.dumps({"id": id, "type": "turn", "direction": direction}))
    current_commands[id] = asyncio.get_event_loop().create_future()
    response = await current_commands[id]
    # print("after send turn response await")
    # print(response)
    return response


async def send_refuel(websocket, slot=None):
    if slot is not None:
        id = str(uuid.uuid4())
        await websocket.send(json.dumps({"id": id, "type": "refuel", "slot": slot}))
        current_commands[id] = asyncio.get_event_loop().create_future()
        response = await current_commands[id]
        return response
    else:
        id = str(uuid.uuid4())
        await websocket.send(json.dumps({"id": id, "type": "refuel"}))
        current_commands[id] = asyncio.get_event_loop().create_future()
        response = await current_commands[id]
        return response


def check_do_not_break(name):
    do_not_break_list = [
        # to do
        # need to fill this with blocks we actually do not want the turtles to break.
        "minecraft:stone"
    ]
    if name in do_not_break_list:
        return True
    return False


class Turtle:
    def __init__(self, name, websocket):
        self.location = {"x": 0, "y": 0, "z": 0}
        self.name = name
        self.direction = "x"
        self.websocket = websocket
        self.block_buffer = []
        self.last_refuel = 10

    async def check_refuel(self):
        if self.last_refuel == 10:
            self.last_refuel = 0
            await send_refuel(self.websocket)

    # def check_geofence():

    async def forward(self):
        return await send_move(self.websocket, "forward")

    async def back(self):
        return await send_move(self.websocket, "back")

    async def up(self):
        return await send_move(self.websocket, "up")

    async def down(self):
        return await send_move(self.websocket, "down")

    async def turn_left(self):
        return await send_turn(self.websocket, "left")

    async def turn_right(self):
        return await send_turn(self.websocket, "right")

    async def inspect_up(self):
        return await send_inspect(self.websocket, "up")

    async def inspect_down(self):
        return await send_inspect(self.websocket, "down")

    async def inspect(self):
        return await send_inspect(self.websocket, "forward")

    async def place(self):
        return await send_place(self.websocket, "forward")

    async def place_up(self):
        return await send_place(self.websocket, "up")

    async def place_down(self):
        return await send_place(self.websocket, "down")

    async def dig(self):
        return await send_dig(self.websocket, "forward")

    async def dig_up(self):
        return await send_dig(self.websocket, "up")

    async def dig_down(self):
        return await send_dig(self.websocket, "down")

    async def full_inspect(self):
        results = {}
        results["up"] = await self.inspect_up()
        results["down"] = await self.inspect_down()
        results["forward"] = await self.inspect()
        await self.turn_left()
        results["left"] = await self.inspect()
        await self.turn_left()
        results["behind"] = await self.inspect()
        await self.turn_left()
        results["right"] = await self.inspect()
        await self.turn_left()
        return results

    async def inspect_walls(self):
        results = {}
        results["up"] = await self.inspect_up()
        results["down"] = await self.inspect_down()
        await self.turn_left()
        results["left"] = await self.inspect()
        await self.turn_right()
        await self.turn_right()
        results["right"] = await self.inspect()
        await self.turn_left()
        return results

    async def inspect_top(self):
        results = {}
        results["up"] = await self.inspect_up()
        await self.turn_left()
        results["left"] = await self.inspect()
        await self.turn_right()
        await self.turn_right()
        results["right"] = await self.inspect()
        await self.turn_left()
        return results


    async def inspect_bottom(self):
        results = {}
        results["down"] = await self.inspect_down()
        await self.turn_left()
        results["left"] = await self.inspect()
        await self.turn_right()
        await self.turn_right()
        results["right"] = await self.inspect()
        await self.turn_left()
        return results

    """
Effectively a test method to try working on if the commands work and return what we need

Eventually we will make a async queue that gets propigated with commands to send to the turtle based off of user input we provide it from a turtle admin control
"""

def is_valuable(block):
    if block is None:
        return False
    name = block.get("name", "")
    valuable_keywords = ["coal", "iron", "gold", "copper", "diamond", "lapis", "emerald", "redstone"]
    return any(ore in name for ore in valuable_keywords)

def dig_valuable(blocks):
    """
    takes a dictionary of direction -> block info, and returns a list of
    instructions to efficiently mine valuable ores.
    :param blocks: Dictionary like {"up": {...}, "left": {...}, ...}
    :return: List of instructions (e.g. ["dig_down", "turn_left", "dig", ...])
    """
    valuable_directions = [direction for direction, block in blocks.items() if is_valuable(block)]
    instructions = []

    for direction in ["down", "up", "forward"]:
        if direction in valuable_directions:
            instructions.append(f"dig_{direction}" if direction != "forward" else "dig")
            valuable_directions.remove(direction)

    if "left" in valuable_directions and "behind" in valuable_directions and "right" not in valuable_directions:
        instructions += ["turn_left", "dig", "turn_left", "dig", "turn_left", "turn_left"]
        valuable_directions.remove("left")
        valuable_directions.remove("behind")
    elif "right" in valuable_directions and "behind" in valuable_directions and "left" not in valuable_directions:
        instructions += ["turn_right", "dig", "turn_right", "dig", "turn_left", "turn_left"]
        valuable_directions.remove("right")
        valuable_directions.remove("behind")
    elif all(d in valuable_directions for d in ["left", "right", "behind"]):
        instructions += ["turn_left", "dig", "turn_left", "dig", "turn_left", "dig", "turn_left"]
        valuable_directions.remove("left")
        valuable_directions.remove("right")
        valuable_directions.remove("behind")

    turn_map = {
        "left": ["turn_left", "dig", "turn_right"],
        "right": ["turn_right", "dig", "turn_left"],
        "behind": ["turn_left", "turn_left", "dig", "turn_left", "turn_left"]
    }

    for direction in ["left", "right", "behind"]:
        if direction in valuable_directions:
            instructions += turn_map[direction]

    return instructions

async def go_mining(turtle):
    turtle.location = await send_gps(turtle.websocket)
    print(turtle.location)
    home = turtle.location.copy()
    instructions = []
    x = 0
    y = 0
    z = 0
    blocks = await turtle.full_inspect()
    if blocks:
        instructions = dig_valuable(blocks)

    # Map instruction strings to Turtle methods
    instruction_map = {
        "dig": turtle.dig,
        "dig_up": turtle.dig_up,
        "dig_down": turtle.dig_down,
        "turn_left": turtle.turn_left,
        "turn_right": turtle.turn_right,
    }

    for instruction in instructions:
        action = instruction_map.get(instruction)
        if action:
            await action()
        else:
            print(f"Unknown instruction: {instruction}")









    # # refueled = await send_refuel(websocket, 1)
    # # print(f"Refueled: {refueled}")
    # print("in go mining")
    # await send_turn(websocket, "left")
    # print("after turn left in go mining")
    # # print(location)
    # await send_inspect(websocket, "down")
    # print("after the send inspect")
    # for i in range(20):
    #     print("iteration " + str(i))
    #     print(await send_move(websocket, "up"))
    # # print("after the up movement")
    # # print(block)
    # location = await send_gps(websocket)
    # print(location)
    # pass


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
                print(mssg["job"])
                if mssg["job"] == "miner":
                    # this has to be in the background and can not be awaited as it will block all the threads
                    turtle = Turtle(mssg["computer_name"], websocket)
                    asyncio.get_event_loop().create_task(go_mining(turtle))
        elif "command_id" in mssg:
            if mssg["command_id"] in current_commands:
                command = current_commands.pop(mssg["command_id"])
                command.set_result(mssg)


async def handle_client(websocket):
    # asyncio.create_task(keep_alive(websocket))

    try:
        await handle_message(websocket)
        # while True:

        # await websocket.send(json.dumps({'type': 'eval', 'command': 'turtle.turnLeft()'}))
        # await go_mining(websocket)
        print("Just sent the test message")

    except websockets.exceptions.ConnectionClosed as e:
        print("The websocket closed unexpectedly: " + str(e))
        pass
    # finally:
    #     del clients[client_id]


async def main():
    async with websockets.serve(handle_client, "localhost", 7788):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
