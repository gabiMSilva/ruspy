"""
# cfg-bnf

Entender e reconhecer operações básicas de gramática generativa na notação BNF

* Reconhecer linguagens regulares na forma de gramática livre de contexto.
* Identificar quando uma gramática livre de contexto corresponde a uma linguagem regular.

A regra para "seq" e "block" na gramática do ruspy está incorreta (?seq: cmd+). Traduza para 
a versão correta utilizando operadores BNF ou EBNF. Em texto livre, a regra de
seq pode ser descrita como:

Um "seq" pode ser:
  - um "cmd"
  - um "expr_s"
  - um "expr_b" seguido de ponto-e-vírgula, seguido de um "seq"
  - um "cmd" seguido de um "seq"

As regras para avaliação do valor de seq são:
  - quando recebe um único argumento, retorna estes argumento
  - quando recebe 2 argumentos, retorna o segundo

Um "block" pode ser:
  - abre chaves, seguida de um seq, seguida de fechar chaves
  - abre chaves e fecha chaves (um bloco vazio)

Um bloco possui o mesmo valor do seq contido ou None, caso seja vazio

DICA: Atualize a implementação de lit de acordo com o exemplo do repositório, 
caso ainda esteja desatualizada
"""
import pytest
import lark


@pytest.mark.parametrize(
    "src,v",
    {
        "1; 2": 2,
        "42;": None,
        "len": len,
        "42": 42,
        "1; 2; 3; 4": 4,
        "{ 42 }": 42,
        "{}": None,
        "{ }": None,
        "{ 1; 2; 3 }": 3,
        "{ 1; 2; 3; }": None,
        "{ 1; 2 }; 3": 3,
        "0; { 1; 2 }": 2,
    }.items(),
)
def test_exemplos_positivos(src, v, mod):
    print(f'Testando: {src!r}')
    print(mod.pretty(mod.parse(src)))
    assert mod.eval(src) == v


@pytest.mark.parametrize("src", [
  "1 2",
  "1 ;; 2",
  "1 ;;",
])
def test_exemplos_negativos(src, mod, data):
    with pytest.raises(lark.LarkError):
        print(f"Código inválido foi aceito: {src!r}")
        print(mod.parse_seq(src).pretty())
