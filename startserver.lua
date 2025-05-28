local random = math.random
local ws, err = http.websocket("ws://localhost:7788")
local computer_info = nil
local args = {...}


local function uuid()
	local template = "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx"
	return string.gsub(template, "[xy]", function(c)
		local v = (c == "x") and random(0, 0xf) or random(8, 0xb)
		return string.format("%x", v)
	end)
end

function file_exists(name)
	local f = io.open(name, "r")
	return f ~= nil and io.close(f)
end

function check_inventory()
	local inventory = {}
	for i = 1, 9, 1 do
		local item = turtle.getItemDetail(i)
		inventory[i] = item
	end
	return inventory
end

function send_message(message)
	ws.send(string.format('{"name": "%s", "message": "%s"}', computer_info, message))
end

function handle_message(message)
	local info = textutils.unserializeJSON(message)

	if info["type"] == "eval" then
		--print(info["command"])
		local f = load(info["command"])
		local command_output = f()
		local output_table = { command_output = command_output, command_id = info["id"] }
		--print(textutils.serializeJSON(output_table))
		ws.send(textutils.serializeJSON(output_table))
		do
			return
		end
	elseif info["type"] == "inspect" then
		--print("Inpecting " .. info["direction"])
		if info["direction"] == "down" then
			local bool, block_info = turtle.inspectDown()
			if bool then
				block_info["command_id"] = info["id"]
				ws.send(textutils.serializeJSON(block_info))
				do
					return
				end
			else
				local output = { command_output = bool, command_id = info["id"] }
				ws.send(textutils.serializeJSON(output))
				do
					return
				end
			end
		elseif info["direction"] == "forward" then
			local bool, block_info = turtle.inspect()
			if bool then
				block_info["command_id"] = info["id"]
				ws.send(textutils.serializeJSON(block_info))
				do
					return
				end
			else
				local output = { command_output = bool, command_id = info["id"] }
				ws.send(textutils.serializeJSON(output))
				do
					return
				end
			end
		elseif info["direction"] == "up" then
			local bool, block_info = turtle.inspectUp()
			if bool then
				block_info["command_id"] = info["id"]
				ws.send(textutils.serializeJSON(block_info))
				do
					return
				end
			else
				local output = { command_output = bool, command_id = info["id"] }
				ws.send(textutils.serializeJSON(output))
				do
					return
				end
			end
		else
			ws.send("You need to turn dumbass?")
			do
				return
			end
		end
	elseif info["type"] == "inventory" then
		local inv = check_inventory()
		inv["command_id"] = info["id"]
		ws.send(textutils.serializeJSON(inv))
		do
			return
		end
	elseif info["type"] == "gps" then
		local position = vector.new(gps.locate(5))
		position.command_id = info["id"]
		print("in the gps")
		ws.send(textutils.serializeJSON(position))
		do
			return
		end
	elseif info["type"] == "turn" then
		if info["direction"] == "left" then
			local stuffs = turtle.turnLeft()
			local output = { command_output = stuffs, command_id = info["id"] }
			--print("After Left turn")
			--print("Sending: " .. textutils.serializeJSON(output))
			--print("WebSocket OPEN:", tostring(ws and ws.send ~= nil))
			local ok, err = pcall(function()
				ws.send(textutils.serializeJSON(output))
			end)
			-- if not ok then
			--     print("message could not send")
			-- else
			--     print("message should have send")
			-- end
			--print("After Sent the message")
			do
				return
			end
		else
			local output = { command_output = turtle.turnRight(), command_id = info["id"] }
			ws.send(textutils.serializeJSON(output))
			do
				return
			end
		end
	elseif info["type"] == "dig" then
		if info["direction"] == "down" then
			local bool, mssg = turtle.digDown("right")
			if not bool then
				local issue = { command_id = info["id"], command_output = mssg }
				ws.send(textutils.serializeJSON(issue))
				do
					return
				end
			else
				local issue = { command_id = info["id"], command_output = bool }
				ws.send(textutils.serializeJSON(issue))
				do
					return
				end
			end
		elseif info["direction"] == "forward" then
			local bool, mssg = turtle.dig("right")
			if not bool then
				local issue = { command_id = info["id"], command_output = mssg }
				ws.send(textutils.serializeJSON(issue))
				do
					return
				end
			else
				local issue = { command_id = info["id"], command_output = bool }
				ws.send(textutils.serializeJSON(issue))
				do
					return
				end
			end
		elseif info["direction"] == "up" then
			local bool, mssg = turtle.digUp("right")
			if not bool then
				local issue = { command_id = info["id"], command_output = mssg }
				ws.send(textutils.serializeJSON(issue))
				do
					return
				end
			else
				local issue = { command_id = info["id"], command_output = bool }
				ws.send(textutils.serializeJSON(issue))
				do
					return
				end
			end
		else
			ws.send("You need to turn dumbass?")
			do
				return
			end
		end
	elseif info["type"] == "suck" then
		if info["direction"] == "down" then
			local bool, mssg = nil, nil
			if not info["count"] then
				bool, mssg = turtle.suckDown()
			else
				bool, mssg = turtle.suckDown(info["count"])
			end

			if not bool then
				local issue = { command_output = mssg, command_id = info["id"] }
				ws.send(textutils.serializeJSON(issue))
				do
					return
				end
			else
				local issue = { command_output = bool, command_id = info["id"] }
				ws.send(textutils.serializeJSON(issue))
				do
					return
				end
			end
		elseif info["direction"] == "forward" then
			local bool, mssg = nil, nil
			if not info["count"] then
				bool, mssg = turtle.suck()
			else
				bool, mssg = turtle.suck(info["count"])
			end

			if not bool then
				local issue = { command_output = mssg, command_id = info["id"] }
				ws.send(textutils.serializeJSON(issue))
				do
					return
				end
			else
				local issue = { command_output = bool, command_id = info["id"] }
				ws.send(textutils.serializeJSON(issue))
				do
					return
				end
			end
		elseif info["direction"] == "up" then
			local bool, mssg = nil, nil
			if not info["count"] then
				bool, mssg = turtle.suckUp()
			else
				bool, mssg = turtle.suckUp(info["count"])
			end

			if not bool then
				local issue = { command_output = mssg, command_id = info["id"] }
				ws.send(textutils.serializeJSON(issue))
				do
					return
				end
			else
				local issue = { command_output = bool, command_id = info["id"] }
				ws.send(textutils.serializeJSON(issue))
				do
					return
				end
			end
		else
			ws.send("You need to turn dumbass?")
			do
				return
			end
		end
	elseif info["type"] == "place" then
		if info["direction"] == "down" then
			local bool, mssg = turtle.placeDown()
			if not bool then
				local issue = { command_output = mssg, command_id = info["id"] }
				ws.send(textutils.serializeJSON(issue))
				do
					return
				end
			else
				local issue = { command_output = bool, command_id = info["id"] }
				ws.send(textutils.serializeJSON(issue))
				do
					return
				end
			end
		elseif info["direction"] == "forward" then
			local bool, mssg = turtle.place()
			if not bool then
				local issue = { command_output = mssg, command_id = info["id"] }
				ws.send(textutils.serializeJSON(issue))
				do
					return
				end
			else
				local issue = { command_output = bool, command_id = info["id"] }
				ws.send(textutils.serializeJSON(issue))
				do
					return
				end
			end
		elseif info["direction"] == "up" then
			local bool, mssg = turtle.placeUp()
			if not bool then
				local issue = { command_output = mssg, command_id = info["id"] }
				ws.send(textutils.serializeJSON(issue))
				do
					return
				end
			else
				local issue = { command_output = bool, command_id = info["id"] }
				ws.send(textutils.serializeJSON(issue))
				do
					return
				end
			end
		else
			ws.send("You need to turn dumbass?")
			do
				return
			end
		end
	elseif info["type"] == "refuel" then
		if info["slot"] ~= nil then
			local fueled, mssg = turtle.refuel()
			print(fueled)
			print(mssg)
			if not fueled then
				local issue = { command_output = mssg, command_id = info["id"] }
				ws.send(textutils.serializeJSON(issue))
				do
					return
				end
			else
				local output = { command_output = turtle.getFuelLevel(), command_id = info["id"] }
				ws.send(textutils.serializeJSON(output))
				do
					return
				end
			end
		else
			turtle.select(info["slot"])
			local fueled, mssg = turtle.refuel()
			if not fueled then
				local issue = { command_output = mssg, command_id = info["id"] }
				ws.send(textutils.serializeJSON(issue))
				do
					return
				end
			else
				local output = { command_output = turtle.getFuelLevel(), command_id = info["id"] }
				ws.send(textutils.serializeJSON(output))
				do
					return
				end
			end
		end
	elseif info["type"] == "move" then
		if info["direction"] == "forward" then
			local move_attempt, mssg = turtle.forward()
			if not move_attempt then
				local issue = { command_output = mssg, command_id = info["id"] }
				ws.send(textutils.serializeJSON(issue))
				do
					return
				end
			else
				ws.send(textutils.serializeJSON({
					bool = move_attempt,
					command_output = turtle.getFuelLevel(),
					command_id = info["id"],
				}))
				do
					return
				end
			end
		elseif info["direction"] == "back" then
			local move_attempt, mssg = turtle.back()
			--print(tostring(move_attempt) .. " " .. mssg)
			if not move_attempt then
				local issue = { command_output = mssg, command_id = info["id"] }
				ws.send(textutils.serializeJSON(issue))
				do
					return
				end
			else
				ws.send(textutils.serializeJSON({
					bool = move_attempt,
					command_output = turtle.getFuelLevel(),
					command_id = info["id"],
				}))
				do
					return
				end
			end
		elseif info["direction"] == "up" then
			local move_attempt, mssg = turtle.up()
			if not move_attempt then
				local issue = { command_output = mssg, command_id = info["id"] }
				ws.send(textutils.serializeJSON(issue))
				do
					return
				end
			else
				ws.send(textutils.serializeJSON({
					bool = move_attempt,
					command_output = turtle.getFuelLevel(),
					command_id = info["id"],
				}))
				do
					return
				end
			end
		elseif info["direction"] == "down" then
			local move_attempt, mssg = turtle.down()
			if not move_attempt then
				local issue = { command_output = mssg, command_id = info["id"] }
				ws.send(textutils.serializeJSON(issue))
				do
					return
				end
			else
				ws.send(textutils.serializeJSON({
					bool = move_attempt,
					command_output = turtle.getFuelLevel(),
					command_id = info["id"],
				}))
				do
					return
				end
			end
		end
	elseif info["type"] == "test" then
		print("It got the test command")
	else
		print("Could not understand the command")
	end
	--ws.send("Ready")
end

function main()
    local length = #args
	if file_exists("computer_info.txt") then
		local file = io.open("computer_info.txt", "r")
		computer_info = textutils.unserialize(file:read("*all"))
	else
		computer_info = { name = uuid(), job = "miner" }
		local file = io.open("computer_info.txt", "w")
		file:write(textutils.serialize(computer_info))
	end
	ws.send(string.format('{"computer_name": "%s", "job": "%s"}', computer_info.name, computer_info.job))
	--ws.send("ready")
	while true do
		local message = ws.receive()
		--print(message)
		if message == nil then
			ws = assert(http.websocket("ws://localhost:7788"))
			message = ws.receive()
		end
		handle_message(message)
	end
end

main()
