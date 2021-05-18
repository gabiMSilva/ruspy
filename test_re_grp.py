'''
# re-grp

Aplicar expressões regulares e utilizar grupos e sub-padrões para extrair informação a partir de um texto. 

* Conhecer sintaxe para criação de grupos nomeados e posicionais.
* Obter grupos de um objeto de match.
* Identificar sub-padrões de uma string maior a partir de expressões regulares.

---

Expressões regulares são uma ferramenta útil para realizar alguns tipos de 
edição de código em larga escala e podem economizar bastante esforço em algumas
refatorações (comite antes, pois se algo der errado, também podem gerar resultados
catastróficos!).

Suponha que você leu o livro "Clean Code" do Robert C. Martin e concluiu que 
comentários de código são uma má pratica, já que um código limpo deve ser claro
o suficiente para não precisar de explicações adicionais. Esta é uma interpretação
equivocada do texto, mas não importa, queremos ser eficientes nos nossos erros 
também. Crie uma expressão regular que identifique todos comentários Python de 
um programa. Considere apenas comentários no formato

    # comentário...

Teste no editor de código e salve a expressão na forma 

SUBS_REMOVER_COMENTARIOS = (r"...", "")

Onde temos um par com a expressão regular, seguida de um padrão de substituição,
que neste caso é a string vazia (já que queremos remover os comentários).

Na segunda parte do exercício, vista a camisa de um colega que odeia esta mania de
apagar comentários e decide, para se proteger, reescrever todos os comentários  
como strings de aspas triplas. Outro erro, mas queremos aplicar as melhores 
ferramentas.

Encontre um par de expressão regular e padrão de substituição (a segunda caixa na
opção ctrl + H do VSCode) e salve-os na variável abaixo

SUBS_COMENTARIOS_STRINGS = (r"regex", 'substituição')

Identifique apenas comentários que ocorrem sozinhos na linha e deixe os que
aparecem à direita de um trecho de código intocados. Um exemplo de aplicação é 
dado abaixo: 

    # trocar este comentário
    def f(x):
        # este também
        return x  # mas não este, porque tem código antes.

Este código viraria:

    """trocar este comentário"""
    def f(x):
        """este também"""
        return x  # mas não este, porque tem código antes.

'''
import pytest

def test_verificações_básicas():
    pytest.skip('o código de teste ainda não está pronto')

