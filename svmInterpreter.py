import AST
from AST import addToClass

operations = {
	'+' : 'ADD',
	'-' : 'SUB',
	'*' : 'MUL',
	'/' : 'DIV'
}

def whilecounter():
	whilecounter.current += 1
	return whilecounter.current

whilecounter.current = 0

#programme
@addToClass(AST.ProgramNode)
def compile(self):
	bytecode = ""
	for c in self.children:
		bytecode += c.compile()
	return bytecode

#node variable
@addToClass(AST.TokenNode)
def compile(self):
	bytecode = ""
	if isinstance(self.tok, str):
		bytecode += "PUSHV %s\n" % self.tok
	else:
		bytecode += "PUSHC %s\n" % self.tok
	return bytecode

@addToClass(AST.AssignNode)
def compile(self):
	bytecode = ""
	bytecode += self.children[1].compile()
	bytecode += "SET %s\n" % self.children[0].tok
	return bytecode
	
#print
@addToClass(AST.LogNode)
def compile(self):
	bytecode = ""
	bytecode += self.children[0].compile()
	bytecode += "PRINT\n"
	return bytecode
	 
#operation
@addToClass(AST.OpNode)
def compile(self):
	bytecode = ""
	if len(self.children) == 1:
		bytecode += self.children[0].compile()
		bytecode += "USUB\n"
	else:
		for c in self.children:
			bytecode += c.compile()
		bytecode += operations[self.op] + "\n"
	return bytecode
	
#while
@addToClass(AST.WhileNode)
def compile(self):
	counter = whilecounter()
	bytecode = ""
	bytecode += "JMP cond%s\n" % counter
	bytecode += "body%s: " % counter
	bytecode += self.children[1].compile()
	bytecode += "cond%s: " % counter
	bytecode += self.children[0].compile()
	bytecode += "JINZ body%s\n" % counter
	return bytecode
	

# #ifNode
# @addToClass(AST.IfNode)
# def compile(self):
# 	return null

# #elseNode
# @addToClass(AST.ElseNode)
# def compile(self):
# 	return null

# #startforNode
# @addToClass(AST.startForNode)
# def compile(self):
# 	return null

# #incForNode
# @addToClass(AST.incForNode)
# def compile(self):
# 	return null

# #logNode
# @addToClass(AST.LogNode)
# def compile(self):
# 	return null

# #arrayNode
# @addToClass(AST.ArrayNode)
# def compile(self):
# 	return null

# #breakNode
# @addToClass(AST.BreakNode)
# def compile(self):
# 	return null

# #continueNode
# @addToClass(AST.ContinueNode)
# def compile(self):
# 	return null

# #variableNode
# @addToClass(AST.VariableNode)
# def compile(self):
# 	return null

# #doNode
# @addToClass(AST.DoNode)
# def compile(self):
# 	return null

# #switchNode
# @addToClass(AST.SwitchNode)
# def compile(self):
# 	return null

# #caseNode
# @addToClass(AST.CaseNode)
# def compile(self):
# 	return null

# #caseListNode
# @addToClass(AST.CaseListNode)
# def compile(self):
# 	return null

# #defaultNode
# @addToClass(AST.DefaultNode)
# def compile(self):
# 	return null

# #andNode
# @addToClass(AST.AndNode)
# def compile(self):
# 	return null

# #orNode
# @addToClass(AST.OrNode)
# def compile(self):
# 	return null

# #notNode
# @addToClass(AST.NotNode)
# def compile(self):
# 	return null

# #conditionNode
# @addToClass(AST.ConditionNode)
# def compile(self):
# 	return null

# #forNode
# @addToClass(AST.ForNode)
# def compile(self):
# 	return null

# #entryNode
# @addToClass(AST.EntryNode)
# def compile(self):
# 	return null


if __name__ == "__main__":
	from parserJS import parse
	import sys,os
	prog = open(sys.argv[1]).read()
	ast = parse(prog)
	compiled = ast.compile()
	name = os.path.splitext(sys.argv[1])[0]+'.vm'
	outfile = open(name,'w')
	outfile.write(compiled)
	outfile.close()
	print("Wrote output to",name)