from lxml import etree

import grok

from persistent import Persistent

from zope.interface import Interface, alsoProvides
import zope.datetime
from zope.location import Location

from zope.component import getMultiAdapter

from zope.schema import getFieldsInOrder
from zope.schema.interfaces import IText, IInt, IObject, IList, IChoice, ISet
from zope.schema.interfaces import IDatetime

from zope.publisher.interfaces.browser import IBrowserRequest

def serialize_to_tree(container, schema, instance, request):
    for name, field in getFieldsInOrder(schema):
        value = field.get(instance)
        getMultiAdapter(
            (field, request), IXMLGenerator).output(container, value)
    return container

def serialize(
        container_name, schema, instance, request,
        encoding='UTF-8', pretty_print=True):
    container = etree.Element(container_name)
    container = serialize_to_tree(container, schema, instance, request)
    return etree.tostring(
        container, encoding=encoding, pretty_print=pretty_print)

def deserialize_from_tree(container, schema, instance, request):
    for element in container:
        field = schema[element.tag]
        value = getMultiAdapter(
            (field, request), IXMLGenerator).input(element)
        field.set(instance, value)

    alsoProvides(instance, schema)

def deserialize(xml, schema, instance, request):
    container = etree.XML(xml)
    deserialize_from_tree(container, schema, instance, request)

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

class XMLGeneratorBase(grok.MultiAdapter):
    grok.baseclass()
    grok.implements(IXMLGenerator)

    def __init__(self, field, request):
        self.field = field
        self.request = request

class Text(XMLGeneratorBase):
    grok.adapts(IText, IBrowserRequest)

    def output(self, container, value):
        element = etree.SubElement(container, self.field.__name__)
        element.text = value

    def input(self, element):
        if element.text is not None:
            return unicode(element.text)
        return None

class Int(XMLGeneratorBase):
    grok.adapts(IInt, IBrowserRequest)

    def output(self, container, value):
        element = etree.SubElement(container, self.field.__name__)
        if value is not None:
            element.text = str(value)

    def input(self, element):
        if element.text is not None and element.text != '':
            return int(element.text)
        return None

class Object(XMLGeneratorBase):
    grok.adapts(IObject, IBrowserRequest)

    def output(self, container, value):
        container = etree.SubElement(container, self.field.__name__)

        for name, field in getFieldsInOrder(self.field.schema):
            adapter = getMultiAdapter((field, self.request), IXMLGenerator)
            adapter.output(container, field.get(value))

    def input(self, element):
        instance = GeneratedObject()
        deserialize_from_tree(
            element, self.field.schema, instance, self.request)
        return instance

class List(XMLGeneratorBase):
    grok.adapts(IList, IBrowserRequest)

    def output(self, container, value):
        container = etree.SubElement(container, self.field.__name__)
        field = self.field.value_type
        for v in value:
            adapter = getMultiAdapter((field, self.request), IXMLGenerator)
            adapter.output(container, v)

    def input(self, element):
        field = self.field.value_type
        return [
            getMultiAdapter(
                (field, self.request), IXMLGenerator).input(sub_element)
            for sub_element in element]

class Datetime(XMLGeneratorBase):
    grok.adapts(IDatetime, IBrowserRequest)

    def output(self, container, value):
        element = etree.SubElement(container, self.field.__name__)
        if value is not None:
            element.text = value.isoformat()

    def input(self, element):
        if element.text is not None:
            return zope.datetime.parseDatetimetz(element.text)
        return None

class Choice(XMLGeneratorBase):
    grok.adapts(IChoice, IBrowserRequest)

    def output(self, container, value):
        element = etree.SubElement(container, self.field.__name__)
        element.text = value

    def input(self, element):
        value = element.text
        if value is not None:
            self.field.validate(value) # raises an error if not valid.
            return value
        return None

class Set(XMLGeneratorBase):
    grok.adapts(ISet, IBrowserRequest)

    def output(self, container, value):
        container = etree.SubElement(container, self.field.__name__)
        field = self.field.value_type
        for v in value:
            adapter = getMultiAdapter((field, self.request), IXMLGenerator)
            adapter.output(container, v)

    def input(self, element):
        field = self.field.value_type
        return set([
            getMultiAdapter(
                (field, self.request), IXMLGenerator).input(sub_element)
            for sub_element in element])
