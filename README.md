
# HTML Structured Data Extractor to RDF

Note: since I retired a few months ago I do not really maintain this package any more. I would be more than happy if an interested party was interested to take over. In the meantime, I have "archived" the repository to clearly signal that there is no maintenance. I would be happy to unarchive it and transfer ownership if someone is interested.  
@iherman

This is a common Python interface to extract structured data from HTML files in RDF. Structured data can be in <a href="http://www.w3.org/TR/microdata/">microdata</a>, <a href="http://www.w3.org/TR/rdfa-in-html/">RDFa</a>, or <a href="http://www.w3.org/TR/turtle/#in-html">Turtle embedded in HTML</a>. While RDFa and Turtle are both RDF serialization syntaxes, microdata is not; it is simply <span property="doap:description"><a href="/TR/microdata/"></a> a specification for attributes to be used with HTML5 to express structured data. A separate <a href="http://www.w3.org/TR/microdata-rdf/">Semantic Web Interest Group Note</a> defines a mapping from HTML5+Microdata to RDF.

The software in this repository is only a thin layer on top of:

- [PyRdfa](https://github.com/RDFLib/pyrdfa3), a full RDFa parser and distiller, built on top of [RDFLib](https://github.com/RDFLib/rdflib)
- [pyMicrodata](https://github.com/RDFLib/pymicrodata), a microdata to RDF distiller, built on top of the same [RDFLib](https://github.com/RDFLib/rdflib)

The local package includes the extraction of Turtle embedded in HTML.

The library is used by the [SDE service at W3C](https://www.w3.org/2012/sde/).

