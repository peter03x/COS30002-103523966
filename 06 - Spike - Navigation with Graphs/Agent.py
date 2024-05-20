class Agent(object):
    def __init__(self, id, speedType="FAST", agentType="HUMAN"):
        
        self.id = id
        
        self.name = "{}_{}".format(speedType, agentType)
        
        self.speed = speedType
        
        self.type = agentType
        
        self.traversalCost = TRAVERSAL_COSTS[speedType]
        
        self.colors = AGENT_COLORS[self.name]
        
        self.startBox = None
        
        self.currentBox = None
        
        self.targetBox = None
        
# Define the traversal costs for different agent types and tile types
TRAVERSAL_COSTS = {
    "FAST": {
        "CLEAR": 1,
        "MUD": 2,
        "WATER": 5,
        "BRIDGE": 7,
        "SWAMP": 18,
        "WALL": float("inf")
    },
    "SLOW": {
        "CLEAR": 2,
        "MUD": 4,
        "WATER": 10,
        "BRIDGE": 14,
        "SWAMP": 36,
        "WALL": float("inf")
    },
    # Add more agent types and their respective traversal costs here
}

AGENT_COLORS = {
    "FAST_HUMAN": {
        "Start": "LIGHT_PURPLE",
        "Path": "PURPLE"
    },
    "SLOW_HUMAN": {
        "Start": "DARK_PURPLE",
        "Path": "PURPLE"
    },
    "FAST_MONSTER": {
        "Start": "LIGHT_ORANGE",
        "Path": "ORANGE"
    },
    "SLOW_MONSTER": {
        "Start": "DARK_ORANGE",
        "Path": "ORANGE"
    },
}