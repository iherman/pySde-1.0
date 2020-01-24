# -*- coding: utf-8 -*-
"""

@summary: Structural data extractor (distiller)
@requires: Python version 2.5 or up
@requires: U{RDFLib<http://rdflib.net>}
@requires: U{html5lib<http://code.google.com/p/html5lib/>} for the HTML5 parsing; note possible dependecies on Python's version on the project's web site
@organization: U{World Wide Web Consortium<http://www.w3.org>}
@author: U{Ivan Herman<a href="http://www.w3.org/People/Ivan/">}
@license: This software is available for use under the
U{W3C® SOFTWARE NOTICE AND LICENSE<href="http://www.w3.org/Consortium/Legal/2002/copyright-software-20021231">}

@var builtInTransformers: list of built-in transformers that are unconditionally executed.
"""

"""
$Id: __init__.py,v 1.3 2012/09/05 16:42:44 ivan Exp $ $Date: 2012/09/05 16:42:44 $


"""

__version__ = "2.0"
__author__  = 'Ivan Herman'
__contact__ = 'Ivan Herman, ivan@w3.org'
__license__ = 'W3C® SOFTWARE NOTICE AND LICENSE, http://www.w3.org/Consortium/Legal/2002/copyright-software-20021231'

import sys
PY3 = (sys.version_info[0] >= 3)

if PY3 :
	from io import StringIO
else :
	from io import StringIO

import datetime
import os

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

import urllib.parse

from pyRdfa.utils import URIOpener
from pyRdfa       import HTTPError, FailedSource

from pyMicrodata.microdata	import MicrodataConversion

from pySde.options import SDEOptions

debug = False

ns_sde   = Namespace("http://www.w3.org/2012/pySde/vocab#")
ns_dc    = Namespace("http://purl.org/dc/terms/")
ns_xsd   = Namespace('http://www.w3.org/2001/XMLSchema#')
ns_ht    = Namespace("http://www.w3.org/2006/http#")

#########################################################################################################
class pySde :
	"""Main processing class for the distiller
	@ivar base: the base value for processing
	@ivar http_status: HTTP Status, to be returned when the package is used via a CGI entry. Initially set to 200, may be modified by exception handlers
	"""

	def __init__(self, base = "", options = SDEOptions()) :
		"""
		@keyword base: URI for the default "base" value (usually the URI of the file to be processed)
		"""
		self.http_status = 200
		self.base        = base
		self.options     = options
		if options.rdfa == False and options.microdata == False and options.hturtle == False :
			self.empty = True
		else :
			self.empty = False

	def _generate_error_graph(self, pgraph, full_msg, uri = None) :
		"""
		Generate an error message into the graph. This method is usually used reacting on exceptions.

		Later versions of pyMicrodata may have more detailed error conditions on which it wishes to react. At the moment, this
		is fairly crude...
		"""
		if pgraph == None :
			retval = Graph()
		else :
			retval = pgraph

		pgraph.bind( "dc","http://purl.org/dc/terms/" )
		pgraph.bind( "xsd",'http://www.w3.org/2001/XMLSchema#' )
		pgraph.bind( "ht",'http://www.w3.org/2006/http#' )
		pgraph.bind( "pySde",'http://www.w3.org/2012/pySde/vocab#' )

		bnode = BNode()
		retval.add((bnode, ns_rdf["type"], ns_micro["Error"]))
		retval.add((bnode, ns_dc["description"], Literal(full_msg)))
		retval.add((bnode, ns_dc["date"], Literal(datetime.datetime.utcnow().isoformat(),datatype=ns_xsd["dateTime"])))

		if uri != None :
			htbnode = BNode()
			retval.add( (bnode, ns_micro["context"],htbnode) )
			retval.add( (htbnode, ns_rdf["type"], ns_ht["Request"]) )
			retval.add( (htbnode, ns_ht["requestURI"], Literal(uri)) )

		if self.http_status != 200 :
			htbnode = BNode()
			retval.add( (bnode, ns_micro["context"],htbnode) )
			retval.add( (htbnode, ns_rdf["type"], ns_ht["Response"]) )
			retval.add( (htbnode, ns_ht["responseCode"], URIRef("http://www.w3.org/2006/http#%s" % self.http_status)) )

		return retval

	def _get_input(self, name) :
		"""
		Trying to guess whether "name" is a URI, a string; it then tries to open these as such accordingly,
		returning a file-like object. If name is a plain string then it returns the input argument (that should
		be, supposidly, a file-like object already)
		@param name: identifier of the input source
		@type name: string or a file-like object
		@return: a file like object if opening "name" is possible and successful, "name" otherwise
		"""
		try :
			# Python 2 branch
			is_string = isinstance(name, basestring)
		except :
			# Python 3 branch
			is_string = isinstance(name, str)
	
		if is_string :
			# check if this is a URI, ie, if there is a valid 'scheme' part
			# otherwise it is considered to be a simple file
			if urllib.parse.urlparse(name)[0] != "" :
				url_request = URIOpener(name)
				self.base   = url_request.location
				return url_request.data
			else :
				self.base = 'file://' + name
				return open(name, 'rb')
		else :
			return name

	####################################################################################################################
	# Externally used methods
	#
	def graph_from_DOM(self, dom, graph = None) :
		"""
		Extract the RDF Graph from a DOM tree.
		@param dom: a DOM Node element, the top level entry node for the whole tree (to make it clear, a dom.documentElement is used to initiate processing)
		@keyword graph: an RDF Graph (if None, than a new one is created)
		@type graph: rdflib Graph instance. If None, a new one is created.
		@return: an RDF Graph
		@rtype: rdflib Graph instance
		"""
		if graph == None :
			# Create the RDF Graph that will contain the return triples...
			graph   = Graph()

		if self.options.rdfa :
			from pyRdfa         import pyRdfa
			from pyRdfa.options import Options
			from pyRdfa.host    import HostLanguage
			rdfa_options = Options(
				embedded_rdf    = False,
				vocab_expansion = self.options.vocab_expansion
			)
			rdfa_options.set_host_language(HostLanguage.html5)
			processor = pyRdfa(rdfa_options, self.base)
			graph = processor.graph_from_DOM(dom, graph)
		if self.options.microdata :
			from pyMicrodata import pyMicrodata
			processor = pyMicrodata(base = self.base)
			graph = processor.graph_from_DOM(dom, graph)
			pass
		if self.options.hturtle :
			from pySde.hturtle import handle_embeddedRDF
			handle_embeddedRDF(dom.documentElement, graph, self.base)

		return graph

	def graph_from_source(self, name, graph = None, rdfOutput = False) :
		"""
		Extract an RDF graph from an HTML source. The source is parsed, the RDF extracted, and the RDF Graph is
		returned. This is a front-end to the L{pySde.graph_from_DOM} method.

		@param name: a URI, a file name, or a file-like object
		@return: an RDF Graph
		@rtype: rdflib Graph instance
		"""
		# First, open the source...
		try :
			# First, open the source... Possible HTTP errors are returned as error triples
			input = None
			try :
				input = self._get_input(name)
			except FailedSource :
				f = sys.exc_info()[1]
				self.http_status = 400
				if not rdfOutput : raise f
				return self._generate_error_graph(graph, f.msg, uri=name)
			except HTTPError :
				h = sys.exc_info()[1]
				self.http_status = h.http_code
				if not rdfOutput : raise h
				return self._generate_error_graph(graph, "HTTP Error: %s (%s)" % (h.http_code,h.msg), uri=name)
			except Exception :
				e = sys.exc_info()[1]
				# Something nasty happened:-(
				self.http_status = 500
				if not rdfOutput : raise e
				return self._generate_error_graph(graph, str(e), uri=name)

			dom = None
			try :
				import warnings
				warnings.filterwarnings("ignore", category=DeprecationWarning)
				import html5lib
				parser = html5lib.HTMLParser(tree=html5lib.treebuilders.getTreeBuilder("dom"))
				dom = parser.parse(input)
				return self.graph_from_DOM(dom, graph)
			except Exception :
				e = sys.exc_info()[1]
				# Something nasty happened:-(
				self.http_status = 400
				if not rdfOutput : raise e
				return self._generate_error_graph(graph, str(e), uri=name)

		except Exception :
			e = sys.exc_info()[1]
			# Something nasty happened:-(
			self.http_status = 500
			if not rdfOutput : raise e
			return self._generate_error_graph(graph, str(e), uri=name)

	def rdf_from_sources(self, names, outputFormat = "pretty-xml", rdfOutput = False) :
		"""
		Extract and RDF graph from a list of RDFa sources and serialize them in one graph. The sources are parsed, the RDF
		extracted, and serialization is done in the specified format.
		@param names: list of sources, each can be a URI, a file name, or a file-like object
		@keyword outputFormat: serialization format. Can be one of "turtle", "n3", "xml", "pretty-xml", "nt". "xml" and "pretty-xml", as well as "turtle" and "n3" are synonyms.
		@return: a serialized RDF Graph
		@rtype: string
		"""
		if rdflib.__version__ >= "3.0.0" :
			graph = Graph()
		else :
			# We may need the extra utilities for older rdflib versions...
			try :
				from pyRdfaExtras import MyGraph
				graph = MyGraph()
			except :
				graph = Graph()

		# the value of rdfOutput determines the reaction on exceptions...
		if self.empty == False :
			for name in names :
				self.graph_from_source(name, graph, rdfOutput)

		# Stupid difference between python2 and python3...
		if PY3 :
			return str(graph.serialize(format=outputFormat), encoding='utf-8')
		else :
			return graph.serialize(format=outputFormat)


	def rdf_from_source(self, name, outputFormat = "pretty-xml", rdfOutput = False) :
		"""
		Extract and RDF graph from an RDFa source and serialize it in one graph. The source is parsed, the RDF
		extracted, and serialization is done in the specified format.
		@param name: a URI, a file name, or a file-like object
		@keyword outputFormat: serialization format. Can be one of "turtle", "n3", "xml", "pretty-xml", "nt". "xml" and "pretty-xml", as well as "turtle" and "n3" are synonyms.
		@return: a serialized RDF Graph
		@rtype: string
		"""
		return self.rdf_from_sources([name], outputFormat, rdfOutput)

################################################# CGI Entry point
def processURI(uri, outputFormat, form) :
	"""The standard processing of a microdata uri options in a form, ie, as an entry point from a CGI call.

	The call accepts extra form options (eg, HTTP GET options) as follows:

	@param uri: URI to access. Note that the "text:" and "uploaded:" values are treated separately; the former is for textual intput (in which case a StringIO is used to get the data) and the latter is for uploaded file, where the form gives access to the file directly.
	@param outputFormat: serialization formats, as understood by RDFLib. Note that though "turtle" is
	a possible parameter value, some versions of the RDFLib turtle generation does funny (though legal) things with
	namespaces, defining unusual and unwanted prefixes...
	@param form: extra call options (from the CGI call) to set up the local options
	@type form: cgi FieldStorage instance
	@return: serialized graph
	@rtype: string
	"""
	def _get_option(param, compare_value, default) :
		param_old = param.replace('_','-')
		if param in list(form.keys()) :
			val = form.getfirst(param).lower()
			return val == compare_value
		elif param_old in list(form.keys()) :
			# this is to ensure the old style parameters are still valid...
			# in the old days I used '-' in the parameters, the standard favours '_'
			val = form.getfirst(param_old).lower()
			return val == compare_value
		else :
			return default

	if uri == "uploaded:" :
		input	= form["uploaded"].file
		base	= ""
	elif uri == "text:" :
		input	= StringIO(form.getfirst("text"))
		base	= ""
	else :
		input	= uri
		base	= uri

	vocab_expansion     = _get_option( "vocab_expansion", "true", False)

	sources = form.getlist("source")
	rdfa      = "rdfa" in sources
	microdata = "microdata" in sources
	hturtle   = "hturtle" in sources

	options = SDEOptions( hturtle         = "hturtle" in sources,
						  rdfa            = "rdfa" in sources,
						  microdata       = "microdata" in sources,
						  vocab_expansion = vocab_expansion)

	processor = pySde(base = base, options = options)

	# Decide the output format; the issue is what should happen in case of a top level error like an inaccessibility of
	# the html source: should a graph be returned or an HTML page with an error message?

	try :
		graph = processor.rdf_from_source(input, outputFormat, rdfOutput = ("forceRDFOutput" in list(form.keys())))
		if outputFormat == "n3" :
			retval = 'Content-Type: text/rdf+n3; charset=utf-8\n'
		elif outputFormat == "nt" or outputFormat == "turtle" :
			retval = 'Content-Type: text/turtle; charset=utf-8\n'
		elif outputFormat == "json-ld" or outputFormat == "json" :
			retval = 'Content-Type: application/json; charset=utf-8\n'
		else :
			retval = 'Content-Type: application/rdf+xml; charset=utf-8\n'
		retval += '\n'

		retval += graph
		return retval
	except HTTPError as h :
		import cgi

		retval = 'Content-type: text/html; charset=utf-8\nStatus: %s \n\n' % h.http_code
		retval += "<html>\n"
		retval += "<head>\n"
		retval += "<title>HTTP Error in structured data processing</title>\n"
		retval += "</head><body>\n"
		retval += "<h1>HTTP Error in distilling structured data</h1>\n"
		retval += "<p>HTTP Error: %s (%s)</p>\n" % (h.http_code,h.msg)
		retval += "<p>On URI: <code>'%s'</code></p>\n" % cgi.escape(uri)
		retval +="</body>\n"
		retval +="</html>\n"
		return retval
	except :
		# This branch should occur only if an exception is really raised, ie, if it is not turned
		# into a graph value.
		(type,value,traceback) = sys.exc_info()

		import traceback, cgi

		retval = 'Content-type: text/html; charset=utf-8\nStatus: %s\n\n' % processor.http_status
		retval += "<html>\n"
		retval += "<head>\n"
		retval += "<title>Exception in structured data processing</title>\n"
		retval += "</head><body>\n"
		retval += "<h1>Exception in distilling structured data</h1>\n"
		retval += "<pre>\n"
		strio  = StringIO()
		traceback.print_exc(file=strio)
		retval += strio.getvalue()
		retval +="</pre>\n"
		retval +="<pre>%s</pre>\n" % value
		retval +="<h1>Request details</h1>\n"
		retval +="<dl>\n"
		if uri == "text:" and "text" in form and form["text"].value != None and len(form["text"].value.strip()) != 0 :
			retval +="<dt>Text input:</dt><dd>%s</dd>\n" % cgi.escape(form["text"].value).replace('\n','<br/>')
		elif uri == "uploaded:" :
			retval +="<dt>Uploaded file</dt>\n"
		else :
			retval +="<dt>URI received:</dt><dd><code>'%s'</code></dd>\n" % cgi.escape(uri)
		retval +="<dt>Output serialization format:</dt><dd> %s</dd>\n" % outputFormat
		retval +="</dl>\n"
		retval +="</body>\n"
		retval +="</html>\n"
		return retval

###################################################################################################
