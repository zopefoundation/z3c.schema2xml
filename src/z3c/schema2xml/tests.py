import unittest

from zope.testing import doctest

def grok_setup(iets):
    import grok
    grok.grok('z3c.schema2xml')

def test_suite():
    optionflags = (
        doctest.ELLIPSIS
        | doctest.REPORT_NDIFF
        | doctest.NORMALIZE_WHITESPACE
        )

    return unittest.TestSuite([
        doctest.DocFileSuite(
            'README.txt', setUp=grok_setup, optionflags=optionflags)
        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

