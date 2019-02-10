import logging
from .utils import Event
from .utils import EventQueue
import csv
import copy
import random


class Resource:

    CATEGORY_DEFAULT = "default"

    def __init__(self, name : str, description : str, category : str = CATEGORY_DEFAULT):
        self.name = name
        self.description = description
        self.category = category

    def __str__(self):
        _str = "{0}: {1} ({2})".format(self.name, self.description, self.category)
        return _str

class Creatable():

    def __init__(self, name : str, description : str, ticks_required : int = 10):
        self.name = name
        self.description = description
        self.pre_requisites = {}
        self.ticks_done = 0
        self.ticks_required = ticks_required
        self.output = {}

    def __str__(self):

        _str = "{0} ({1}) {2}% complete".format(self.name, self.description, self.percent_complete)

        if len(self.pre_requisites.keys()) > 0:
            for k,v in self.pre_requisites.items():
                _str += "\n\t{0} ({1}) : {2}".format(k.name, k.description, v)

        return _str

    @property
    def is_complete(self):
        return self.ticks_done >= self.ticks_required

    @property
    def percent_complete(self):
        return int(min(100, self.ticks_done * 100 / self.ticks_required))

    def add_pre_requisite(self, new_resource : Resource, item_count : int = 1):

        if new_resource not in self.pre_requisites.keys():
            self.pre_requisites[new_resource] = 0

        self.pre_requisites[new_resource] += item_count

    def add_output(self, new_resource : Resource, item_count : int = 1):

        if new_resource not in self.output.keys():
            self.output[new_resource] = 0

        self.output[new_resource] += item_count

    def tick(self):
        if self.is_complete is False:
            self.ticks_done += 1
            if self.is_complete is True:
                self.do_complete()

    def do_complete(self):
        print("Construction complete for {0}!".format(self.name))

class Inventory():

    def __init__(self):

        self.resources = {}

    @property
    def resource_type_count(self):
        return len(self.resources.keys())

    def add_resource(self, new_resource : Resource, item_count : int = 1):

        if new_resource not in self.resources.keys():
            self.resources[new_resource] = 0

        self.resources[new_resource] += item_count

    def is_creatable(self, new_creatable : Creatable):

        is_creatable = True

        for pre_req, count in new_creatable.pre_requisites.items():
            inv_count = self.resources[pre_req]
            if count > inv_count:
                is_creatable = False
                break

        return is_creatable

    def print(self):
        if len(self.resources.keys()) > 0:
            _str = "Inventory ({0} resource types)".format(self.resource_type_count)
            for k, v in self.resources.items():
                _str += "\n\t{0} ({1}) : {2}".format(k.name, k.description, v)
        else:
            _str = "No resources in your inventory!"

        print(_str)


class ResourceFactory:

    resources = {}

    def __init__(self):
        pass

    @staticmethod
    def get_resource(name : str):
        resource = None

        if name in ResourceFactory.resources.keys():
            resource = ResourceFactory.resources[name]

        return resource

    @staticmethod
    def get_resource_copy(self, name : str):
        resource = None

        if name in self.resources.keys():
            resource = copy.deepcopy(ResourceFactory.resources[name])

        return resource

    @staticmethod
    def get_resource_types():

        return list(ResourceFactory.resources.keys())


    def load(self):

        print("\nLoading resources...")

        # Attempt to open the file
        with open(".\\model\\data\\resources.csv", 'r') as object_file:

            # Load all rows in as a dictionary
            reader = csv.DictReader(object_file)

            # For each row in the file....
            for row in reader:
                name = row.get("Name")
                description = row.get("Description")
                category = row.get("Category")
                new_resource = Resource(name, description, category)
                ResourceFactory.resources[new_resource.name] = new_resource

                print(str(new_resource))

            # Close the file
            object_file.close()

        print("\n{0} resources loaded.".format(len(self.resources.keys())))

class CreatableFactory():

    def __init__(self):
        self.creatables = {}

    def load(self):
        resource_types = ResourceFactory.get_resource_types()
        creatables = ("house", "field", "pie")
        for creatable in creatables:
            new_creatable = Creatable(creatable, creatable)
            for resource_type in resource_types:
                new_resource = ResourceFactory.get_resource(resource_type)
                new_creatable.add_pre_requisite(new_resource, random.randint(1,3))
                self.creatables[creatable] =  new_creatable

            print(str(new_creatable))
