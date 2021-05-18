# Ruspy

Olá! Nessa série de trabalhos, criaremos um interpretador de uma linguagem
de programação nova, que chamaremos de Ruspy. Ruspy funciona como o Python, mas 
se fantasia de Rust na sua sintaxe.

No fim da atividade, criaremos um interpretador ruspy.py capaz de ler e 
executar o código em um arquivo .rpy. Abaixo segue o exemplo clássico de um
código que imprime a sequência de Fibonacci:

```rust
// Calcula números de fibonacci
fn fib(n: int) {
    if n <= 1 {
        return 1
    } else {
        return fib(n - 1) + fib(n - 2)
    }
}

fn main() {
    for i in 0..10 {
        println(fib(i))
    }
}
```

Podemos executar este código (e visualizar a sequência de Fibonacci) rodando
o seguinte comando no shell:
    
    $ python ruspy.py fib.rpy.

Python é implementado em C e tipicamente é algumas dezenas de vezes mais lento 
que C (ou Rust). Ruspy é implementado em Python e podemos esperar algo algumas 
dezenas de vezes mais lento que próprio Python. Claramente nosso objetivo aqui
é velocidade de execução!  

## Rodando os testes e verificando competências

Cada atividade é composta por um módulo de teste que utiliza as bibliotecas
pytest e hypothesis. A implementação utiliza o Lark. Começamos com as instalações:

    $ python3 -m pip install pytest hypothesis lark-parser

O nome de cada atividade segue o padrão "test_<nome_da_competência>.py". As 
competências adicionais terminam sempre com o sufixo "_opt". Por exemplo, 
podemos começar pela competência "re_basico". Algumas competências podem conter
arquivos de testes separados como "test_competencia_V1.py" e 
"test_competencia_V2.py". Aqui temos dois caminhos alternativos: você pode 
implementar a versão 1 ou 2 (ou ambas!) para obter a competência correspondente. 
 
Sugiro que abra o arquivo test_re_basico.py para verificar o enunciado na string
de documentação. Não ligue muito para o código nestes módulos, porque está fora do 
escopo da disciplina e só servem para rodar os testes. A string de documentação dos
testes pode conter informação útil sobre o objetivo de cada teste e porque o teste 
falhou.

Executamos os testes com o comando:

    $ python3 -m pytest test_re_basico.py --maxfail=1

(dependendo da instalação, podemos omitir o "python3 -m" e começar com "pytest" diretamente)
Considere também utilizar "--lf" no final do comando para executar apenas os testes
que falharam na última execução.

## Ferramentas opcionais

Considere instalar o black, o flake8 e mypy (pip install black mypy). O primeiro formata automaticamente
código Python e os outros dois conseguem encontrar possíveis errors. Os trẽs ajudam em manter a qualidade do 
código e facilitam a nossa vida a longo prazo. Executamos cada ferramenta como 
"black|flake8|mypy <nome-do-arquivo>". Dependendo das configurações do Python, pode ser necessário fazer
python3 -m <ferramenta> <nome-do-arquivo>. 

O VSCode possui plugins que integram estas 3 ferramentas. Formate um arquivo Python com "ctrl + shift + i"
e normalmente o VSCode perguntará se quer instalar o Black. Os avisos do Mypy e flake8 aparecem se estas 
ferramentas estiverem habilitadas. Digite "ctrl + ," para abrir as configurações e busque por Mypy ou Flake8.

O plugin Python da Microsoft utiliza o Pyright, que possui um escopo parecido com estas ferramentas e é uma
boa alternativa ao Mypy e ao Flake8 já integrada ao próprio VSCode. 

## Enviando resultados

Modifique o arquivo ruspy.py até passar em todos os testes. Quando isto acontecer,
parabéns! Você comprovou esta habilidade. Submeta esta resposta no formulário
https://forms.gle/R7UZP1UFfG4oW8Rb8 marcando nome, matrícula e a competência 
"re_basico" (ou competência correspondente) no campo "Competência"). Executarei
os testes na minha máquina só para confirmar, mas quem passou em todos os testes
já possui a competência correspondente.

Idealmente, você deve editar um único arquivo ruspy.py que funciona com todos os
testes simultaneamente. Neste caso, é possível enviar um único arquivo ruspy.py
na competência "ruspy" que será utilizado para testar todas competências 
relacionadas ao ruspy. Utilizarei sempre a última versão enviada para cada 
compentência dentro do prazo para realizar os testes. Deste modo, não existe 
problema algum em fazer várias submissões de versões diferentes do mesmo arquivo.

## Gramática 

A gramática fornecida abaixo é um ponto de partida. Ela possui a estrutura geral
mais ou menos correta e vários pequenos errinhos ou pedaços incompletos. Cada
atividade se concenta em um aspecto incorreto e vai progressivamento nos levando
a uma implementação progressivamente mais correta do Ruspy.

```lark
// Um módulo ruspy é uma sequência de declarações de funções.
// O ruspy executa o módulo chamando a função main() sem nenhum argumento, caso
// ela esteja definida.
// Ex:
//  fn fat(n: int) { if n == 0 { 1 } else { n * fat(n - 1) }}
//
//  fn main() {
//      println("fat(5) =", fat(5))
//  }
mod    : fn+

// Declaração de funções
// Ex:
//     fn fat(n: int) {
//         let tot = n;
//         for i in 1..n {
//             tot = tot * i;
//         }
//         return tot
//     }
//
// O ruspy usa a palavra reservada "fn" de forma similar ao "def" do Python.
// A declaração dos argumentos é semelhante e o corpo da função é delimitado por
// chaves ao invés de utilizar indentação.
fn     : "fn" ID "(" args ")" block 
args   : arg+
arg    : ID ":" ID

// Comandos básicos de ruspy. Verifique a declaração de expr_s e expr_b para 
// saber mais.
?cmd   : expr_s ";"       -> cmd
       | expr_b
       | "let" assign ";" -> let

// A sequência de comandos é a porta de entrada do ruspy no modo "eval". Executamos
// cada comando e o valor resultante corresponde ao valor do último elemento da 
// sequência. 
?seq   : cmd+

// Comandos e controle de fluxo (if, for, while)
// Diferentemente do Python, estes comandos podem ser utilizados como valores
// e salvos em variáveis, argumentos de funções, etc.
// Os comandos for e while sempre retornam null como valor final, enquanto o if 
// retorna o último valor do bloco utilizado.
if_    : "if" expr block "else" block
for_   : "for" ID "in" expr block
while_ : "while" expr block

// Bloco de comandos.
// Ex:
//     {x = 1; y = 2; x + y}
//
// Diferentemente do Python, blocos podem ser utilizados em
// qualquer lugar que aceita um valor como em argumentos de funções
// ou valores de variáveis. O valor do bloco corresponde ao do último
// termo. Caso o último termo contenha um ";" como em {x; y;}, o bloco
// retorna o valor nulo e executa os comandos apenas pelos seus efeitos 
// externos como alteração do valor de variáveis, prints, etc. 
block  : "{" seq "}"

// Atribui um valor a um nome
// Ex:
//    x = 42
//
// Uma atribução também pode ser usada como um valor. Neste caso, dizemos que
// o valor da atribuição corresponde ao valor do lado direito.
// Assim, é possível fazer f(x=1, y=2) para ao mesmo tempo salvar os
// valores 1 e 2 nas variáveis x e y como passar estes mesmos valores para a 
// função f.
assign : ID "=" expr

// Valores básicos do Ruspy. Todas alternativas para expr podem ser utilizadas
// como valores. As expressões são divididas em expr_s e expr_b
?expr  : expr_s 
       | expr_b

// Expressões simples. Exigem ";" numa sequência.
expr_s : assign
       | lambd

// Expressões com blocos. O ";" é opcional nas sequências.
// Note que ruspy aceita construções curiosas como 
// 
//     x = { y = 1; z = 2; y + z }
//     a = if x > 2 {
//         z = x * 2;
//         z * z
//     } else {
//         println("x pequeno!");
//         x
//     }
expr_b : block 
       | if_
       | for_
       | while_


// Funções anônimas.
// Ex:
//     |x, y| x + y => lambda x, y: x + y
//
// Lembrando que "lambda x, y: x + y" em python cria uma função equivalente a 
//
//     def f(x, y):
//         return x + y
//
// mas utiliza menos linhas de código. Ruspy é mais flexível porque a expressão
// pode corresponder a um bloco e portanto conter várias linhas de código.
?lambd : "|" args "|" expr
       | range

// Intervalos, incluindo ou não o último elemento
// Ex: 
//  1..5  => 1, 2, 3, 4
//  1..=5 => 1, 2, 3, 4, 5
// Equivale à função range(a, b) do Python. No segundo caso (intervalo inclusivo)
// utilizamos range(a, b + 1), para incluir o valor b em "a ..= b"
?range : and_e ".." and_e
       | and_e "..=" and_e -> irange
       | and_e

// Conectivos lógicos "and" (&&) e "or" (||)
?and_e : and_e "&&" or_e
       | or_e

?or_e  : or_e "||" cmp
       | cmp

// Operadores de comperação
?cmp   : cmp "==" bit      -> eq
       | cmp "!=" bit      -> ne
       | cmp "<"  bit      -> lt
       | cmp ">"  bit      -> gt
       | cmp "<=" bit      -> le
       | cmp ">=" bit      -> ge
       | bit

// Operações bit a bit
?bit   : bit "|" shift     -> or_
       | bit "^" shift     -> xor
       | bit "&" shift     -> and_  
       | shift    

?shift : shift ">>" sum    -> rshift     
       | shift "<<" sum    -> lshift
       | sum

// Operações aritiméticas
?sum   : sum "+" mul       -> add     
       | sum "-" mul       -> sub
       | mul

?mul   : mul "*" typed     -> mul     
       | mul "/" typed     -> div     
       | typed

// Conversão de tipos
// Ex:
//    42 as float => float(42)
//
// Converte valor no lado esquerdo para tipo do lado direito
?typed : typed "as" unary  -> typed     
       | unary

// Operações unárias
// Ex:
//    -x => -x, negativo do número
//    !x => not x, negação lógica
//    x? => verifica se objeto não é nulo. Não será implementado
?unary : "-" atom          -> neg 
       | "!" atom          -> not_ 
       | call "?"          -> opt 
       | call

// Chamada de funções
?call  : ID "(" xargs ")" 
       | attr

?xargs : expr ("," expr)*

// Acesso de atributos como em x.foo.bar.
?attr  : call ("." ID)+
       | ret

// Comandos de controle como return, continue, break.
// Permitidos apenas dentro de loops ou funções.
?ret   : "return" expr   -> ret
       | "continue"      -> loop_continue
       | "break"         -> loop_break
       | atom

?atom  : lit
       | "(" expr ")"

// Símbolos literais
lit    : INT
       | FLOAT
       | RESERVED
       | STRING
       | ID                -> name


// SÍMBOLOS TERMINAIS
//
// Você pode mudar estas regras, mas talvez seja necessário adaptar a regra de 
// "lit" no parser)

// Tipos inteiros
INT          : SIMPLE_INT | BIN_INT | OCT_INT | HEX_INT
SIMPLE_INT   : /0|1|42/
BIN_INT      : /0b101010/ 
OCT_INT      : /0o52/ 
HEX_INT      : /0x2A/ 

// Tipos de ponto-flutante
FLOAT        : FLOAT_SCI | FLOAT_SIMPLE
FLOAT_SCI    : /4.2e+1/
FLOAT_SIMPLE : /42./

// Strings
STRING       : /"string"/

// Nomes de variáveis, valores especiais
ID           : /x|y|z/
RESERVED     : /true|false|null/

// Comentários
COMMENT      : LINE_COMMENT | BLOCK_COMMENT
LINE_COMMENT : "// line comment"
BLOCK_COMMENT: "/* block comment */"

%ignore COMMENT
%ignore /\s+/
```

Uma cópia exata desta gramática está no arquivo "ruspy.lark" neste mesmo repositório.

## Começando os trabalhos

Crie uma cópia do arquivo exemplo.py como ruspy.py e começe a trabalhar! A atividade mais fácil para começar a aquecer provavelmente é a re_basico. Mãos à obra!


## Roteiro sugerido

Vocês podem resolver as questões em qualquer ordem, mas existe uma sequência
natural para se seguir. Podemos dividir as questões em alguns temas independentes
e para cada tema sugiro uma sequência específica:

Ruspy

1. re_basico
2. lex_ler
3. lex_re
5. cfg_list
6. cfg_bnf
7. cfg_ebnf
8. cfg_op
9. cfg_reduce
10. cfg_ast
11. re_prog (ganha automaticamente se lex_re passar)

Autômatos

1. O arquivo test_automatos.py na realidade testa 5 competências: dfa-repr, nfa-repr, nfa-thompson, nfa-epsilon, nfa-dfa

Arquitetura de compiladores

1. comp_org
2. comp_vs_interp

Padrões de expressões regulares

1. re_ler
2. re_pat
3. re_grp