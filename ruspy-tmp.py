import builtins
import math
from operator import truediv
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

block  : "{" seq "}" ";"?   -> seq
       | "{" "}"            -> null

?seq   : cmd+

// "fn" necessário para impedir que uma função seja lida como uma sequência
?cmd   : "fn"? expr_s ";"   -> null
       | expr_s        
       | expr_b
       | "let" assign ";"   -> let

if_    : "if" expr block ("else" "if" expr block)? ("else" block)?

for_   : "for" ID "in" expr block

while_ : "while" expr block

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

?range : or_e ".." or_e
       | or_e "..=" or_e -> irange
       | or_e

?or_e  : or_e "||" and_e
       | and_e

?and_e : and_e "&&" cmp
       | cmp

?cmp   : or_ "==" or_      -> eq
       | or_ "!=" or_      -> ne
       | or_ "<"  or_      -> lt
       | or_ ">"  or_      -> gt
       | or_ "<=" or_      -> le
       | or_ ">=" or_      -> ge
       | or_

?or_   : or_ "|" xor 
       | xor

?xor    : xor "^" and_ 
       | and_  

?and_   : and_ "&" shift  
        | shift

?shift : shift ">>" sum    -> rshift     
       | shift "<<" sum    -> lshift
       | sum

?sum   : sum "+" mul       -> add     
       | sum "-" mul       -> sub
       | mul

?mul   : mul "*" typed     -> mul     
       | mul "/" typed     -> div_ 
       | mul "%" typed     -> rest     
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

lit    : FLOAT
       | INT
       | BIN_INT
       | OCT_INT
       | HEX_INT
       | RESERVED
       | STRING
       | ID                -> name
       | ID "(" expr ")"   -> func     
       | "(" expr ")" 


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
STRING    : /"(\w|\W|\d|\\n|\\r|\\t|\\'|\\"|\\\\|\\0|\\x[0-9a-fA-F]|\\u\{([0-9a-fA-F]_*){1,6}\})*"/

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

    def STRING(self, tk):
        return str(tk[1:-1])

    # Trata símbolos não-terminais ---------------------------------------------
    def lit(self, tk):
        if not isinstance(tk, Token):
            return tk
        try:
            return getattr(self, tk.type)(tk)
        except AttributeError:
            raise NotImplementedError(f"Implemente a regra def {tk.type}(self, tk): ... no transformer")

    def name(self, name):
        try:
            return self.env[name]
        except KeyError:
            raise ValueError(f'variável inexistente: {name}')

    def assign(self, name, value):
        self.env[str(name)] = self.eval(value);

    def null(self, *tk):
        return None;
    
    def xargs(self, *tk):
        return self.eval(tk);

    def func(self, name, arg):
        fn = self.name(name);

        if callable(fn):
            return fn(arg)
        raise ValueError(f'{fn} não é uma função!')

    def call(self, name, args):
        fn = self.name(name);

        if callable(fn):
            return fn(args)
        raise ValueError(f'{fn} não é uma função!')
    
    def seq(self, *tk):
        return tk[-1]

    def rest(self, n1, n2):
        if(isinstance(n1, int) and isinstance(n2, int)):
            return int(n1 % n2);
        return n1 % n2;

    def div_(self, n1, n2):
        if(isinstance(n1, int) and isinstance(n2, int)):
            return n1 // n2;

        return float(n1 / n2);

    def range(self, a, b):
        return range(a, b);
    
    def irange(self, a, b):
        return range(a, b + 1);

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
        return self.eval(x) or self.eval(y);

    def xargs(self, *tk):
        self.eval(tk);

    def if_(self, cond, then, elif_cond=None, elif_then=None, else_=None):
        # print("ARGS: ", self.eval(cond), self.eval(then), self.eval(elif_cond), self.eval(elif_then), self.eval(else_))
        if(elif_cond == None and elif_then == None and else_ == None):
            # Só tem if
            if(self.eval(cond)):
                return self.eval(then)

        elif(elif_then == None and else_ == None):
            # If e else
            if(self.eval(cond)):
                return self.eval(then)
            else:
                return self.eval(elif_cond)
        elif(else_ == None):
            # if e elif
            if(self.eval(cond)):
                return self.eval(then)
            elif(self.eval(elif_cond)):
                return self.eval(elif_then)
            else:
                None
        else:
            # id, elif e else
            if(self.eval(cond)):
                return self.eval(then)
            elif(self.eval(elif_cond)):
                return self.eval(elif_then)
            else:
                return self.eval(else_)

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


# test_comp_org

COMP_ORG = """
    * Análise léxica:
                            A análise léxica é a etapa onde os lexemas são identificados e agrupados, gerando Tokens que são caracterizados a partir de 
                        definições de padrões definidos para cada um deles. 
                            Isso significa dizer que só serão identificados os lexemas que estiverem de acordo com um padrão pré definido da linguagem 
                        ou será gerado um erro.

    * Análise sintática:
                            Na etapa de análise sintática (também conhecida como 'parser') o compilador irá reconhecer os conjuntos de Tokens do código e 
                        determinar se ele é valido ou não. 
                            Para isso podem ser usadas gramáticas livres de contexto, por exemplo.

    * Análise semântica: 
                            A análise semântica é responsável por verificar aspectos de significado dos comandos. Em uma atribuição de valor à um identificador, 
                        temos alguns exemplos abaixo de validações que o analizador semântico deve fazer :
                        
                        - O identificador é uma variável?
                        - As variáveis usadas já foram declaradas anteriormente?
                        - Qual o tipo da variável?
                        - O tipo do valor que está sendo atribuído corresponde ao tipo declarado?
                        - A variável foi declarada em um contexto que pode ser acessado nesse local?

    * Otimização:
                            Na etapa de otimização, o compilador deve identificar comandos e regras que estão sendo utilizadas de forma ineficientes e 
                        melhorá-las a fim de obter um melhor desempenho. Alguns exemplos de otimiza'ção de código são: 
                            
                        - Remoção de código redundante
                        - Remoção de código inalcançável (dentro de um 'if(false)', por exemplo)
                        - Repetição de atriuições com os mesmos valores
                            - x = 2;
                              x = 2;
                            - A segunda atribuição poderia ser removida sem prejuízo ao programa.

                            Há muitos outros pontos de otimização, esses são exemplos simples apenas para visualização do conceito apresentado.
    * Emissão de código:
                            Nessa etapa, o compilador deve gerar um código que possa ser lido diretamente pelo SO.
                            Na linguagem C podemos ver claramente o objeto de código gerado após executar a compilação.

"""

COMP_VS_INTERP_Q1 = """
                            Tanto o interpretador quanto o compilador, traduzem instruções de código para linguagem de máquina, a principal diferença entre 
                        compiladores e interpretadores é a forma como os códigos são traduzidos. 
                            Enquanto um compilador traduz todo o código e executa o arquivo final depois, o interpretador traduz por blocos ou instruções e não possui um arquivo resultante.
                            Isso leva o compilador a ser mais eficiente, pois o código não precisa ser traduzido sempre que for executado. Em compensação, o interpretador pode ser 
                        executado em qualquer SO, pois traduz o código em tempo de execução, bastando que o interpretador esteja instalado na máquina.

"""

COMP_VS_INTERP_Q2 = """

                            O C/C++ é uma linguagem tida geralmente como compilada, porém tembém existem interpretadores para C!
                            O PicoC (https://github.com/jpoirier/picoc) é um deles.


                            "PicoC is a very small C interpreter for scripting. It was originally written as a script language for a 
                        UAV on-board flight system. It's also very suitable for other robotic, embedded and non-embedded applications.

                            The core C source code is around 3500 lines of code. It's not intended to be a complete implementation of ISO 
                        C but it has all the essentials. When compiled it only takes a few k of code 
                        space and is also very sparing of data space. This means it can work well in small embedded devices. It's also 
                        a fun example of how to create a very small language implementation while still keeping the code readable."
                        
                        Fonte: https://github.com/jpoirier/picoc



"""


# // Fatorial
# fn fat(n: int) {
#     r = n
#     for i in 1..n {
#         r *= i
#     }
#     r
# }


#     ID  - identificadores 
#     INT - inteiros
#     OP  - operadores binários
#     LBRACE/RBRACE - chaves (abrir/fechar) 
#     LPAR/RPAR     - parênteses (abrir/fechar) 

FAT_LEXEMAS = ["fn", "fat", "n:int", "r" ,"n", "for", "i", "1..n", "1", "n", "r", "i"] 

FAT_TOKENS = ["fn FN", "fat ID", "n:int ARG", "r ID", "n INT","for FOR", "i INT", "1..n RANGE", "1 INT", "n INT", "r ID", "i INT"] 