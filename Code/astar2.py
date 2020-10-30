from queue import PriorityQueue
import copy
import time

LEFT = (-1,0)
RIGHT = (1,0)
DOWN = (0,1)
UP = (0,-1)

MOVES = [UP, LEFT, RIGHT, DOWN]
MOVENAMES = ['UP', 'LEFT', 'RIGHT', 'DOWN']

WIDTH = 10
HEIGHT = 12

numberOfStates = 1
numberOfDifferentStates =1

exploredStates = set()
frontier = PriorityQueue()

seeds = dict()

class Snake:

    def __init__(self, head, tail, body = [], length = 1):
        self.headY = head[0]
        self.headX = head[1]
        self.tailY = tail[0]
        self.tailX = tail[1]
        self.length = length
        self.body = body
        if len(body) == 0:
            self.body.append((self.headY,self.headX))

    def calNewSnake(self, direction, addToBody):
        if addToBody == False:
            return self.move(direction)
        else:
            lastTailY = self.tailY
            lastTailX = self.tailX
            temp = self.move(direction)
            temp["body"].append((lastTailY, lastTailX))
            temp["length"] = temp["length"] + 1
            temp["tail"] = (lastTailY, lastTailX)
            return temp

    def move(self, direction):
        global HEIGHT, WIDTH
        temp = copy.copy(self.body)
        tempHeadY = self.headY
        tempHeadX = self.headX
        tempTailY = self.tailY
        tempTailX = self.tailX
        tempHeadY = (tempHeadY + direction[0])%HEIGHT
        tempHeadX = (tempHeadX + direction[1])%WIDTH
        if self.length == 1:
            tempTailY = tempHeadY
            tempTailX = tempHeadX
            temp.pop()
            temp.append((tempHeadY,tempHeadX))
        else:
            temp.pop()
            temp.insert(0, (tempHeadY,tempHeadX))
            tempTailY = temp[-1][0]
            tempTailX = temp[-1][1]
        return {"head": (tempHeadY, tempHeadX), "tail": (tempTailY, tempTailX), "length": self.length, "body": temp}

    def didGetSeed(self, seeds):
        if (self.headY, self.headX) in seeds:
            return True
        return False

    def isValidMove(self, direction):
        tempHeadY = self.headY
        tempHeadX = self.headX
        tempHeadY = (tempHeadY + direction[0])%HEIGHT
        tempHeadX = (tempHeadX + direction[1])%WIDTH
        if tempHeadY == self.tailY and tempHeadX == self.tailX:
            if self.length == 2:
                return False
            return True
        if (tempHeadY, tempHeadX) in self.body:
            return False
        return True

    def __eq__(self, other):
        return self.body == other.body

class State:
    
    def __init__(self, seeds, snake, lastMove = None, parent = None, depth = 0, initial = False):
        self.lastMove = lastMove
        self.parent = parent
        self.seeds = seeds
        self.snake = snake
        self.depth = depth
        self.isInitial = initial

    def calNewState(self, direction):
        if self.snake.didGetSeed(self.seeds) and self.isInitial == False:
            seedCopy = copy.copy(self.seeds)
            if seedCopy[(self.snake.headY,self.snake.headX)] == 2:
                seedCopy[(self.snake.headY,self.snake.headX)] -= 1
            else:
                del seedCopy[(self.snake.headY,self.snake.headX)]
            newSnakePorp = self.snake.calNewSnake(direction, True)
            newSnake = Snake(newSnakePorp["head"], newSnakePorp["tail"], newSnakePorp["body"], newSnakePorp["length"])
            return newSnake, seedCopy
        else:
            seedCopy = copy.copy(self.seeds)
            newSnakePorp = self.snake.calNewSnake(direction, False)
            newSnake = Snake(newSnakePorp["head"], newSnakePorp["tail"], newSnakePorp["body"], newSnakePorp["length"])
            return newSnake, seedCopy

    def hasParent(self):
        if self.parent:
            return True
        return False

    def isGoal(self):
        if len(self.seeds) == 1:
            for key in self.seeds:
                if self.seeds[key] == 1 and key == (self.snake.headY, self.snake.headX):
                    return True
        return False

    def hScore(self):
        h = 0
        for key in self.seeds:
            h += self.seeds[key]
        return h

    def fScore(self):
        g = self.depth
        h = self.hScore()
        return g + h

    def __lt__(self, other):
        return False
    
    def __eq__(self, other):
        return self.seeds == other.seeds and self.snake == other.snake

    def __hash__(self):
        hashList = []
        for point in self.snake.body:
            hashList.append(point)
        for seed in self.seeds:
            hashList.append((seed[0], seed[1], self.seeds[seed]))
        hashList = tuple(hashList)
        return hash(hashList)

def printSolution(node):
    stack = []
    while node.hasParent():
        stack.append(node.lastMove)
        node = node.parent
    print(len(stack))
    while len(stack) != 0:
        print(MOVENAMES[stack.pop()])

def aStarSearch():

    global MOVES, frontier, exploredStates, numberOfDifferentStates, numberOfStates
    start = time.time()
    while not frontier.empty():
        node = frontier.get()[1]
        if node.isInitial == False:
            exploredStates.add(node)
        for i in range(len(MOVES)):
            if node.snake.isValidMove(MOVES[i]):
                numberOfStates += 1
                newSnake, newSeeds = node.calNewState(MOVES[i])
                newState = State(newSeeds, newSnake, i, node, node.depth+1)
                if newState not in exploredStates:
                    numberOfDifferentStates += 1
                    if newState.isGoal():
                        print(time.time() - start)
                        print(numberOfStates)
                        print(numberOfDifferentStates)
                        printSolution(newState)
                        return True
                    frontier.put((newState.fScore(), newState))
    return False

size = input().split(',')
WIDTH = int(size[0])
HEIGHT = int(size[1])

intialSnakePosition = input().split(',')
initialSnake = Snake((int(intialSnakePosition[1]), int(intialSnakePosition[0])), (int(intialSnakePosition[0]), int(intialSnakePosition[1])))

numberOfSeeds = int(input())
for i in range(numberOfSeeds):
    seedInfo = input().split(',')
    seeds[(int(seedInfo[1]), int(seedInfo[0]))] = int(seedInfo[2])

initialState = State(seeds, initialSnake, initial= True)
frontier.put((0, initialState))


if aStarSearch() == False:
    print("No solution found!")