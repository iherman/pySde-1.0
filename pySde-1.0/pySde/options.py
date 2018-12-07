# -*- coding: utf-8 -*-
"""
L{Options} class: collect the possible options that govern the parsing possibilities. The module also includes the L{ProcessorGraph} class that handles the processor graph, per RDFa 1.1 (i.e., the graph containing errors and warnings). 

@summary: RDFa parser (distiller)
@requires: U{RDFLib<http://rdflib.net>}
@organization: U{World Wide Web Consortium<http://www.w3.org>}
@author: U{Ivan Herman<a href="http://www.w3.org/People/Ivan/">}
@license: This software is available for use under the
U{W3C SOFTWARE NOTICE AND LICENSE<href="http://www.w3.org/Consortium/Legal/2002/copyright-software-20021231">}
"""

"""
$Id: options.py,v 1.2 2012/08/22 12:47:06 ivan Exp $ $Date: 2012/08/22 12:47:06 $
"""

import sys, datetime

import rdflib
from rdflib	import URIRef
from rdflib	import Literal
from rdflib	import BNode
from rdflib	import Namespace
if rdflib.__version__ >= "3.0.0" :
	from rdflib	import Graph
	from rdflib	import RDF  as ns_rdf
	from rdflib	import RDFS as ns_rdfs
else :
	from rdflib.Graph	import Graph
	from rdflib.RDFS	import RDFSNS as ns_rdfs
	from rdflib.RDF		import RDFNS  as ns_rdf

class SDEOptions :
	"""Settable options. 
	"""
	def __init__(self, hturtle = True, rdfa = True, microdata = True, vocab_expansion = False) :
		"""
		@keyword space_preserve: whether plain literals should preserve spaces at output or not
		@type space_preserve: Boolean
		@keyword output_default_graph: whether the 'default' graph should be returned to the user
		@type output_default_graph: Boolean
		@keyword output_processor_graph: whether the 'processor' graph should be returned to the user
		@type output_processor_graph: Boolean
		@keyword transformers: extra transformers
		@type transformers: list
		"""
		self.hturtle         = hturtle
		self.rdfa	         = rdfa
		self.microdata       = microdata
		self.vocab_expansion = vocab_expansion

			
	def __str__(self) :
		retval = """Current options:
		extract turtle            : %s
		extract rdfa              : %s
		extract microdata         : %s
		expand rdfa vocabularies  : %s

		"""
		return retval % (self.hturtle, self.rdfa, self.microdata, self.vocab_expansion)
		
