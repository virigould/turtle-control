import asyncio
from wsgiref.validate import check_status

import websockets
import json
import uuid

current_commands = {}
current_id = 0
clients = {}
# cardinal directions in clockwise order:
# North (z-), East (x+), South (z+), West (x-)
CARDINALS = [("z", -1), ("x", 1), ("z", 1), ("x", -1)]


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
    # print("in send inspect")
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


async def send_get_inv(websocket):
    id = str(uuid.uuid4())
    await websocket.send(json.dumps({"id": id, "type": "get_inv"}))
    current_commands[id] = asyncio.get_event_loop().create_future()
    response = await current_commands[id]
    return response


async def send_pump(websocket, slot):
    id = str(uuid.uuid4())
    await websocket.send(json.dumps({"id": id, "type": "pump", "slot": slot}))
    current_commands[id] = asyncio.get_event_loop().create_future()
    response = await current_commands[id]
    return response


async def send_dump(websocket):
    id = str(uuid.uuid4())
    await websocket.send(json.dumps({"id": id, "type": "dump"}))
    current_commands[id] = asyncio.get_event_loop().create_future()
    response = await current_commands[id]
    return response


async def send_drop(websocket):
    id = str(uuid.uuid4())
    await websocket.send(json.dumps({"id": id, "type": "drop"}))
    current_commands[id] = asyncio.get_event_loop().create_future()
    response = await current_commands[id]
    return response


async def send_select_slot(websocket, slot):
    id = str(uuid.uuid4())
    await websocket.send(json.dumps({"id": id, "type": "select_slot", "slot": slot}))
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


def y_from(here, y):
    diff = y - here["y"]
    return diff


def x_from(here, x):
    diff = x - here["x"]
    return diff


def z_from(here, z):
    diff = z - here["z"]
    return diff


def is_valuable(block):
    if block is None:
        return False
    name = block.get("name", "")
    valuable_keywords = [
        "coal",
        "iron",
        "gold",
        "copper",
        "diamond",
        "lapis",
        "emerald",
        "redstone",
        "ore",
    ]
    return any(ore in name for ore in valuable_keywords)


def dig_valuable(blocks):
    """
    takes a dictionary of direction -> block info, and returns a list of
    instructions to efficiently mine ores.
    :param blocks: Dictionary like {"up": {...}, "left": {...}, ...}
    :return: List of instructions (e.g. ["dig_down", "turn_left", "dig", ...])
    """
    valuable_directions = [
        direction
        for direction, block in blocks.items()
        if is_valuable(block) and block is not None
    ]

    instructions = []

    for direction in ["down", "up", "forward"]:
        if direction in valuable_directions:
            instructions.append(f"dig_{direction}" if direction != "forward" else "dig")
            valuable_directions.remove(direction)

    if (
        "left" in valuable_directions
        and "behind" in valuable_directions
        and "right" not in valuable_directions
    ):
        instructions += [
            "turn_left",
            "dig",
            "turn_left",
            "dig",
            "turn_left",
            "turn_left",
        ]
        valuable_directions.remove("left")
        valuable_directions.remove("behind")
    elif (
        "right" in valuable_directions
        and "behind" in valuable_directions
        and "left" not in valuable_directions
    ):
        instructions += [
            "turn_right",
            "dig",
            "turn_right",
            "dig",
            "turn_left",
            "turn_left",
        ]
        valuable_directions.remove("right")
        valuable_directions.remove("behind")
    elif all(d in valuable_directions for d in ["left", "right", "behind"]):
        instructions += [
            "turn_left",
            "dig",
            "turn_left",
            "dig",
            "turn_left",
            "dig",
            "turn_left",
        ]
        valuable_directions.remove("left")
        valuable_directions.remove("right")
        valuable_directions.remove("behind")

    turn_map = {
        "left": ["turn_left", "dig", "turn_right"],
        "right": ["turn_right", "dig", "turn_left"],
        "behind": ["turn_left", "turn_left", "dig", "turn_left", "turn_left"],
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


async def clear_falling_blocks(turtle):
    while True:
        block = await turtle.inspect()
        name = block.get("name", "")
        if "sand" in name or "gravel" in name:
            await turtle.dig()
            await asyncio.sleep(0.2)
        else:
            await turtle.dig()
            break


async def tunnel(turtle, axis, pattern, n):
    """
    :param turtle: the turtle
    :param axis: axis the turtle is meant to travel on
    :param pattern: walls, top or bottom
    :param n: how far to mine
    """

    pattern_map = {
        "walls": turtle.inspect_walls,
        "top": turtle.inspect_top,
        "bottom": turtle.inspect_bottom,
        "up": turtle.dig_up,
        "down": turtle.dig_down,
    }

    for i in range(n):
        if axis in ("x", "z"):
            action = pattern_map.get(pattern)
            blocks = await action()
            if blocks:
                await mine(blocks, turtle)
            await clear_falling_blocks(turtle)
            await turtle.forward()
        else:
            action = pattern_map.get(pattern)
            await action()
            if pattern == "down":
                await turtle.down()
            elif pattern == "up":
                await turtle.up()


async def tunnel_transition(turtle, transition_type, reflection):
    """
    :param turtle: the turtle
    :param transition_type: from which tunnel to which tunnel
    :param reflection: which way does the turtle need to turn
    """
    reflection_map = {"right": turtle.turn_right, "left": turtle.turn_left}

    if transition_type == "interior":
        action = reflection_map.get(reflection)
        await turtle.dig_up()
        await turtle.up()
        await action()
        await action()

    elif transition_type == "bottom trough to top trough":
        action = reflection_map.get(reflection)
        await turtle.down()
        await action()
        await clear_falling_blocks(turtle)
        await turtle.forward()
        await clear_falling_blocks(turtle)
        await turtle.forward()
        await turtle.dig_down()
        await turtle.down()
        await action()

    elif transition_type == "top trough to bottom trough":
        action = reflection_map.get(reflection)
        await action()
        await clear_falling_blocks(turtle)
        await turtle.forward()
        await turtle.dig_up()
        await turtle.up()
        await clear_falling_blocks(turtle)
        await turtle.forward()
        await action()

    elif transition_type == "interior to interior":
        action = reflection_map.get(reflection)
        await turtle.down()
        await action()
        for i in range(4):
            await clear_falling_blocks(turtle)
            await turtle.forward()
        await action()


async def mine_chunk(turtle):
    """
    the chunk algorithm that the turtles will mine in
    :param turtle:
    :return None:
    """

    ##################
    ### FIRST PASS ###
    ##################

    for i in range(2):
        await refuel_and_relieve(turtle)
        # bottom blue tunnel
        await tunnel(turtle, "z", "walls", 16)
        # bottom blue to green
        await tunnel_transition(turtle, "top trough to bottom trough", "left")
        # green tunnel
        await tunnel(turtle, "z", "bottom", 16)
        # green to purple
        await tunnel_transition(turtle, "interior", "left")
        # purple tunnel
        await tunnel(turtle, "z", "top", 16)
        # purple to bottom blue
        await tunnel_transition(turtle, "bottom trough to top trough", "left")
        # bottom blue tunnel backwards
        await tunnel(turtle, "z", "walls", 16)
        # bottom blue to green backside
        await tunnel_transition(turtle, "top trough to bottom trough", "right")
        # green tunnel backwards
        await tunnel(turtle, "z", "bottom", 16)
        # green to purple
        await tunnel_transition(turtle, "interior", "left")
        # purple tunnel backwards
        await tunnel(turtle, "z", "top", 16)
        if i == 0:
            # purple backside to bottom blue
            await tunnel_transition(turtle, "bottom trough to top trough", "right")

    ##################
    ### MAIN CHUNK ###
    ##################

    for i in range(3):
        await refuel_and_relieve(turtle)
        # purple to yellow
        await tunnel_transition(turtle, "top trough to bottom trough", "left")
        # yellow and blue tunnels
        for j in range(4):
            # yellow tunnel
            await tunnel(turtle, "z", "bottom", 16)
            # yellow to blue
            await tunnel_transition(turtle, "interior", "left")
            # blue tunnel
            await tunnel(turtle, "z", "top", 16)
            if j < 3:
                # blue to yellow
                await tunnel_transition(turtle, "interior to interior", "left")
        # blue to green
        await tunnel_transition(turtle, "top trough to bottom trough", "right")
        # green and purple tunnels
        for j in range(4):
            await refuel_and_relieve(turtle)
            # green tunnel
            await tunnel(turtle, "z", "bottom", 16)
            # green to purple
            await tunnel_transition(turtle, "interior", "left")
            # purple tunnel
            await tunnel(turtle, "z", "top", 16)
            if j < 3:
                # purple to green
                await tunnel_transition(turtle, "interior to interior", "right")
    # green to yellow
    await tunnel_transition(turtle, "top trough to bottom trough", "left")

    #################
    ### LAST PASS ###
    #################

    # top yellow tunnels
    for i in range(4):
        await refuel_and_relieve(turtle)
        if i % 2 == 0:
            # tunnel
            await tunnel(turtle, "z", "walls", 16)
            # to next tunnel
            await tunnel_transition(turtle, "interior to interior", "right")
        else:
            # tunnel opposite direction
            await tunnel(turtle, "z", "walls", 16)
            # to next tunnel but only on the first pass
            if i < 3:
                await tunnel_transition(turtle, "interior to interior", "left")

    #################
    ### NEW CHUNK ###
    #################

    await tunnel(turtle, "y", "down", 15)
    await turtle.down()
    await turtle.turn_left()
    await turtle.turn_left()
    for i in range(16):
        await turtle.forward()


def get_direction_index(axis, direction):
    return CARDINALS.index((axis, direction))


def get_turn_diff(current_axis, current_dir, target_axis, target_dir):
    current = get_direction_index(current_axis, current_dir)
    target = get_direction_index(target_axis, target_dir)
    return (target - current) % 4


async def orient(turtle):
    """
    determines which axis the turtle is currently facing, and in which direction (+/-).
    :param turtle:
    :return axis, direction:
    """
    baseline = await send_gps(turtle.websocket)
    for i in range(2):
        await turtle.forward()
    new = await send_gps(turtle.websocket)
    dx = new.get("x") - baseline.get("x")
    dz = new.get("z") - baseline.get("z")
    if abs(dx) > abs(dz):
        axis = "x"
        direction = 1 if dx > 0 else -1
    else:
        axis = "z"
        direction = 1 if dz > 0 else -1
    await turtle.turn_left()
    await turtle.turn_left()
    for i in range(2):
        await turtle.forward()
    await turtle.turn_left()
    await turtle.turn_left()
    return axis, direction


async def face_axis(turtle, facing_axis, facing_dir, target_axis, distance):
    """
    points the turtle in the cardinal direction it needs to be facing
    :param turtle:
    :param facing_axis: axis the turtle is currently on (x/z)
    :param facing_dir: direction the turtle is currently facing (+/-)
    :param target_axis: the axis the turtle needs to be on (x/z)
    :param distance: direction the turtle needs to be facing (+/-)
    :return None:
    """
    target_dir = 1 if distance > 0 else -1
    diff = get_turn_diff(facing_axis, facing_dir, target_axis, target_dir)

    if diff == 0:
        return
    elif diff == 1:
        await turtle.turn_right()
        return
    elif diff == 3:
        await turtle.turn_left()
        return
    elif diff == 2:
        await turtle.turn_left()
        await turtle.turn_left()
        return


async def navigate(turtle, axis, direction, destination):
    """
    sends the turtle toward its destination on the x and z axis
    :param turtle:
    :param axis: the axis the turtle is currently on (x/z)
    :param direction: the direction the turtle is currently facing (+/-)
    :param destination: where the turtle needs to be
    :return:
    """
    current = await send_gps(turtle.websocket)
    dx = destination.get("x") - current.get("x")
    if dx != 0:
        await face_axis(turtle, axis, direction, "x", dx)
        for i in range(abs(dx)):
            await turtle.forward()
        axis, direction = "x", 1 if dx > 0 else -1
    current = await send_gps(turtle.websocket)
    dz = destination.get("z") - current.get("z")
    if dz != 0:
        await face_axis(turtle, axis, direction, "z", dz)
        for i in range(abs(dz)):
            await turtle.forward()


async def go_to(location, turtle):
    """
    sends the turtle to a specified set of coordinates (x, y, z)
    :param location: dict of coordinates
    :param turtle:
    :return:
    """
    here = await send_gps(turtle.websocket)
    y_distance = y_from(here, 130)
    await tunnel(turtle, "y", "up", y_distance)
    axis, direction = await orient(turtle)
    await navigate(turtle, axis, direction, location)
    current = await send_gps(turtle.websocket)
    y_distance = y_from(current, location.get("y"))
    direction = 1 if y_distance > 0 else -1
    await tunnel(turtle, "y", "down" if direction < 0 else "up", abs(y_distance))


async def pump_n_dump(turtle, chest):
    """
    have the turtle drop all its items in its inventory into a chest, then go to a new chest to pick up fuel
    :param turtle:
    :param chest: dict of coordinates
    :return:
    """
    axis, direction = await orient(turtle)
    await navigate(turtle, axis, direction, chest)
    await send_dump(turtle.websocket)
    await turtle.turn_right()
    await turtle.forward()
    await turtle.turn_left()
    await send_pump(turtle.websocket, 1)


async def refuel_and_relieve(turtle):
    """
    refuel the turtle with items in its inventory, then drop the junk blocks its collected
    :param turtle:
    :return: fuel_level and fuel
    """
    fuel_message = await send_refuel(turtle.websocket, 1)
    if fuel_message["command_output"] == "No items to combust":
        for i in range(2, 17):
            fuel_message = await send_refuel(turtle.websocket, i)
            if fuel_message["command_output"] != "No items to combust":
                break
    await clear_falling_blocks(turtle)
    response = await turtle.forward()
    fuel_level = response["command_output"]
    inventory = await check_inventory(turtle.websocket)
    fuel = 0
    fuel_items = ["fuel", "coal", "wood", "lava", "blaze_rod"]
    junk_items = ["cobble", "dirt", "gravel", "tuff", "sand", "andesite", "diorite", "calcite", "granite"]
    for slot, item in inventory.items():
        if slot == "command_id":
            continue
        if not item:
            continue
        item_name = item["name"]
        print(slot, item)
        if any(fuel_type in item_name for fuel_type in fuel_items):
            fuel += item["count"]
        if any(junk in item_name for junk in junk_items):
            await send_select_slot(turtle.websocket, int(slot))
            await send_drop(turtle.websocket)
    return fuel_level, fuel


async def go_mining(turtle, chunks, home, chest, the_mines):
    """
    send the turtle mining
    :param turtle:
    :param chunks: number of chunks to mine
    :param home: dict of coordinates
    :param chest: dict of coordinates
    :param the_mines: dict of coordinates
    :return:
    """

    await refuel_and_relieve(turtle)

    '''# move the turtle to its mining location
    await go_to(the_mines, turtle)

    # each chunk = 738 fuel
    for chunk in range(chunks):
        await mine_chunk(turtle)
        fuel_level, fuel = await refuel_and_relieve(turtle)
        await send_select_slot(turtle.websocket, 1)
        last_position = await send_gps(turtle.websocket)
        if fuel_level < 10000 & fuel < 10:
            await go_to(home, turtle)
            await pump_n_dump(turtle, chest)
            await go_to(last_position, turtle)

    # move the turtle back home to await orders
    await go_to(home, turtle)'''


async def handle_message(websocket):
    async for message in websocket:
        # print("Message: " + message)
        mssg = json.loads(message)
        if "computer_name" in mssg:
            client_id = mssg["computer_name"]
            # print(client_id)
            if client_id not in clients:
                clients[client_id] = websocket
            if "job" in mssg:
                # print(mssg["job"])
                if mssg["job"] == "miner":
                    # this has to be in the background and can not be awaited as it will block all the threads
                    turtle = Turtle(mssg["computer_name"], websocket)
                    chunks = int(mssg["chunks"])  # int
                    home = mssg["home"]  # dict: { "x": ..., "y": ..., "z": ... }
                    chest = mssg["chest"]  # dict: { "x": ..., "y": ..., "z": ... }
                    destination = mssg["destination"]  # dict: { "x": ..., "y": ..., "z": ... }
                    asyncio.get_event_loop().create_task(
                        go_mining(turtle, chunks, home, chest, destination)
                    )
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
        # print("Just sent the test message")

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
