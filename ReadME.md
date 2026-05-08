This is a 2 phase project.

Phase 1: Multi-agent prey escaping rule based predator agent to generate synthetic data for data analysis
Phase 2: Data analysis of synthetic data to detect emergent behaviour

Purpose: To learn basic workings of Q-learning by coding it from scratch (not a priority), and then use generated data to improve data analysis skills (priority)

# Phase 1: Snake MARL Game

This world is modelled after the classic snake game world where there is a boundary within which a predator pursues food. However, in this world, the food can move and must try to survive as long as possible.

## Agents:
- Snake - The snake is of length 1 and does not grow. Snake is also non-learning, and implements greedy-pursuit algorithm (move towards closest prey) with barrier avoidance for when the safe_zone is active.
- Prey - There are 2 kinds of prey: learning and non-learning prey. All prey start with random movements, and the learning prey must learn to avoid the snake.
- Learning prey will have a 3x3 observable neighbourhood. In this world they will be able to detect other prey that are within this neighbourhood; the snake when it is in this neighbourhood; and walls when they are in the neighbourhood. They will also be able to detect the distance to the safe_zone marker from any place on the global grid.

## Environment:
- Grid - Grid is a standard box with no intermediate obstacles.
- Safe zones - The grid contains safe zones that have a specific carrying capacity. When the number of prey inside of the zone is below the carrying capacity, the edges of the safe zone become walls to the snake (active safe zone). When the number of prey inside the zone exceeds carrying capacity, the walls collapse and allow snake entry (inactive safe zone). The safe zone will remain inactive until both the occupancy of the safe zone is below capacity and the snake has left the safe zone (so that the snake is not trapped in the safe zone).

## Data persistence:
A game state dictionary holds some of the states of the different objects and is stored in a JSON file for eventual data analysis and model visualization.

## Visualization:
- Matplotlib is currently being used for visuals.
- The background and safezones are represented as a grid and drawn as a heatmap, while the agents (snake and prey) are plotted using the scatter function to allow for overlapping which heatmapping does not allow for in the current implementation.
- The figure displays the step number and also displays the number of times particular prey have been captured using their prey_list indices as identifiers.

## Learning System:
- Q-Learning using the Bellman Equation is used to improve prey decision making.
- State definition: The prey observes information about other prey, the snake and its environment only within its immediate vicinity (i.e in a 3x3 grid in which it is centered). This information encodes details about the cell type (normal, active safe zone or inactive safe zone), occupants (empty, prey or snake), and boundary into a 27-character long string.
    - The following characters are used to encode features in the prey's neighbourhood:
        - "NN": normal cell type
        - "O+": active safe zone cell
        - "O-": inactive safe zone cell
        - "P": prey
        - "S": snake
        - ".": empty cell/no occupant
        - "XXX": boundary/wall
- Reward profile - The following reward profile is being used and will be captured as global variables so that all changes can happen there should changes be required:
    - capture : -10
    - boundary collision: -5
    - survival: +1
    - survival in active safe-zone: +2


- Quirks:
    Unlike standard implementations where prey capture might end the episode, prey captures only cause respawns in this implementation. Episodes are governed by a total step count. This allows for uniform training opportunity for all learning prey and not have learning speed affected randomly.
    As a result of the above, the capture reward may need to be tweaked as it is much more than what is currently stated. This is because the next_q value in the bellman equation cannot be determined (since the prey will respawn at a randomish location), nor should it be determined because that state has no bearing on the last action made. This means that next_q will evaluate to 0.0 when the update_q_table function is called after a capture.
    This means that the Bellman Equation will simplify to {new_q = old_q + alpha*(reward - old_q)}; and since reward will be negative as well, the perceived consequence of a capture is even more severe.

    This should be monitored to ensure it does not adversely affect learning progression.
    
