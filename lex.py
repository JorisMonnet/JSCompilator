import ply.lex as lex

reserved_words = (
    'for',
    'while',
    'log',
    'var',
    'let',
    'do',
    'if',
    'else',
    'switch',
    'case',
    'default'
)

conditions_symbols = (
    'LT','GT','LTE','GTE','EQUALV','EQUALVT','NOTEQUALV','NOTEQUALVT','OR','AND'
)

t_LT = r'<'
t_GT = r'>'
t_LTE = r'<='
t_GTE = r'>='
t_EQUALVT = r'==='
t_NOTEQUALVT = r'!==' 
t_EQUALV = r'==' 
t_NOTEQUALV = r'!='
t_NEWLINE = r'\n'
t_AND=r'&&'
t_OR=r'\|\|'

tokens = (
    'NUMBER',
    'ADD_OP',
    'MUL_OP',
    'IDENTIFIER',
    'NEWLINE',
) + tuple(map(lambda s:s.upper(),reserved_words)) + conditions_symbols

literals = '();={}?&|:!,'

def t_ADD_OP(t):
    r'[+-]'
    return t

def t_MUL_OP(t):
    r'[*/]'
    return t

def t_NUMBER(t):
    r'\d+(\.\d+)?'
    try:
        t.value = float(t.value)
    except ValueError:
        print ("Line %d: Problem while parsing %s!" %(t.lineno,t.value))
        t.value = 0
    return t

def t_IDENTIFIER(t):
    r'[A-Za-z_]\w*'
    if t.value in reserved_words:
        t.type = t.value.upper()
    return t

def t_NEWLINE(t):
    r'\n'
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

t_ignore = ' \t'

def t_error(t):
    print ("Illegal character '%s'" % repr(t.value[0]))
    t.lexer.skip(1)

lex.lex()

if __name__ == "__main__":
    import sys
    prog = open(sys.argv[1]).read()
    lex.input(prog)
    while 1:
        tok = lex.token()
        if not tok: break
        print ("line %d: %s(%s)" % (tok.lineno, tok.type, tok.value))
