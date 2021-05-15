import builtins
import math
import sys
from typing import Any
from lark import Lark, InlineTransformer, LarkError, Token, Tree

# Constantes (algumas tarefas pedem para incluir variáveis específicas nesta
# parte do arquivo)
NAME = "Meu nome"
MATRICULA = "01/2345678"
...


# Gramática do Ruspy. (não modifique o nome desta variável, testes dependem disto!)
GRAMMAR = r"""
mod    : fn+
fn     : "fn" ID "(" args? ")" block 
       | ID "(" xargs? ")" ";"

args   : arg ","?
       | arg ("," arg)*

arg    : ID (":" ID)?

?cmd   : expr_s ";"       -> cmd
       | expr_b
       | "let" assign ";" -> let

?seq   : cmd+
if_    : "if" expr block "else" block
for_   : "for" ID "in" expr block
while_ : "while" expr block
block  : "{" seq "}"
assign : ID "=" expr

?expr  : expr_s 
       | expr_b

?expr_s: assign
       | lambd

?expr_b: block 
       | if_
       | for_
       | while_

?lambd : "|" args "|" expr
       | range

?range : and_e ".." and_e
       | and_e "..=" and_e -> irange
       | and_e

?and_e : and_e "&&" or_e
       | or_e

?or_e  : or_e "||" cmp
       | cmp

?cmp   : cmp "==" bit      -> eq
       | cmp "!=" bit      -> ne
       | cmp "<"  bit      -> lt
       | cmp ">"  bit      -> gt
       | cmp "<=" bit      -> le
       | cmp ">=" bit      -> ge
       | bit

?bit   : bit "|" shift     -> or_
       | bit "^" shift     -> xor
       | bit "&" shift     -> and_  
       | shift    

?shift : shift ">>" sum    -> rshift     
       | shift "<<" sum    -> lshift
       | sum

?sum   : sum "+" mul       -> add     
       | sum "-" mul       -> sub
       | mul

?mul   : mul "*" typed     -> mul     
       | mul "/" typed     -> div     
       | typed

?typed : typed "as" unary  -> typed     
       | unary

?unary : "-" atom          -> neg 
       | "!" atom          -> not_ 
       | call "?"          -> opt 
       | call

?call  : ID "(" xargs ")" 
       | attr

xargs : expr ("," expr)*

?attr  : call ("." ID)+
       | ret

?ret   : "return" expr   -> ret
       | "continue"      -> loop_continue
       | "break"         -> loop_break
       | atom

?atom  : lit
       | "(" expr ")"

lit    : FLOAT
       | BIN_INT
       | OCT_INT
       | HEX_INT
       | INT
       | RESERVED
       | STRING
       | ID                -> name

INT: DEC_DIGIT (DEC_DIGIT | "_")*
BIN_INT   : "0b" (BIN_DIGIT | "_")* BIN_DIGIT (BIN_DIGIT | "_")*
OCT_INT   : "0o" (OCT_DIGIT | "_")* OCT_DIGIT (OCT_DIGIT | "_")*
HEX_INT   : "0x" (HEX_DIGIT | "_")* HEX_DIGIT (HEX_DIGIT | "_")*

// Tipos de ponto-flutante

FLOAT:  BEGIN INT "." END
        | INT FLOAT_EXP
        | INT "." INT FLOAT_EXP?
        | INT ("." INT)? FLOAT_EXP? FLOAT_SUFFIX

// DÍGITOS
BIN_DIGIT : /[0-1]/
DEC_DIGIT : /[0-9]/
HEX_DIGIT : /[0-9a-fA-F]/
OCT_DIGIT : /[0-7]/

FLOAT_EXP : /[eE][+-]?[0-9_]+/

//SUFFIX

FLOAT_SUFFIX : "f32" | "f64"

// UTILS
BEGIN     : /^/ 
END       : /$/ 

// Strings
STRING       : /"string"/

// Nomes de variáveis, valores especiais
ID           : /[a-zA-Z][a-zA-Z0-9_]*|_[a-zA-Z0-9_]+/
RESERVED     : /true|false|null/

// Comentários
COMMENT      : LINE_COMMENT | BLOCK_COMMENT
LINE_COMMENT : /\/\/.*/
BLOCK_COMMENT: /\/\*.*\*\//

%ignore COMMENT
%ignore /\s+/
"""
grammar_expr = Lark(GRAMMAR, parser="lalr", start="seq")
grammar_mod = Lark(GRAMMAR, parser="lalr", start="mod")


# (não modifique o nome desta classe, fique livre para alterar as implementações!)
class RuspyTransformer(InlineTransformer):
    from operator import add, sub, mul, truediv as div, pow, neg, pos
    from operator import rshift, lshift, or_, and_, xor
    from operator import eq, ne, gt, lt, ge, le

    global_names = {
        **vars(math),  # Inclui todas funções do módulo math
        **vars(builtins),  # Inclui todas funções padrão do python
        "answer": 42,
        "println": print,
        "true": True,
        "false": False,
        "null": None,
    }

    # Estas declarações de tipo existem somente para deixar o VSCode feliz.
    _transform_children: Any
    _call_userfunc: Any
    transform: Any

    # Construtor
    def __init__(self):
        super().__init__()
        self.env = self.global_names.copy()

    # Trata símbolos terminais -------------------------------------------------
    def INT(self, tk):
        data = tk.replace('_', '')
        if set(data) == {'0'}:
            return 0  
        return int(data)
    
    def BIN_INT(self, tk):
        return int(tk.replace('_', ''), 2)

    def HEX_INT(self, tk):
        return int(tk.replace('_', ''), 16)
    
    def OCT_INT(self, tk):
        return int(tk.replace('_', ''), 8)

    def ID(self, tk):
        return str(tk)

    def FLOAT(self, tk):
        return float(tk.replace('_', ''))

    # Trata símbolos não-terminais ---------------------------------------------
    def lit(self, tk):
        if not isinstance(tk, Token):
            return tk
        try:
            return getattr(self, tk.type)(tk)
        except AttributeError:
            raise NotImplementedError(f"Implemente a regra def {tk.type}(self, tk): ... no transformer")

    def name(self, name):
        raise NotImplementedError("name")

    def assign(self, name, value):
        raise NotImplementedError("assign")

    ...

    # Formas especiais --------------------------------------------------------

    # Não-terminais normais recebem argumentos já transformados. As formas
    # especiais exigem a avaliação manual, o que pode ser útil para controlar
    # com mais precisão quantas vezes cada argumento deve ser avaliado. Isto é
    # útil em laços, execução condicional etc.
    #
    # A lista de formas especiais precisa ser declarada explicitamente
    special = {"if_", "for_", "while_", "fn", "lambd", "and_e", "or_e"}

    # Sobrescrevemos este método para habilitar formas especiais no transformer.
    def _transform_tree(self, tree):
        if tree.data in self.special:
            children = tree.children
        else:
            children = list(self._transform_children(tree.children))
        return self._call_userfunc(tree, children)

    # A avaliação é feita pelo método eval.
    def eval(self, obj):
        """
        Força a avaliação de um nó da árvore sintática em uma forma especial.
        """
        if isinstance(obj, Tree):
            return self.transform(obj)
        elif isinstance(obj, Token):
            try:
                return getattr(self, obj.type)(obj)
            except AttributeError:
                return obj
        else:
            return obj

    # Lista de formas especiais
    def and_e(self, x, y):
        # Esta é a forma mais simples. Avaliamos explicitamente cada argumento.
        # Note que "x and y" em Python avalia x e somente avalia y caso o primeiro
        # argumento seja verdadeiro. Este é exatamente o comportamento desejado.
        return self.eval(x) and self.eval(y)

    def or_e(self, x, y):
        raise NotImplementedError("or_e")

    def if_(self, cond, then, else_=None):
        raise NotImplementedError("if")

    def while_(self, cond, block):
        raise NotImplementedError("while")

    def for_(self, id, expr, block):
        raise NotImplementedError("for")

    def fn(self, name, args, block):
        # Dica: reaproveite a implementação de lambd
        raise NotImplementedError("fn")

    def lambd(self, args, block):
        raise NotImplementedError("fn")


def eval(src):
    """
    Avalia uma expressão ruspy.

    >>> eval("1 + 1")
    2
    """
    return _eval_or_exec(src, is_exec=False)


def module(src) -> dict:
    """
    Avalia um módulo ruspy e retorna um dicionário com as funções definidas
    no módulo.

    Você pode utilizar estas funções a partir de código Python.

    >>> dic = module("fn incr(n: int) { n + 1 }")
    >>> f = dic["incr"]
    >>> f(1)
    2
    """
    return _eval_or_exec(src, is_exec=True)


def run(src):
    """
    Avalia um módulo ruspy e executa automaticamente a função main.

    >>> src = '''
    ... fn main() {
    ...     print("hello world!")
    ... }
    ... '''
    hello world!
    """
    mod = module(src)
    main = mod.get("main")
    if not main:
        raise RuntimeError('módulo não define uma função "main()"')
    main()


def _eval_or_exec(src: str, is_exec=False) -> Any:
    # Função utilizada internamente por eval/module/run.
    if is_exec:
        grammar = grammar_mod
    else:
        grammar = grammar_expr
    try:

        tree = grammar.parse(src)
    except LarkError:
        print(f"Erro avaliando a expressão: \n{src}")
        print("\nImprimindo tokens")
        for i, tk in enumerate(grammar.lex(src), start=1):
            print(f" - {i}) {tk} ({tk.type})")
        raise
    transformer = RuspyTransformer()
    result = transformer.transform(tree)

    if isinstance(result, Tree):
        print(tree.pretty())
        bads = [*tree.find_pred(lambda x: not hasattr(transformer, x.data))]
        bad = bads[0] if bads else tree
        raise NotImplementedError(
            f"""
            não implementou regra para lidar com: {tree.data!r}.
            Crie um método como abaixo na classe do transformer.
                def {bad.data}(self, ...): 
                    return ... 
            """
        )
    return result


# Interface de linha de comando. Lê um arquivo ruspy e passa para a função
# eval ou equivalente. Você pode modificar o conteúdo dentro do "if" para
# executar outros códigos de teste quando for rodar o arquivo. O exemplo abaixo
# fornece uma interface de linha de comando minimamente decente para interagir
# com o ruspy.
if __name__ == "__main__":
    if "--help" in sys.argv:
        print("Digite python ruspy.py [ARQUIVO] [--script]")
        print("")
        print("Opções:")
        print("  --help:")
        print("         mostra mensagem de ajuda")
        print("  --script:")
        print("         avalia como expressão no modo script, como se")
        print("         estivéssemos executando o código dentro da função main()")
        exit()
    elif "--script" in sys.argv:
        do_eval = True
        del sys.argv[sys.argv.index("--script")]
    else:
        do_eval = False
    with open(sys.argv[-1]) as fd:
        src = fd.read()
        if do_eval:
            print(f"\n> {eval(src)}")
        else:
            run(src)
