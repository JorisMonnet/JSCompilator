import ply.yacc as yacc
from lex import tokens
import AST

vars = {}

def p_programme_statement(p):
    ''' programme : statement '''
    p[0] = AST.ProgramNode(p[1])

def p_programme_recursive(p):
    ''' programme : statement ';' programme '''
    p[0] = AST.ProgramNode([p[1]]+p[3].children)

def p_statement(p):
    ''' statement : assignation
    | structure '''
    p[0] = p[1]

def p_for(p):
    '''structure : FOR '(' assignation ';' expression ';' assignation ')' '{' programme '}' '''
    p[0]=AST.ForNode([p[3],p[5],p[7],p[10]])

def p_do_while(p):
    '''structure : DO '{' programme '}' WHILE '(' expression ')' '''
    p[0] = AST.DoNode([p[3],AST.WhileNode([p[7],p[3]])])

def p_statement_log(p):
    ''' statement : LOG expression '''
    p[0] = AST.LogNode(p[2])

def p_structure_while(p):
    ''' structure : WHILE '(' expression ')' '{' programme '}' '''
    p[0] = AST.WhileNode([p[3],p[6]])
    
def p_expression_op(p):
    '''expression : expression ADD_OP expression
    | expression MUL_OP expression'''
    p[0] = AST.OpNode(p[2], [p[1], p[3]])

def p_expression_op_assignation(p):
    '''statement : IDENTIFIER ADD_OP '=' expression
    | IDENTIFIER MUL_OP '=' expression'''
    p[0] = AST.AssignNode([AST.TokenNode(p[1]),AST.OpNode(p[2], [AST.TokenNode(p[1]), p[4]])])
def p_expression_op_assign_double(p):
    '''statement : IDENTIFIER ADD_OP ADD_OP'''
    if p[2]==p[3]:
        p[0] = AST.AssignNode([AST.TokenNode(p[1]),AST.OpNode(p[2], [AST.TokenNode(p[1]), AST.TokenNode('1')])])
    else:
        print (f"Syntax error : +- or -+ after variable name : {p[1]}")

def p_expression_num_or_var(p):
    '''expression : NUMBER
    | IDENTIFIER '''
    p[0] = AST.TokenNode(p[1])

def p_expression_paren(p):
    '''expression : '(' expression ')' '''
    p[0] = p[2]

def p_minus(p):
    ''' expression : ADD_OP expression %prec UMINUS'''
    p[0] = AST.OpNode(p[1], [p[2]])

def p_assign(p):
    ''' assignation : IDENTIFIER '=' expression '''
    p[0] = AST.AssignNode([AST.TokenNode(p[1]),p[3]])

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
        print (result)
        import os
        graph = result.makegraphicaltree()
        name = os.path.splitext(sys.argv[1])[0]+'-ast.pdf'
        graph.write_pdf(name)
        print ("wrote ast to", name)
    else:
        print ("Parsing returned no result!")