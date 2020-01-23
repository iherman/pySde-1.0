#!/usr/bin/env python3
"""
Run the sde extraction package locally
"""

import sys

# You may want to adapt this to your environment...
import sys, getopt, platform

sys.path.insert(0,"/Users/ivan/Library/Python")
sys.path.insert(0,"/Users/ivan/Library/Python/RDFa")

from pySde.options import SDEOptions
from pySde import pySde

###########################################


usageText="""Usage: %s -[armsvxtjnpb:] [filename[s]]
where:
  -r: distill RDFa
  -m: distill Microdata
  -h: distill hturtle script
  -a: distill in RDFa, Microdata, and hturtle (shorthand for -rmh)
  -x: output format RDF/XML
  -t: output format Turtle (default)
  -j: output format JSON-LD
  -n: output format N Triples
  -p: output format pretty RDF/XML
  -b: give the base URI; if a file name is given, this can be left empty and the file name is used
  -v: (in case RDFa is used) expand vocabularies

'Filename' can be a local file name or a URI. In case there is no filename, stdin is used.

"""

def usage() :
	print(usageText % sys.argv[0])

format       = "turtle"
base         = ""
rdfa         = False
microdata    = False
hturtle      = False
vocab_expand = False

try :
	opts, value = getopt.getopt(sys.argv[1:],"armsvxtjnpb:")
	for o,a in opts:
		if o == "-t" :
			format = "turtle"
		elif o == "-j" :
			format = "json-ld"
		elif o == "-n" :
			format = "nt"
		elif o == "-p" or o == "-x":
			format = "pretty-xml"
		elif o == "-b" :
			base = a
		elif o == "-r" :
			rdfa = True
		elif o == "-m" :
			microdata = True
		elif o == "-h" :
			hturtle = True
		elif o == "-a" :
			rdfa = microdata = hturtle = True
		elif o == "-v" :
			vocab_expand = True
		else :
			usage()
			sys.exit(1)
except :
	usage()
	sys.exit(1)

options = SDEOptions(hturtle=hturtle, rdfa = rdfa, microdata = microdata, vocab_expansion = vocab_expand)
processor = pySde(base, options)

if len(value) >= 1 :
	print(processor.rdf_from_sources(value, outputFormat = format))
else :
	print(processor.rdf_from_source(sys.stdin, outputFormat = format))
