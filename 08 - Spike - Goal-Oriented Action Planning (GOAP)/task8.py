class Graph:

    def __init__(self):
        self.goals = {
            'keep fit': 5,
            'eat': 3,
            'study': 2
        }

        self.actions = {
            'eat fast food': {'eat': -2, 'keep fit': +3, 'study': +1},
            'work in mine': {'eat': 6, 'keep fit': +2, 'study': -3},
            'eat healthy food': {'eat': -4, 'keep fit': -3, 'study': +3},
            'doing homework': {'eat': -1, 'keep fit': -1, 'study': -1}
        }


class Node:

    def __init__(self, state=None, parentNode=None, previousActions=[]):
        self.state = state
        if state is None:
            graph = Graph()

            self.state = graph.goals

        self.parentNode = parentNode

        self.previousActions = previousActions

    def goalsAreReached(self):
        for value in self.state.values():
            if value != 0:
                return False

        return True

    def getChild(self, action):

        graph = Graph()
        newState = {}

        if action in graph.actions.keys():

            for goalName in graph.goals.keys():
                newState[goalName] = max(0, self.state[goalName] + graph.actions[action][goalName])

            return Node(state=newState, parentNode=self, previousActions=self.previousActions + [action])

        return None

    def printNode(self):
        print("\n=====================================================================")
        print("The remaining values to reach each goal are:")
        for key in self.state.keys():
            print("    - Goal {}: {}".format(key, self.state[key]))

        print("Actions taken to reach this state: {}".format(self.previousActions))


def searchBFS(initialNode):
    frontier = [initialNode]

    visitedStates = []

    while frontier:

        currentNode = frontier.pop(0)

        currentNode.printNode()

        visitedStates.append(currentNode.state)

        if currentNode.goalsAreReached():
            print("\n=====================================================================")
            print("ALL GOALS REACHED!")

            return

        graph = Graph()

        for action in graph.actions.keys():

            childNode = currentNode.getChild(action=action)

            if childNode.state not in visitedStates:
                frontier.append(childNode)

    raise ValueError("Can't finf any solution!")


if __name__ == '__main__':
    # Initialize the first node
    graph = Graph()

    initialNode = Node()

    searchBFS(initialNode=initialNode)