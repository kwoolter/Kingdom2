import logging
import sys

import colorama

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
    COLOURS_EMPTY_TILE = colorama.Fore.GREEN + colorama.Back.GREEN
    COLOURS_NON_EMPTY_TILE = colorama.Fore.BLACK + colorama.Back.GREEN

    def __init__(self, model: model.WorldMap):

        self.model = model

        if sys.stdout.isatty() is False:
            colorama.init(convert=False, strip=False)
        else:
            colorama.init(convert=True)

    def draw(self, rect: list = None):

        if rect is not None:
            ox, oy, width, height = rect
        else:
            ox = 0
            oy = 0
            width = self.model.width
            height = self.model.height

        print(WorldMapTextView.COLOURS_TITLE, end="")
        print("+" + "-" * width + "+" + WorldMapTextView.COLOURS_DEFAULT)
        title = "{0:^" + str(width) + "}"
        print(WorldMapTextView.COLOURS_TITLE, end="")
        print("|" + title.format(self.model.name) + "|" + WorldMapTextView.COLOURS_DEFAULT)
        print(WorldMapTextView.COLOURS_TITLE, end="")
        print("+" + "-" * width + "+" + WorldMapTextView.COLOURS_DEFAULT)

        for y in range(oy, oy + height):
            print(WorldMapTextView.COLOURS_TITLE + "|" + WorldMapTextView.COLOURS_DEFAULT, end="")
            row = ""
            for x in range(ox, ox + width):
                c = self.model.get(x, y)
                if c is not None:
                    row += WorldMapTextView.COLOURS_NON_EMPTY_TILE + c + WorldMapTextView.COLOURS_DEFAULT
                else:
                    row += WorldMapTextView.COLOURS_EMPTY_TILE + " " + WorldMapTextView.COLOURS_DEFAULT

            print(row + WorldMapTextView.COLOURS_TITLE + "|" + WorldMapTextView.COLOURS_DEFAULT)

        print(WorldMapTextView.COLOURS_TITLE, end="")
        print("+" + "-" * width + "+" + WorldMapTextView.COLOURS_DEFAULT)


class WorldTopoModelTextView(View):

    def __init__(self, model: model.WorldMap):

        self.model = model

    def draw(self, rect: list = None):

        if rect is not None:
            ox, oy, width, height = rect
        else:
            ox = 0
            oy = 0
            width = self.model.width
            height = self.model.height

        for x in range(0, width):
            print(",{0}".format(x), end="")
        print("")

        for y in range(0, height):
            row = "{0},".format(y)
            for x in range(0, width):
                a = self.model.topo_model_pass2[x][y]
                row += "{0:.4},".format(a)

            print(row)
