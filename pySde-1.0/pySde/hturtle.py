# -*- coding: utf-8 -*-
"""
Extracting possible embedded Turtle content from the file and parse it separately into the Graph. This is used, for example
by U{SVG 1.2 Tiny<http://www.w3.org/TR/SVGMobile12/>}.

@author: U{Ivan Herman<a href="http://www.w3.org/People/Ivan/">}
@license: This software is available for use under the
U{W3C® SOFTWARE NOTICE AND LICENSE<href="http://www.w3.org/Consortium/Legal/2002/copyright-software-20021231">}
@contact: Ivan Herman, ivan@w3.org
@version: $Id: hturtle.py,v 1.1 2012/03/13 16:34:18 ivan Exp $
$Date: 2012/03/13 16:34:18 $
"""

import sys
from pySde import PY3
if PY3 :
	from io import StringIO
else :
	from StringIO import StringIO

import re

def handle_embeddedRDF(node, graph, base) :
	"""
	"""
	def _get_literal(Pnode):
		"""
		Get the full text
		@param Pnode: DOM Node
		@return: string
		"""
		rc = ""
		for node in Pnode.childNodes:
			if node.nodeType in [node.TEXT_NODE, node.CDATA_SECTION_NODE] :
				rc = rc + node.data
		# Sigh... the HTML5 parser does not recognize the CDATA escapes, ie, it just passes on the <![CDATA[ and ]]> strings:-(
		return rc.replace("<![CDATA[","").replace("]]>","")

	if node.nodeName.lower() == "script" :
		if node.hasAttribute("type") and node.getAttribute("type") == "text/turtle" :
			content  = _get_literal(node)
			rdf = StringIO(content)
			graph.parse(rdf, format="n3", publicID = base)
	else :
		for child in node.childNodes :
			if node.nodeType == node.ELEMENT_NODE :
				handle_embeddedRDF(child, graph, base)

