Schema To XML
*************

Introduction
============

This package can convert objects described by Zope 3 schema to simple
XML structures. It's also able to convert this XML back into objects.
The export and import processes are completely schema-driven; any
attribute not described in the schema is not seen by this system at
all.

This system can be used to create export and import systems for Zope 3
applications. It could also be used to provide XML representations of
objects for other purposes, such as XSLT transformations, or even just
to get a full-text representation for index purposes.

The package relies on ``lxml`` for the serialization to XML. 

Serialization
=============

Let's first define a simple Zope 3 schema::

    >>> from zope import interface, schema
    >>> class IName(interface.Interface):
    ...     first_name = schema.TextLine(title=u'First name')
    ...     last_name = schema.TextLine(title=u'Last name')

Let's now make a class that implements this schema::

    >>> from zope.interface import implements
    >>> class Name(object):
    ...     implements(IName)
    ...     def __init__(self, first_name, last_name):
    ...         self.first_name = first_name
    ...         self.last_name = last_name

Let's make an instance of the class::

    >>> name = Name('Karel', 'Titulaer')

Now let's serialize it to XML:

    >>> from z3c.schema2xml import serialize
    >>> print serialize('container', IName, name)
    <container>
      <first_name>Karel</first_name>
      <last_name>Titulaer</last_name>
    </container>

This also works for other kinds of fields::

    >>> from zope import interface, schema
    >>> class IAddress(interface.Interface):
    ...     street_name = schema.TextLine(title=u'Street name')
    ...     number = schema.Int(title=u'House number')
    >>> class Address(object):
    ...     implements(IAddress)
    ...     def __init__(self, street_name, number):
    ...         self.street_name = street_name
    ...         self.number = number
    >>> address = Address('Hofplein', 42)
    >>> print serialize('container', IAddress, address)
    <container>
      <street_name>Hofplein</street_name>
      <number>42</number>
    </container>

If a field is not filled in, the serialization will result in an empty
element::

    >>> address2 = Address(None, None)
    >>> print serialize('container', IAddress, address2)
    <container>
      <street_name/>
      <number/>
    </container>

If a schema defines an Object field with its own schema, the serialization
can also handle this::

    >>> class IPerson(interface.Interface):
    ...     name = schema.Object(title=u"Name", schema=IName)
    ...     address = schema.Object(title=u"Address", schema=IAddress)

    >>> class Person(object):
    ...     implements(IPerson)
    ...     def __init__(self, name, address):
    ...         self.name = name
    ...         self.address = address

    >>> person = Person(name, address)
    >>> print serialize('person', IPerson, person)
    <person>
      <name>
        <first_name>Karel</first_name>
        <last_name>Titulaer</last_name>
      </name>
      <address>
        <street_name>Hofplein</street_name>
        <number>42</number>
      </address>
    </person>

A schema can also define a List field with elements with their own
schema. Let's make an object and serialize it::

    >>> class ICommission(interface.Interface):
    ...     members = schema.List(
    ...         title=u"Commission",
    ...         value_type=schema.Object(__name__='person',
    ...         schema=IPerson))

Note that we have to explicitly specify __name__ for the field that's
used for value_type here, otherwise we have no name to serialize to
XML with.

    >>> class Commission(object):
    ...     implements(ICommission)
    ...     def __init__(self, members):
    ...         self.members = members

    >>> commission = Commission(
    ...     [person, Person(Name('Chriet', 'Titulaer'), Address('Ruimteweg', 3))])
    >>> print serialize('commission', ICommission, commission)
    <commission>
      <members>
        <person>
          <name>
            <first_name>Karel</first_name>
            <last_name>Titulaer</last_name>
          </name>
          <address>
            <street_name>Hofplein</street_name>
            <number>42</number>
          </address>
        </person>
        <person>
          <name>
            <first_name>Chriet</first_name>
            <last_name>Titulaer</last_name>
          </name>
          <address>
            <street_name>Ruimteweg</street_name>
            <number>3</number>
          </address>
        </person>
      </members>
    </commission>

We get an adapter lookop failure whenever we try to serialize a field type for
which there's no an serializer::

    >>> class IWithNonSerializableField(interface.Interface):
    ...     field = schema.Field(title=u"Commission")
    >>> class NotSerializable(object):
    ...     implements(IWithNonSerializableField)
    ...     def __init__(self, value):
    ...         self.field = value
    >>> not_serializable = NotSerializable(None)
    >>> serialize('noway', IWithNonSerializableField, not_serializable)
    Traceback (most recent call last):
     ...
    TypeError: ('Could not adapt', <zope.schema._bootstrapfields.Field object at ...>, <InterfaceClass z3c.schema2xml._schema2xml.IXMLGenerator>)

Deserialization
===============

Now we want to deserialize XML according to a schema to an object that
provides this schema.

    >>> from z3c.schema2xml import deserialize
    >>> xml = '''
    ...  <container>
    ...    <first_name>Karel</first_name>
    ...    <last_name>Titulaer</last_name>
    ...  </container>
    ...  '''
    >>> name = Name('', '')
    >>> deserialize(xml, IName, name)
    >>> name.first_name
    u'Karel'
    >>> name.last_name
    u'Titulaer'

The order of the fields in XML does not matter::

    >>> xml = '''
    ...  <container>
    ...    <last_name>Titulaer</last_name>
    ...    <first_name>Karel</first_name>
    ...  </container>
    ...  '''
    >>> name = Name('', '')
    >>> deserialize(xml, IName, name)
    >>> name.first_name
    u'Karel'
    >>> name.last_name
    u'Titulaer'

After deserialization, the object alsoProvides the schema interface::

    >>> IName.providedBy(name)
    True

This also works for other kinds of fields::

    >>> xml = '''
    ...  <container>
    ...    <street_name>Hofplein</street_name>
    ...    <number>42</number>
    ...  </container>
    ...  '''
    >>> address = Address('', 0)
    >>> deserialize(xml, IAddress, address)
    >>> address.street_name
    u'Hofplein'
    >>> address.number
    42

If a schema defines an Object field with its own schema, the serialization
can also handle this::

    >>> xml = '''
    ...  <person>
    ...    <name>
    ...      <first_name>Karel</first_name>
    ...      <last_name>Titulaer</last_name>
    ...    </name>
    ...    <address>
    ...      <street_name>Hofplein</street_name>
    ...      <number>42</number>
    ...    </address>
    ...  </person>
    ...  '''
    >>> person = Person(Name('', ''), Address('', 0))
    >>> deserialize(xml, IPerson, person)
    >>> person.name.first_name
    u'Karel'
    >>> person.name.last_name
    u'Titulaer'
    >>> person.address.street_name
    u'Hofplein'
    >>> person.address.number
    42
    >>> IPerson.providedBy(person)
    True
    >>> IName.providedBy(person.name)
    True
    >>> IAddress.providedBy(person.address)
    True

Again the order in which the fields come in XML shouldn't matter::

    >>> xml = '''
    ...  <person>
    ...    <address>
    ...      <number>42</number>
    ...      <street_name>Hofplein</street_name>
    ...    </address>
    ...    <name>
    ...      <last_name>Titulaer</last_name>
    ...      <first_name>Karel</first_name>
    ...    </name>
    ...  </person>
    ...  '''
    >>> person = Person(Name('', ''), Address('', 0))
    >>> deserialize(xml, IPerson, person)
    >>> person.name.first_name
    u'Karel'
    >>> person.name.last_name
    u'Titulaer'
    >>> person.address.street_name
    u'Hofplein'
    >>> person.address.number
    42
    >>> IPerson.providedBy(person)
    True
    >>> IName.providedBy(person.name)
    True
    >>> IAddress.providedBy(person.address)
    True

    >>> xml = '''
    ... <commission>
    ...  <members>
    ...    <person>
    ...      <name>
    ...        <first_name>Karel</first_name>
    ...        <last_name>Titulaer</last_name>
    ...      </name>
    ...      <address>
    ...        <street_name>Hofplein</street_name>
    ...        <number>42</number>
    ...      </address>
    ...    </person>
    ...    <person>
    ...      <name>
    ...        <first_name>Chriet</first_name>
    ...        <last_name>Titulaer</last_name>
    ...     </name>
    ...      <address>
    ...        <street_name>Ruimteweg</street_name>
    ...        <number>3</number>
    ...      </address>
    ...    </person>
    ...  </members>
    ... </commission>
    ... '''

    >>> commission = Commission([])
    >>> deserialize(xml, ICommission, commission)
    >>> len(commission.members)
    2
    >>> member = commission.members[0]
    >>> member.name.first_name
    u'Karel'
    >>> member.address.street_name
    u'Hofplein'
    >>> member = commission.members[1]
    >>> member.name.first_name
    u'Chriet'
    >>> member.address.street_name
    u'Ruimteweg'

Whenever the XML element is empty, the resulting value should be None:

    >>> from z3c.schema2xml import deserialize
    >>> xml = '''
    ...  <container>
    ...    <first_name></first_name>
    ...    <last_name/>
    ...  </container>
    ...  '''
    >>> name = Name('', '')
    >>> deserialize(xml, IName, name)
    >>> name.first_name is None
    True
    >>> name.last_name is None
    True

For all kinds of fields, like strings and ints...::

    >>> xml = '''
    ...  <container>
    ...    <street_name/>
    ...    <number/>
    ...  </container>
    ...  '''
    >>> address = Address('', 0)
    >>> deserialize(xml, IAddress, address)
    >>> address.street_name is None
    True
    >>> address.number is None
    True

...and the fields of subobjects (but not the subobject themselves!)::

    >>> xml = '''
    ...  <person>
    ...    <name>
    ...      <first_name/>
    ...      <last_name/>
    ...    </name>
    ...    <address>
    ...      <street_name/>
    ...      <number/>
    ...    </address>
    ...  </person>
    ...  '''
    >>> person = Person(Name('', ''), Address('', 0))
    >>> deserialize(xml, IPerson, person)
    >>> person.name.first_name is None
    True
    >>> person.name.last_name is None
    True
    >>> IPerson.providedBy(person)
    True
    >>> IName.providedBy(person.name)
    True
    >>> person.address is None
    False
    >>> person.address.street_name is None
    True
    >>> person.address.number is None
    True
    >>> IAddress.providedBy(person.address)
    True

Similarly, where a sequence is expected the value should be an empty sequence:

    >>> xml = '''
    ... <commission>
    ...   <members/>
    ... </commission>
    ... '''
    >>> commission = Commission([])
    >>> deserialize(xml, ICommission, commission)
    >>> len(commission.members)
    0

TextLine, Int, Object and List have just been tested. Now follow tests
for the other field types that have a serializer.

Datetime
========

Datetime objects::

    >>> from datetime import datetime
    >>> class IWithDatetime(interface.Interface):
    ...     datetime = schema.Datetime(title=u'Date and time')
    >>> class WithDatetime(object):
    ...     implements(IWithDatetime)
    ...     def __init__(self, datetime):
    ...         self.datetime = datetime
    >>> with_datetime = WithDatetime(datetime(2006, 12, 31))
    >>> xml = serialize('container', IWithDatetime, with_datetime)
    >>> print xml
    <container>
      <datetime>2006-12-31T00:00:00</datetime>
    </container>
    >>> new_datetime = WithDatetime(None)
    >>> deserialize(xml, IWithDatetime, new_datetime)
    >>> new_datetime.datetime.year
    2006
    >>> new_datetime.datetime.month
    12
    >>> new_datetime.datetime.day
    31

Let's try it with the field not filled in::

    >>> with_datetime = WithDatetime(None)
    >>> xml = serialize('container', IWithDatetime, with_datetime)
    >>> print xml
    <container>
      <datetime/>
    </container>
    >>> new_datetime= WithDatetime(None)
    >>> deserialize(xml, IWithDatetime, new_datetime)
    >>> new_datetime.datetime is None
    True

Choice
======

Choice fields. For now, we only work with Choice fields that have 
text values::


    >>> from zc.sourcefactory.basic import BasicSourceFactory
    >>> class ChoiceSource(BasicSourceFactory):
    ...     def getValues(self):
    ...         return [u'alpha', u'beta']
    >>> class IWithChoice(interface.Interface):
    ...     choice = schema.Choice(title=u'Choice', required=False,
    ...                            source=ChoiceSource())
    >>> class WithChoice(object):
    ...     implements(IWithChoice)
    ...     def __init__(self, choice):
    ...         self.choice = choice
    >>> with_choice = WithChoice('alpha')
    >>> xml = serialize('container', IWithChoice, with_choice)
    >>> print xml
    <container>
      <choice>alpha</choice>
    </container>
    >>> new_choice = WithChoice(None)
    >>> deserialize(xml, IWithChoice, new_choice)
    >>> new_choice.choice
    'alpha'
    >>> with_choice = WithChoice(None)
    >>> xml = serialize('container', IWithChoice, with_choice)
    >>> print xml
    <container>
      <choice/>
    </container>
    >>> deserialize(xml, IWithChoice, new_choice)
    >>> new_choice.choice is None
    True

Set
===

Set fields are very similar to List fields::

    >>> class IWithSet(interface.Interface):
    ...     set = schema.Set(title=u'Set', required=False,
    ...                      value_type=schema.Choice(__name__='choice',
    ...                                               source=ChoiceSource()))
    >>> class WithSet(object):
    ...     implements(IWithSet)
    ...     def __init__(self, set):
    ...         self.set = set
    >>> with_set = WithSet(set(['alpha']))
    >>> xml = serialize('container', IWithSet, with_set)
    >>> print xml
    <container>
      <set>
        <choice>alpha</choice>
      </set>
    </container>
    >>> with_set = WithSet(set(['alpha', 'beta']))
    >>> xml = serialize('container', IWithSet, with_set)
    >>> print xml
    <container>
      <set>
        <choice>alpha</choice>
        <choice>beta</choice>
      </set>
    </container>
    >>> new_set = WithSet(None)
    >>> deserialize(xml, IWithSet, new_set)
    >>> new_set.set
    set(['alpha', 'beta'])
   

Deserialization with errors
===========================

We define the IName interface again but with constraints:

    >>> from zope.schema.fieldproperty import FieldProperty
    >>> from z3c.schema2xml import DeserializationError

    >>> class INameConstraint(interface.Interface):
    ...     first_name = schema.TextLine(title=u'First name', max_length=3)
    ...     last_name = schema.TextLine(title=u'Last name')

Our change the implementation of our content class. We use now
Field properties to reflect the changes form our interface.

    >>> class NameConstraint(object):
    ...     implements(IName)
    ...     first_name = FieldProperty(INameConstraint['first_name'])
    ...     last_name = FieldProperty(INameConstraint['last_name'])
    ...     def __init__(self, first_name, last_name):
    ...         self.first_name = first_name
    ...         self.last_name = last_name


    >>> xml = '''
    ...  <container>
    ...    <first_name>Karel</first_name>
    ...    <last_name>Titulaer</last_name>
    ...  </container>
    ...  '''
    >>> name = NameConstraint(u'', u'')

We try to deserialize against the constraint and
we get an DeserializationError:

    >>> deserialize(xml, INameConstraint, name)
    Traceback (most recent call last):
    ...
    DeserializationError

Let's catch the error.

    >>> try:
    ...     deserialize(xml, INameConstraint, name)
    ... except DeserializationError, e:
    ...     pass

We get detailed information which value has an error.

    >>> key, value = e.field_errors.values()[0]
    >>> key
    TooLong(u'Karel', 3)

    >>> value
    <Element first_name at ...>
