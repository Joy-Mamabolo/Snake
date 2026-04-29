import random

class Agent:
    def __init__(self, x, y, speed = 1, symbol = 'A'):
        self.x = x
        self.y = y
        self.speed = speed
        self.symbol = symbol
    
    def move(self, dx, dy, grid_size):
        self.x = max(0, min(grid_size-1, self.x + dx*self.speed))
        self.y = max(0, min(grid_size-1, self.y + dy*self.speed))

class Snake(Agent):
    def __init__(self, x, y)
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
                self.move(self.speed, 0, grid_size = 20 )
            else:
                self.move(0, self.speed, grid_size = 20)
             
        
class Prey(Agent):
    def __init__(self, x, y, learning = False):
        super().__init__(x, y, speed = 1, symbol="P")
        self.learning = learning
    
    def random_move(self, grid_size):

        dx, dy = random.choice([(0,1),(0,-1),(1,0),(-1,0)])
        self.move(dx, dy, grid_size)

class SafeZone:
    def __init__(self, x, y, size = 4, capacity = 3):
        self.x = x
        self.y = y
        self.size = size
        self.capacity = capacity
        self.occupants = []
    
    def admit(self, prey):
        if len(self.occupants) < self.capacity:
            self.occupants.append(prey)
            return True
        return False
    
    def release(self, prey):
        if prey in self.occupants:
            self.occupants.remove(prey)

class Game:
    def __init__(self, grid_size = 20, num_prey = 5):
        self.grid_size = grid_size
        self.snake = Snake(grid_size//2, grid_size//2)
        self.prey_list = [Prey(random.randint(0, grid_size-1), random.randint(0, grid_size -1)) for _ in range(num_prey)]
        self.safe_zone = [SafeZone(5, 5)]
    
    def step(self):
        # snake moves
        self.snake.chase(self.prey_list)

        #prey moves
        for prey in self.prey_list:
            prey.random_move(self.grid_size)
        
        # check safe zone admissions
        
        # check captures

