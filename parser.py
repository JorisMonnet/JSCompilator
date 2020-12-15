import ply.yacc as yacc
from lex import tokens
import AST

vars = []
def p_programme_statement(p):
    ''' programme : statement '''
    p[0] = AST.ProgramNode(p[1])

def p_programme_recursive(p):
    ''' programme : statement ';' programme '''
    p[0] = AST.ProgramNode([p[1]]+p[3].children)

def p_statement(p):
    ''' statement : assignation
    | structure 
    | structureIf
    | structureIfElse
    | varList'''
    p[0] = p[1]

def p_ternary_operator(p):
    '''structure : condition '?' expression ':' expression'''
    p[0] = AST.IfNode([p[1],AST.ProgramNode(p[3]),AST.ElseNode(AST.ProgramNode(p[5]))])

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

def p_if_alone(p):
    '''structureIf : IF '(' condition ')' '{' programme '}' '''
    p[0] = AST.IfNode([p[3],p[6]])

def p_if_else(p):
    '''structureIfElse : structureIf ELSE '{' programme '}' '''
    p[0] = AST.IfNode([AST.ElseNode(p[4])]+p[1].children)

def p_if_elseif(p): 
    '''structure : structureIf ELSE structureIf
    | structureIf ELSE structureIfElse'''
    p[0] = AST.IfNode([AST.ElseNode(p[3])]+p[1].children)

def p_for(p):
    '''structure : FOR '(' assignation ';' condition ';' assignation ')' '{' programme '}' '''
    p[0]=AST.ForNode([p[3],p[5],p[7],p[10]])

def p_switch(p):
    '''structure : SWITCH '(' IDENTIFIER ')' '{' caseStructureList '}' '''
    if p[3] in vars:
        p[0] = AST.SwitchNode([AST.TokenNode(p[3]),p[6]])
    else :
        print(f"{p[3]} is not declared")

def p_case(p):
    '''caseStructure : CASE expression ':' programme '''
    p[0] = AST.CaseNode([p[2],p[4]])

def p_case_list_alone(p) :
    '''caseStructureList : caseStructure'''
    p[0] = p[1]

def p_default(p):
    '''caseStructure : DEFAULT ':' programme'''
    p[0] = AST.DefaultNode([p[3]])

def p_case_List(p):
    '''caseStructureList : caseStructure caseStructureList'''
    p[0] =  p[1]

def p_do_while(p):
    '''structure : DO '{' programme '}' WHILE '(' condition ')' '''
    p[0] = AST.DoNode([p[3],AST.WhileNode([p[7],p[3]])])

def p_statement_log(p):
    ''' statement : LOG expression '''
    p[0] = AST.LogNode(p[2])

def p_creation(p):
    '''varCreation : VAR IDENTIFIER
    | LET IDENTIFIER'''
    vars.append(p[2])
    p[0] = AST.VariableNode([AST.TokenNode(p[2])])

def p_creation_list(p): 
    '''varList : varCreation ',' IDENTIFIER
    |  varList ',' IDENTIFIER'''
    vars.append(p[3])
    p[0]= AST.VariableNode([AST.TokenNode(p[3])]+p[1].children)

def p_creation_list_alone(p):
    '''varList : varCreation'''
    p[0] = p[1]
    
def p_creation_assignation(p):
    '''statement : varList '=' expression'''
    p[0] = AST.AssignNode(p[1].children+[p[3]],True)

def p_structure_while(p):
    ''' structure : WHILE '(' condition ')' '{' programme '}' '''
    p[0] = AST.WhileNode([p[3],p[6]])

def p_expression_op(p):
    '''expression : expression ADD_OP expression
    | expression MUL_OP expression'''
    p[0] = AST.OpNode(p[2], [p[1], p[3]])

def p_expression_op_assignation(p):
    '''statement : IDENTIFIER ADD_OP '=' expression
    | IDENTIFIER MUL_OP '=' expression'''
    if p[1] in vars:
        p[0] = AST.AssignNode([AST.TokenNode(p[1]),AST.OpNode(p[2], [AST.TokenNode(p[1]), p[4]])])
    else : 
        print(f"{p[1]} is not declared")

def p_expression_op_assign_double(p):
    '''statement : IDENTIFIER ADD_OP ADD_OP'''
    if p[2]==p[3]:
        if p[1] in vars:
            p[0] = AST.AssignNode([AST.TokenNode(p[1]),AST.OpNode(p[2], [AST.TokenNode(p[1]), AST.TokenNode('1')])])
        else : 
            print(f"{p[1]} is not declared")
    else:
        print (f"Syntax error : +- or -+ after variable name : {p[1]}")

def p_expression_num(p):
    '''expression : NUMBER '''
    p[0] = AST.TokenNode(p[1])

def p_expression_var(p):
    '''expression : IDENTIFIER '''
    if p[1] in vars:
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
    if(p[1] in vars) : 
        p[0] = AST.AssignNode([AST.TokenNode(p[1]),p[3]])
    else : 
        print(f"{p[1]} is not declared")

def p_error(p):
    if p:
        print (f"Syntax error in line {p.lineno}")
        parser.errok()
    else:
        print ("Sytax error: unexpected end of file!")

precedence = (
    ('left', 'ADD_OP'),
    ('left', 'MUL_OP'),
    ('right', 'UMINUS'),
)

def parse(program):
    return yacc.parse(program)

parser = yacc.yacc(outputdir='generated')

if __name__ == "__main__":
    import sys

    prog = open(sys.argv[1]).read()
    result = yacc.parse(prog)
    if result:
        AST.recreateVariableNode()
        print (result)
        import os
        graph = result.makegraphicaltree()
        name = os.path.splitext(sys.argv[1])[0]+'-ast.pdf'
        graph.write_pdf(name)
        print ("wrote ast to", name)
    else:
        print ("Parsing returned no result!")