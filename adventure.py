import json
import random
import os

'''
Allows the user to navigate around a (text based) world.
Data comes from custom.json
'''
data = json.load(open('custom.json'))
START = 'North Pole'
FINISH = 'Hobbs\' Apartment'
current = START

'''
Used for the finish() function to help keep track of and calculate game statistics upon completion of the game
'''
collection = []
found_obj = 0
all_obj = []
num_rooms = 1 # starts off with 1 to account for the start room

TOTAL_ROOMS = len(data)
TOTAL_SPEC_OBJECTS = 0
TOTAL_OBJECTS = 0
rooms = list(data.keys())

for location, objs in data.items():
	objects = objs.get('objects', [])

	for obj in objects:
		obj_name = obj.get('name')
		all_obj.append(obj_name)
		TOTAL_OBJECTS += 1

		if obj.get("type") == "special":
			TOTAL_SPEC_OBJECTS += 1

'''
Checks to see if 'location.json' is already a file 
and loads the dictionary information (users and their current location) into the game
ELSE:
	creates the empty dictionary that will collect information to later be dumped into the 'location.json' file
'''

if os.path.isfile('location.json'): 
	with open('location.json', 'r') as file:
		users = json.load(file)
else:
	users = {}


def main():
	'''
	Begins the game by creating a list of possible starting positions (starting_pos), 
	then chooses a random room for the player to start in (current)

	For the purpose of game analytics, the starting room is removed from the list of rooms
	made at the beginning
	'''

	starting_pos = [location for location in data if location != FINISH]
	current = random.choice(starting_pos)
	rooms.remove(current)
	play_game(data, current)

def play_game(data, curr):
	'''
	Main game loop that allows the player to:
	- move around the world
	- collect special objects
	- find the finish point

	Continuing with the end of game stats: (purpose of the 2 global vars)
	- counts the number of rooms the user finds
	- the current rooms continue to be removed from rooms to make sure
	  they are only being counted once

	Parameters:
		data (dict): the dictionary that has the information of the world
		curr (str): the user's current location within the game
	'''

	global rooms
	global num_rooms

	print('Welcome to the Elf Adventure Game:\n')
	username = input('Please enter in your name:\n')

	while curr != FINISH:
		users[username] = curr
		with open ('location.json', 'w') as file:
			json.dump(users, file)
			
		print_room_description(data, curr)
		
		user_move = input('Choose your next move:\nOr type \"exit" or \"quit" to leave the game\n').lower()
		if move_user(data, curr, user_move) == False:
			print('\nInvalid choice. Please enter a valid move.\n')
		elif (user_move == 'exit') or (user_move == 'quit'):
			print('You have quit the game.\nThanks for playing.')
			exit()
		else:
			curr = move_user(data, curr, user_move)

			if curr in rooms:
				num_rooms += 1
				rooms.remove(curr)

	finish()
	exit()

def print_room_description(data, current):
	'''
	Prints out the full description of the current room:
	- The text associated with the room
	- Any objects in the room
		* If the object is special, gives them an initial option
		  to pick it up, but will add it to the global collection
		  variable no matter what
		* If the object is normal, it just states that the object 
		  is in the room
	- Available moves

	Parameters:
		data (dict): the dictionary that has the information of the world
		current (str): the user's current location within the game
	'''
	global all_obj
	global found_obj
	global collection

	output = describe(data, current)
	output = output.split('\n')
	output.remove('')

	room_info = output[0] + '\n' + output[1]
	print(room_info)

	if len(output) > 2:
		if "objects" in data.get(current, {}):
			options_str = output[3] + '\n'
			locations = output[4:]
			for obj in data[current]["objects"]:
				if obj['name'] in all_obj:
					found_obj += 1
					all_obj.remove(obj['name'])
					if obj['type'] == 'special':
						if obj['name'] not in collection:
							collection.append(obj["name"])
							user_choice = input(f'Do you want to pick up {obj["name"]}?\nyes or no?\n')
							if user_choice == 'yes':
								print(f'Buddy picked up {obj["name"]} for safe keeping.')
							else:
								print(f'Buddy pick up {obj["name"]} anyways.')
						else:
							break
					else:
						break
				else:
					print(f'Buddy sees {obj["name"]}')

		else:
			options_str = '\n' + output[2] + '\n'
			locations = output[3:]

		print(options_str)
		for move in locations:
			print(move)

def describe(data, current):
	'''
	Finds the full description of the current room:
	- The text associated with the room
	- Any object in the room
	- Available moves

	Parameters:
		data (dict): the dictionary that has the information of the world
		current (str): the user's current location within the game

	Returns:
		output (str): the description of the current room
	'''

	output = data.get(current, {}).get("text", "")
	if "objects" in data.get(current, {}):
		for obj in data[current]["objects"]:
			output += (f'\nYou see {obj["name"]}.\n')

	output += '\nYour options are:\n'
	for move, location in data.get(current, {}).get("moves", {}).items():
		output += "'" + move + "' to go to " + location + '\n'
	return output

def move_user(data, current, move):
	'''
	Moves the user to the chosen room upon user input

	Parameters:
		data (dict): the dictionary that has the information of the world
		current (str): the user's current location within the game
		move (str): user's inputed room

	Returns:
		False (bool): will only return if the inputed room is not an available option
					  which would then print an 'Invaild' message in the play_game() function
		moves[move] (str): the name of the new location
	'''
	current_room = data[current]
	moves = current_room.get('moves', {})

	if move not in moves:
		return False
	return moves[move]

def finish():
	'''
	Print the final results and statistics of the game:
	- A congrats for finishing
	- The list of collected objects
	- The number and percentage of special object collected, total objects found, and room vistied
		* If the user for 100% of the category, prints an acheivement message
	'''
	print('\nCONGRATS! You helped Buddy find his Dad in New York!\n')
	print('You have collected:', end= " ")

	for item in collection:
		if collection.index(item) < (len(collection) - 1):
			print(item, end= ', ')
		elif len(collection) == 1:
			print(f'{item}')
		else:
			print(f'and {item}')
		print()

	if (len(collection) / TOTAL_SPEC_OBJECTS) == 1:
		print("You found all the collectable objects!")
	else:
		print(f'{len(collection)}/{TOTAL_SPEC_OBJECTS} ({(len(collection) / TOTAL_SPEC_OBJECTS) * 100:.2f}%) collectable objects')

	if (found_obj / TOTAL_OBJECTS) == 1:
		print("You found all the objects!")
	else:
		print(f'{found_obj}/{TOTAL_OBJECTS} ({(found_obj / TOTAL_OBJECTS) * 100:.2f}%) total found objects')

	if (num_rooms / TOTAL_ROOMS) == 1:
		print("You visited all the rooms!")
	else:
		print(f'{num_rooms}/{TOTAL_ROOMS} ({(num_rooms / TOTAL_ROOMS) * 100:.2f}%) rooms visited')



if __name__ == '__main__':
	main()