import AST,re
from AST import addToClass

operations = {
	'+' : 'ADD',
	'-' : 'SUB',
	'*' : 'MUL',
	'/' : 'DIV'
}

operationsLambda = {
	'ADD' : lambda x,y: x+y,
	'SUB' : lambda x,y: x-y,
	'MUL' : lambda x,y: x*y,
	'DIV' : lambda x,y: x/y 
}

varValues = {} # varName : Value -> scope managed in parser

def condcounter():
	condcounter.current += 1
	return condcounter.current

condcounter.current = 0

def functioncounter():
	functioncounter.current += 1
	return functioncounter.current

functioncounter.current = 0

def isFloat(nbToCheck):
	try:
		float(nbToCheck)
	except ValueError:
		return False
	return True

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
	bytecode = "func%s: \n" % fcounter
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
	compiledChildren = self.children[1].compile()
	search = re.search("\d+",compiledChildren)
	if search:
		if self.children[1].__class__.__name__!="OpNode": 
			varValues[self.children[0].tok] = float(search.group(0))
		else:
			searchOperation = 	'ADD' if compiledChildren.find('ADD') else \
								'MUL' if compiledChildren.find('MUL') else \
								'DIV' if compiledChildren.find('DIV') else \
								'SUB' if compiledChildren.find('SUB') else ""
			try:
				varValues[self.children[0].tok] = operationsLambda[searchOperation](float(search.group(0)),float(search.group(1)))
			except IndexError:
				varValues[self.children[0].tok] = -float(search.group(0))
	else:
		raise Exception("Error on assignation")

	bytecode = compiledChildren
	bytecode += "SET %s\n" % self.children[0].tok
	return bytecode

@addToClass(AST.VariableNode)
def compile(self):
	return "" 

@addToClass(AST.ArrayNode)
def compile(self):
	return ""

####################################################################################################################

################################################# STRUCTURE ########################################################


@addToClass(AST.IfNode)
def compile(self):
	if int(self.children[0].compile()[-2]):
		return self.children[1].compile()
	if len(self.children) > 2 :
		return self.children[2].compile()
	return ""

@addToClass(AST.ElseNode)
def compile(self):
	return self.children[0].compile()

@addToClass(AST.ForNode)
def compile(self):
	counter = condcounter() 
	bytecode = self.children[0].compile()
	bytecode += "JMP cond%s\n" % counter 
	bytecode += "body%s: " % counter 
	bytecode += self.children[2].compile()
	bytecode += self.children[3].compile() 
	bytecode += "cond%s: " % counter
	bytecode += self.children[1].compile() 
	bytecode += "JINZ body%s\n" % counter 
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
	if len(self.children)==2 and self.children[1].type=='Token':return "" #void switch
	for children in self.children[1:]:
		print(varValues)
		if children.type !='Default' and float(children.children[0].tok) == varValues[self.children[0].tok]:
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
	return "BREAK\n"

@addToClass(AST.ContinueNode)
def compile(self):
	return f"JMP cond{condcounter()-1}\n"

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
	firstValue 	= None
	
	if hasattr(self.children[0],'tok') and isFloat(self.children[0].tok):
		firstValue 	= self.children[0].tok 
	elif hasattr(self.children[0],'tok') :
		firstValue = varValues[self.children[0].tok]
	else :
		firstValue = self.children[0].compile()
	
	secondValue = None

	if hasattr(self.children[2],'tok') and isFloat(self.children[2].tok):
		secondValue = self.children[2].tok 
	elif hasattr(self.children[2],'tok') :
		secondValue = varValues[self.children[2].tok]
	else :
		compiledChildren = self.children[2].compile()
		search = re.search('\d+',compiledChildren)

		searchOperation = 'ADD' if compiledChildren.find('ADD') else \
						'MUL' if compiledChildren.find('MUL') else \
						'DIV' if compiledChildren.find('DIV') else \
						'SUB' if compiledChildren.find('SUB') else ""
		if search :
			try:
				secondValue = operationsLambda[searchOperation](float(search.group(0)),float(search.group(1)))
			except IndexError:
				secondValue = -float(search.group(0))
		else :
			pass #arrayValue
	return "PUSHC " + str(dicConditions[self.children[1].tok](int(firstValue),int(secondValue)))+"\n"

@addToClass(AST.AndNode)
def compile(self):
	children1Code = int(self.children[0].compile()[-2]) 	#get 0 or 1		[-1]="\n"
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