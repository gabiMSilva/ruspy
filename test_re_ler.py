"""
# re-ler

Compreender e elicitar a linguagem gerada por expressões regulares simples. 

* Identificar exemplos clássicos de linguagens regulares escritas como regex.
* Identificar exemplos simples gerados pela combinação de 2 a 3 operadores.

----

Para provar a competência, resolva 3 problemas dentro das categorias 
"intermediate" ou "experienced" do site Regex Crosswords (https://regexcrossword.com/challenges/intermediate/puzzles/1). 

Salve o resultado num dicionário como abaixo

    REGEX_CROSSWORDS = {
        "intermediate/puzzles/X": "RESPOSTA-X",
        "intermediate/puzzles/Y": "RESPOSTA-Y",
        "intermediate/puzzles/Z": "RESPOSTA-Z",
    }

As chaves do dicionário são a parte da URL após https://regexcrossword.com/challenges/.
Também funciona se incluir a URL completa.
"""
import pytest
import re

def test_palavras_cruzadas(var):
    dic = var("REGEX_CROSSWORDS", type=dict)

    assert all(isinstance(x, str) for x in dic.values()), 'valores devem ser strings'
    url = re.compile(r'(https?://regexcrossword.com/challenges/)?(intermediate|experienced)/puzzles/\d+/?')
    for k in dic:
        assert isinstance(k, str)
        assert url.fullmatch(k), f'url inválida: {k}'

    pytest.skip("pensando em um modo de corrigir sem revelar as respostas...")
