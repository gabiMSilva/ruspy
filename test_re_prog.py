"""
# re-prog

Converter e associar expressões regulares da teoria de compiladores com expressões regulares escritas em linguagem de programação. 

* Criar e manipular expressões regulares em Python ou outra linguagem de programação.
* Escrever expressões do livro texto na sintaxe utilizada em linguagens de programação.

---- 

Esta é uma competência virtual, já que quem resolver lex-re já ganha automaticamente
re-prog. Caso você tenha conseguido traduzir as expressões regulares de cada 
categoria individualmente, mas não conseguiu fazer com que elas funcionem corretamente
em conjunto no lexer, pode submeter as expressões na variável

    RE_PROG = {
        "DEC": r"...",
        "HEX": r"...",
        "OCT": r"...",
        "BIN": r"...",
        "FLOAT": r"...",
        "ID": r"...",
    }

Lembrando mais uma vez: se os testes de lex-re passaram, NÂO PRECISA submeter
esta resposta já que a pontuação é conferida automaticamente.
"""
import pytest
import re


@pytest.fixture(scope="module")
def regex_prog(mod):
    try:
        return mod.REGEX_PROG
    except AttributeError:
        pytest.skip("verifique manualmente se você passou em lex-re")


@pytest.mark.parametrize("grp", "ID INT BIN_INT OCT_INT HEX_INT FLOAT".split())
def test_exemplos_positivos(grp, mod, data, regex_prog):
    regex = re.compile(regex_prog[grp])
    for ex in sorted(data(grp), key=len):
        assert regex.fullmatch(ex), f"Valor não aceito: {ex}"


@pytest.mark.parametrize("grp", "ID INT BIN_INT OCT_INT HEX_INT FLOAT COMMENT".split())
def test_exemplos_negativos(grp, mod, data, regex_prog):
    all_regex = [re.compile(v) for v in regex_prog.values()]

    for ex in sorted(data(grp + "_bad"), key=len):
        assert all(not re.fullmatch(ex) for re in all_regex), f'padrão inválido foi aceito: {ex}'