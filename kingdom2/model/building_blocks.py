import logging
from .utils import Event
from .utils import EventQueue
from .utils import is_numeric
import csv
import copy
import random
from xml.dom.minidom import *


class Resource:

    CATEGORY_DEFAULT = "default"

    def __init__(self, name : str, description : str, category : str = CATEGORY_DEFAULT, graphic : str = None):
        self.name = name
        self.description = description
        self.category = category
        self.graphic = graphic

    def __str__(self):
        _str = "{0} ({3}): {1} ({2})".format(self.name, self.description, self.category, self.graphic)
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
            _str += "\n\tPre-requisites:"
            for k,v in self.pre_requisites.items():
                _str += "\n\t\t- {0}:{1}".format(k, v)

        if len(self.output.keys()) > 0:
            _str += "\n\tOutputs:"
            for k,v in self.output.items():
                _str += "\n\t\t- {0}:{1}".format(k, v)

        return _str

    @property
    def is_complete(self):
        return self.ticks_done >= self.ticks_required

    @property
    def percent_complete(self):
        try:
            percent_complete = int(min(100, self.ticks_done * 100 / self.ticks_required))
        except Exception as err:
            print("{0}/{1}".format(self.ticks_done,self.ticks_required))
            print(str(err))
            percent_complete = 0

        return percent_complete

    def add_pre_requisite(self, new_resource_name : str, item_count : int = 1):

        if new_resource_name not in self.pre_requisites.keys():
            self.pre_requisites[new_resource_name] = 0

        self.pre_requisites[new_resource_name] += item_count

    def add_output(self, new_resource_name : str, item_count : int = 1):

        if new_resource_name not in self.output.keys():
            self.output[new_resource_name] = 0

        self.output[new_resource_name] += item_count

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

        for pre_req_name, count in new_creatable.pre_requisites.items():
            pre_req = ResourceFactory.get_resource(pre_req_name)
            if pre_req not in self.resources.keys():
                is_creatable = False
                break
            else:
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
    def get_resource_copy(name : str):
        resource = None

        if name in ResourceFactory.resources.keys():
            resource = copy.deepcopy(ResourceFactory.resources[name])

        return resource

    @staticmethod
    def get_resource_types():

        return list(ResourceFactory.resources.keys())


    def load(self):

        print("\nLoading resources...")

        # Attempt to open the file
        with open(".\\kingdom2\\model\\data\\resources.csv", 'r') as object_file:

            # Load all rows in as a dictionary
            reader = csv.DictReader(object_file)

            # For each row in the file....
            for row in reader:
                name = row.get("Name")
                description = row.get("Description")
                category = row.get("Category")
                graphic = row.get("Graphic")
                if graphic == "":
                    graphic = None

                new_resource = Resource(name, description, category, graphic)
                ResourceFactory.resources[new_resource.name] = new_resource

                print(str(new_resource))

            # Close the file
            object_file.close()

        print("\n{0} resources loaded.".format(len(self.resources.keys())))


class CreatableFactoryXML(object):
    '''
    Load some creatables from an XML file and store them in a dictionary
    '''

    def __init__(self, file_name : str):

        self.file_name = file_name
        self._dom = None
        self._creatables = {}

    @property
    def count(self):
        return len(self._creatables)

    @property
    def names(self):
        return list(self._creatables.keys())

    # Load in the quest contained in the quest file
    def load(self):

        self._dom = parse(self.file_name)

        assert self._dom.documentElement.tagName == "creatables"

        logging.info("%s.load(): Loading in %s", __class__, self.file_name)

        # Get a list of all quests
        creatables = self._dom.getElementsByTagName("creatable")

        # for each quest...
        for creatable in creatables:

            # Get the main tags that describe the quest
            name = self.xml_get_node_text(creatable, "name")
            desc = self.xml_get_node_text(creatable, "description")
            ticks_required = self.xml_get_node_value(creatable, "ticks_required")

            # ...and create a basic creatable object
            new_creatable = Creatable(name=name, description=desc, ticks_required=ticks_required)

            logging.info("%s.load(): Loading Creatable '%s'...", __class__, new_creatable.name)

            # Next get a list of all of the pre-requisites
            pre_requisites = creatable.getElementsByTagName("pre_requisites")[0]
            resources = pre_requisites.getElementsByTagName("resource")

            # For each pre-requisite resource...
            for resource in resources:

                # Get the basic details of the resource
                name = self.xml_get_node_text(resource, "name")
                count = self.xml_get_node_value(resource, "count")

                new_creatable.add_pre_requisite(name, count)

                logging.info("{0}.load(): adding pre-req {1} ({2})".format(__class__, name, count))

            # Next get a list of all of the outputs
            pre_requisites = creatable.getElementsByTagName("outputs")[0]
            resources = pre_requisites.getElementsByTagName("resource")

            # For each output resource...
            for resource in resources:

                # Get the basic details of the resource
                name = self.xml_get_node_text(resource, "name")
                count = self.xml_get_node_value(resource, "count")
                action = self.xml_get_node_text(resource, "action")
                if action is not None:
                    action = "replace"
                else:
                    action = "inventory"

                new_creatable.add_output(name, count)

                logging.info("{0}.load(): adding output {1} ({2})".format(__class__, name, count))

            logging.info("{0}.load(): Creatable '{1}' loaded".format(__class__, new_creatable.name))
            print(str(new_creatable))


            # Add the new creatable to the dictionary
            self._creatables[new_creatable.name] = new_creatable

        self._dom.unlink()

    # From a specified node get the data value
    def xml_get_node_text(self, node, tag_name: str):

        tag = node.getElementsByTagName(tag_name)

        # If the tag exists then get the data value
        if len(tag) > 0:
            value = tag[0].firstChild.data
        # Else use None
        else:
            value = None

        return value

    def xml_get_node_value(self, node, tag_name: str):

        value = self.xml_get_node_text(node, tag_name)

        return is_numeric(value)

    def print(self):
        for creatable in self._creatables.values():
            print(creatable)


    def get_creatable(self, name : str):

        return self._creatables[name]

    def get_creatable_copy(self, name : str):
        return copy.deepcopy(self._creatables[name])


class WorldMap:

    TILE_GRASS = "Grass"

    def __init__(self, name : str, width : int = 50, height : int = 50):
        self.name = name
        self._width = width
        self._height = height
        self.map = []

    def initialise(self):
        # Clear the map squares
        self.map = [[None for y in range(0, self._height)] for x in range(0, self._width)]

        grass = ResourceFactory.get_resource_copy(WorldMap.TILE_GRASS)
        self.add_objects(grass.graphic, 40)

    @property
    def width(self):
        return len(self.map)

    @property
    def height(self):
        return len(self.map[0])

    # Are the specified coordinates within the area of the map?
    def is_valid_xy(self, x: int, y: int):

        result = False

        if x >= 0 and x < self.width and y >= 0 and y < self.height:
            result = True

        return result

    # Get a map square at the specified co-ordinates
    def get(self, x: int, y: int):

        if self.is_valid_xy(x, y) is False:
            raise Exception("Trying to get tile at ({0},{1}) which is outside of the world!".format(x, y))

        return self.map[x][y]

    # Set a map square at the specified co-ordinates with the specified object
    def set(self, x: int, y: int, c):

        if self.is_valid_xy(x, y) is False:
            raise Exception("Trying to set tile at ({0},{1}) which is outside of the world!".format(x, y))

        self.map[x][y] = c

    # Add objects to random tiles
    def add_objects(self, object_type, count: int = 20):

        for i in range(0, count):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            if self.get(x, y) is None:
                self.set(x, y, object_type)