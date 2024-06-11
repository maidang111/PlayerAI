import heapq
import random
import json
import os

def load_status(file_path='stats.json'):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)
    else:
        return {
            "Stamina": 50,
            "Hunger": 50,
            "Gain_Stamina": False,
            "Visited": []
        }

def save_status(status, file_path='stats.json'):
    with open(file_path, 'w') as file:
        json.dump(status, file, indent=4)

def a_star(start, goal, dungeon_map, coins, potions, foods, visited):
    directions = [(0, -1), (-1, 0), (0, 1), (1, 0)]
    direction_map = {(-1, 0): 'A', (1, 0): 'D', (0, -1): 'W', (0, 1): 'S'}

    def is_within_bounds(position):
        x, y = position
        return 0 <= x < len(dungeon_map[0]) and 0 <= y < len(dungeon_map)

    def is_walkable(position):
        x, y = position
        return dungeon_map[y][x] == 'floor'

    def is_empty(position):
        return position not in coins and position not in potions and position not in foods

    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    open_list = []
    heapq.heappush(open_list, (0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}

    while open_list:
        _, current = heapq.heappop(open_list)

        if current == goal:
            path = []
            while current in came_from:
                prev = came_from[current]
                path.append(direction_map[(current[0] - prev[0], current[1] - prev[1])])
                current = prev
            return path[::-1]

        for direction in directions:
            neighbor = (current[0] + direction[0], current[1] + direction[1])
            if not is_within_bounds(neighbor) or not is_walkable(neighbor):
                continue

            tentative_g_score = g_score[current] + 1

            if is_empty(neighbor):
                tentative_g_score += 1

            if neighbor in visited:
                tentative_g_score += 2 

            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                heapq.heappush(open_list, (f_score[neighbor], neighbor))

    return []

def player1_logic(coins, potions, foods, dungeon_map, self_position, other_agent_position):
    directions = {'W': (0, -1), 'A': (-1, 0), 'S': (0, 1), 'D': (1, 0)}
    status = load_status()
    if status["Stamina"] <= 0:
        status["Stamina"] = 50
        status["Hunger"] = 50
        status["Gain_Stamina"] = False
        status["Visited"] = []


    if self_position not in status["Visited"]:
        status["Visited"].append(self_position)

    if other_agent_position not in status["Visited"]:
        status["Visited"].append(other_agent_position)

    targets = coins + potions + foods

    status["Hunger"] -= 0.5

    if not status["Gain_Stamina"]:
        status["Stamina"] -= 1
    
    status["Gain_Stamina"] = not status["Gain_Stamina"]

    if status["Hunger"] < 15:
        targets = foods
        
    if status["Stamina"] < 30:
        targets = potions

    if not targets:
        targets = coins

    if targets:
        min_distance = float('inf')
        target_position = None

        for target in targets:
            distance = abs(self_position[0] - target[0]) + abs(self_position[1] - target[1])
            if distance < min_distance or (min_distance == distance and (target in foods or target in potions)):
                min_distance = distance
                target_position = target

        if target_position:
            path = a_star(self_position, target_position, dungeon_map, coins, potions, foods, status["Visited"])
            if path:
                new_pos = (self_position[0] + directions[path[0]][0], self_position[1] + directions[path[0]][1])
                if new_pos not in status["Visited"]:
                    status["Visited"].append(new_pos)

                if new_pos in potions:
                    status["Stamina"] = min(status["Stamina"] + 20, 50)
                elif new_pos in foods:
                    status["Hunger"] = min(status["Hunger"] + 30, 50)
                save_status(status)
                return path[0]

    valid_moves = []
    for move, (dx, dy) in directions.items():
        nx, ny = self_position[0] + dx, self_position[1] + dy
        if dungeon_map[ny][nx] == 'floor':
            valid_moves.append(move)

    if not valid_moves:
        save_status(status)
        return 'I'

    save_status(status)
    return random.choice(valid_moves)