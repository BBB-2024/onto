import requests
import json
from math import sqrt
from typing import List, Dict, Union

class Scenario:
    def __init__(self, input_data: Dict, result: List[str]):
        self.data = input_data
        self.result = result

    def __repr__(self):
        return f"Scenario(data={self.data}, result={self.result})"

class City:
    def __init__(self, name: str, position: Dict[str, int], distances: Dict[str, int]):
        self.name = name
        self.position = position
        self.distances = distances

class ScenarioManager:
    def __init__(self):
        self.scenarios = []

    def de_ja_vu(self, data: Dict) -> bool:
        """Check if the scenario already exists in the list."""
        for scenario in self.scenarios:
            if scenario.data == data:
                return True
        return False

    def get_scenario(self, data: Dict) -> Union[Scenario, None]:
        """Retrieve a scenario based on the data."""
        for scenario in self.scenarios:
            if scenario.data == data:
                return scenario
        return None

    def add_scenario(self, data: Dict, result: List[str]):
        """Add a new scenario."""
        self.scenarios.append(Scenario(data, result))

class MapSolver:
    def __init__(self):
        self.scenario_manager = ScenarioManager()
        self.base_url = "http://bitkozpont.mik.uni-pannon.hu/2024"
        self.team_code = "be98b0b567b9887e75e5"

    def heuristic(self, a: Dict, b: Dict) -> int:
        """Heuristic function for A* (Manhattan distance)."""
        return max(abs(a['x'] - b['x']), abs(a['y'] - b['y']))

    def dot_product(self, a: Dict, b: Dict) -> int:
        """Dot product function to check directional movement towards the goal."""
        return a['x'] * b['x'] + a['y'] * b['y']

    def find_shortest_path_length(self, city1: Dict, city2: Dict) -> Union[int, float]:
        """A* Algorithm to find the shortest path length between two cities."""
        open_list = []
        closed_list = set()

        start_node = {
            'x': city1['x'],
            'y': city1['y'],
            'g': 0,  # Cost from start node
            'h': self.heuristic(city1, city2),  # Heuristic to goal
            'f': self.heuristic(city1, city2),  # Total cost f = g + h
            'parent': None
        }

        open_list.append(start_node)

        directions = [
            {'x': 0, 'y': -1, 'cost': 1},  # Up
            {'x': 1, 'y': 0, 'cost': 1},   # Right
            {'x': 0, 'y': 1, 'cost': 1},   # Down
            {'x': -1, 'y': 0, 'cost': 1},  # Left
            {'x': -1, 'y': -1, 'cost': sqrt(2)},  # Diagonal movements
            {'x': 1, 'y': -1, 'cost': sqrt(2)},
            {'x': 1, 'y': 1, 'cost': sqrt(2)},
            {'x': -1, 'y': 1, 'cost': sqrt(2)}
        ]

        while open_list:
            open_list.sort(key=lambda node: node['f'])
            current_node = open_list.pop(0)

            if current_node['x'] == city2['x'] and current_node['y'] == city2['y']:
                return current_node['g']  # Return the g-value which is the path length

            closed_list.add(f"{current_node['x']},{current_node['y']}")

            goal_direction = {
                'x': city2['x'] - current_node['x'],
                'y': city2['y'] - current_node['y']
            }

            for direction in directions:
                neighbor = {
                    'x': current_node['x'] + direction['x'],
                    'y': current_node['y'] + direction['y'],
                    'g': current_node['g'] + direction['cost'],
                    'h': self.heuristic(city2, {
                        'x': current_node['x'] + direction['x'],
                        'y': current_node['y'] + direction['y']
                    }),
                    'parent': current_node
                }
                neighbor['f'] = neighbor['g'] + neighbor['h']

                if f"{neighbor['x']},{neighbor['y']}" in closed_list:
                    continue

                move_vector = {
                    'x': neighbor['x'] - current_node['x'],
                    'y': neighbor['y'] - current_node['y']
                }

                dp = self.dot_product(goal_direction, move_vector)

                if dp < 0:
                    continue

                if not any(node['x'] == neighbor['x'] and node['y'] == neighbor['y'] for node in open_list):
                    open_list.append(neighbor)

        return -1  # Return -1 if no path is found

    def get_varos_by_name(self, name: str, varosok: List[Dict]) -> Union[City, None]:
        """Retrieve city by its name."""
        for city in varosok:
            if city['name'] == name:
                return city
        return None

    def find_shortest_path_pitagoras(self, city1: Dict, city2: Dict) -> float:
        """Use Pythagorean theorem to calculate the shortest path."""
        x_diff = city1['x'] - city2['x']
        y_diff = city1['y'] - city2['y']
        return sqrt(x_diff**2 + y_diff**2)

    def make_request(self, task_id: str) -> Dict:
        """Make a request to the API to get the tasks."""
        url = f"{self.base_url}/gettasks.php"
        payload = {'id': task_id, 'teamcode': self.team_code}
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, headers=headers, data=json.dumps(payload))

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Request failed with status {response.status_code}")

    def process_task(self, task_id: str):
        """Main processing method to handle tasks."""
        response = self.make_request(task_id)
        print(response)

        response_data = {
            'original_data': response['data'],
            'id': response['data']['ID'],
            'teamcode': self.team_code,
            'original_hash': response['hash'],
            'answer_data': []
        }

        # Check if we have encountered this task before
        if self.scenario_manager.de_ja_vu(response['data']):
            scenario = self.scenario_manager.get_scenario(response['data'])
            if scenario:
                response_data['answer_data'].append({
                    'id': scenario.data['ID'],
                    'answer': scenario.result
                })
        else:
            for element in response['data']['questions']:
                varosok = element['params']['map']['cities']
                city1p, city2p = None, None
                worst_ratio = 0

                for city1 in varosok:
                    for key, distance in city1['distances'].items():
                        city2 = self.get_varos_by_name(key, varosok)
                        if city2:
                            path_length = self.find_shortest_path_length(city1['position'], city2['position'])
                            ratio = distance - path_length
                            if ratio > worst_ratio:
                                worst_ratio = ratio
                                city1p = city1
                                city2p = city2

                if city1p and city2p:
                    answer = [city1p['name'], city2p['name']]
                    self.scenario_manager.add_scenario(response['data'], answer)
                    response_data['answer_data'].append({'id': element['ID'], 'answer': answer})

        # Send the answer back
        answer_url = f"{self.base_url}/answer.php"
        response_post = requests.post(answer_url, headers={'Content-Type': 'application/json'}, data=json.dumps(response_data))

        if response_post.status_code == 200:
            print("Answer sent successfully!")
        else:
            print(f"Failed to send answer. Status code: {response_post.status_code}")

# Example of how to use the classes:
solver = MapSolver()
solver.process_task("9")
