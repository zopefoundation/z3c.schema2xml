from lxml import etree

import grokcore.component as grok

from persistent import Persistent

from zope.interface import Interface, alsoProvides
import zope.datetime
from zope.location import Location
from zope.schema import getFieldsInOrder
from zope.schema.interfaces import IText, IInt, IObject, IList, IChoice, ISet
from zope.schema.interfaces import IDatetime

def serialize_to_tree(container, schema, instance):
    for name, field in getFieldsInOrder(schema):
        value = field.get(instance)
        IXMLGenerator(field).output(container, value)
    return container

def serialize(
        container_name, schema, instance, encoding='UTF-8', pretty_print=True):
    container = etree.Element(container_name)
    container = serialize_to_tree(container, schema, instance)
    return etree.tostring(
        container, encoding=encoding, pretty_print=pretty_print)

def deserialize_from_tree(container, schema, instance):
    for element in container:
        field = schema[element.tag]
        value = IXMLGenerator(field).input(element)
        field.set(instance, value)

    alsoProvides(instance, schema)

def deserialize(xml, schema, instance):
    container = etree.XML(xml)
    deserialize_from_tree(container, schema, instance)

class GeneratedObject(Location, Persistent):
    def __init__(self):
        pass

class IXMLGenerator(Interface):

    def output(container, value):
        """Output value as XML element according to field.
        """

    def input(element):
        """Input XML element according to field and return value.
        """

class Text(grok.Adapter):
    grok.context(IText)
    grok.implements(IXMLGenerator)

    def output(self, container, value):
        element = etree.SubElement(container, self.context.__name__)
        element.text = value

    def input(self, element):
        if element.text is not None:
            return unicode(element.text)
        return None

class Int(grok.Adapter):
    grok.context(IInt)
    grok.implements(IXMLGenerator)

    def output(self, container, value):
        element = etree.SubElement(container, self.context.__name__)
        if value is not None:
            element.text = str(value)

    def input(self, element):
        if element.text is not None and element.text != '':
            return int(element.text)
        return None

class Object(grok.Adapter):
    grok.context(IObject)
    grok.implements(IXMLGenerator)

    def output(self, container, value):
        container = etree.SubElement(container, self.context.__name__)

        for name, field in getFieldsInOrder(self.context.schema):
            IXMLGenerator(field).output(container, field.get(value))

    def input(self, element):
        instance = GeneratedObject()
        deserialize_from_tree(element, self.context.schema, instance)
        return instance

class List(grok.Adapter):
    grok.context(IList)
    grok.implements(IXMLGenerator)

    def output(self, container, value):
        container = etree.SubElement(container, self.context.__name__)
        field = self.context.value_type
        for v in value:
            IXMLGenerator(field).output(container, v)

    def input(self, element):
        field = self.context.value_type
        return [
            IXMLGenerator(field).input(sub_element)
            for sub_element in element]

class Datetime(grok.Adapter):
    grok.context(IDatetime)
    grok.implements(IXMLGenerator)

    def output(self, container, value):
        element = etree.SubElement(container, self.context.__name__)
        if value is not None:
            element.text = value.isoformat()

    def input(self, element):
        if element.text is not None:
            return zope.datetime.parseDatetimetz(element.text)
        return None

class Choice(grok.Adapter):
    grok.context(IChoice)
    grok.implements(IXMLGenerator)
    
    def output(self, container, value):
        element = etree.SubElement(container, self.context.__name__)
        element.text = value

    def input(self, element):
        if element.text is not None:
            return element.text
        return None

class Set(grok.Adapter):
    grok.context(ISet)
    grok.implements(IXMLGenerator)

    def output(self, container, value):
        container = etree.SubElement(container, self.context.__name__)
        field = self.context.value_type
        for v in value:
            IXMLGenerator(field).output(container, v)

    def input(self, element):
        field = self.context.value_type
        return set([
            IXMLGenerator(field).input(sub_element)
            for sub_element in element])
