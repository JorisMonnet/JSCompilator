# coding: UTF-8

''' Petit module utilitaire pour la construction, la manipulation et la 
représentation d'arbres syntaxiques abstraits.
Sûrement plein de bugs et autres surprises. à prendre comme un 
"work in progress"...
Notamment, l'utilisation de pydot pour représenter un arbre syntaxique cousu
est une utilisation un peu "limite" de graphviz. ça marche, mais le layout n'est
pas toujours optimal...
'''
dicNode = {}

import pydot
class Node:
    count = 0
    type = 'Node (unspecified)'
    shape = 'ellipse'
    def __init__(self,children=None):
        self.ID = str(Node.count)
        self.hasGraphicalTree=False
        Node.count+=1
        dicNode[self.ID]= self
        if not children: self.children = []
        elif hasattr(children,'__len__'):
            self.children = children
        else:
            self.children = [children]
        self.next = []

    def addNext(self,next):
        self.next.append(next)

    def asciitree(self, prefix=''):
        result = "%s%s\n" % (prefix, repr(self))
        prefix += '|  '
        for c in self.children:
            if not isinstance(c,Node):
                result += "%s*** Error: Child of type %r: %r\n" % (prefix,type(c),c)
                continue
            result += c.asciitree(prefix)
        return result
    
    def __str__(self):
        return self.asciitree()
    
    def __repr__(self):
        return self.type
    
    def makegraphicaltree(self, dot=None, edgeLabels=True, firstTime = False):
            if not dot: dot = pydot.Dot()
            dot.add_node(pydot.Node(self.ID,label=repr(self), shape=self.shape))
            label = edgeLabels and len(self.children)-1
            for i, c in enumerate(self.children):
                if c.hasGraphicalTree: return
                c.makegraphicaltree(dot, edgeLabels)
                c.hasGraphicalTree = c.type != 'Program' and c.type != 'Token' and c.type !='Function'
                if self.type=='Function':
                    c.hasGraphicalTree = True
                edge = pydot.Edge(self.ID,c.ID)
                if label:
                    edge.set_label(str(i))
                dot.add_edge(edge)
                #Workaround for a bug in pydot 1.0.2 on Windows:
                #dot.set_graphviz_executables({'dot': r'C:\Program Files\Graphviz2.38\bin\dot.exe'})
            return dot
        
    def threadTree(self, graph, seen = None, col=0):
            colors = ('red', 'green', 'blue', 'yellow', 'magenta', 'cyan')
            if not seen: seen = []
            if self in seen: return
            seen.append(self)
            new = not graph.get_node(self.ID)
            if new:
                graphnode = pydot.Node(self.ID,label=repr(self), shape=self.shape)
                graphnode.set_style('dotted')
                graph.add_node(graphnode)
            label = len(self.next)-1
            for i,c in enumerate(self.next):
                if not c: return
                col = (col + 1) % len(colors)
                col=0 # FRT pour tout afficher en rouge
                color = colors[col]                
                c.threadTree(graph, seen, col)
                edge = pydot.Edge(self.ID,c.ID)
                edge.set_color(color)
                edge.set_arrowsize('.5')
                # Les arrêtes correspondant aux coutures ne sont pas prises en compte
                # pour le layout du graphe. Ceci permet de garder l'arbre dans sa représentation
                # "standard", mais peut provoquer des surprises pour le trajet parfois un peu
                # tarabiscoté des coutures...
                # En commantant cette ligne, le layout sera bien meilleur, mais l'arbre nettement
                # moins reconnaissable.
                edge.set_constraint('false') 
                if label:
                    edge.set_taillabel(str(i))
                    edge.set_labelfontcolor(color)
                graph.add_edge(edge)
            return graph    

class ProgramNode(Node):
    type = 'Program'
    def __init__(self,children):
        self.variableNode = None
        super().__init__(children)

    def addVariables(self,variables):
        if not self.variableNode : 
            self.variableNode = VariableNode(variables)
            self.children.insert(0,self.variableNode)
        else:
            self.variableNode.children.extend(variables)
   
class TokenNode(Node):
    type = 'Token'
    def __init__(self, tok):
        Node.__init__(self)
        self.tok = tok
        
    def __repr__(self):
        return repr(self.tok)

class EntryNode(Node):
    type = 'ENTRY'
    def __init__(self):
        Node.__init__(self, None)

####################################################################################################################

class FunctionNode(Node):
    type = 'Function'
    def verifyArgumentsNumber(self,nb):
        if nb == 0:
            return self.children[1].children[0].tok == 'No Arguments'
        return len(self.children[1].children) == nb and self.children[1].children[0].tok != 'No Arguments'

class ReturnNode(Node):
    type = 'Return'

class FunctionCallNode(Node):
    type = 'FunctionCall'

class ArgNode(Node):
    type = 'Argument(s)'

####################################################################################################################

class OpNode(Node):
    def __init__(self, op, children):
        Node.__init__(self,children)
        self.op = op
        try:
            self.nbargs = len(children)
        except AttributeError:
            self.nbargs = 1
        
    def __repr__(self):
        return f"{self.op}"

class AssignNode(Node):
    type = '='
    def __init__(self,children,isCreated=False):
        self.isCreated = isCreated
        super().__init__(children)

class VariableNode(Node):
    type ='Variable(s)'

class ArrayNode(Node):
    type = 'Array'

####################################################################################################################

class IfNode(Node):
    type = 'If'

class ElseNode(Node):
    type = 'Else'

class ForNode(Node):
    type = 'For'

class StartForNode(Node):
    type = 'Start'

class IncForNode(Node):
    type = 'Incrementer'

class WhileNode(Node):
    type = 'While'

class DoNode(Node):
    type = 'Do'

class SwitchNode(Node):
    type = 'Switch'
    def verifyDefault(self):
        return len([child for child in self.children if child.type == 'Default']) < 2 # allow 0 or 1 defaultNode per switchNode

class CaseNode(Node):
    type = 'Case'
    
class DefaultNode(Node):
    type = 'Default'

####################################################################################################################

class LogNode(Node):
    type = 'Log'

class BreakNode(Node):
    type = 'Break'

class ContinueNode(Node):
    type = 'Continue'

####################################################################################################################

class ConditionNode(Node):
    type = 'Condition'
    
class AndNode(Node):
    type = '&&'

class OrNode(Node):
    type = '||'

class NotNode(Node):
    type = 'NOT (!)'

####################################################################################################################
    
def addToClass(cls):
    def decorator(func):
        setattr(cls,func.__name__,func)
        return func
    return decorator
                    
def recreateVariableNode():
    """ replace all variables under one variable node per scope (per programmeNode)"""
    programNodeList = set([dicNode[key] for key in dicNode if dicNode[key].type == 'Program'])
    variableNodeList = set([dicNode[key] for key in dicNode if dicNode[key].type == 'Variable(s)'])
    assignCreationNodeList = set([dicNode[key] for key in dicNode if dicNode[key].type == '=' and dicNode[key].isCreated])

    for programNode in programNodeList:
        # var nodes
        for variableNode in set([variableNode for variableNode in variableNodeList if variableNode in programNode.children]):
            programNode.addVariables(list(set(variableNode.children)))
            programNode.children.remove(variableNode)

        # assign nodes with creation of variables
        for assignNode in set([assignNode for assignNode in assignCreationNodeList if assignNode in programNode.children]):
            programNode.addVariables(list(set(assignNode.children[:len(assignNode.children)-1])))

def getArrayNodeById(id):
    """ return the ArrayNode corresponding to the given id"""
    arrayNodes = set([dicNode[key] for key in dicNode if dicNode[key].type == 'Array'])
    assignNodes = set([dicNode[key] for key in dicNode if dicNode[key].type == '='])
    for node in [node for node in assignNodes if len(set(node.children).intersection(arrayNodes))]:
        if id == node.children[0].tok: 
            return node

def getFunction(id):
    """ return a functioncallNode containing the function Node from the given id"""
    from functools import reduce
    functionNodes = [dicNode[key] for key in dicNode if dicNode[key].type == 'Function' and dicNode[key].children[0].tok==id]
    if functionNodes:
        return FunctionCallNode(functionNodes[0])
    return None


def verifyReturnNode():
    """ verify if all return nodes are in programmes block from function nodes"""
    returnNodes = set([dicNode[key] for key in dicNode if dicNode[key].type == 'Return'])
    if returnNodes == None : return True
    functionNodes = set([dicNode[key] for key in dicNode if dicNode[key].type == 'Function'])
    functionProgramsNodes = []
    for functionNode in functionNodes:
        functionProgramsNodes.extend(functionNode.children[2].children)
        
    for returnNode in returnNodes:
        if returnNode not in functionProgramsNodes:
            print("ERROR : return outside of a function")
            return False
    return True

def verifyBreakContinueNode():
    """ verify if all continue nodes are in loops and all break nodes are in structures"""
    continueNodes = []
    breakNodes = []
    switchNodes = []
    loopNodesToCheck = []   

    for key in dicNode:                         #more efficient than 5 list comprehension, only one loop
        if dicNode[key].type == 'Continue':
            continueNodes.append(dicNode[key])
        elif dicNode[key].type == 'Break':
            breakNodes.append(dicNode[key])
        elif dicNode[key].type == 'For':
            loopNodesToCheck.extend(dicNode[key].children[3].children) #ProgramNode children of ForNode
        elif dicNode[key].type == 'Switch':
            switchNodes.append(dicNode[key])
        elif dicNode[key].type == 'While':      # do while have the same program
            loopNodesToCheck.extend(dicNode[key].children[1].children) #ProgramNode children of WhileNode

    if continueNodes == None and breakNodes == None : return True
    
    for continueNode in continueNodes:
        nodeVerified = False
        for loopNode in loopNodesToCheck:
            if checkInChildren(loopNode,continueNode):
                nodeVerified = True
        if not nodeVerified:
            print("ERROR : Continue Node outside of a loop")
            return False
    
    nodesToCheck = loopNodesToCheck+switchNodes

    for breakNode in breakNodes:
        nodeVerified = False
        for nodeToCheck in nodesToCheck:
            if checkInChildren(nodeToCheck,breakNode):
                nodeVerified = True
        if not nodeVerified:
            print("ERROR : Break Node outside of a loop or switch")
            return False

    return True

def checkInChildren(nodeToCheck,nodeSearched):
    """check if a given node is in the nodeToCheck or its children"""
    if nodeToCheck==nodeSearched:
        return True
    if nodeToCheck.children == None:
        return False
    for c in nodeToCheck.children:
         if checkInChildren(c,nodeSearched):
             return True
    return False

def verifyDefault():
    """verify if all switch nodes have only 0 or 1 default node in their children"""
    for node in  set([dicNode[key] for key in dicNode if dicNode[key].type == 'Switch']):
        if not node.verifyDefault():
            print("ERROR : two default in the same switch")
            return False
    return True

def verifyNode():
    """verify if return, break, continue and Default Nodes are well placed"""
    return verifyReturnNode() and verifyBreakContinueNode() and verifyDefault()