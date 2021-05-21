"""
# lex-ler

Compreender a motivação e mecanismos da análise léxica. 

* Separar um código fonte em tokens e lexemas.
* Identificar os diferentes tipos de lexemas.
* Identificar lexemas em linguagens de programação reais como Python ou C.

----

Atenção! Este não é um exercício de programação, mas sim de compreensão dos 
conceitos relacionados à análise léxica. Ainda assim, a resposta é corrigida
de forma automatizada. 

Considere o código ruspy abaixo:

    // Fatorial
    fn fat(n: int) {
        r = n
        for i in 1..n {
            r *= i
        }
        r
    }

Separe este programa em lexemas e salve-os como uma lista de strings na variável:

    FAT_LEXEMAS = ["fn", "fat", ...] 

Os comentários são removidos da lista de lexemas, já que não interessam à análise
semântica. Você pode gerar esta lista de forma manual, automática ou semi-automática.
A única parte importante é obter o valor correto no final.

Na segunda parte faça a classificação de cada lexema em sua categoria e salve
como 
    
    FAT_TOKENS = ["fn FN", "fat ID", ...] 

ou seja, cada string contêm o lexema e a categoria de não-terminal separados
por um espaço. Considere as seguintes categorias:

    ID  - identificadores 
    INT - inteiros
    OP  - operadores binários
    LBRACE/RBRACE - chaves (abrir/fechar) 
    LPAR/RPAR     - parênteses (abrir/fechar) 

Cada palavra reservada possui sua categoria a parte como FN, IF, etc.
"""
import pytest


def test_verificações_básicas(var, check_value, fn):
    size_hint = 24

    lexemas = var("FAT_LEXEMAS")
    tokens = var("FAT_TOKENS")
    assert len(lexemas) == len(tokens)
    tok_class = {tk.split()[1] for tk in tokens}
    assert tok_class == {"FN", "FOR", "IN", "ID", "INT", "OP", "LBRACE", "RBRACE", "LPAR", "RPAR"} 

    check_value(
        lexemas,
        name="FAT_LEXEMAS",
        type=list,
        hash="MjQ6AD8NORcHa9YKPMlnYAmp6A==",
        check=[fn.size(size_hint)],
    )
    check_value(
        tokens,
        name="FAT_TOKENS",
        type=list,
        hash="MjQ6eDGqAGldx9jyZm2FqVyIJg==",
        check=[fn.size(size_hint)],
    )
