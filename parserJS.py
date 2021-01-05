import ply.yacc as yacc
from lex import tokens
import AST

listScope = []

class Scope():
    def __init__(self):
        if len(listScope) > 1:
            self.vars = listScope[-1].vars
            self.functionVars = listScope[-1].functionVars
        elif len(listScope) == 1:
            self.vars = listScope[0].vars
            self.functionVars = listScope[0].functionVars
        else :
            self.vars = []
            self.functionVars = []

listScope = [Scope()]
listFunctions = []
error = False

def popscope():
    listScope.pop()

def p_beginning_of_program(p):
    ''' programme : NEWLINE programme'''
    p[0] = p[2]

def p_program_block(p):
    ''' programmeBlock : '{' new_scope programme '}' '''
    p[0] = p[3]
    popscope()

def p_program_block_indent(p):
    ''' programmeBlock : NEWLINE programmeBlock'''
    p[0] = p[2]

def p_program_case_block(p):
    '''caseProgramme : ':' new_scope programme '''
    p[0] = p[3]
    popscope()

def p_programme_statement_alone(p):
    '''programmeStatement : assignation
    | structure 
    | logStatement
    | breakStatement 
    | continueStatement 
    | arrayDeclaration
    | functionCall'''
    p[0] = AST.ProgramNode([p[1]])

def p_newline_programmeStatement(p):
    '''programmeStatement : NEWLINE programmeStatement'''
    p[0] = p[2]

def p_programme_statement(p):
    ''' programme : statement  ';' 
    | statement NEWLINE ''' 
    p[0] = AST.ProgramNode(p[1])

def p_programme_recursive(p):
    ''' programme : statement ';' programme 
    | statement NEWLINE programme '''
    p[0] = AST.ProgramNode([p[1]]+p[3].children)

def p_newline_statement(p):
    '''statement : NEWLINE statement'''
    p[0] = p[2]

def p_statement(p):
    ''' statement : assignation
    | structure 
    | structureIf
    | logStatement
    | breakStatement
    | continueStatement 
    | arrayDeclaration
    | functionDeclaration
    | functionCall'''
    p[0] = p[1]

def p_ternary_operator(p):
    '''structure : condition '?' expression ':' expression'''
    p[0] = AST.IfNode([p[1],AST.ProgramNode(p[3]),AST.ElseNode(AST.ProgramNode(p[5]))])

def p_newscope(p):
    '''new_scope : '''
    listScope.append(Scope())

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

def p_if(p):
    '''structureIf : IF '(' condition ')' programmeStatement NEWLINE
    | IF '(' condition ')' programmeBlock '''
    p[0] = AST.IfNode([p[3],p[5]])

def p_else(p):
    '''structureElse : ELSE programmeStatement 
    | ELSE structureIf
    | ELSE programmeBlock '''
    p[0] = AST.ElseNode([p[2]])
    
def p_if_else(p):
    '''structure : structureIf structureElse '''
    p[0] = AST.IfNode(p[1].children+[p[2]])
    
def p_for(p):
    '''structure : FOR '(' assignation ';' condition ';' assignation ')' programmeBlock 
    | FOR '(' assignation ';' condition ';' assignation ')' programmeStatement '''
    p[0]=AST.ForNode([AST.startForNode(p[3]),p[5],AST.incForNode(p[7]),p[9]])

def p_break(p):
    ''' breakStatement : BREAK '''
    p[0] = AST.BreakNode()

def p_continue(p):
    ''' continueStatement : CONTINUE '''
    p[0] = AST.ContinueNode()

def p_switch(p):
    '''structure : SWITCH '(' IDENTIFIER ')' '{' new_scope caseStructureList '}' '''
    if (len(listScope) > 1 and p[3] in listScope[-1].vars) or (len(listScope) == 1 and p[3] in listScope[0].vars):
        p[0] = AST.SwitchNode([AST.TokenNode(p[3]),p[7]])
        popscope()
    else :
        print(f"{p[3]} is not declared")

def p_newline_case(p):
    '''caseStructureList : NEWLINE caseStructureList'''
    p[0] = p[2]

def p_case(p):
    '''caseStructure : CASE expression caseProgramme '''
    p[0] = AST.CaseNode([p[2],p[3]])

def p_case_list_alone(p) :
    '''caseStructureList : caseStructure '''
    p[0] = p[1]

def p_default(p):
    '''defaultStructure : DEFAULT caseProgramme '''
    p[0] = AST.DefaultNode([p[2]])

def p_case_List(p):
    '''caseStructureList : caseStructureList caseStructure
    | caseStructureList defaultStructure '''
    if p[1].type !='case':
        p[0] = AST.CaseListNode(p[1].children+[p[2]])
    else :
        p[0] = AST.CaseListNode([p[1],p[2]])

def p_do_while(p):
    '''structure : DO programmeBlock WHILE '(' condition ')' 
    | DO programmeStatement WHILE '(' condition ')' '''
    p[0] = AST.DoNode([p[2],AST.WhileNode([p[5],p[2]])])

def p_log(p):
    ''' logStatement : LOG expression '''
    p[0] = AST.LogNode(p[2])

def p_creation(p):
    '''varCreation : VAR IDENTIFIER
    | LET IDENTIFIER'''
    if p[2] not in listScope[-1 if len(listScope)>1 else 0].vars:
        listScope[-1 if len(listScope)>1 else 0].vars.append(p[2])
        p[0] = AST.VariableNode([AST.TokenNode(p[2])])
    else : 
        print(f"ERROR : {p[2]} is already declared")

def p_array_empty(p):
    '''arrayDeclaration : '[' ']' '''
    p[0] = AST.ArrayNode(AST.TokenNode('Empty Array'))

def p_array_creation(p):
    '''arrayDeclaration : '[' tokenList ']' '''
    p[0] = AST.ArrayNode(p[2])

def p_array_access(p):
    ''' expression : IDENTIFIER '[' NUMBER ']' '''
    if p[1] in listScope[-1 if len(listScope)>1 else 0].vars and int(p[3])==p[3]:
        node = AST.getArrayNodeById(p[1])
        if node :
            if len(node.children) + 1 >= int(p[3]):
                p[0] = AST.TokenNode(p[1]+'['+str(int(p[3]))+']'+'('+node.children[1].children[int(p[3])].tok+')')
            else: 
                print(f"index out of bounds")
        else : 
            print(f"{p[1]} is not declared as array")
    else : 
        print(f"{p[1]} is not declared")

#return a list
def p_token_list_solo(p):
    '''tokenList : IDENTIFIER
    | NUMBER '''
    p[0] = [AST.TokenNode(p[1])]

def p_token_list(p):
    '''tokenList : tokenList ',' IDENTIFIER
    | tokenList ',' NUMBER '''
    p[0] = [AST.TokenNode(p[3])]+p[1]

def p_creation_list(p): 
    '''varList : varList ',' IDENTIFIER'''
    if p[3] not in listScope[-1 if len(listScope)>1 else 0].vars:
        listScope[-1 if len(listScope)>1 else 0].vars.append(p[3])
        p[0]= AST.VariableNode([AST.TokenNode(p[3])]+p[1].children)
    else : 
        print(f"ERROR : {p[3]} is already declared")

def p_creation_list_alone(p):
    '''varList : varCreation'''
    p[0] = p[1]
    
def p_creation_assignation(p):
    '''assignation : varList '=' expression
    | varList '=' arrayDeclaration '''
    p[0] = AST.AssignNode(p[1].children+[p[3]],True)

def p_structure_while_without_bracket(p):
    ''' structure : WHILE '(' condition ')' programmeStatement 
    | WHILE '(' condition ')' programmeBlock'''
    p[0] = AST.WhileNode([p[3],p[5]])

def p_expression_op(p):
    '''expression : expression ADD_OP expression
    | expression MUL_OP expression'''
    p[0] = AST.OpNode(p[2], [p[1], p[3]])

def p_expression_op_assignation(p):
    '''assignation : IDENTIFIER ADD_OP '=' expression
    | IDENTIFIER MUL_OP '=' expression '''
    if (len(listScope) > 1 and p[1] in listScope[-1].vars) or (len(listScope) == 1 and p[1] in listScope[0].vars):
        p[0] = AST.AssignNode([AST.TokenNode(p[1]),AST.OpNode(p[2], [AST.TokenNode(p[1]), p[4]])])
    else : 
        print(f"ERROR : {p[1]} is not declared")

def p_expression_op_assign_double(p):
    '''assignation : IDENTIFIER ADD_OP ADD_OP'''
    if p[2]==p[3]:
        if (len(listScope) > 1 and p[1] in listScope[-1].vars) or (len(listScope) == 1 and p[1] in listScope[0].vars):
            p[0] = AST.AssignNode([AST.TokenNode(p[1]),AST.OpNode(p[2], [AST.TokenNode(p[1]), AST.TokenNode('1')])])
        else : 
            print(f"{p[1]} is not declared")
    else:
        print (f"ERROR : {p[2]}{p[2]} after variable name : {p[1]}")

def p_expression_num(p):
    '''expression : NUMBER '''
    p[0] = AST.TokenNode(p[1])

def p_expression_var(p):
    '''expression : IDENTIFIER '''        
    if (len(listScope) > 1 and p[1] in listScope[-1].vars) or (len(listScope) == 1 and p[1] in listScope[0].vars):
        p[0] = AST.TokenNode(p[1])
    else :
        print(f"{p[1]} is not declared")

def p_expression_paren(p):
    '''expression : '(' expression ')' '''
    p[0] = p[2]

def p_condtition_paren(p):
    '''condition : '(' condition ')' '''
    p[0]=p[2]

def p_minus(p):
    ''' expression : ADD_OP expression %prec UMINUS'''
    p[0] = AST.OpNode(p[1], [p[2]])

def p_assign(p):
    ''' assignation : IDENTIFIER '=' expression '''
    if (len(listScope) > 1 and p[1] in listScope[-1].vars) or (len(listScope) == 1 and p[1] in listScope[0].vars):
        p[0] = AST.AssignNode([AST.TokenNode(p[1]),p[3]])
    else : 
        print(f"ERROR : {p[1]} is not declared")

def p_error(p):
    error = True
    if p:
        print (f"Syntax error in line {p.lineno} with {p}")
        parser.errok()
    else:
        print ("Sytax error: unexpected end of file!")

def p_function_creation(p):
    '''functionDeclaration : FUNCTION IDENTIFIER '(' new_scope argList ')' programmeBlock'''
    if p[2] not in listScope[-1 if len(listScope)>1 else 0].functionVars:
        listScope[-1 if len(listScope)>1 else 0].functionVars.append(p[2])
        p[0] = AST.FunctionNode([AST.TokenNode(p[2]),p[5],p[7]])
    else : 
        print(f"ERROR : {p[2]} is already a declared function")

def p_function_creation_without_arg(p):
    '''functionDeclaration : FUNCTION IDENTIFIER '(' ')' programmeBlock'''
    if p[2] not in listScope[-1 if len(listScope)>1 else 0].functionVars:
        listScope[-1 if len(listScope)>1 else 0].functionVars.append(p[2])
        p[0] = AST.FunctionNode([AST.TokenNode(p[2]),AST.ArgNode(AST.TokenNode('No Arguments')),p[5]])
    else : 
        print(f"ERROR : {p[2]} is already a declared function")
    
def p_arglist(p):
    '''argList : IDENTIFIER'''
    if p[1] not in listScope[-1 if len(listScope)>1 else 0].vars:
        listScope[-1 if len(listScope)>1 else 0].vars.append(p[1])
        p[0] = AST.ArgNode([AST.TokenNode(p[1])])
    else : 
        print(f"ERROR : {p[1]} is already declared")

def p_arglist_multiple(p):
    '''argList : argList ',' IDENTIFIER'''
    if p[3] not in listScope[-1 if len(listScope)>1 else 0].vars:
        listScope[-1 if len(listScope)>1 else 0].vars.append(p[3])
        p[0] = AST.ArgNode(p[1].children+[AST.TokenNode(p[3])])
    else : 
        print(f"ERROR : {p[3]} is already declared")
    
def p_function_call(p):
    '''functionCall : IDENTIFIER '(' ')' '''
    if p[1] in listScope[-1 if len(listScope)>1 else 0].functionVars:
        functionCallNode = AST.getFunction(p[1])
        if functionCallNode and functionCallNode.children[0].verifyArgumentsNumber(0):
            p[0] = functionCallNode
        else :
           print(f"ERROR : {p[1]} doesn't have this number of arguments") 
    else : 
        print(f"ERROR : {p[1]} is not declared")

def p_function_call_args(p):
    '''functionCall : IDENTIFIER '(' expressionList ')' '''
    if p[1] in listScope[-1 if len(listScope)>1 else 0].functionVars:
        functionCallNode = AST.getFunction(p[1])
        if functionCallNode.children[0].verifyArgumentsNumber(len(p[3].children)):
            functionCallNode.children.append(p[3])
            p[0] = functionCallNode
        else :
            print(f"ERROR : {p[1]} hasn't {len(p[3].children)} arguments")
    else : 
        print(f"ERROR : {p[1]} is not declared")

def p_expression_list_solo(p):
    '''expressionList : expression'''
    p[0] = AST.ArgNode([p[1]])

def p_expression_list(p):
    '''expressionList : expressionList ',' expression '''
    p[0] = AST.ArgNode(p[1].children+[p[3]])

#http://www.dabeaz.com/ply/ply.html#ply_nn27
precedence = (
    ('left','ELSE','NEWLINE','AND','OR','IDENTIFIER', '!',','),
    ('nonassoc','LT','GT','EQUALV','EQUALVT','NOTEQUALV','NOTEQUALVT', 'LTE','GTE'),
    ('left', 'ADD_OP'),
    ('left', 'MUL_OP'),
    ('right', 'UMINUS')
)

def parse(program):
    if program[-1]==';': #allow to finish with a ;
        program=program[:-1]
    return yacc.parse(program+"\n")

parser = yacc.yacc(outputdir='generated')

if __name__ == "__main__":
    import sys
    prog = open(sys.argv[1]).read()
    result = parse(prog) 
    if result and not error:
        AST.recreateVariableNode()
        print (result)
        import os
        graph = result.makegraphicaltree()
        name = os.path.splitext(sys.argv[1])[0]+'-ast.pdf'
        graph.write_pdf(name)
        print ("wrote ast to", name)
    else:
        print ("Parsing returned no result!")