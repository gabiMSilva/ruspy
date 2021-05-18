"""
# cfg-list

Representar sequências em notação BNF e EBNF.

* Representar sequências com separadores.
* Diferenciar separadores intercalados de listas com último separador opcional.
* Representar listas com delimitadores.

-----

Testaremos esta competência corrigindo a implementação das regras "args" e "xargs" 
na gramática. A regra args se refere aos argumentos durante a DECLARAÇÃO de 
uma função enquanto xargs dita como estes argumentos devem ser passados durante
a EXECUÇÃO da função.

A regra args está incorreta porque não utiliza vírgula entre os argumentos. Assim,
de acordo com a gramática do exemplo expressões como a abaixo seriam aceitas:

    fn f(x y) { x + y }

As vírgulas são OBRIGATÓRIAS entre os argumentos e pode aparecer uma vírgula 
OPCIONAL após o último argumento. A lista de argumentos pode ser vazia, mas 
cuidado para não aceitar coisas como

    fn say_hello(,) { print("hello world!") }

ou print(,).

Finalmente, a regra implementada para processar argumentos de funções obriga
a especificação de tipo como em

    fn f(x: int) { x + 1 }

Esta especificação deve ser opcional, aceitando assim expressões como

    fn f(x) { x + 1 }
"""
import pytest
import lark


@pytest.mark.parametrize(
    "src,leaves",
    {
        "fn f(x: int) { x + 1; }": "x int",
        "fn f(x) { x + 1; }": "x",
        "fn f() { x; }": "",
        "fn f(x) { x; } ": "x",
        "fn f(x, y) { x; }": "x y",
        "fn g(x: a, y: b) { x; }": "x a y b",
        "fn g(x,) { x; }": "x",
        "println();": "",
        "f(x);": "x",
        "f(42);": "42",
    }.items(),
)
def test_exemplos_positivos(src, leaves, mod):
    print(f'Processando: {src}')
    ast: lark.Tree = mod.parse(src)
    print(ast.pretty())
    nodes = [*ast.find_data("args"), *ast.find_data("xargs")]
    print('Nós:', nodes)
    
    if not leaves and not nodes:
        return
    elif not nodes:
        raise AssertionError("não encontrou nenhum nó de args ou xargs na árvore")
    elif len(nodes) > 1:
        raise AssertionError("mais de um nó encontrado")
    else:
        args = nodes[0]
        print(mod.leaves(args))
        assert " ".join(map(str, mod.leaves(args))) == leaves


@pytest.mark.parametrize(
    "ex",
    [
        "print(,);",
        "f(x y);",
        "f(x,,y);",
        "g(x:a, b:c);",
        "h(42:a);",
        "h(x:42);",
        'fn say_hello(,) { print("hello world!") }',
        "fn f(x y) { x }",
        "fn f(x:a y:b) { x }",
        "fn f(x:42) { x }",
        "fn f(42) { x }",
    ],
)
def test_exemplos_negativos(ex, mod):
    with pytest.raises(lark.LarkError):
        print(f"Código inválido foi aceito: {ex!r}")
        print(mod.parse_seq(ex).pretty())
        
