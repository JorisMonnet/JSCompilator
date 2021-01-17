#!/usr/bin/env python

""" ParserJS : syntaxical and semantical analysis with Ply.yacc
authors: Adrien Paysant & Joris Monnet
Date : 2021
"""
import ply.yacc as yacc
from lex import tokens
import AST
from copy import deepcopy

################################################### SCOPE ############################################################
listScope = []

class Scope():
    """class managing the scopes of the variables and function name"""
    def __init__(self):
        if len(listScope) > 1:
            self.vars = deepcopy(listScope[-1].vars)
            self.functionVars = listScope[-1].functionVars
        elif len(listScope) == 1:
            self.vars = deepcopy(listScope[0].vars)
            self.functionVars = listScope[0].functionVars
        else :
            self.vars = []
            self.functionVars = []
        self.argVars = []

def popscope():
    """go in the parent scope"""
    listScope.pop()

def p_new_scope(p):
    '''new_scope : '''
    listScope.append(Scope())

listScope = [Scope()]
listFunctions = []
error = False

start = '''program'''
####################################################################################################################

############################################ PROGRAMS ############################################################
def p_newline_program(p):
    ''' program : NEWLINE program'''
    p[0] = p[2]

def p_program(p):
    ''' program : statement  ';' NEWLINE
    | statement NEWLINE ''' 
    p[0] = AST.ProgramNode(p[1])

def p_program_recursive(p):
    ''' program : statement ';' program 
    | statement NEWLINE program '''
    p[0] = AST.ProgramNode([p[1]]+p[3].children)

def p_program_block(p):
    ''' programBlock : '{' new_scope program '}' '''
    p[0] = p[3]
    popscope()

def p_newline_program_block(p):
    ''' programBlock : NEWLINE programBlock'''
    p[0] = p[2]

def p_case_program(p):
    '''caseProgram : ':' new_scope program '''
    p[0] = p[3]
    popscope()

def p_program_statement(p):
    '''programStatement : statement'''
    p[0] = AST.ProgramNode([p[1]])

####################################################################################################################

##################################################### STATEMENT ####################################################
def p_newline_statement(p):
    '''statement : NEWLINE statement'''
    p[0] = p[2]

def p_statement(p):
    ''' statement : assignation
    | structure 
    | structureIf
    | structureTernary
    | logStatement
    | breakStatement
    | continueStatement 
    | functionDeclaration
    | functionCall
    | returnStatement
    | varList'''
    p[0] = p[1]
####################################################################################################################

############################################### STRUCTURE ##########################################################
#IF
def p_if(p):
    '''structureIf : IF '(' condition ')' programStatement NEWLINE
    | IF '(' condition ')' programBlock '''
    p[0] = AST.IfNode([p[3],p[5]])

def p_else(p):
    '''structureElse : ELSE programStatement 
    | ELSE programBlock '''
    p[0] = AST.ElseNode([p[2]])

def p_if_else(p):
    '''structure : structureIf structureElse'''
    p[0] = AST.IfNode(p[1].children+[p[2]])

def p_ternary_operator(p):
    '''structureTernary : condition '?' returnValues ':' returnValues ''' #see returnValues in functions -> expression or arrayDeclaration or functionCall
    p[0] = AST.IfNode([p[1],AST.ProgramNode(p[3]),AST.ElseNode(AST.ProgramNode(p[5]))])

#FOR
def p_for(p):
    '''structure : FOR new_scope '(' assignation ';' condition ';' assignation ')' programBlock 
    | FOR new_scope '(' assignation ';' condition ';' assignation ')' programStatement '''
    p[0]=AST.ForNode([AST.StartForNode(p[4]),p[6],AST.IncForNode(p[8]),p[10]])
    popscope()

#WHILE
def p_while(p):
    ''' structure : WHILE '(' condition ')' programStatement 
    | WHILE '(' condition ')' programBlock'''
    p[0] = AST.WhileNode([p[3],p[5]])

def p_do_while(p):
    '''structure : DO programBlock WHILE '(' condition ')' '''
    p[0] = AST.DoNode([p[2],AST.WhileNode([p[5],p[2]])])

def p_do_while_without_bracket(p):
    '''structure : DO programStatement NEWLINE WHILE '(' condition ')'  '''
    p[0] = p[0] = AST.DoNode([p[2],AST.WhileNode([p[6],p[2]])])

#SWITCH
def p_switch(p):
    '''structure : SWITCH '(' IDENTIFIER ')' '{' new_scope caseList '}' '''
    if p[3] in listScope[-1 if len(listScope)>1 else 0].vars:
        p[0] = AST.SwitchNode([AST.TokenNode(p[3])]+p[7])
        popscope()
    else :
        error = True
        print(f"ERROR :{p[3]} is not declared")

def p_switch_void(p):
    ''' structure : SWITCH '(' IDENTIFIER ')' '{' '}' '''
    if p[3] in listScope[-1 if len(listScope)>1 else 0].vars:
        p[0] = AST.SwitchNode([AST.TokenNode(p[3]),AST.TokenNode('Empty switch')])
    else :
        error = True
        print(f"ERROR :{p[3]} is not declared")

def p_newline_case_list(p):
    '''caseList : NEWLINE caseList'''
    p[0] = p[2]

def p_case(p):
    '''caseStructure : CASE expression caseProgram '''
    p[0] = AST.CaseNode([p[2],p[3]])

def p_case_list(p) :
    '''caseList : caseStructure '''
    p[0] = [p[1]]

def p_default(p):
    '''caseStructure : DEFAULT caseProgram '''
    p[0] = AST.DefaultNode([p[2]])

def p_case_list_recursive_newline(p):
    '''caseList : caseList NEWLINE caseStructure '''
    p[0] = p[1]+[p[3]]

def p_case_list_recursive(p):
    '''caseList : caseList caseStructure '''
    p[0] = p[1]+[p[2]]

####################################################################################################################

############################################## CONDITION ###########################################################
def p_conditionSymbol(p):
    '''conditionSymbol : LT
    | GT
    | LTE
    | GTE
    | EQUALV
    | EQUALVT
    | NOTEQUALV
    | NOTEQUALVT
    '''
    p[0]=p[1]

def p_condition_not(p):
    '''condition : '!' condition'''
    p[0] = AST.NotNode([p[2]])

def p_condition_and(p):
    '''condition : condition AND condition'''
    p[0] = AST.AndNode([p[1],p[3]])

def p_condition_or(p):
    '''condition : condition OR condition'''
    p[0] = AST.OrNode([p[1],p[3]])

def p_condition(p):
    '''condition : expression conditionSymbol expression'''
    p[0] = AST.ConditionNode([p[1],AST.TokenNode(p[2]),p[3]])

def p_condtition_paren(p):
    '''condition : '(' condition ')' '''
    p[0]=p[2]

####################################################################################################################

########################################### WORD STATEMENT #########################################################
def p_break(p):
    ''' breakStatement : BREAK '''
    p[0] = AST.BreakNode()

def p_continue(p):
    ''' continueStatement : CONTINUE '''
    p[0] = AST.ContinueNode()

def p_log(p):
    ''' logStatement : LOG '(' returnValues ')' '''
    p[0] = AST.LogNode(p[3])

####################################################################################################################

################################################## VARIABLES #######################################################
def p_var_creation(p):
    '''varCreation : VAR IDENTIFIER
    | LET IDENTIFIER'''
    if p[2] not in listScope[-1 if len(listScope)>1 else 0].vars:
        listScope[-1 if len(listScope)>1 else 0].vars.append(p[2])
        p[0] = AST.VariableNode([AST.TokenNode(p[2])])
    else : 
        error = True
        print(f"ERROR : {p[2]} is already declared")

def p_var_creation_list(p):
    '''varList : varCreation'''
    p[0] = p[1]

def p_var_creation_list_recursive(p): 
    '''varList : varList ',' IDENTIFIER'''
    if p[3] not in listScope[-1 if len(listScope)>1 else 0].vars:
        listScope[-1 if len(listScope)>1 else 0].vars.append(p[3])
        p[0]= AST.VariableNode([AST.TokenNode(p[3])]+p[1].children)
    else : 
        error = True
        print(f"ERROR : {p[3]} is already declared")

#ARRAY
def p_array_empty(p):
    '''arrayDeclaration : '[' ']' '''
    p[0] = AST.ArrayNode(AST.TokenNode('Empty Array'))

def p_array_declaration(p):
    '''arrayDeclaration : '[' tokenList ']' '''
    p[0] = AST.ArrayNode(p[2])

def p_token_list(p): #return a list of TokenNode
    '''tokenList : IDENTIFIER
    | NUMBER '''
    p[0] = [AST.TokenNode(p[1])]

def p_token_list_recursive(p):
    '''tokenList : tokenList ',' IDENTIFIER
    | tokenList ',' NUMBER '''
    p[0] = p[1]+[AST.TokenNode(p[3])]

def p_array_access(p):
    ''' expression : IDENTIFIER '[' NUMBER ']' '''
    if p[1] in listScope[-1 if len(listScope)>1 else 0].vars :
        if int(p[3])==p[3] :
            node = AST.getArrayNodeById(p[1])
            if node :
                if len(node.children[1].children) > int(p[3]):
                    p[0] = AST.TokenNode(p[1]+'['+str(int(p[3]))+']'+'('+node.children[1].children[int(p[3])].tok+')')
                else: 
                    error = True
                    print(f"ERROR : index out of bounds")
            else : 
                error = True
                print(f"ERROR : {p[1]} is not declared as array")
        else : 
            error = True
            print(f"ERROR : {p[1]} must be accessed with a integer number")
    else : 
        error = True
        print(f"ERROR : {p[1]} is not declared")

####################################################################################################################

############################################## EXPRESSIONS #########################################################

def p_expression_num(p):
    '''expression : NUMBER '''
    p[0] = AST.TokenNode(p[1])

def p_expression_var(p):
    '''expression : IDENTIFIER '''        
    if p[1] in listScope[-1 if len(listScope)>1 else 0].vars:
        p[0] = AST.TokenNode(p[1])
    else :
        error = True
        print(f"ERROR : {p[1]} is not declared")

def p_expression_paren(p):
    '''expression : '(' expression ')' '''
    p[0] = p[2]
    
def p_expression_op(p):
    '''expression : expression ADD_OP expression
    | expression MUL_OP expression'''
    p[0] = AST.OpNode(p[2], [p[1], p[3]])

def p_minus(p):
    ''' expression : ADD_OP expression %prec UMINUS'''
    p[0] = AST.OpNode(p[1], [p[2]])

####################################################################################################################

################################################### ASSIGNATION ####################################################

def p_expression_op_assignation(p):
    '''assignation : IDENTIFIER ADD_OP '=' expression
    | IDENTIFIER MUL_OP '=' expression 
    | IDENTIFIER ADD_OP '=' functionCall
    | IDENTIFIER MUL_OP '=' functionCall'''
    if p[1] in listScope[-1 if len(listScope)>1 else 0].vars:
        p[0] = AST.AssignNode([AST.TokenNode(p[1]),AST.OpNode(p[2], [AST.TokenNode(p[1]), p[4]])])
    else : 
        error = True
        print(f"ERROR : {p[1]} is not declared")

def p_expression_op_assign_double(p):
    '''assignation : IDENTIFIER ADD_OP ADD_OP'''
    if p[2]==p[3]:
        if p[1] in listScope[-1 if len(listScope)>1 else 0].vars:
            p[0] = AST.AssignNode([AST.TokenNode(p[1]),AST.OpNode(p[2], [AST.TokenNode(p[1]), AST.TokenNode('1')])])
        else : 
            error = True
            print(f"ERROR : {p[1]} is not declared")
    else:
        error = True
        print (f"ERROR : {p[2]}{p[2]} after variable name : {p[1]}")

def p_assign(p):
    ''' assignation : IDENTIFIER '=' returnValues '''
    if p[1] in listScope[-1 if len(listScope)>1 else 0].vars:
        p[0] = AST.AssignNode([AST.TokenNode(p[1]),p[3]])
    else : 
        error = True
        print(f"ERROR : {p[1]} is not declared")

def p_creation_assignation(p):
    '''assignation : varList '=' returnValues
    | varList '=' structureTernary'''
    p[0] = AST.AssignNode(p[1].children+[p[3]],True)

####################################################################################################################

############################################## FUNCTIONS ###########################################################
def p_function_creation(p):
    '''functionDeclaration : FUNCTION IDENTIFIER '(' new_scope argList ')' programBlock'''
    if p[2] not in listScope[-1 if len(listScope)>1 else 0].functionVars:
        listScope[-1 if len(listScope)>1 else 0].functionVars.append(p[2])
        p[0] = AST.FunctionNode([AST.TokenNode(p[2]),p[5],p[7]])
        popscope()
    else : 
        error = True
        print(f"ERROR : {p[2]} is already a declared function")

def p_function_creation_without_arg(p):
    '''functionDeclaration : FUNCTION IDENTIFIER '(' ')' programBlock'''
    if p[2] not in listScope[-1 if len(listScope)>1 else 0].functionVars:
        listScope[-1 if len(listScope)>1 else 0].functionVars.append(p[2])
        p[0] = AST.FunctionNode([AST.TokenNode(p[2]),AST.ArgNode(AST.TokenNode('No Arguments')),p[5]])
    else : 
        error = True
        print(f"ERROR : {p[2]} is already a declared function")
    
def p_arglist(p):
    '''argList : IDENTIFIER'''
    if p[1] not in listScope[-1 if len(listScope)>1 else 0].vars: #if the var exist already, it will be erased by local variables : https://www.w3schools.com/js/js_scope.asp
        listScope[-1 if len(listScope)>1 else 0].vars.append(p[1])
    listScope[-1 if len(listScope)>1 else 0].argVars.append(p[1])
    p[0] = AST.ArgNode([AST.TokenNode(p[1])])

def p_arglist_recursive(p):
    '''argList : argList ',' IDENTIFIER'''
    if p[3] not in listScope[-1 if len(listScope)>1 else 0].argVars :
        if p[3] not in listScope[-1 if len(listScope)>1 else 0].vars:
            listScope[-1 if len(listScope)>1 else 0].vars.append(p[3])
        listScope[-1 if len(listScope)>1 else 0].argVars.append(p[3])
        p[0] = AST.ArgNode(p[1].children+[AST.TokenNode(p[3])])
    else : 
        error = True
        print(f"ERROR : {p[3]} is already declared")
    
def p_function_call(p):
    '''functionCall : IDENTIFIER '(' expressionList ')' '''
    if p[1] in listScope[-1 if len(listScope)>1 else 0].functionVars:
        functionCallNode = AST.getFunction(p[1])
        if functionCallNode.children[0].verifyArgumentsNumber(len(p[3].children)):
            functionCallNode.children.append(p[3])
            p[0] = functionCallNode
        else :
            error = True
            print(f"ERROR : {p[1]} hasn't {len(p[3].children)} arguments")
    else : 
        error = True
        print(f"ERROR : {p[1]} is not a declared function")

def p_function_call_withous_args(p):
    '''functionCall : IDENTIFIER '(' ')' '''
    if p[1] in listScope[-1 if len(listScope)>1 else 0].functionVars:
        functionCallNode = AST.getFunction(p[1])
        if functionCallNode and functionCallNode.children[0].verifyArgumentsNumber(0):
            p[0] = functionCallNode
        else :
            error = True
            print(f"ERROR : {p[1]} doesn't have this number of arguments") 
    else : 
        error = True
        print(f"ERROR : {p[1]} is not a declared function")

def p_expression_list(p):
    '''expressionList : expression'''
    p[0] = AST.ArgNode([p[1]])

def p_expression_list_recursive(p):
    '''expressionList : expressionList ',' expression '''
    p[0] = AST.ArgNode(p[1].children+[p[3]])

def p_return(p):
    '''returnStatement : RETURN '''
    p[0] = AST.ReturnNode()

def p_return_expression(p):
    '''returnStatement : RETURN returnValues
    | RETURN condition'''
    p[0] = AST.ReturnNode([p[2]])

def p_return_values(p):
    '''returnValues : expression
    | arrayDeclaration
    | functionCall'''
    p[0] = p[1]
####################################################################################################################

#http://www.dabeaz.com/ply/ply.html#ply_nn27
precedence = (
    ('left','NEWLINE','ELSE','OR','IDENTIFIER',',',';'),
    ('nonassoc','LT','GT','EQUALV','EQUALVT','NOTEQUALV','NOTEQUALVT', 'LTE','GTE'),
    ('left','AND'),
    ('left', 'ADD_OP'),
    ('left', 'MUL_OP'),
    ('right', 'UMINUS','!')
)

def p_error(p):
    error = True
    if p:
        print (f"Syntax error in line {p.lineno} with {p}")
        parser.errok()
    else:
        print ("Sytax error: unexpected end of file!")
        
def parse(program):
    """parse the specified program"""
    import re
    program = re.sub(r";+",";",program) # allow multiple ; as in javascript
    # to finish in a structure with a ; , we replace all the occurrences of ;\n with \n  
    result = yacc.parse(program.replace(";\n","\n")+"\n")
    if result and not error : 
        AST.recreateVariableNode()
        isVerified = AST.verifyNode()
        return result,isVerified
    print ("Parsing Error")
    return None,False
                                   
parser = yacc.yacc(outputdir='generated')

if __name__ == "__main__":
    import sys
    prog = open(sys.argv[1]).read()
    result, isVerified = parse(prog) 
    if isVerified:
        print (result)
        graph = result.makegraphicaltree()
        import os
        name = os.path.splitext(sys.argv[1])[0]+'-ast.pdf'
        graph.write_pdf(name)
        print ("wrote ast to", name)
        