import os
import sys
import time
from heapq import heappush, heappop

def reverse_action(action):
    if action == "UP":
        return "DOWN"
    if action == "DOWN":
        return "UP"
    if action == "LEFT":
        return "RIGHT"
    if action == "RIGHT":
        return "LEFT"

class Node():
    def __init__(self, state, path):
        self.state = state
        self.path = path
        self.n = len(state)
        self.zero_coord = []
        self.actions = self.valid_actions()
        self.hash_string = self.hash()
        self.evaluation = len(self.path) + self.heuristic()

    def hash(self):
        hash_string = ""
        for i in range(self.n):
            for j in range(self.n):
                hash_string += str(self.state[i][j])
                if (i < len(self.state) - 1) or (j < len(self.state[i]) - 1):
                    hash_string += ","
        return hash_string

    def __str__(self):
        output = str(self.path) + "\n"
        for i in range(self.n):
            for j in range(self.n):
                output += str(self.state[i][j]) + " "
            output += "\n"
        return output

    # valid actions based on the position of the empty block only
    def valid_actions(self):
        actions = []
        for i in range(self.n):
            for j in range(self.n):
                if self.state[i][j] == 0:
                    if i < self.n - 1:
                        actions.append("UP")
                    if i > 0:
                        actions.append("DOWN")
                    if j < self.n - 1:
                        actions.append("LEFT")
                    if j > 0:
                        actions.append("RIGHT")
                    self.zero_coord = [i, j]
                    break
        return actions

    def expand(self):
        last_action = ""
        if len(self.path) > 0:
            last_action = self.path[-1]
        expanded_nodes = []
        for action in self.actions:
            if action != reverse_action(last_action):
                new_state = [row[:] for row in self.state] # deep copy
                i = self.zero_coord[0]
                j = self.zero_coord[1]
                if action == "UP":
                    new_state[i][j] = new_state[i + 1][j]
                    new_state[i + 1][j] = 0
                elif action == "DOWN":
                    new_state[i][j] = new_state[i - 1][j]
                    new_state[i - 1][j] = 0
                elif action == "LEFT":
                    new_state[i][j] = new_state[i][j + 1]
                    new_state[i][j + 1] = 0
                elif action == "RIGHT":
                    new_state[i][j] = new_state[i][j - 1]
                    new_state[i][j - 1] = 0
                expanded_nodes.append(Node(new_state, self.path + [action]))
        return expanded_nodes

    def is_goal(self):
        for i in range(self.n):
            for j in range(self.n):
                if self.state[i][j] != (i * self.n + j + 1) % (self.n * self.n):
                    return False
        return True

    def get_goal_i(self, n):
        if n == 0:
            return self.n - 1
        else:
            return (n - 1) / self.n

    def get_goal_j(self, n):
        if n == 0:
            return self.n - 1
        else:
            return (n - 1) % self.n

    def is_in_conflict(self, i, j, a, b):
        if self.state[i][j] == 0 or self.state[a][b] == 0:
            return False
        if i == a:
            if j == b:
                return False
            if self.get_goal_i(self.state[i][j]) != i:
                return False
            if self.get_goal_i(self.state[a][b]) != i:
                return False
            if j < b:
                return self.get_goal_j(self.state[i][j]) > self.get_goal_j(self.state[a][b])
            if j > b:
                return self.get_goal_j(self.state[i][j]) < self.get_goal_j(self.state[a][b])
        elif j == b:
            if i == a:
                return False
            if self.get_goal_j(self.state[i][j]) != j:
                return False
            if self.get_goal_j(self.state[a][b]) != j:
                return False
            if i < a:
                return self.get_goal_i(self.state[i][j]) > self.get_goal_i(self.state[a][b])
            if i > a:
                return self.get_goal_i(self.state[i][j]) < self.get_goal_i(self.state[a][b])
        else:
            return False

    def heuristic(self):
        h = 0
        # Manhattan distance
        for i in range(self.n):
            for j in range(self.n):
                if self.state[i][j] == 0:
                    continue
                else:
                    goal_i = self.get_goal_i(self.state[i][j])
                    goal_j = self.get_goal_j(self.state[i][j])
                h += abs(goal_i - i) + abs(goal_j - j)
        # Linear conflict on rows
        linear_conflict = 0
        for i in range(self.n):
            num_tiles_in_conflict = []
            tile_removed = []
            for j in range(self.n):
                num_tiles_in_conflict.append(0)
                tile_removed.append(False)
                for k in range(self.n):
                    if self.is_in_conflict(i, j, i, k):
                        num_tiles_in_conflict[j] += 1
            while sum(num_tiles_in_conflict) != 0:
                max_conflict = 0
                max_conflict_tile = 0
                for k in range(self.n):
                    if num_tiles_in_conflict[k] > max_conflict:
                        max_conflict = num_tiles_in_conflict[k]
                        max_conflict_tile = k
                num_tiles_in_conflict[max_conflict_tile] = 0
                tile_removed[max_conflict_tile] = True
                for k in range(self.n):
                    if not tile_removed[k] and self.is_in_conflict(i, max_conflict_tile, i, k):
                        num_tiles_in_conflict[k] -= 1
                linear_conflict += 1
        # Linear conflict on columns
        for j in range(self.n):
            num_tiles_in_conflict = []
            tile_removed = []
            for i in range(self.n):
                num_tiles_in_conflict.append(0)
                tile_removed.append(False)
                for k in range(self.n):
                    if self.is_in_conflict(i, j, k, j):
                        num_tiles_in_conflict[i] += 1
            while sum(num_tiles_in_conflict) != 0:
                max_conflict = 0
                max_conflict_tile = 0
                for k in range(self.n):
                    if num_tiles_in_conflict[k] > max_conflict:
                        max_conflict = num_tiles_in_conflict[k]
                        max_conflict_tile = k
                num_tiles_in_conflict[max_conflict_tile] = 0
                tile_removed[max_conflict_tile] = True
                for k in range(self.n):
                    if not tile_removed[k] and self.is_in_conflict(max_conflict_tile, j, k, j):
                        num_tiles_in_conflict[k] -= 1
                linear_conflict += 1
        h += 2 * linear_conflict
        return h

    def __cmp__(self, other):
        return cmp(self.evaluation, other.evaluation)

class Puzzle(object):
    def __init__(self, init_state, goal_state):
        # you may add more attributes if you think is useful
        self.init_state = init_state
        self.goal_state = goal_state
        self.count = 0
        self.time = 0.0

    def solve(self, timeout = -1):
        start_time = time.time()
        start_node = Node(self.init_state, [])
        if start_node.is_goal():
            return []
        visited = {}
        node_queue = []
        heappush(node_queue, start_node)

        while True:
            if timeout != -1 and time.time() - start_time > timeout:
                self.count = -1
                self.time = -1 # undefined due to timeout
                return []
            if len(node_queue) <= 0:
                return ["UNSOLVABLE"]
            node = heappop(node_queue)
            visited[node.hash_string] = node
            if node.is_goal():
                self.time = time.time() - start_time
                # print self.count # total traversed nodes
                # print self.time
                return node.path
            expanded_nodes = node.expand()
            for new_node in expanded_nodes:
                if new_node.hash_string in visited:
                    continue
                heappush(node_queue, new_node)
                self.count += 1
        
    # you may add more functions if you think is useful

if __name__ == "__main__":
    # do NOT modify below

    # argv[0] represents the name of the file that is being executed
    # argv[1] represents name of input file
    # argv[2] represents name of destination output file
    if len(sys.argv) != 3:
        raise ValueError("Wrong number of arguments!")

    try:
        f = open(sys.argv[1], 'r')
    except IOError:
        raise IOError("Input file not found!")

    lines = f.readlines()
    
    # n = num rows in input file
    n = len(lines)
    # max_num = n to the power of 2 - 1
    max_num = n ** 2 - 1

    # Instantiate a 2D list of size n x n
    init_state = [[0 for i in range(n)] for j in range(n)]
    goal_state = [[0 for i in range(n)] for j in range(n)]
    

    i,j = 0, 0
    for line in lines:
        for number in line.split(" "):
            if number == '':
                continue
            value = int(number , base = 10)
            if  0 <= value <= max_num:
                init_state[i][j] = value
                j += 1
                if j == n:
                    i += 1
                    j = 0

    for i in range(1, max_num + 1):
        goal_state[(i-1)//n][(i-1)%n] = i
    goal_state[n - 1][n - 1] = 0

    puzzle = Puzzle(init_state, goal_state)
    ans = puzzle.solve()

    with open(sys.argv[2], 'a') as f:
        for answer in ans:
            f.write(answer+'\n')







