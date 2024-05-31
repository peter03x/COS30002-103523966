class TacticalMove(object):
    planet_value_compare = []
    i = 0;

    def __init__(self):
        self.mode = "defensive"  # Start in defensive mode

    def update(self, gameinfo):
        self.get_planet_value(gameinfo)
        self.detect_events(gameinfo)
        self.execute_strategy(gameinfo)

    def get_planet_value(self, gameinfo):
        for my_planet in gameinfo.my_planets.values():
            self.planet_value_compare.append(my_planet.num_ships)

    def detect_events(self, gameinfo):


        for planet in gameinfo.my_planets.values():
            if (planet.num_ships < self.planet_value_compare[self.i]):
                if planet.num_ships < 20:
                    self.mode = "defensive"
                else:
                    self.mode = "aggressive"
            else:
                self.mode = "aggressive"
            self.i = self.i +1

    def execute_strategy(self, gameinfo):
        if self.mode == "defensive":
            self.defend_planets(gameinfo)
        elif self.mode == "aggressive":
            self.attack_weakest_target(gameinfo)

    def defend_planets(self, gameinfo):
        # Defensive strategy implementation
        #send ships to self.defend_planet
        # Only send one fleet at a time
        if gameinfo.my_fleets:
            return

        # Find the source planet with the maximum number of ships
        src = None
        max_ships = 0  # Initialize with lowest possible value: 0
        for planet in gameinfo.my_planets.values():
            if planet.num_ships > max_ships:
                src = planet
                max_ships = planet.num_ships

            # Find the target planet with the minimum number of ships
            dest = None
            min_ships = float('inf')  # Initialize with a massive value: + infinity
            for planet in gameinfo.my_planets.values():
                if planet.num_ships < min_ships:
                    dest = planet
                    min_ships = planet.num_ships
        # Launch a new fleet if there are enough ships
        if src is not None and src.num_ships > 10:
            gameinfo.planet_order(src, dest, int(src.num_ships * 0.55))

    def attack_weakest_target(self, gameinfo):
        # Aggressive strategy implementation

        # Only send one fleet at a time
        if gameinfo.my_fleets:
            return

        # Check if we should attack
        if gameinfo.my_planets and gameinfo.not_my_planets:
            # Find the source planet with the maximum number of ships
            src = None
            max_ships = 0  # Initialize with lowest possible value: 0
            for planet in gameinfo.my_planets.values():
                if planet.num_ships > max_ships:
                    src = planet
                    max_ships = planet.num_ships

            # Find the target planet with the minimum number of ships
            dest = None
            min_ships = float('inf')  # Initialize with a massive value: + infinity
            for planet in gameinfo.not_my_planets.values():
                if planet.num_ships < min_ships:
                    dest = planet
                    min_ships = planet.num_ships

            # Launch a new fleet if there are enough ships
            if src is not None and src.num_ships > 10:
                gameinfo.planet_order(src, dest, int(src.num_ships * 0.75))