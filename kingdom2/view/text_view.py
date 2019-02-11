import logging
import colorama
import sys

import kingdom2.model as model


class View():

    def __init__(self):
        self.tick_count = 0

    def initialise(self):
        pass

    def tick(self):
        self.tick_count += 1

    def process_event(self, new_event: model.Event):
        logging.info("Default View Class event process:{0}".format(new_event))

    def draw(self):
        pass


class TextView(View):

    def __init__(self, model: model.Game):
        super(TextView, self).__init__()

        self.model = model

    def draw(self):
        print("Text View of {0}".format(self.model))

        inv_view = InventoryTextView(self.model.inventory)
        inv_view.draw()

        creations_view = CreationsTextView(self.model.creations)
        creations_view.draw()


class InventoryTextView(View):

    def __init__(self, model: model.Inventory):

        super(InventoryTextView, self).__init__()

        self.model = model

    def draw(self):
        if self.model is not None:
            self.model.print()
        else:
            print("No inventory to print!")


class CreationsTextView(View):

    def __init__(self, model: list):

        super(CreationsTextView, self).__init__()

        self.model = model

    def draw(self):
        if self.model is not None:
            print("{0} creations:".format(len(self.model)))
            for creation in self.model:
                print(str(creation))

        else:
            print("No creations to print!")


class WorldMapTextView(View):

    COLOURS_DEFAULT = colorama.Fore.RESET + colorama.Back.RESET
    COLOURS_TITLE = colorama.Fore.BLACK + colorama.Back.YELLOW


    def __init__(self, model: model.WorldMap):
        self.model = model

        if sys.stdout.isatty() is False:
            colorama.init(convert=False, strip=False)
        else:
            colorama.init(convert=True)

    def draw(self):

        print(WorldMapTextView.COLOURS_TITLE, end="")
        print("+" + "-" * (self.model.width) + "+" + WorldMapTextView.COLOURS_DEFAULT)
        title = "{0:^" + str(self.model.width) + "}"
        print(WorldMapTextView.COLOURS_TITLE, end="")
        print("|" + title.format(self.model.name) + "|" + WorldMapTextView.COLOURS_DEFAULT)
        print(WorldMapTextView.COLOURS_TITLE, end="")
        print("+" + "-" * (self.model.width) + "+"  + WorldMapTextView.COLOURS_DEFAULT)

        for y in range(0, self.model.height):
            print(WorldMapTextView.COLOURS_TITLE + "|" + WorldMapTextView.COLOURS_DEFAULT, end="")
            row = ""
            for x in range(0, self.model.width):
                c = self.model.get(x, y)
                if c is not None:
                    row += c
                else:
                    row += " "
            print(row + WorldMapTextView.COLOURS_TITLE + "|" + WorldMapTextView.COLOURS_DEFAULT)

        print(WorldMapTextView.COLOURS_TITLE, end="")
        print("+" + "-" * (self.model.width) + "+" + WorldMapTextView.COLOURS_DEFAULT)
