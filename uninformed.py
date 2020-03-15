import os
import sys
import time
from Queue import Queue

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
    def __init__(self, state, path, is_forward, zero_coord):
        self.state = state
        self.path = path
        self.is_forward = is_forward
        self.n = len(state)
        self.zero_coord = zero_coord
        self.actions = self.valid_actions()
        self.hash_string = self.hash()

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
        if len(self.zero_coord) == 0:
            for i in range(self.n):
                for j in range(self.n):
                    if self.state[i][j] == 0:
                        self.zero_coord = [i, j]
                        break
        if self.zero_coord[0] < self.n - 1:
            actions.append("UP")
        if self.zero_coord[0] > 0:
            actions.append("DOWN")
        if self.zero_coord[1] < self.n - 1:
            actions.append("LEFT")
        if self.zero_coord[1] > 0:
            actions.append("RIGHT")
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
                    i += 1
                elif action == "DOWN":
                    new_state[i][j] = new_state[i - 1][j]
                    new_state[i - 1][j] = 0
                    i -= 1
                elif action == "LEFT":
                    new_state[i][j] = new_state[i][j + 1]
                    new_state[i][j + 1] = 0
                    j += 1
                elif action == "RIGHT":
                    new_state[i][j] = new_state[i][j - 1]
                    new_state[i][j - 1] = 0
                    j -= 1
                expanded_nodes.append(Node(new_state, self.path + [action], self.is_forward, [i, j]))
        return expanded_nodes

    def is_goal(self):
        for i in range(self.n):
            for j in range(self.n):
                if self.state[i][j] != (i * self.n + j + 1) % (self.n * self.n):
                    return False
        return True

class Puzzle(object):
    def __init__(self, init_state, goal_state):
        # you may add more attributes if you think is useful
        self.init_state = init_state
        self.goal_state = goal_state
        self.count = 0
        self.time = 0.0

    def solve(self, timeout = -1):
        start_time = time.time()
        forward_flag = True # forward expansion or backward expansion for bidirectional search
        start_node = Node(self.init_state, [], True, [])
        goal_node = Node(self.goal_state, [], False, [])
        if start_node.is_goal():
            return []
        forward_visited = { start_node.hash_string: start_node }
        backward_visited = { goal_node.hash_string: goal_node }
        node_queue = Queue()
        node_queue.put(start_node)
        node_queue.put(goal_node)
        result = None

        while True:
            if timeout != -1 and time.time() - start_time > timeout:
                self.count = -1
                self.time = -1 # undefined due to timeout
                return []
            if node_queue.empty():
                result = ["UNSOLVABLE"]
                break
            node = node_queue.get()
            forward_flag = node.is_forward
            expanded_nodes = node.expand()
            for node in expanded_nodes:
                if forward_flag and node.hash_string in forward_visited \
                    or not forward_flag and node.hash_string in backward_visited:
                    continue
                if forward_flag and node.hash_string in backward_visited:
                    result = self.formulate_solution(node, backward_visited[node.hash_string])
                    break
                elif not forward_flag and node.hash_string in forward_visited:
                    result = self.formulate_solution(forward_visited[node.hash_string], node)
                    break
                else:
                    node_queue.put(node)
                    if forward_flag:
                        forward_visited[node.hash_string] = node
                    else:
                        backward_visited[node.hash_string] = node
            if result is not None:
                break
        self.count = len(forward_visited.keys()) + len(backward_visited.keys())
        self.time = time.time() - start_time
        # print len(forward_visited.keys()) + len(backward_visited.keys())  # number of traversed nodes
        # print time.time() - start_time
        return result

    def formulate_solution(self, forward_node, backward_node):
        path = forward_node.path
        for i in range(len(backward_node.path)-1, -1, -1):
            path.append(reverse_action(backward_node.path[i]))
        return path
        
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







