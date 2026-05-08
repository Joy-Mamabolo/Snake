import json
import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys

GRID_SIZE = 20
NUM_PREY = 6
STEPS = 50
DEBUG = True
SZ_SIZE = 6
SZ_CAP = 3


class Agent:
    def __init__(self, x, y, speed = 1, symbol = 'A'):
        self.x = x
        self.y = y
        self.speed = speed
        self.symbol = symbol
        self.actions = [(0,self.speed),(0,-self.speed),(self.speed,0),(-self.speed,0)] #Up, Down, Right, Left
    
    def move(self, dx, dy, grid_size = GRID_SIZE):
        self.x = max(0, min(grid_size-1, self.x + dx*self.speed))
        self.y = max(0, min(grid_size-1, self.y + dy*self.speed))

class Snake(Agent):
    def __init__(self, x, y):
        super().__init__(x, y, speed=1, symbol = "S")

        # Added for the purpose of considering predator and prey swaps as captures. Currently, this is not the case.
        self.prev_x = GRID_SIZE//2 # initial snake spawn
        self.prev_y = GRID_SIZE//2 # initial snake spawn

    
    def chase(self, prey_list):

        #prey_distance = [] 

        closest_prey = None
        min_distance = float('inf')

        for prey in prey_list:
            distance = (abs(self.x-prey.x) + abs(self.y - prey.y))
            # prey_distance.append((prey, distance))
            
            if distance < min_distance:
                min_distance = distance
                closest_prey = prey
        
        if closest_prey:
            if closest_prey.x == self.x:
                # snake and prey are on the same vertical line, but at different heights
                return (0, self.speed) if closest_prey.y>=self.y else (0, -self.speed) # go up if the prey is above, otherwise go down
            elif closest_prey.y == self.y:
                # snake and prey are on the same horizontal line, but at different widths
                return (self.speed, 0) if closest_prey.x>=self.x else (-self.speed,0) # go right if prey is to the right, otherwise left
            elif closest_prey.x>closest_prey.y:
                # when deciding whether to move vertically or horizontally, favour the larger distance - x
                return (self.speed, 0) if closest_prey.x>=self.x else (-self.speed, 0)
            else:
                # when deciding whether to move vertically or horizontally, favour the larger distance - y
                return (0, self.speed) if closest_prey.y>=self.y else (0, -self.speed)
        else:
            return 0, 0 # if there are no prey, stay in place - should not be the case since the game should end when all prey are captured

class Prey(Agent):
    def __init__(self, x, y, learning = False):
        super().__init__(x, y, speed = 1, symbol="P")
        self.alive = True
        self.generation = 0 # generation of the prey - also used to track how many times the prey has been captured and respawned.
        
        self.learning = learning

        if learning:
            self.q_table = {} # State-action value table for Q-learning not implemented yet
            self.reward = 0 # reward received in the current step, used for learning prey. Not implemented yet
            self.alpha = 0.3
            self.gamma = 0.9
            self.epsilon = 0.1
            
    
    def get_q(self, state, action):
        # Function takes q_table key consisting of a state string and action tuple, where the action is itself a tuple encoding
        # up, down, left, right using positive and negative binary digit combinations. if the dictionary key does not exist, it returns 0.0

        try: 
            return self.q_table[(state, action)]
        
        except KeyError:
            # KeyError means that state and action combination do not exist in the current q-table. Update q-table and return 0.0

            self.q_table[(state, action)] = 0.0

            return 0.0
        else:
            print("Unknown Error involving q-table data extraction using key.")
            raise UnboundLocalError
    
    def update_q_table(self, state, action, reward, next_state):
        old_q = self.get_q(state, action) #because of how get_q is defined, if state and action combination do not exist, they are created
        next_q = max([self.get_q(next_state, a) for a in self.actions]) # Return the largest q-value (assuming optimal play)

        # Bellman Eq.
        new_q = old_q + self.alpha*(reward + self.gamma*next_q-old_q)

        self.q_table[(state, action)] = new_q

    def observe(self, world):
        # This function defines how the prey observes the world. Characters are used to encode different things as follows:
        # Each cell contains 2 pieces of information: cell type and occupant
        # cell type can be either active safe zone ('O+'), inactive safe zone ('O-'), or empty ('.')
        # occupant will be 'P' for prey and 'S' for snake or "." for neither.
        # walls will be encoded as XXX in order to maintain consistent patterns and lengths.
        # Safe zone distance pointers will also be given representing closer, further or same

        # 3x3 grid around the prey
        neighbourhood = ""
        for dx in range(-1,2):
            for dy in range(-1,2):
                nx = self.x + dx
                ny = self.y +dy

                if world.is_in_bounds(nx,ny):
                    # cell type:
                    in_sz, sz_active = world.is_in_safe_zone(nx,ny)

                    if in_sz:
                        if sz_active:
                            neighbourhood+="O+"
                        else:
                            neighbourhood+="O-"
                    else:
                        # normal cell type encoded with "NN" for normal, and doubled to maintain consistent length with other cell type
                        neighbourhood+="NN"

                    # Occupant type
                    if world.snake.x == nx and world.snake.y == ny:
                        neighbourhood+="S"
                    elif any(prey.x == nx and prey.y == ny for prey in world.prey_list):
                        neighbourhood+='P'
                    else:
                        neighbourhood+='.'
                else:
                    neighbourhood+='XXX'# Out of bounds
        
        return neighbourhood 
    
    def propose_move(self, world): # This function defines how the prey moves randomly in the environment. This will be used for the non-learning prey in the long term, but for the learning prey, this will be replaced by a Q-table based action selection function.
        if self.learning:
            # Observe the world and update the Q-table based on the reward received from the previous action. Then select an action based on the Q-table. Not implemented yet.
            
            # Observe
            state = self.observe(world)

            # Determine if we consult q-table or explore using epsilon
            if random.random()<self.epsilon:
                # Be adventurous, explore - ignore q-table and make a random move
                candidate = [random.choice(self.actions)] # made it a list for consistency
            else:
                # Be principled - consult your q-table
                candidate = [(0,0)] # default value although it should not be necessary 
                threshold = 0.0

                for action in self.actions:
                    q = self.get_q(state, action)
                    if q > threshold:
                        # Best move thus far
                        threshold = q # raise standard for best move
                        candidate = [action] # Erase previous moves if there were any
                    elif q == threshold:
                        # One of the best moves, choose any
                        candidate.append(action)
                    else:
                        # Not good enough
                        pass

                # Make final choice randomly if more than one decision possible
            if len(candidate)>1:
                # more than one best move
                return random.choice(candidate)
            else:
                # Only one answer
                return candidate[0] # tuple not list
        else:
            return random.choice(self.actions)

class SafeZone:
    def __init__(self, x, y, size = SZ_SIZE, capacity = SZ_CAP):
        # x,y represents bottom left corner of safe zone
        self.x = x
        self.y = y

        self.size = size # safe zone is a square of length size

        self.capacity = capacity
        self.current_occupants = 0 # number of prey currently in the safe zone

        self.active = True # whether the safe zone is currently preventing snake entry. If the safe zone is beyond capacity, it becomes inactive and allows the snake to enter and capture prey inside. The safe zone becomes active again once the number of occupants falls below capacity and snake is no longer inside the safe zone
    
        # Deleted the list of occupants in favour of just keeping track of the number. Also don't need to track admission or release.

class Game:
    def __init__(self, grid_size = GRID_SIZE, num_prey = NUM_PREY):
        self.grid_size = grid_size
        self.snake = Snake(grid_size//2, grid_size//2)
        self.prey_list = [Prey(random.randint(0, grid_size-1), random.randint(0, grid_size -1), learning = bool(random.random()<0.5)) for _ in range(num_prey)]
        self.safe_zone = [SafeZone(5, 5)] # x,y of safe zone represents bottom left corner
        self.step_count = 0 # keep track of the number of steps taken in the game
    
    def is_in_safe_zone(self, x, y):
        for safe_zone in self.safe_zone:
            if (safe_zone.x<=x<=safe_zone.x+safe_zone.size) and (safe_zone.y<=y<=safe_zone.y+safe_zone.size):
                return (True, safe_zone.active)
        return False, None

    def is_in_bounds(self, x, y):
        return False if x < 0 or x >= self.grid_size or y < 0 or y >= self.grid_size else True

    def step(self):
        # snake moves
        self.step_count+=1
        sdx,sdy = self.snake.chase(self.prey_list) # chase function determines the proposed move of the snake and game checks if the move is valid before executing it.

        proposed_snake_x = self.snake.x + sdx
        proposed_snake_y = self.snake.y + sdy

        #print(f"proposed_snake-x: {self.snake.x, sdx}\tproposed_snake_y: {self.snake.y, sdy}")

        if self.is_in_bounds(proposed_snake_x, proposed_snake_y):
            for sz in self.safe_zone:
                if (sz.active and sz.x <= proposed_snake_x < sz.x + sz.size and sz.y <= proposed_snake_y < sz.y + sz.size):
                    #print("Safe Zone Entry prevention")
                    self.snake.prev_x, self.snake.prev_y = self.snake.x, self.snake.y
                    # self.snake.move(0, 0) # if proposed move is into an active safe zone, stay in place. Would like to consider other options later.
                    # Alternative implementation of what happens after invalid move

                    if self.snake.x ==sz.x or self.snake.x==sz.x+sz.size: 
                        # stuck on left or right wall of safe zone, move either up or down
                        if self.snake.y >= sz.y+sz.size//2:
                            # more than half way up - go up (assuming wall is sketched from bottom left corner)
                            self.snake.move(0,self.snake.speed)
                        else:
                            # less than half way up - go down
                            self.snake.move(0, -self.snake.speed)
                    else:
                        # stuck on top or bottom wall of safe zone, move either left or right
                        if self.snake.x >= sz.x+sz.size//2:
                            # more than half way right, go right
                            self.snake.move(self.snake.speed,0)
                        else:
                            # less than half way right, go left
                            self.snake.move(-self.snake.speed, 0)
                else:
                    self.snake.prev_x, self.snake.prev_y = self.snake.x, self.snake.y
                    self.snake.move(sdx, sdy) # proposed move is valid, execute it
        else:
            self.snake.prev_x, self.snake.prev_y = self.snake.x, self.snake.y
            #self.snake.move(0, 0) # if proposed move is out of bounds, stay in place. Would like to consider other options such as bouncing back or wrapping around later.

            # Alternative motion instead of snake not moving - though I don't think this is a likely occurence
            if self.snake.x ==0 or self.snake.x==self.grid_size-1: 
                # stuck on left or right wall of safe zone, move either up or down

                if self.snake.y >= self.grid_size//2:
                    # more than half way up - go up (assuming wall is sketched from bottom left corner)
                    self.snake.move(0,self.snake.speed)
                else:
                    # less than half way up - go down
                    self.snake.move(0, -self.snake.speed)
            else:
                # stuck on top or bottom wall of safe zone, move either left or right

                if self.snake.x >= self.grid_size//2:
                    # more than half way right, go right
                    self.snake.move(self.snake.speed,0)
                else:
                    # less than half way right, go left
                    self.snake.move(-self.snake.speed, 0)

        #prey moves/acts
        for prey in self.prey_list:
            
            if not prey.alive:
                # Captured Prey Respawns
                prey.x = 0 if self.snake.x>self.grid_size-1-self.snake.x else self.grid_size-1  # furthest distance away from the snake within bounds at that step.
                prey.y = 0 if self.snake.y>self.grid_size-1-self.snake.y else self.grid_size-1
                prey.generation+=1
                prey.alive = True
            

            elif (prey.x == self.snake.x and prey.y == self.snake.y) or (prey.x == self.snake.prev_x and prey.y == self.snake.prev_y):
                # Check captures
                prey.alive = False
                # self.prey_list.remove(prey) # remove captured prey from the game. Perhaps prey should not be removed from list, but respawned some safe distance away from snake and log the capture instead
            else:
                # Prey moves
                dx, dy = prey.propose_move(self)

                if self.is_in_bounds(prey.x + dx, prey.y + dy):
                    prey.move(dx, dy, grid_size = self.grid_size)
                else:
                    prey.move(0, 0, grid_size = self.grid_size) # if proposed move is out of bounds, stay in place
                    prey.reward = -1 # negative reward for trying to move out of bounds. This is for learning prey. 
        
        # check safe zone admissions
        for sz in self.safe_zone: # there is only one safe zone for now but this allows for more than one should we wish

            sz.current_occupants = 0 # must reset in every step so that it keeps the current count and not total count

            # Set safe zone to off as soon as snake is inside, even if snake spawned there. Alternatively prohibit snake from spawning in sz

            if (sz.x<=self.snake.x<sz.x+sz.size) and (sz.y<=self.snake.y<sz.y+sz.size):
                sz.active = False 

            for prey in self.prey_list:
                if (sz.x<=prey.x<sz.x+sz.size) and (sz.y<=prey.y<sz.y+sz.size):
                    sz.current_occupants +=1

                if sz.active and sz.current_occupants >= sz.capacity:
                    sz.active = False # Safe zone becomes inactive when capacity is reached.
                elif sz.active and sz.current_occupants < sz.capacity:
                    pass # Safe zone is active and below capacity, nothing changes
                elif not sz.active and sz.current_occupants < sz.capacity and not (sz.x<=self.snake.x<sz.x+sz.size and sz.y<=self.snake.y<sz.y+sz.size):
                    sz.active = True # Safe zone becomes active again when occupants are below capacity and snake is no longer inside the safe zone.
                else:
                    pass # Safe zone is inactive and either occupants are above capacity or snake is still inside, nothing changes


        return self.snake, self.prey_list, self.safe_zone

    def game_write_to_file(self):
        # Save the current game to a file for later analysis.
        data = {
            #'game': 0, # I want to implement a game counter for the visualization portion
            'step': self.step_count,
            'snake_position': (self.snake.x, self.snake.y),
            'prey_positions': [(prey.x, prey.y, prey.learning, prey.alive, prey.generation) for prey in self.prey_list],
            'safe_zone_status': [(sz.x, sz.y, sz.size, sz.active, sz.current_occupants) for sz in self.safe_zone]
        }

        with open('game_log.json', 'a') as f:
            f.write(json.dumps(data) + '\n')
    
    def game_from_file(self, filename):
        # Load a game from a file. This is for analysis and visualization of past games, not for resuming a game. It returns a list of game states.
        with open(filename, 'r') as f:
            game_states = [json.loads(line) for line in f]
        
        return game_states


def visualize_game(game_states, grid_size = GRID_SIZE):

    grid = np.zeros((grid_size, grid_size))
    _, ax = plt.subplots()
    img = ax.imshow(grid, cmap = 'tab20', vmin=0, vmax = 4, alpha = 0.5, zorder = 1)

    capture_text = ax.text(1.05,0.95,f"Captures", transform = ax.transAxes, color = "black", fontsize = 8, verticalalignment = "top")

    snake_scatter = ax.scatter([],[], c = "red", label = "Snake", zorder = 3)
    prey_scatter = ax.scatter([], [],label = "Prey", zorder = 2)

    ax.legend(loc = "upper right")

    for game_state in game_states:

        grid = np.zeros((grid_size, grid_size)) # grid to be used for environment and safezones only, kept here in case the safe zone needs to be updated

        # Mark safe zone
        for sz in game_state['safe_zone_status']:
            grid[sz[0]:sz[0] + sz[2], sz[1]:sz[1] + sz[2]] = 3 if sz[3] else 1

        # Mark snake position
        # grid[game_state['snake_position'][0], game_state['snake_position'][1]] = 1 # No longer using grids because overlaps loses data
        snake_x, snake_y = game_state['snake_position']


        # Mark prey positions
        prey_position = [ (prey[0], prey[1]) for prey in game_state['prey_positions']]

        img.set_data(grid)
        
        snake_scatter.set_offsets([[snake_y, snake_x]])

        if prey_position:
            prey_scatter.set_offsets([(p[1], p[0]) for p in prey_position])

            new_colors = ["yellow" if not p[2] else "green" for p in game_state['prey_positions']]
            prey_scatter.set_facecolor(new_colors)
            
            # Add total capture per prey
            capture_string = "\n".join(
                f"Prey_ID {i}: {prey[-1]}times" for i, prey in enumerate(game_state['prey_positions'])
            )
        else:
            prey_scatter.set_offsets([])
            capture_string = ""
            
        capture_text.set_text("Captures:\n"+ capture_string)

        

        plt.title(f'Snake Game Visualization: Step {game_state["step"]}')

        plt.pause(0.5)
    
    plt.show()

    if DEBUG:
        # overwrite JSON file
        with open('game_log.json', 'w'):
            pass

def main(no_steps = STEPS):
    global STEPS 

    STEPS = no_steps

if __name__ == "__main__":
    
    if DEBUG:
        main(int(sys.argv[1])) # To allow for quick changes in step counts during debugging
    
    game = Game()
    for _ in range(STEPS):
        snake, prey_list, safe_zone = game.step()
        game.game_write_to_file()
    
    game_states = game.game_from_file('game_log.json')
    game_data = pd.read_json('game_log.json', lines = True)

    visualize_game(game_states)

    

    #print(game_data.head())
    #print(game_data.tail(10))
    #print(game_data.summary())