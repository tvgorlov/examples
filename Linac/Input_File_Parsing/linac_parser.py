import sys,os

#import python XML DOM parser
import xml.dom.minidom

# import pyORBIT Python utilities classes for objects with names, types, and dictionary parameters
from orbit.utils import orbitFinalize
from orbit.utils   import NamedObject, TypedObject, ParamsDictObject

class LinacStuctNode(NamedObject, TypedObject, ParamsDictObject):
	"""
	The node that keeps the information from xml file.
	Parameters includes position length and others type dependent.
	"""
	def __init__(self,name = "node"):
		NamedObject.__init__(self,name)
		TypedObject.__init__(self,type_in = "none")
		ParamsDictObject.__init__(self)		

		
class LinacStructSeq(	NamedObject, TypedObject, ParamsDictObject):
	"""	
	The linac sequence. It includes the LinacStuctNodes. It has the length parameter
	"""
	def __init__(self, name = "None"):
		NamedObject.__init__(self,name)
		TypedObject.__init__(self,type_in = "sequence")
		ParamsDictObject.__init__(self)
		self.nodes = []
		self.setParam("length",0.)
		
	def addNode(self,node):
		if(not isinstance(node,LinacStuctNode)):
			msg = "LinacStructSeq: cannot add node. It is not LinacStuctNode instance!"
			msg = msg + os.linesep
			msg = msg + "========================================="
			msg = msg + os.linesep
			orbitFinalize(msg)	
		self.nodes.append(node)

	def getSeqs(self):
		return self.nodes
		
	def getLength(self):
		return self.getParam("length")

class LinacStructTree(NamedObject, TypedObject, ParamsDictObject):
	"""	
	The linac lattice. It includes set of LinacStructSeq.
	"""
	def __init__(self, name = "None"):
		NamedObject.__init__(self,name)
		TypedObject.__init__(self,type_in = "linac")
		ParamsDictObject.__init__(self)		
		self.seqs = []
		self.length = 0.
		
	def addSeq(self,node):
		if(not isinstance(node,LinacStructSeq)):
			msg = "LinacStructTree: cannot add node. It is not LinacStructSeq instance!"
			msg = msg + os.linesep
			msg = msg + "========================================="
			msg = msg + os.linesep
			orbitFinalize(msg)	
		self.seqs.append(node)
		self.length = self.length + node.getParam("length")

	def getSeqs(self):
		return self.seqs

	def getLength(self):
		return self.length

class SimplifiedLinacParser:
	"""
	This is a parser for simplified XML file with a linac structure.
	The linac structure has sequences with elements. RF gaps has the name of a 
	RF cavity as an envelop structure.
	"""
	def __init__(self,xml_file_name):
		self.dom_doc = xml.dom.minidom.parse("sns_linac.xml")
		if(len(self.dom_doc.childNodes) != 1):
			msg = "SimplifiedLinacParser: input xml file has a wrong structure!"
			msg = msg + os.linesep
			msg = msg + "File: " + xml_file_name
			msg = msg + os.linesep
			msg = msg + "========================================="
			msg = msg + os.linesep
			orbitFinalize(msg)		
		self.domLinac = self.dom_doc.childNodes[0]
		self.linacTree = LinacStructTree(name = self.domLinac.localName)		
		domSequences = self._stripDOMtoElements(self.domLinac)
		for domSeq in domSequences:
			linacSeq = LinacStructSeq(name = domSeq.localName)
			seqParamDict = {}
			for i in range(domSeq.attributes.length):
				seqParamDict[domSeq.attributes.item(i).name] = domSeq.attributes.item(i).value
			linacSeq.setParam("length",float(seqParamDict["length"]))
			domNodes = self._stripDOMtoElements(domSeq)
			for domNode in domNodes:
				nNodeParam = domNode.attributes.length
				paramDict = {}
				for i in range(nNodeParam):
					paramDict[domNode.attributes.item(i).name] = domNode.attributes.item(i).value
					#print "i=",i," name=",domNode.attributes.item(i).name," val=",domNode.attributes.item(i).value
				#---- add parameters from <parameters> child domNode
				domParameters = self._stripDOMtoElements(domNode)
				#print "domNode =",domNode.localName ," domParameters=",domParameters
				if(len(domParameters) > 1):
					msg = "SimplifiedLinacParser:more than 1 child in accNode!"
					msg = msg + os.linesep	
					orbitFinalize(msg)
				if(len(domParameters) == 1):
					domParameter = domParameters[0]
					for i in range(domParameter.attributes.length):
						paramDict[domParameter.attributes.item(i).name] = domParameter.attributes.item(i).value
				nodeName = paramDict["name"]
				del paramDict["name"]			
				linacNode = LinacStuctNode(name = nodeName)
				if(paramDict.has_key("type")):
					linacNode.setType(type_in = paramDict["type"])
					del paramDict["type"]
				else:
					linacNode.setType(type_in = "marker")
				linacNode.setParamsDict(paramDict)
				linacSeq.addNode(linacNode)
			self.linacTree.addSeq(linacSeq)
			print "name=",linacSeq.getName()," type=",linacSeq.getType()," length=",linacSeq.getLength()

	def _stripDOMtoElements(self,domNode):
		"""
		Removes all DOM Document componenets that are not DOM Elements and
		returns the array with dom elements.
		"""
		domChildren = []
		for child in domNode.childNodes:
			if(child.nodeType == child.ELEMENT_NODE):
				domChildren.append(child)
		return domChildren	

	def getLinacStructTree(self):
		"""
		Returns the linac structure tree. It will be used to build the linac accelerator lattice.
		"""
		return self.linacTree





parser = SimplifiedLinacParser("sns_linac.xml")
linacTree = parser.getLinacStructTree()
print "Total length=",linacTree.getLength()
sys.exit(1)

