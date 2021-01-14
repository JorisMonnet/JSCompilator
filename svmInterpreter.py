import AST
from AST import addToClass

operations = {
	'+' : 'ADD',
	'-' : 'SUB',
	'*' : 'MUL',
	'/' : 'DIV'
}

dicConditions = {
	'<' 	: lambda x,y : int(x < y),
	'>' 	: lambda x,y : int(x > y),
	'<=' 	: lambda x,y : int(x <= y),
	'>=' 	: lambda x,y : int(x >= y),
	'===' 	: lambda x,y : int(x == y and type(y)==type(x)),
	'!==' 	: lambda x,y : int(x != y or type(y)!=type(x)),
	'==' 	: lambda x,y : int(x == y),
	'!=' 	: lambda x,y : int(x != y)
}

def condcounter():
	condcounter.current += 1
	return condcounter.current

condcounter.current = 0

def functioncounter():
	functioncounter.current += 1
	return functioncounter.current

functioncounter.current = 0

#program
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
	
#conditionNode
@addToClass(AST.ConditionNode)
def compile(self):
	bytecode = ""
	bytecode += "cond%s: " % dicConditions[self.children[1].tok](self.children[0].compile,self.children[2].compile)
	return bytecode

#while
@addToClass(AST.WhileNode)
def compile(self):
	counter = condcounter() 
	bytecode = ""
	bytecode += "JMP cond%s\n" % counter 
	bytecode += "body%s: " % counter 
	bytecode += self.children[1].compile() 
	bytecode += "cond%s: " % counter
	bytecode += self.children[0].compile() 
	bytecode += "JINZ body%s\n" % counter 
	return bytecode

#functionNode
@addToClass(AST.FunctionNode)
def compile(self):
	fcounter = functioncounter()
	bytecode = ""
	bytecode += "func%s: \n" % fcounter
	bytecode += self.children[1].compile()
	bytecode += self.children[2].compile()	
	bytecode += "JINZ func%s\n" % fcounter
	return bytecode

#returnNode
@addToClass(AST.ReturnNode)
def compile(self):
	bytecode=""
	bytecode+=(self.children[0].compile())
	return bytecode

#argNode
@addToClass(AST.ArgNode)
def compile(self):
	bytecode = ""
	if( isinstance(self.children[0].tok, str) and self.children[0].tok != "No Arguments"):
		bytecode += "PUSHV %s\n" % self.children[0].tok
	return bytecode

"""
#ifNode
@addToClass(AST.IfNode)
def compile(self):
	bytecode = ""
	bytecode += self.children[0].compile(condcounter())
	bytecode += self.children[1].compile()
	return bytecode
"""
if __name__ == "__main__":
	from parserJS import parse
	import sys
	prog = open(sys.argv[1]).read()
	ast, isVerified = parse(prog)
	if isVerified:
		compiled = ast.compile()
		import os
		name = os.path.splitext(sys.argv[1])[0]+'.vm'
		outfile = open(name,'w')
		outfile.write(compiled)
		outfile.close()
		print("Wrote output to",name)