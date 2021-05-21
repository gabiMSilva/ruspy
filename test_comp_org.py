'''
# [comp-org]

Compreender as etapas tradicionais de análise do código em um compilador. 

* Conhecer o papel e função das etapas de análise léxica, análise sintática, análise semântica, otimização e geração de código.
* Conhecer superficialmente como esse mecanismo funciona em alguma linguagem real e possuir elementos conceituais para comparar estas etapas em diferentes linguagens.

-----

Descreva a função de cada etapa no processo de compilação de um código

* Análise léxica
* Análise sintática
* Análise semântica
* Otimização
* Emissão de código

Salve a sua resposta em uma variável de string como abaixo:

    COMP_ORG = """
    
    Minha resposta aqui! 

    """
'''
import pytest

def test_verificações_básicas(var):
    print(var('COMP_ORG'))
    pytest.skip('a resposta será avaliada manualmente')