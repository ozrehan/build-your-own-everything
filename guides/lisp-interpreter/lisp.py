#!/usr/bin/env python3
"""
lisp.py -- a tiny Lisp interpreter, built from scratch.

A Lisp interpreter has three classic stages (just like real ones):

    1. TOKENIZE: source text -> flat list of tokens.
    2. PARSE:    tokens -> AST (nested Python lists = S-expressions).
    3. EVALUATE: walk the AST with an environment of variable bindings.

Special forms: define, lambda, if, quote, begin, set!
Builtins: + - * /, = < > <= >=, car cdr cons list null?,
           display newline, not, number?, equal?, length, apply.
Comments start with ';' and run to end of line.

Usage:
    python3 lisp.py               # start the REPL
    python3 lisp.py program.lisp  # run a program file

    (define (fact n) (if (= n 0) 1 (* n (fact (- n 1)))))
    (fact 5)   ; -> 120

Stdlib only. No dependencies.
"""

import sys


class LispError(Exception):
    """Raised for any Lisp-level error (undefined var, bad call, ...)."""


# ---------------------------------------------------------------------------
# Values
# ---------------------------------------------------------------------------

class Str(str):
    """A string literal. Subclassed so the evaluator can tell
    "hello" (literal) apart from hello (a variable name)."""


def is_symbol(x):
    return isinstance(x, str) and not isinstance(x, Str)


# ---------------------------------------------------------------------------
# 1. Tokenizer -- source text -> tokens.
#    Tokens are: '('  ')'  "'"  Str("...")  or plain strings (numbers/symbols).
# ---------------------------------------------------------------------------

def tokenize(src):
    tokens = []
    i, n = 0, len(src)
    while i < n:
        c = src[i]
        if c in " \t\n\r":
            i += 1
        elif c == ";":                       # comment -> skip to newline
            while i < n and src[i] != "\n":
                i += 1
        elif c in "()":
            tokens.append(c)
            i += 1
        elif c == "'":
            tokens.append("'")
            i += 1
        elif c == '"':                        # string literal
            j = i + 1
            buf = []
            while j < n and src[j] != '"':
                if src[j] == "\\" and j + 1 < n:
                    e = src[j + 1]
                    buf.append({"n": "\n", "t": "\t", '"': '"',
                                "\\": "\\"}.get(e, e))
                    j += 2
                else:
                    buf.append(src[j])
                    j += 1
            if j >= n:
                raise LispError("unterminated string literal")
            tokens.append(Str("".join(buf)))
            i = j + 1
        else:                                 # number or symbol
            j = i
            while j < n and src[j] not in " \t\n\r();\"'":
                j += 1
            tokens.append(src[i:j])
            i = j
    return tokens


# ---------------------------------------------------------------------------
# 2. Parser -- tokens -> AST. '(' starts a list, "'" is sugar for (quote x).
# ---------------------------------------------------------------------------

def atom(token):
    if isinstance(token, Str):
        return token
    if token == "#t":
        return True
    if token == "#f":
        return False
    try:
        return int(token)
    except ValueError:
        pass
    try:
        return float(token)
    except ValueError:
        pass
    return token  # a symbol


def parse(tokens):
    """Parse a token list into a list of top-level expressions."""
    exprs = []
    pos = [0]

    def parse_expr():
        if pos[0] >= len(tokens):
            raise LispError("unexpected end of input")
        tok = tokens[pos[0]]
        pos[0] += 1
        if tok == "(":
            lst = []
            while pos[0] < len(tokens) and tokens[pos[0]] != ")":
                lst.append(parse_expr())
            if pos[0] >= len(tokens):
                raise LispError("missing closing ')'")
            pos[0] += 1
            return lst
        if tok == ")":
            raise LispError("unexpected ')'")
        if tok == "'":
            return ["quote", parse_expr()]
        return atom(tok)

    while pos[0] < len(tokens):
        exprs.append(parse_expr())
    return exprs


# ---------------------------------------------------------------------------
# 3. Evaluator -- walk the AST with an environment (a chain of dicts).
# ---------------------------------------------------------------------------

class Env(dict):
    """An environment: a dict of bindings plus a link to the outer scope."""
    def __init__(self, params=(), args=(), outer=None):
        self.update(zip(params, args))
        self.outer = outer

    def find(self, var):
        """The innermost Env where `var` is bound (else LispError)."""
        if var in self:
            return self
        if self.outer is not None:
            return self.outer.find(var)
        raise LispError("undefined variable: %s" % var)


class Proc:
    """A user-defined procedure: parameter names + body + captured env.

    Capturing the defining environment is what makes closures work."""
    def __init__(self, params, body, env):
        self.params = params
        self.body = body
        self.env = env

    def __call__(self, *args):
        if len(args) != len(self.params):
            raise LispError("expected %d argument(s), got %d"
                            % (len(self.params), len(args)))
        return eval_begin(self.body, Env(self.params, args, self.env))

    def __repr__(self):
        return "<procedure>"


def is_true(x):
    # Only #f is false -- everything else (including 0 and '()) is true.
    return x is not False


def eval_begin(exprs, env):
    result = None
    for e in exprs:
        result = evl(e, env)
    return result


def apply_proc(proc, args):
    if isinstance(proc, Proc):
        return proc(*args)
    if callable(proc):
        try:
            return proc(*args)
        except LispError:
            raise
        except Exception as e:
            raise LispError("error in builtin: %s" % e)
    raise LispError("not a function: %s" % to_str(proc))


def evl(x, env):
    """Evaluate one AST node in `env`."""
    # -- atoms ---------------------------------------------------------
    if isinstance(x, Str):      # string literal -> itself
        return x
    if is_symbol(x):            # variable -> look it up
        return env.find(x)[x]
    if not isinstance(x, list):  # numbers, booleans -> themselves
        return x
    if len(x) == 0:
        raise LispError("cannot evaluate empty list ()")

    head, args = x[0], x[1:]

    # -- special forms (head used literally, args NOT all evaluated) ----
    if is_symbol(head):
        if head == "quote":
            if len(args) != 1:
                raise LispError("quote takes exactly 1 argument")
            return args[0]
        if head == "if":
            if len(args) != 3:
                raise LispError("if takes exactly 3 arguments")
            test, conseq, alt = args
            return evl(conseq, env) if is_true(evl(test, env)) \
                else evl(alt, env)
        if head == "define":
            # (define name expr)  or  (define (f params...) body...)
            if isinstance(args[0], list):
                name = args[0][0]
                if not is_symbol(name):
                    raise LispError("bad function name in define")
                env[name] = Proc(args[0][1:], args[1:], env)
            else:
                if not is_symbol(args[0]) or len(args) != 2:
                    raise LispError("bad define syntax")
                env[args[0]] = evl(args[1], env)
            return None
        if head == "lambda":
            # (lambda (params...) body...)
            params = args[0]
            if not isinstance(params, list) or \
                    not all(is_symbol(p) for p in params):
                raise LispError("lambda needs a list of parameter names")
            return Proc(params, args[1:], env)
        if head == "begin":
            return eval_begin(args, env)
        if head == "set!":
            if len(args) != 2 or not is_symbol(args[0]):
                raise LispError("bad set! syntax")
            env.find(args[0])[args[0]] = evl(args[1], env)
            return None

    # -- procedure application: evaluate head and all args, then call --
    return apply_proc(evl(head, env), [evl(a, env) for a in args])


# ---------------------------------------------------------------------------
# Builtins
# ---------------------------------------------------------------------------

def _car(x):
    if not isinstance(x, list) or not x:
        raise LispError("car expects a non-empty list")
    return x[0]


def _cdr(x):
    if not isinstance(x, list) or not x:
        raise LispError("cdr expects a non-empty list")
    return x[1:]


def _cons(a, b):
    if not isinstance(b, list):
        raise LispError("cons expects a list as its second argument")
    return [a] + b


def _div(a, *rest):
    if not rest:
        raise LispError("/ needs at least one divisor")
    result = a
    for b in rest:
        if b == 0:
            raise LispError("division by zero")
        result = result / b
    # Keep ints as ints when the division is exact: (/ 8 2) -> 2
    if isinstance(result, float) and result.is_integer():
        return int(result)
    return result


def standard_env():
    """An Env pre-loaded with all builtin procedures."""
    env = Env()
    env.update({
        "+": lambda *a: sum(a),
        "-": lambda a, *b: a - sum(b) if b else -a,
        "*": lambda *a: _mul(a),
        "/": _div,
        "=": lambda a, b: a == b,
        "<": lambda a, b: a < b,
        ">": lambda a, b: a > b,
        "<=": lambda a, b: a <= b,
        ">=": lambda a, b: a >= b,
        "car": _car,
        "cdr": _cdr,
        "cons": _cons,
        "list": lambda *a: list(a),
        "length": lambda x: _length(x),
        "null?": lambda x: x == [],
        "number?": lambda x: isinstance(x, (int, float))
                             and not isinstance(x, bool),
        "equal?": lambda a, b: a == b,
        "not": lambda x: x is False,
        "display": lambda x: print(to_str(x), end=""),
        "newline": lambda: print(),
        "apply": lambda proc, args: apply_proc(proc, args),
    })
    return env


def _mul(args):
    result = 1
    for a in args:
        result *= a
    return result


def _length(x):
    if not isinstance(x, list):
        raise LispError("length expects a list")
    return len(x)


# ---------------------------------------------------------------------------
# Printing values
# ---------------------------------------------------------------------------

def to_str(x):
    if x is True:
        return "#t"
    if x is False:
        return "#f"
    if isinstance(x, Str):
        return str(x)
    if isinstance(x, str):      # an unevaluated symbol (via quote)
        return x
    if isinstance(x, list):
        return "(" + " ".join(to_str(e) for e in x) + ")"
    if isinstance(x, Proc):
        return "<procedure>"
    if x is None:
        return ""
    return str(x)


# ---------------------------------------------------------------------------
# Running code: eval_str (for tests / embedding), files, REPL
# ---------------------------------------------------------------------------

def eval_str(src, env=None):
    """Evaluate source text; return the last expression's value."""
    env = env if env is not None else standard_env()
    result = None
    for expr in parse(tokenize(src)):
        result = evl(expr, env)
    return result


def run_file(path):
    with open(path) as f:
        src = f.read()
    env = standard_env()
    for expr in parse(tokenize(src)):
        value = evl(expr, env)
        if value is not None:
            print(to_str(value))


def repl():
    env = standard_env()
    print("tiny lisp -- type expressions, Ctrl-D to quit")
    while True:
        try:
            src = input("lisp> ")
        except EOFError:
            print()
            break
        except KeyboardInterrupt:
            print()
            continue
        if not src.strip():
            continue
        try:
            value = eval_str(src, env)
            if value is not None:
                print(to_str(value))
        except LispError as e:
            print("error: %s" % e)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_file(sys.argv[1])
    else:
        repl()
