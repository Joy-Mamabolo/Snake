import json
import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

GRID_SIZE = 20
NUM_PREY = 5
STEPS = 50
DEBUG = False


class Agent:
    def __init__(self, x, y, speed = 1, symbol = 'A'):
        self.x = x
        self.y = y
        self.speed = speed
        self.symbol = symbol
    
    def move(self, dx, dy, grid_size = GRID_SIZE):
        self.x = max(0, min(grid_size-1, self.x + dx*self.speed))
        self.y = max(0, min(grid_size-1, self.y + dy*self.speed))

class Snake(Agent):
    def __init__(self, x, y):
        super().__init__(x, y, speed=1, symbol = "S")
    
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
            if closest_prey.x > closest_prey.y:
                return (self.speed, 0) if closest_prey.x>=self.x else (-self.speed,0)
            else:
                return (0, self.speed) if closest_prey.y>=self.y else (0, -self.speed)
        else:
            return 0, 0 # if there are no prey, stay in place - should not be the case since the game should end when all prey are captured

class Prey(Agent):
    def __init__(self, x, y, learning = False):
        super().__init__(x, y, speed = 1, symbol="P")
        self.alive = True
        self.generation = 0 # generation of the prey - also used to track how many times the prey has been captured and respawned.
        
        self.learning = learning
        self.q_table = {} if learning else None # State-action value table for Q-learning not implemented yet
        self.reward = 0 # reward received in the current step, used for learning prey. Not implemented yet
        
    
    def propose_move(self): # This function defines how the prey moves randomly in the environment. This will be used for the non-learning prey in the long term, but for the learning prey, this will be replaced by a Q-table based action selection function.
        if self.learning:
            # Observe the world and update the Q-table based on the reward received from the previous action. Then select an action based on the Q-table. Not implemented yet.
            if not DEBUG:
                dx = 0
                dy = 0
                pass  # action selection based on Q-table
            else:
                dx, dy = random.choice([(0,self.speed),(0,-self.speed),(self.speed,0),(-self.speed,0)])
        else:
            dx, dy = random.choice([(0,self.speed),(0,-self.speed),(self.speed,0),(-self.speed,0)])
        
        return dx, dy
    
    def observe(self, world):
        # This function defines how the prey observes the world 

        obs = {}

        # 3x3 grid around the prey
        neighbourhood = []
        for dx in range(-1,2):
            for dy in range(-1,2):
                nx = self.x + dx
                ny = self.y +dy

                if 0 <= nx < world.grid_size and 0 <= ny < world.grid_size:
                    if world.snake.x == nx and world.snake.y == ny:
                        neighbourhood.append('S')
                    elif any(prey.x == nx and prey.y == ny for prey in world.prey_list):
                        neighbourhood.append('P')
                    else:
                        neighbourhood.append('.')
                else:
                    neighbourhood.append('X') # Out of bounds
        
        obs['neighbourhood'] = tuple(neighbourhood)
        obs['in_safe_zone'] = world.is_in_safe_zone(self)
        obs['neighbour_count'] = sum(1 for cell in neighbourhood if cell == 'P')
        obs['distance_to_safe_zone'] = abs(self.x - world.safe_zone[0].x) + abs(self.y - world.safe_zone[0].y) # Only determines distance to the first safe zone. Must change it once there are more than one
        
        return obs


class SafeZone:
    def __init__(self, x, y, size = 4, capacity = 3):
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
    
    def is_in_safe_zone(self, prey):
        for safe_zone in self.safe_zone:
            if (safe_zone.x<=prey.x<=safe_zone.x+safe_zone.size) and (safe_zone.y<=prey.y<=safe_zone.y+safe_zone.size):
                return True
        return False

    def is_in_bounds(self, x, y):
        return False if x < 0 or x >= self.grid_size or y < 0 or y >= self.grid_size else True

    def step(self):
        # snake moves
        self.step_count+=1
        sdx,sdy = self.snake.chase(self.prey_list) # chase function determines the proposed move of the snake and game checks if the move is valid before executing it.

        proposed_snake_x = self.snake.x + sdx
        proposed_snake_y = self.snake.y + sdy

        if self.is_in_bounds(proposed_snake_x, proposed_snake_y):
            if any((sz.active and sz.x <= proposed_snake_x <= sz.x + sz.size and sz.y <= proposed_snake_y <= sz.y + sz.size) for sz in self.safe_zone):
                self.snake.move(0, 0) # if proposed move is into an active safe zone, stay in place. Would like to condider other options later.
            else:
                self.snake.move(sdx, sdy) # proposed move is valid, execute it
        else:
            self.snake.move(0, 0) # if proposed move is out of bounds, stay in place. Would like to consider other options such as bouncing back or wrapping around later.

        #prey
        for prey in self.prey_list:
            
            if not prey.alive:
                # Captured Prey Respawns
                prey.x = 0 if self.snake.x>self.grid_size-1-self.snake.x else self.grid_size-1  # furthest distance away from the snake within bounds at that step.
                prey.y = 0 if self.snake.y>self.grid_size-1-self.snake.y else self.grid_size-1
                prey.alive = True
            
            else:
                # Prey moves
                dx, dy = prey.propose_move()

                if self.is_in_bounds(prey.x + dx, prey.y + dy):
                    prey.move(dx, dy, grid_size = self.grid_size)
                else:
                    prey.move(0, 0, grid_size = self.grid_size) # if proposed move is out of bounds, stay in place
                    prey.reward = -1 # negative reward for trying to move out of bounds. This is for learning prey. 
        
        # check safe zone admissions
        for sz in self.safe_zone: # there is only one safe zone for now but this allows for more than one should we wish
            sz.current_occupants = 0 # must reset in every step so that it keeps the current count and not total count
            for prey in self.prey_list:
                if (sz.x<=prey.x<=sz.x+sz.size) and (sz.y<=prey.y<=sz.y+sz.size):
                    sz.current_occupants +=1

                    if sz.active and sz.current_occupants >= sz.capacity:
                        sz.active = False # Safe zone becomes inactive when capacity is reached.
                    elif sz.active and sz.current_occupants < sz.capacity:
                        pass # Safe zone is active and below capacity, nothing changes
                    elif not sz.active and sz.current_occupants < sz.capacity and not (sz.x<=self.snake.x<=sz.x+sz.size and sz.y<=self.snake.y<=sz.y+sz.size):
                        sz.active = True # Safe zone becomes active again when occupants are below capacity and snake is no longer inside the safe zone.
                    else:
                        pass # Safe zone is inactive and either occupants are above capacity or snake is still inside, nothing changes
        
        # check captures
        for prey in self.prey_list:
            if prey.x == self.snake.x and prey.y == self.snake.y:
                prey.alive = False
                # self.prey_list.remove(prey) # remove captured prey from the game. Perhaps prey should not be removed from list, but respawned some safe distance away from snake and log the capture instead


        return self.snake, self.prey_list, self.safe_zone

    def game_write_to_file(self):
        # Save the current game to a file for later analysis.
        data = {
            'step': self.step_count,
            'snake_position': (self.snake.x, self.snake.y),
            'prey_positions': [(prey.x, prey.y, prey.learning) for prey in self.prey_list],
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
    img = ax.imshow(grid, cmap = 'tab20', vmin=0, vmax = 4, alpha = 0.5)

    snake_scatter = ax.scatter([],[], c = "red", marker = 's', label = "Snake")
    prey_scatter = ax.scatter([], [], c = "yellow", marker = "o", label = "Snake")

    for game_state in game_states:

        grid = np.zeros((grid_size, grid_size)) # grid to be used for environment and safezones only, kept here in case the safe zone needs to be updated

        # Mark safe zone
        for sz in game_state['safe_zone_status']:
            grid[sz[0]:sz[0] + sz[2], sz[1]:sz[1] + sz[2]] = 3 if sz[3] else 0

        # Mark snake position
        # grid[game_state['snake_position'][0], game_state['snake_position'][1]] = 1 # No longer using grids because overlaps loses data
        snake_x, snake_y = game_state['snake_position']


        # Mark prey positions
        prey_position = [ (prey[0], prey[1]) for prey in game_state['prey_positions']]
        
        img.set_data(grid)
        
        snake_scatter.set_offsets([[snake_x, snake_y]])

        if prey_position:
            prey_scatter.set_offsets([(p[0], p[1]) for p in prey_position])

        

        plt.title(f'Snake Game Visualization: Step {game_state["step"]}')

        plt.pause(0.5)
    
    plt.show()

    if DEBUG:
        # overwrite JSON file
        with open('game_log.json', 'w'):
            pass


if __name__ == "__main__":
    game = Game()
    for _ in range(STEPS):
        snake, prey_list, safe_zone = game.step()
        game.game_write_to_file()
    
    game_states = game.game_from_file('game_log.json')
    game_data = pd.read_json('game_log.json', lines = True)

    visualize_game(game_states)

    

    print(game_data.head())
    print(game_data.tail(10))
    #print(game_data.summary())