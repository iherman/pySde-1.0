from setuptools import setup

setup(name="sde",
      description="Structured Data Extractor Libray",
      version="2.0",
      author="Ivan Herman",
      author_email="ivan@w3.org",
	  maintainer="Ivan Herman",
	  maintainer_email="ivan@w3.org",
      packages=['pySde'],
      requires = ['rdflib', 'pyrdfa3', 'pyMicrodata-1.0'],
 )
