import logging
from .utils import Event
from .utils import EventQueue
from .building_blocks import Resource
from .building_blocks import Inventory
from .building_blocks import Creatable
from .building_blocks import ResourceFactory

class Game:

    # States
    STATE_LOADED = "loaded"
    STATE_PLAYING = "playing"
    STATE_GAME_OVER = "game over"

    # Events
    EVENT_TICK = "tick"
    EVENT_STATE = "state"

    def __init__(self, name : str):

        self.name = name
        self.events = EventQueue()
        self._state = Game.STATE_LOADED
        self._tick_count = 0
        self.inventory = None
        self.resources = None
        self.creations = None


    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, new_state):
        self._old_state = self.state
        self._state = new_state

        self.events.add_event(Event(self._state,
                                    "Game state change from {0} to {1}".format(self._old_state, self._state),
                                    Game.EVENT_STATE))

    def __str__(self):
        return self.name

    def start(self):
        self.state = Game.STATE_PLAYING

        self.inventory = Inventory()
        self.resources = ResourceFactory()
        self.resources.load()

        self.creations = []

    def add_creation(self, new_creation : Creatable):
        self.creations.append(new_creation)

    def tick(self):
        self._tick_count += 1

        self.events.add_event(Event(Game.EVENT_TICK,
                                    "Game ticked to {0}".format(self._tick_count),
                                    Game.EVENT_TICK))

        for creation in self.creations:
            creation.tick()

    def do_game_over(self):

        self.state = Game.STATE_GAME_OVER

    def get_next_event(self):

        next_event = None
        if self.events.size() > 0:
            next_event = self.events.pop_event()

        return next_event