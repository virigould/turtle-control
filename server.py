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
    if "No block to inspect" not in response:
        return response
    else:
        return None


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
def y_from(here, y):
    diff = here["y"] - y
    return diff
def x_from(here, x):
    diff = here["x"] - x
    return diff
def z_from(here, z):
    diff = here["z"] - z
    return diff

def is_valuable(block):
    if block is None:
        return False
    name = block.get("name", "")
    valuable_keywords = ["coal", "iron", "gold", "copper", "diamond", "lapis", "emerald", "redstone","ore"]
    return any(ore in name for ore in valuable_keywords)

def dig_valuable(blocks):
    """
    takes a dictionary of direction -> block info, and returns a list of
    instructions to efficiently mine ores.
    :param blocks: Dictionary like {"up": {...}, "left": {...}, ...}
    :return: List of instructions (e.g. ["dig_down", "turn_left", "dig", ...])
    """
    valuable_directions = [direction for direction, block in blocks.items() if is_valuable(block) and block is not None]
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

async def mine(blocks, turtle):
    """
    Given a turtle and inspection result (blocks), determine valuable blocks
    and execute mining instructions.
    """
    if not blocks:
        return
        # map strings to methods
    instruction_map = {
        "dig": turtle.dig,
        "dig_up": turtle.dig_up,
        "dig_down": turtle.dig_down,
        "turn_left": turtle.turn_left,
        "turn_right": turtle.turn_right,
    }
    instructions = dig_valuable(blocks)

    for instruction in instructions:
        action = instruction_map.get(instruction)
        if action:
            await action()
        else:
            print(f"Unknown instruction: {instruction}")

async def tunnel(turtle, axis, direction, pattern, n, x, y, z):
    """
    :param turtle: the turtle
    :param axis: axis the turtle is meant to travel on
    :param direction: either +1 or -1
    :param pattern: walls, top or bottom
    :param n: how far to mine
    :param x: current x coordinate
    :param y: current y coordinate
    :param z: current z coordinate
    :return: the relevant coordinate (x, y, or z)
    """

    pattern_map = {
        "walls": turtle.inspect_walls,
        "top": turtle.inspect_top,
        "bottom": turtle.inspect_bottom,
        "up": turtle.dig_up,
        "down": turtle.dig_down
    }

    for i in range(n):
        if axis in ("x","z"):
            action = pattern_map.get(pattern)
            blocks = await action()
            if blocks:
                await mine(blocks, turtle)
            await turtle.dig()
            await turtle.forward()
            if axis == "x":
                x += direction
                return x
            elif axis == "z":
                z += direction
                return z
        else:
            action = pattern_map.get(pattern)
            await action()
            if direction < 0:
                await turtle.down()
            else:
                await turtle.up()
            y += direction
            return y

async def tunnel_transition(turtle, x, y, z, transition_type, reflection):
    """

    :param turtle: the turtle
    :param x: current x coordinate
    :param y: current y coordinate
    :param z: current z coordinate
    :param transition_type: from which tunnel to which tunnel
    :param reflection: which way does the turtle need to turn
    :return: x, y, z
    """
    reflection_map = {
        "right": turtle.turn_right,
        "left": turtle.turn_left
    }

    if transition_type == "interior":
        action = reflection_map.get[reflection]
        await turtle.dig_up()
        await turtle.up()
        await action()
        await action()
        y += 1
        return x, y, z

    elif transition_type == "bottom trough to top trough":
        action = reflection_map.get[reflection]
        await turtle.down()
        await action()
        await turtle.dig()
        await turtle.forward()
        await turtle.dig()
        await turtle.forward()
        await turtle.dig_down()
        await turtle.down()
        await action()
        y -= 2
        if reflection == "left":
            x += 2
        elif reflection == "right":
            x -= 2
        return x, y, z

    elif transition_type == "top trough to bottom trough":
        action = reflection_map.get[reflection]
        await action()
        await turtle.dig()
        await turtle.forward()
        await turtle.dig_up()
        await turtle.up()
        await turtle.dig()
        await turtle.forward()
        await action()
        y += 1
        if reflection == "left":
            x += 2
        elif reflection == "right":
            x -= 2
        return x, y, z

    elif transition_type == "interior to interior":
        action = reflection_map.get[reflection]
        await turtle.down()
        await action()
        await turtle.dig()
        await turtle.forward()
        await turtle.dig()
        await turtle.forward()
        await turtle.dig()
        await turtle.forward()
        await turtle.dig()
        await turtle.forward()
        await action()
        y -= 1
        if reflection == "right":
            x += 4
        elif reflection == "left":
            x -= 4
        return x, y, z

async def go_mining(turtle):
    # store a copy of the home coordinates, and initiate distance variables
    turtle.location = await send_gps(turtle.websocket)
    home = turtle.location.copy()
    x = 0
    y = 0
    z = 0

    # move the turtle to the desired depth
    # y_distance = y_from(home, -48)
    # y = await tunnel(turtle, "y", -1, "down", y_distance, x, y, z)
    
    for i in range(1):

        #bottom blue tunnel
        print(37595648465)
        z = await tunnel( turtle, "z", 1, "walls", 15, x, y, z)
    
        #bottom blue to green
        print(283964293856)
        x, y, z = await tunnel_transition(turtle, x, y, z,"top trough to bottom trough", "left")
    
        #green tunnel
        print(719879324789432)
        z = await tunnel(turtle, "z", -1, "bottom", 15, x, y, z)
    
        #green to purple
        print(536739475632)
        x, y, z = await tunnel_transition(turtle, x, y, z, "interior", "left")
    
        #purple tunnel
        print(638202187346)
        z = await tunnel(turtle, "z", 1, "top", 15, x, y, z)
    
        #purple to bottom blue
        print(526109176373)
        x, y, z = await tunnel_transition(turtle, x, y, z, "bottom trough to top trough", "left")
    
        # bottom blue tunnel backwards
        print(6230232386483)
        z = await tunnel(turtle, "z", -1, "walls", 15, x, y, z)
    
        # bottom blue to green backside
        print(7437389267382)
        x, y, z = await tunnel_transition(turtle, x, y, z, "top trough to bottom trough", "right")
    
        #green tunnel backwards
        print(7347823764872)
        z = await tunnel(turtle, "z", 1, "bottom", 15, x, y, z)
    
        #green to purple
        print(768908231144323)
        x, y, z = await tunnel_transition(turtle, x, y, z, "interior", "left")
    
        #purple tunnel backwards
        print(63575923625)
        z = await tunnel(turtle, "z", -1, "top", 15, x, y, z)
        if i == 0:
            # purple backside to bottom blue
            print(6445799976443223)
            x, y, z = await tunnel_transition(turtle, x, y, z, "bottom trough to top trough", "right")

    ##################
    ### MAIN CHUNK ###
    ##################

    for i in range(2):

        #purple to yellow
        print(6564564843893)
        x, y, z = await tunnel_transition(turtle, x, y, z, "top trough to bottom trough", "left")

        #yellow and blue tunnels
        for j in range(3):

            #yellow tunnel
            print(555738367864)
            z = await tunnel(turtle, "z", 1, "bottom", 15, x, y, z)

            #yellow to blue
            print(66781117785483)
            x, y, z = await tunnel_transition(turtle, x, y, z, "interior", "left")

            #blue tunnel
            print(66567784839)
            z = await tunnel(turtle, "z", -1, "top", 15, x, y, z)

            if j < 3:
                #blue to yellow
                print(9987637433784)
                x, y, z = await tunnel_transition(turtle, x, y, z, "interior to interior", "left")

        #blue to green
        print(9865432345678)
        x, y, z = await tunnel_transition(turtle, x, y, z, "top trough to bottom trough", "right")

        #green and purple tunnels
        for j in range(3):

            #green tunnel
            print(675248962345089778)
            z = await tunnel(turtle, "z", 1, "bottom", 15, x, y, z)

            #green to purple
            print(6789495876563743)
            x, y, z = await tunnel_transition(turtle, x, y, z, "interior", "left")

            #purple tunnel
            print(785348752345467)
            z = await tunnel(turtle, "z", -1, "top", 15, x, y, z)


            if j < 3:
                #purple to green
                print(678937467689832)
                x,y,z = await tunnel_transition(turtle, x, y, z, "interior to interior", "right")

    #green to yellow
    print(2345678900975)
    x, y, z = await tunnel_transition(turtle, x, y, z, "top trough to bottom trough", "left")

    #top yellow tunnels
    for i in range(3):
        if i %2 == 0:

            #tunnel
            print(23458900007544)
            z = await tunnel(turtle,"z", 1, "walls", 15, x, y, z)

            #to next tunnel
            print(754789097453)
            x, y, z = await tunnel_transition(turtle, x, y, z, "interior to interior", "right")

        else:
            #tunnel opposite direction
            print(4356789767432)
            z = await tunnel(turtle, "z", 1, "walls", 15, x, y, z)

            #to next tunnel but only on the first pass
            if i < 3:
                print(34578999945673)
                x,y,z = await tunnel_transition(turtle, x, y, z, "interior to interior", "left")

    # return to start position
    print(678900034742387564)
    y = await tunnel(turtle, "y", -1, "down", 14, x, y, z)
    await turtle.down()
    y -= 1

    #turn around
    await turtle.turn_left()
    await turtle.turn_left()

    #move to next chunk
    for i in range(16):
        await turtle.forward()
        z += 1

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
