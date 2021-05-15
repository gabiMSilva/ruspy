# ref: https://doc.rust-lang.org/stable/reference/tokens.html#literals
from ast import parse
import math
from typing import Any
from lark import Lark, InlineTransformer, LarkError

grammar = Lark(
    r"""
start  : seq

?seq   : cmd (";" cmd)*

?cmd   : expr
       | assign

assign : ID "=" expr 

?expr  : rng_

?rng_  :  rng_ ".." orcmp   -> range
       |  rng_ "..=" orcmp  -> rangei
       | orcmp

?orcmp : orcmp "||" andcmp   -> or_
       | andcmp

?andcmp : andcmp "&&" cmp -> and_
       | cmp

?cmp   : or_ ">" or_  -> gt
       | or_ ">=" or_ -> ge
       | or_ "<" or_  -> lt
       | or_ "<=" or_ -> le
       | or_ "==" or_ -> eq
       | or_ "!=" or_ -> ne
       | or_

?or_   : or_ "|" xor
       | xor

?xor   : xor "^" and_
       | and_

?and_  : and_ "&" shift
       | shift


?shift : shift ">>" sum   -> rshift     
       | shift "<<" sum   -> lshift
       | sum

?sum   : sum "+" mul      -> add     
       | sum "-" mul      -> sub
       | mul

?mul   : mul "*" typed    -> mul     
       | mul "/" typed    -> div     
       | typed

?typed : typed "as" unary -> typed
       | unary

?unary : "-" atom         -> neg 
       | "!" atom         -> not_
       | atom

?atom  : FLOAT
       | INT
       | HEX_INT
       | OCT_INT
       | BIN_INT
       | ID                -> name    
       | ID "(" expr ")"   -> func     
       | "(" expr ")"     
       | COMMENT
       | STRING

INT       : DEC_DIGIT (DEC_DIGIT | "_")*
BIN_INT   : "0b" (BIN_DIGIT | "_")* BIN_DIGIT (BIN_DIGIT | "_")*
OCT_INT   : "0o" (OCT_DIGIT | "_")* OCT_DIGIT (OCT_DIGIT | "_")*
HEX_INT   : "0x" (HEX_DIGIT | "_")* HEX_DIGIT (HEX_DIGIT | "_")*
COMMENT   : COMMENT_M | COMMENT_S
FLOAT     : INT (FLOAT_EXP|".") INT? FLOAT_EXP?

STRING    : /"(\w|\W|\d|\\n|\\r|\\t|\\'|\\"|\\\\|\\0|\\x[0-9a-fA-F]|\\u\{([0-9a-fA-F]_*){1,6}\})*"/
ID        : /[a-zA-Z][a-zA-Z0-9_]*|_[a-zA-Z0-9_]+/

FLOAT_EXP : /([eE][+-]?[0-9_]+)/
COMMENT_M : /\/\*[\s\S]*\*\//
COMMENT_S : /\/\/.*/
HEX_DIGIT : /[0-9a-fA-F]/
DEC_DIGIT : /[0-9]/
BIN_DIGIT : /[0-1]/
OCT_DIGIT : /[0-7]/

%ignore " "
""", parser='lalr'
)


class CalcTransformer(InlineTransformer):
    from operator import add, sub, mul, truediv as div, pow, neg, pos
    from operator import rshift, lshift, or_, and_, xor
    from operator import gt, ge, lt, le, eq, ne

    names = {
        "pi": math.pi, 
        "e": math.e, 
        "answer": 42,
        "log": math.log,
        "sqrt": math.sqrt,
        "float": float, 
        "int": int,
        "bool": bool,
        "complex": complex,
        "false": False,
        "true": True
    }

    def __init__(self):
        super().__init__()
        self.env = self.names.copy()


    def INT(self, tk):
        return int(tk.replace('_', ''))
    
    def BIN_INT(self, tk):
        return int(tk.replace('_', ''), 2)

    def HEX_INT(self, tk):
        return int(tk.replace('_', ''), 16)
    
    def OCT_INT(self, tk):
        return int(tk.replace('_', ''), 8)

    def FLOAT(self, tk):
        return float(tk.replace('_', ''))

    def ID(self, tk):
        return str(tk)
    
    def not_(self, tk):
        return not tk;

    def typed(self, x, y):
        return y(x);
    
    def range(self, a, b):
        return range(a, b);
    
    def rangei(self, a, b):
        return range(a, b + 1);

    def name(self, name):
        try:
            return self.env[name]
        except KeyError:
            raise ValueError(f'variável inexistente: {name}')
    
    def assign(self, name, value):
        self.env[str(name)] = value

    def func(self, name, arg):
        fn = self.name(name)
        if callable(fn):
            return fn(arg)
        raise ValueError(f'{fn} não é uma função!')

    def seq(self, *args):
        return args[-1]

    def start(self, value):
        return value

def eval_(src):
    tree = grammar.parse(src)
    transformer = CalcTransformer()
    return transformer.transform(tree)

eval = eval_

if __name__ == '__main__':

    # Testes específicos

    assert eval('1 + 2') == 3
    assert eval('1 + 2 * 3') == 7
    assert eval('10 - 5 * 3') == -5
    assert eval('(1 + 2) * 3') == 9
    assert eval('42 >> 1 + 1') == 42 >> 2
    assert eval('!42') == False
    assert eval('42.5 as int') == 42
    assert eval('x = 42; !x') == False
    assert eval('x = 42; x') == 42
    assert eval('42 >> 1 + 1 & 6') == 0b10
    assert eval('42 >> 1 + 1 | 6') == 0b1110
    assert eval('42 >> 1 + 1 ^ 6') == 0b1100
    assert eval('4 > 3') == True
    assert eval('3 < 4') == True
    assert eval('4 == 4') == True
    assert eval('4 >= 3') == True
    assert eval('4 <= 3') == False
    assert eval('4 != 3') == True
    assert eval('1 .. 4') == range(1, 4)
    assert eval('1 ..= 4') == range(1, 5)
    assert eval('x = false; y = true; x && y') == False
    assert eval('x = true; y = true; x && y') == True
    assert eval('0b001') == 1
    eval('53337E-9_77774280');

    # Fim de Testes

    from pathlib import Path
    import json
    path = Path(__file__).parent

    BLACKLIST = {
        'STRING',
        # 'FLOAT',
        # 'ID', 
        # 'COMMENT',
        # 'INT',
        # 'BIN_INT',
        # 'OCT_INT',
        # 'HEX_INT',
    }

    # with open(path / "examples.json") as fd:
    #     data = json.load(fd)

    # for kind, examples in data.items():
    #     if kind in BLACKLIST:
    #         continue

    #     for ex in examples:
    #         try:
    #             seq = list(grammar.lex(ex))
    #         except LarkError:
    #             print(f'erro: {ex}, esperava token do tipo {kind}')
    #             break

    #         try:
    #             [tk] = seq
    #         except ValueError:
    #             print(f'erro: {seq}, tipo: {kind}')
    #             break

    #         assert tk.type == kind, f'tipo errado: {tk} ({tk.type}), esperava {kind}' 