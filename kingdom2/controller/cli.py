import cmd
from .utils import *
import logging
import os
import random

import kingdom2.model as model
import kingdom2.view as view

class GameCLI(cmd.Cmd):

    intro = "Welcome to The Kingdom 2.\nType 'start' to get going!\nType 'help' for a list of commands."
    prompt = "What next?"

    def __init__(self):

        super(GameCLI, self).__init__()

        self.model = model.Game("Kingdom 2")
        self.view = view.TextView(self.model)

    def run(self):
        self.cmdloop()

    def emptyline(self):
        pass

    def do_quit(self, arg):
        """Quit the game"""
        try:

            if confirm("Are you sure you want to quit?") is True:
                print("\nThanks for playing.")

                self.model.do_game_over()
                self.print_events()

                print(str(self.model))
                print("\nBye bye.")

        except Exception as err:
            print(str(err))

    def do_start(self, arg):

        self.model.start()
        self.print_events()

    def do_tick(self, arg : str = "1"):

        i = is_numeric(arg)
        if i is not None:
            for i in range (0, i):
                self.model.tick()
                self.view.tick()

        self.print_events()

    def do_print(self, arg):
        self.view.draw()

    def do_inv(self, arg):
        inv_view = view.InventoryTextView(self.model.inventory)
        inv_view.draw()

    def do_map(self, arg):
        map_view = view.WorldMapTextView(self.model.map)
        map_view.draw()

    def do_test(self, arg):

        resource_types = model.ResourceFactory.get_resource_types()

        for type in resource_types:
            new_resource = model.ResourceFactory.get_resource(type)
            self.model.inventory.add_resource(new_resource, random.randint(20,60))

        self.model.inventory.print()

        for creatable_name in self.model.creatables.names:
            creatable = self.model.creatables.get_creatable_copy(creatable_name)
            ok = self.model.inventory.is_creatable(creatable)
            print("{0}: creatable = {1}".format(creatable.name, ok))
            self.model.add_creation(creatable)

    def print_events(self):

        # Print any events that got raised
        event = self.model.get_next_event()
        if event is not None:
            print("Game event(s)...")

        while event is not None:

            print(" * " + str(event))

            event = self.model.get_next_event()