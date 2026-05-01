import random

GRID_SIZE = 20
NUM_PREY = 5

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
                self.move(self.speed, 0, grid_size = GRID_SIZE )
            else:
                self.move(0, self.speed, grid_size = GRID_SIZE)
             
        
class Prey(Agent):
    def __init__(self, x, y, learning = False):
        super().__init__(x, y, speed = 1, symbol="P")
        self.learning = learning

        self.q_table = {} if learning else None # State-action value table for Q-learning not implemented yet

        self.reward = 0 # reward received in the current step, used for learning prey. Not implemented yet
    
    def propose_move(self, grid_size = GRID_SIZE): # This function defines how the prey moves randomly in the environment. This will be used for the non-learning prey in the long term, but for the learning prey, this will be replaced by a Q-table based action selection function.

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
        self.prey_list = [Prey(random.randint(0, grid_size-1), random.randint(0, grid_size -1)) for _ in range(num_prey)]
        self.safe_zone = [SafeZone(5, 5)] # x,y of safe zone represents bottom left corner
    
    def is_in_safe_zone(self, prey):
        for safe_zone in self.safe_zone:
            if (safe_zone.x<=prey.x<=safe_zone.x+safe_zone.size) and (safe_zone.y<=prey.y<=safe_zone.y+safe_zone.size):
                return True
        return False

    def is_in_bounds(self, x, y):
        return False if x < 0 or x >= self.grid_size or y < 0 or y >= self.grid_size else True

    def step(self):
        # snake moves
        self.snake.chase(self.prey_list) # Snake needs to be prevented from moving into the safe zone if it is active.

        #prey moves
        for prey in self.prey_list:
            dx, dy = prey.propose_move()

            if self.is_in_bounds(prey.x + dx, prey.y + dy):
                prey.move(dx, dy, grid_size = self.grid_size)
            else:
                prey.move(0, 0, grid_size = self.grid_size) # if proposed move is out of bounds, stay in place
                prey.reward = -1 # negative reward for trying to move out of bounds. This is for learning prey.
        
        # check safe zone admissions
        for sz in self.safe_zone: # there is only one safe zone for now but this allows for more than one should we wish
            for prey in self.prey_list:
                if (sz.x<=prey.x<=sz.x+sz.size) and (sz.y<=prey.y<=sz.y+sz.size):
                    sz.current_occupants +=1

                    if sz.active and sz.current_occupants >= sz.capacity:
                        sz.active = False
                    else:





        # check captures

