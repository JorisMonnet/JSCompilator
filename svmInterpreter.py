import AST
from AST import addToClass

operations = {
	'+' : 'ADD',
	'-' : 'SUB',
	'*' : 'MUL',
	'/' : 'DIV'
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

####################################################################################################################

###################################################### FUNCTION ####################################################

@addToClass(AST.FunctionNode)
def compile(self):
	fcounter = functioncounter()
	bytecode = ""
	bytecode += "func%s: \n" % fcounter
	bytecode += self.children[1].compile()
	bytecode += self.children[2].compile()	
	bytecode += "JINZ func%s\n" % fcounter
	return bytecode

@addToClass(AST.ReturnNode)
def compile(self):
	bytecode=""
	bytecode+=(self.children[0].compile())
	return bytecode

@addToClass(AST.ArgNode)
def compile(self):
	bytecode = ""
	if( isinstance(self.children[0].tok, str) and self.children[0].tok != "No Arguments"):
		bytecode += "PUSHV %s\n" % self.children[0].tok
	return bytecode

@addToClass(AST.FunctionCallNode)
def compile(self):
	bytecode = ""
	return bytecode

####################################################################################################################

################################################# OPERATIONS #######################################################

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

@addToClass(AST.AssignNode)
def compile(self):
	bytecode = ""
	bytecode += self.children[1].compile()
	bytecode += "SET %s\n" % self.children[0].tok
	return bytecode

@addToClass(AST.VariableNode)
def compile(self):
	bytecode = ""
	return bytecode

@addToClass(AST.ArrayNode)
def compile(self):
	bytecode = ""
	bytecode += "PUSHV %s\n" % self.children[0].compile
	return bytecode

####################################################################################################################

################################################# STRUCTURE ########################################################


@addToClass(AST.IfNode)
def compile(self):
	if int(self.children[0].compile()[-2]):
		ifIsTrue = True
		return self.children[1].compile()
	if len(self.children) > 2 :
		return self.children[2].compile()

@addToClass(AST.ElseNode)
def compile(self):
	return  self.children[0].compile()

@addToClass(AST.ForNode)
def compile(self):
	bytecode = ""
	bytecode += self.children[0].compile
	bytecode += self.children[1].compile
	bytecode += self.children[2].compile
	bytecode += self.children[3].compile
	return bytecode

@addToClass(AST.StartForNode)
def compile(self):
	return self.children[0].compile()

@addToClass(AST.IncForNode)
def compile(self):
	return self.children[0].compile()

@addToClass(AST.WhileNode)
def compile(self):
	counter = condcounter() 
	bytecode = "JMP cond%s\n" % counter 
	bytecode += "body%s: " % counter 
	bytecode += self.children[1].compile() 
	bytecode += "cond%s: " % counter
	bytecode += self.children[0].compile() 
	bytecode += "JINZ body%s\n" % counter 
	return bytecode

@addToClass(AST.DoNode)
def compile(self):
	return self.children[0].compile() + self.children[1].compile()

@addToClass(AST.SwitchNode)
def compile(self):
	for children in self.children[1:]:
		if children.type !='Default' and children.children[0] == self.children[0]:
			return children.compile()
	for children in self.children[1:]:
		if children.type =='Default':
			return children.compile()
	return ""

@addToClass(AST.CaseNode)
def compile(self):
	return self.children[1].compile()

@addToClass(AST.DefaultNode)
def compile(self):
	return self.children[0].compile()

####################################################################################################################

################################################# STATEMENT ########################################################

@addToClass(AST.LogNode)
def compile(self):
	bytecode = ""
	bytecode += self.children[0].compile()
	bytecode += "PRINT\n"
	return bytecode

@addToClass(AST.BreakNode)
def compile(self):
	bytecode = ""
	return bytecode

@addToClass(AST.ContinueNode)
def compile(self):
	bytecode = ""
	return bytecode

####################################################################################################################

############################################ CONDITIONS ############################################################

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

@addToClass(AST.ConditionNode)
def compile(self):
	return "PUSHC " + str(dicConditions[self.children[1].tok](int(self.children[0].tok),int(self.children[2].tok)))+"\n"

@addToClass(AST.AndNode)
def compile(self):
	children1Code = int(self.children[0].compile()[-2]) #get 0 or 1
	children2Code = int(self.children[1].compile()[-2])
	return "PUSHC " + str(int(children1Code and children2Code)) + "\n"

@addToClass(AST.OrNode)
def compile(self):
	children1Code = int(self.children[0].compile()[-2])
	children2Code = int(self.children[1].compile()[-2])
	return "PUSHC " + str(int(children1Code or children2Code)) + "\n"

@addToClass(AST.NotNode)
def compile(self):
	return "PUSHC " + str(int(not int(self.children[0].compile()[-2]) ))+"\n"

####################################################################################################################

####################################################################################################################

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