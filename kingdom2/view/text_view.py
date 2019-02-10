import kingdom2.model as model
import logging

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

    def __init__(self, model : model.Game):

        super(TextView, self).__init__()

        self.model = model

    def draw(self):
        print("Text View of {0}".format(self.model))

        inv_view = InventoryTextView(self.model.inventory)
        inv_view.draw()

        creations_view = CreationsTextView(self.model.creations)
        creations_view.draw()


class InventoryTextView(View):

    def __init__(self, model : model.Inventory):

        super(InventoryTextView, self).__init__()

        self.model = model

    def draw(self):
        if self.model is not None:
            self.model.print()
        else:
            print("No inventory to print!")


class CreationsTextView(View):

    def __init__(self, model : list):

        super(CreationsTextView, self).__init__()

        self.model = model

    def draw(self):
        if self.model is not None:
            print("{0} creations:".format(len(self.model)))
            for creation in self.model:
                print(str(creation))

        else:
            print("No creations to print!")
