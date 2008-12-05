from setuptools import setup, find_packages
import sys, os

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('src', 'z3c', 'schema2xml', 'README.txt')
    + '\n' +
    read('CHANGES.txt')
    + '\n' +
    'Download\n'
    '********\n'
    )

setup(name='z3c.schema2xml',
      version='1.1dev',
      description="Convert schema-described Zope 3 objects to XML and back",
      long_description=long_description,
      classifiers=[],
      keywords="",
      author="Martijn Faassen, Jan-Wijbrand Kolman",
      author_email="faassen@startifact.com",
      url="",
      license="ZPL",
      package_dir={'': 'src'},
      packages=find_packages('src'),
      namespace_packages=['z3c'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'setuptools',
        'lxml',
        'grokcore.component',
        'zc.sourcefactory',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
