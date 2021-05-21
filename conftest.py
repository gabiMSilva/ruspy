"""
Funcionalidades compartilhadas por todos modulos de teste
"""
from pprint import pformat
from base64 import b64encode
from hashlib import md5
from functools import singledispatch, wraps
import json
from types import SimpleNamespace
from random import choice, random, randint
import pytest
import lark
import os
from pathlib import Path
from hypothesis import settings

settings.register_profile("fast", max_examples=25)
PATH = Path(__file__).parent
EXTRA_SRC = r'''
class _fn:
    def __init__(self, fn):
        self.fn = fn

    def __repr__(self):
        return self.fn.__name__

    def __call__(self, src):
        return self.fn(src)
        

grammar_seq = Lark(GRAMMAR, parser="lalr", start="seq")
grammar_expr = Lark(GRAMMAR, parser="lalr", start="expr")
grammar_mod = Lark(GRAMMAR, parser="lalr", start="mod")

@_fn
def eval(src):
    return _eval_or_exec(src, grammar_seq)

@_fn
def expr(src):
    return _eval_or_exec(src, grammar_expr)

@_fn
def module(src) -> dict:
    return _eval_or_exec(src, grammar_mod)

@_fn
def run(src):
    mod = module(src)
    main = mod.get("main")
    if not main:
        raise RuntimeError('módulo não define uma função "main()"')
    main()

def _eval_or_exec(src: str, grammar) -> Any:
    try:
        tree = grammar.parse(src)
    except LarkError as ex:
        lines = [
            f"Erro avaliando a expressão: \n{src}",
            "",
            "Imprimindo tokens",
            *(f" - {i}) {tk} ({tk.type})" for i, tk in enumerate(grammar.lex(src), start=1)),
        ]
        prefix = '\n'.join(lines)
        raise lark.LarkError(f'{prefix}\n\n{type(ex).__name__}: {ex}')
    transformer = RuspyTransformer()
    result = transformer.transform(tree)

    if isinstance(result, Tree):
        bad = find_bad(tree)
        raise NotImplementedError(
            f"""
{tree.pretty()}

não implementou regra para lidar com: {bad.data!r}.
Crie um método como abaixo na classe do transformer.

    def {bad.data}(self, ...): 
        return ... 

Em casos simples, é possível simplificar a gramática como, por exemplo, 
acrescentando um operador de ? antes do nome da regra.
"""
        )
    return result
'''


@pytest.fixture(scope="session")
def mod():
    mod = os.environ.get("RUSPY", "")
    if mod:
        mod = "-" + mod
    path = Path.cwd() / ("ruspy" + mod + ".py")
    if not mod and not path.exists():
        path = Path.cwd() / "ruspy-tmp.py"

    with open(path, "rb") as fd:
        src = fd.read()
    ns = {}
    exec(compile(src, "ruspy.py", "exec"), ns)
    ns_orig = ns.copy()

    if "GRAMMAR" not in ns:
        raise ValueError("não é permitido modificar o nome da variável GRAMMAR")
    if not isinstance(ns["GRAMMAR"], str):
        raise ValueError("a gramática deve ser uma string")
    if "RuspyTransformer" not in ns:
        raise ValueError("Não encontrou o RuspyTransformer")

    exec(compile(EXTRA_SRC, "extra.py", "exec"), ns)
    lex = ns["grammar_expr"].lex
    transformer = ns["RuspyTransformer"]
    lark.InlineTransformer

    def find_bad(bad: lark.Tree):
        bads = [*bad.find_pred(lambda x: not hasattr(transformer, x.data))]
        return bads[0] if bads else bad

    ns["find_bad"] = find_bad

    def parse(src):
        try:
            return ns["grammar_mod"].parse(src)
        except:
            try:
                return ns["grammar_expr"].parse(src)
            except:
                return ns["grammar_seq"].parse(src)

    def pretty(obj):
        try:
            return obj.pretty()
        except AttributeError:
            return pformat(obj)

    def var(name, **kwargs):
        try:
            res = ns_orig[name]
        except KeyError:
            raise ValueError(
                f"Não encontrei a variável {name}. Ela está declarada no código?"
            )
        check_value(res, name=name, **kwargs)
        return res

    def check_value(value, type=object, hash=None, check=(), name="var"):
        if not isinstance(value, type):
            raise ValueError(
                f"Esperava que {name} fosse um(a) {type.__name__}, mas obtive {type(value).__name__}."
            )

        for fn in check:
            fn(value)

        if hash is not None:
            computed = human_hash(value)
            assert computed == hash, (
                f"hash inválida para {name}:\n"
                f"  - obtida: {computed}\n"
                f"  - esperada: {hash}"
                f"{print(value) or ''}\n"
                f"O valor obtido não corresponde ao registrado no banco de respostas.\n"
            )

    return SimpleNamespace(
        **{
            **ns,
            **{
                "lex": lex,
                "var": var,
                "check_value": check_value,
                "parse": parse,
                "parse_seq": ns["grammar_seq"].parse,
                "parse_expr": ns["grammar_expr"].parse,
                "parse_mod": ns["grammar_mod"].parse,
                "lex_list": lambda s: list(lex(s)),
                "transformer": transformer,
                "transform": lambda ast: [*transformer()._transform_children([ast])][0],
                "check_int": check_int,
                "prob": prob,
                "digit": digit,
                "randrange": randrange,
                "rint": rint,
                "data": data_fn,
                "leaves": leaves,
                "pretty": pretty,
                "PATH": PATH,
            },
        }
    )


@pytest.fixture(scope="session")
def data():
    return data_fn


@pytest.fixture(scope="session")
def var(mod):
    return mod.var


@pytest.fixture(scope="session")
def check_value(mod):
    return mod.check_value


@pytest.fixture(scope="session")
def fn(mod):
    return Validators().namespace()


prob = lambda p: random() < p
digit = lambda ds="123456789": choice(ds)
randrange = lambda a, b: range(a, randint(a, b) + 1)
rint = lambda: (
    digit() + "".join("_" if prob(0.25) else digit() for _ in randrange(0, 10))
)


def check_int(ex: str):
    n = ex.replace("_", "")
    assert not ex.startswith("_")
    assert n
    assert n.isdigit()


def data_fn(name):
    if name.endswith('.py'):
        with open(PATH / "data" / name, encoding="utf8") as fd:
            return fd.read()
    
    with open(PATH / "data" / (name + ".json"), encoding="utf8") as fd:
        return json.load(fd)


def leaves(tree):
    leaves = []

    def visit(node):
        for child in node.children:
            if isinstance(child, lark.Tree):
                visit(child)
            else:
                leaves.append(child)

    visit(tree)
    return leaves


def human_hash(x):
    h = special_hash(x)
    return b64encode(h).decode("ascii")


@singledispatch
def special_hash(x) -> bytes:
    raise NotImplementedError


@special_hash.register(int)
def _int(x):
    return b64encode(x.to_bytes(32, "").lstrip("\x00"))


@special_hash.register(str)
def _str(x):
    hasher = md5(x.encode("utf8"))
    return hasher.digest()


@special_hash.register(tuple)
@special_hash.register(list)
def _seq(xs):
    hasher = md5()
    for x in xs:
        hasher.update(special_hash(x))
    return f"{len(xs)}:".encode("ascii") + hasher.digest()


class Validators:
    METHODS = ["size"]

    def namespace(self):
        return SimpleNamespace(
            **{k: self.validator(getattr(self, k)) for k in self.METHODS}
        )

    def validator(self, fn):
        @wraps(fn)
        def func(*args):
            return lambda data: fn(data, *args)

        return func

    def size(self, data, size):
        if (n := len(data)) != size:
            raise AssertionError(
                f"tamanho incorreto: esperava {size}, mas obteve {n}\n"
                f"    valor inválido: {data}"
            )
