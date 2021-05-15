"""
# cfg-bnf
Entender operadores na notação EBNF
* Reconhecer sintaxe e operdores em sua implementações no Lark.
* Realizar transformação de operações EBNF para suas respectivas representações em BNF.
A regra para "if" abaixo está incompleta.
    if_    : "if" expr block "else" block
Esta declaração requer o bloco else obrigatório e não permite encadeamento de ifs
como nos exemplos que deveriam ser validados
    // If sem o bloco else
    if cond {
        println("Hello World!")
    }
    // Múltiplos blocos if
    if cond1 {
        println("Hello 1!")
    } else if cond2 {
        println("Hello 2!")
    } else if cond3 {
        println("Hello 3!")
    } else {
        println("Hello other!")
    }
Implemente o suporte a estes dois casos e à avaliação do comando if para passar 
nos testes.
"""
import pytest
import lark
import contextlib
import io

def test_eval_if(mod):
    src = 'if { true } { println(0) } else { println(1) }'
    
    print(f"Testando: {src!r}")
    fd = io.StringIO()
    print(mod.pretty(mod.parse(src)))
    
    with contextlib.redirect_stdout(fd):
        try:
            mod.expr(src)
        except NotImplementedError as ex:
            print(ex.args)
            if ex.args != ("if",):
                raise
            raise NotImplementedError("""
O comando if deve ser implementado de forma diferente dos demais. Não podemos
deixar o Transformer avaliar automaticamente a condição e os dois ramos do if,
já que a condição determina qual ramo será executado e qual ficará inerte. 
Para que isso seja possível, registrei o "if_" na lista de formas especiais, em que
o transformer passa o argumento não avaliado como uma árvore sintática. Podemos
forçar a avaliação explícita utilizando o método eval(). A diferença entre uma 
forma normal e uma especial pode ser vista nos dois métodos:
    def normal(self, x, y):
        return f(x, y)  # x e y já estão transformados, já podem ser usados por f
    def especial(self, x, y):
        # x e y ainda precisam ser avaliados
        x = self.eval(x)
        y = self.eval(y)
        return f(x, y)  # depois de usar eval, podemos utilizá-los normalmente
Usando este conhecimento, agora implemente o método def if_(self, cond, then, else_)!
""")
    
    out = fd.getvalue()
    assert out != '0\n1\n', 'avaliou os dois ramos do if'
    assert out != '1\n', 'avaliou o ramo errado do if'
    assert out == '0\n'

@pytest.mark.parametrize(
    "src,v",
    {
        "if true { 0 } else { 1 }": 0,
        "if (true) { 0 } else { 1 }": 0,
        "if 2 > 1 { 0 } else { 1 }": 0,
        "if false { 0 } else { 1 }": 1,
        "if true { 0 }": 0,
        "if false { 0 }": None,
        "if true { 0 } else if true { 1 } else { 2 }": 0,
        "if false { 0 } else if false { 1 } else { 2 }": 2,
        "if true { 0 } else if true { 1 }": 0,
        "if true { 0 } else if false { 1 }": 0,
        "if false { 0 } else if true { 1 }": 1,
        "if false { 0 } else if false { 1 }": None,
    }.items(),
)
def test_exemplos_positivos(src, v, mod):
    print(f"Testando: {src!r}")
    print(mod.pretty(mod.parse(src)))
    assert mod.eval(src) == v


@pytest.mark.parametrize("src", [
    "if (true) 0 else 1",
    "if cond { 0 } else 1",
    "if cond 0 else { 1 }",
    "if (cond) 0",
])
def test_exemplos_negativos(src, mod, data):
    with pytest.raises(lark.LarkError):
        print(f"Código inválido foi aceito: {src!r}")
        print(mod.parse_seq(src).pretty())