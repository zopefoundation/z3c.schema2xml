from setuptools import setup, find_packages
import sys, os

setup(name='z3c.schema2xml',
      version='0.11dev',
      description="Convert schema-described Zope 3 objects to XML and back",
      long_description="""\
""",
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
