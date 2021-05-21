"""
# re-pat

Aplicar expressões regulares para encontrar padrões de texto simples em um documento. 

* Utilizar regex em um programa de computador para identificar padrões de texto.
* Conhecer métodos como match, search, split e finditer.

---

O tema do exercício é utilizar expressões regulares em ferramentas de código
como editores de texto, grep, etc. No caso, vamos propor uma expressão regular
que consiga contar o número de declarações de termos terminais e não-terminais 
numa gramática do Lark.

Faça o teste de busca por regex no editor de código que você utiliza (no VScode, 
por exemplo, digite ctrl + F e habilite o ícone .* para habilitar a busca por regex.)

Para o exercício ser bem sucedido, é necessário criar uma **única** expressão 
regular que identifique todos os casos válidos e não acuse nenhum caso inválido.

A resposta será fornecida declarando 3 variáveis do tipo string no módulo ruspy.py:

REGEX_TERMINAIS = r"..."
REGEX_NAO_TERMINAIS = r"..."
REGEX_TERMINAIS_E_NAO_TERMINAIS = r"..."

Cada variável deve conter uma expressão regular que identifica a categoria 
correspondente de operadores. Elas serão avaliadas como se a busca no editor
de código fosse feita no modo sensível a maiúsculas/minúsculas (habilitando o 
ícone Aa no VScode).

Cuidado com os exemplos abaixo:

?mod   : regra que começa com uma interrogação
and_e  : possui um underscore
?foobar: regra encosta no dois pontos
// ex:    parece uma regra, mas não é
FOOBAR : terminal possui letras maiúsculas

As regex não precisam ser universais no sentido que funcionam em todas as 
gramáticas do lark válidas, mas também não podem ser a solução de maratona
de programação de listar os casos válidos do ruspy.lark explicitamente. Por
isto, existe um limite de 40 caracteres por regex.
"""
import pytest
import re


def test_verificações_básicas(var):
    with open("ruspy.lark") as fd:
        src = fd.read()

    assert check_regex(var("REGEX_NAO_TERMINAIS"), src) == 31
    assert check_regex(var("REGEX_TERMINAIS"), src) == 14
    assert check_regex(var("REGEX_TERMINAIS_E_NAO_TERMINAIS"), src) == 14 + 31


def check_regex(pat, src):
    pat = re.compile(pat)
    count = 0
    for ln in src.splitlines():
        count += len(pat.findall(ln))
    return count