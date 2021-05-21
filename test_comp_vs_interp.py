'''
# [comp-vs-interp]

Compreender as principais diferenças entre um compilador e um interpretador. 

* Situar um interpretador no contexto da arquitetura tradicional de compiladores.
* Compreender a distinção entre um interpretador de árvores sintáticas e uma máquina virtual.
* Identificar, entre as linguagens de programção mais conhecidas, quais são tradicionalmente interpretadas e quais são compiladas. 

-----

Responda às questões:

Q1) Descreva sucintamente as semelhanças e diferenças entre compiladores e 
interpretadores, em especial no que ambos diferem (ou se assemelham) com relação 
às etapas mencionadas na questão anterior em COMP_ORG.

Q2) É um erro comum acreditar que "compilada" vs "interpretada" é uma 
característica da linguagem de programação. Estas são características de 
**implementações** específicas de cada linguagem. Ainda que a implementação de 
Python criada por Guido seja interpretada (e de longe a mais popular) ou que a 
versão do C que presente no GCC seja compilada, nada impede se crie versões 
compiladas de Python ou interpretadas de C. Na realidade, elas existem. 

Encontre pelo menos um exemplo de implementação de um compilador para uma 
linguagem normalmente tida como interpretada ou de um interpretador para uma 
linguagem normalmente tida como compilada. Forneça uma referência como link, 
artigo, etc que aponte para os projetos escolhidos como exemplos.


Salve a sua resposta em duas variáveis do tipo string como abaixo:

    COMP_VS_INTERP_Q1 = """
    
    Minha resposta aqui! 

    """

    COMP_VS_INTERP_Q2 = """
    
    Minha resposta aqui! 

    """
'''
import pytest

def test_verificações_básicas(var):
    print(var('COMP_VS_INTERP_Q1'))
    print(var('COMP_VS_INTERP_Q2'))
    pytest.skip('a resposta será avaliada manualmente')