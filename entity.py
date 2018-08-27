# -*- coding: utf-8 -*-
"""Entity definition."""



class Entity(object):
    """Entity is only an eid, tag and component carrier."""
    def __init__(self, eid, tag=2):
        super(Entity, self).__init__()
        self.eid = eid
        self.tag = tag
        self._components = {}

    def add_component(self, component):
        self._components[component.__class__.__name__] = component
        return component

    def get_component(self, component_class):
        return self._components.get(component_class.__name__)

    def remove_component(self, component_class):
        self._components.pop(component_class.__name__, None)

    def iter_components(self):
        return self._components.itervalues()
