This is a 2 phase project.

Phase 1: Multi-agent prey escaping rule based predator agent to generate synthetic data for data analysis
Phase 2: Data analysis of synthetic data to detect emergent behaviour

Purpose: To learn basic workings of Q-learning by coding it from scratch (not a priority), and then use generated data to improve data analysis skills (priority)

Phase 1: Snake MARL Game

This world is modelled after the classic snake game world where there is a boundary within which a predator pursues food. However, in this world, the food can move and must try to survive as long as possible.

Agents:
> Snake - The snake is of length 1 and does not grow
> Prey - There are 2 kinds of prey: learning and non-learning prey. All prey start with random movements, and the learning prey must learn to avoid the snake.

Environment:
> Grid - Grid is a standard box with no intermediate obstacles.
> Safe zones - The grid contains safe zones that have a specific carrying capacity. When the number of prey inside of the zone is below the carrying capacity, the edges of the safe zone become walls to the snake. When the number of prey inside the zone exceeds carrying capacity, the walls collapse.