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
        try:
            percent_complete = int(min(100, self.ticks_done * 100 / self.ticks_required))
        except Exception as err:
            print("{0}/{1}".format(self.ticks_done,self.ticks_required))
            print(str(err))
            percent_complete = 0

        return percent_complete

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

    # From a specified node get the data value
    def xml_get_node_text(node, tag_name: str):

        tag = node.getElementsByTagName(tag_name)

        # If the tag exists then get the data value
        if len(tag) > 0:
            value = tag[0].firstChild.data
        # Else use None
        else:
            value = None

        return value

    def xml_get_node_value(self, tag_name : str):

        value = self.xml_get_node_text(tag_name)

        return is_numeric(value)


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
            pre_requisites = creatable.getElementsByTagName("pre_requisites")

            # For each pre-requisite resource...
            for resource in pre_requisites:

                # Get the basic details of the resource
                name = self.xml_get_node_text(resource, "name")
                count = self.xml_get_node_value(resource, "count")

                new_resource = ResourceFactory.get_resource_copy(name)
                new_creatable.add_pre_requisite(new_resource, count)


            logging.info("{0}.load(): Creatable '{1}' loaded".format(__class__, new_creatable.name))

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

