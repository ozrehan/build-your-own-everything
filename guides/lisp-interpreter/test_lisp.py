#!/usr/bin/env python3
"""Tests for lisp.py -- run with: python3 test_lisp.py"""
import os
import subprocess
import sys
import tempfile

from lisp import eval_str, standard_env, LispError, tokenize, parse, to_str

passed = failed = 0
HERE = os.path.dirname(os.path.abspath(__file__))


def check(name, got, want):
    global passed, failed
    if got == want and type(got) == type(want):
        passed += 1
        print("ok   " + name)
    else:
        failed += 1
        print("FAIL %s: got %r (%s), want %r (%s)"
              % (name, got, type(got).__name__, want, type(want).__name__))


def check_raises(name, src):
    global passed, failed
    try:
        eval_str(src, standard_env())
    except LispError:
        passed += 1
        print("ok   " + name)
    except Exception as e:
        failed += 1
        print("FAIL %s: wrong exception %r" % (name, e))
    else:
        failed += 1
        print("FAIL %s: no LispError raised" % name)


def ev(src):
    return eval_str(src, standard_env())


# --- tokenizer / parser ---------------------------------------------------------
check("tokenize basics", tokenize("(+ 1 2)"), ["(", "+", "1", "2", ")"])
check("tokenize quote", tokenize("'(1 2)"), ["'", "(", "1", "2", ")"])
check("comment skipped", tokenize("; hi\n(+ 1 2)"), ["(", "+", "1", "2", ")"])
check("parse nested", parse(tokenize("(a (b 1))")), [["a", ["b", 1]]])

# --- arithmetic ---------------------------------------------------------------------
check("add", ev("(+ 1 2 3)"), 6)
check("add none", ev("(+)"), 0)
check("subtract", ev("(- 10 3 2)"), 5)
check("negate", ev("(- 5)"), -5)
check("multiply", ev("(* 2 3 4)"), 24)
check("divide exact", ev("(/ 8 2)"), 4)
check("divide float", ev("(/ 7 2)"), 3.5)
check("nested arith", ev("(* (+ 1 2) (- 10 4))"), 18)

# --- comparisons ----------------------------------------------------------------------
check("less", ev("(< 1 2)"), True)
check("greater false", ev("(> 1 2)"), False)
check("equal nums", ev("(= 3 3)"), True)
check("gte", ev("(>= 5 5)"), True)
check("lte false", ev("(<= 5 4)"), False)

# --- define / if / begin -----------------------------------------------------------------
check("define + use", ev("(define x 10) (+ x 5)"), 15)
check("if true", ev("(if (> 3 2) 10 20)"), 10)
check("if false", ev("(if #f 1 2)"), 2)
check("if only #f is false", ev("(if 0 1 2)"), 1)
check("begin", ev("(begin 1 2 3)"), 3)
check("set!", ev("(define x 1) (set! x 2) x"), 2)
check("define fn shorthand", ev("(define (sq n) (* n n)) (sq 9)"), 81)

# --- lambda & closures ----------------------------------------------------------------------
check("lambda immediate", ev("((lambda (x) (* x x)) 7)"), 49)
check("closure captures env",
      ev("(define (make-adder x) (lambda (y) (+ x y)))"
         " (define add3 (make-adder 3)) (add3 10)"), 13)
check("closure keeps separate state",
      ev("(define (counter) (define n 0)"
         "  (lambda () (set! n (+ n 1)) n))"
         " (define c (counter)) (c) (c) (c)"), 3)

# --- recursion: factorial -----------------------------------------------------------------------
fact_prog = ("(define (fact n) (if (= n 0) 1 (* n (fact (- n 1)))))"
             " (fact 5)")
check("factorial recursion", ev(fact_prog), 120)
check("factorial base", ev("(define (fact n) (if (= n 0) 1 (* n (fact (- n 1)))))"
                           " (fact 0)"), 1)

# --- quote -------------------------------------------------------------------------------------------
check("quote list", ev("'(1 2 3)"), [1, 2, 3])
check("quote symbol", ev("'a"), "a")
check("quote nested", ev("'((1 2) 3)"), [[1, 2], 3])
check("quote not evaluated", ev("(quote (+ 1 2))"), ["+", 1, 2])
check("car of quoted", ev("(car '(4 5))"), 4)
check("cdr of quoted", ev("(cdr '(4 5))"), [5])

# --- list ops -------------------------------------------------------------------------------------------
check("cons", ev("(cons 1 '(2 3))"), [1, 2, 3])
check("list", ev("(list 1 2 3)"), [1, 2, 3])
check("null? true", ev("(null? '())"), True)
check("null? false", ev("(null? '(1))"), False)
check("length", ev("(length '(a b c))"), 3)
check("equal?", ev("(equal? '(1 2) '(1 2))"), True)
check("number?", ev("(number? 42)"), True)
check("not", ev("(not #f)"), True)

# --- strings & comments ------------------------------------------------------------------------------------
# (string literals evaluate to a Str subclass of str -- compare by value)
_got = ev('"hello"')
if isinstance(_got, str) and str(_got) == "hello":
    passed += 1
    print("ok   string literal")
else:
    failed += 1
    print("FAIL string literal: got %r" % (_got,))
check("comment in code", ev("; a comment\n(+ 1 2) ; trailing"), 3)

# --- errors -----------------------------------------------------------------------------------------------------
check_raises("undefined variable", "(+ x 1)")
check_raises("undefined function", "(frobnicate 1 2)")
check_raises("call non-function", "(1 2 3)")
check_raises("car of non-list", "(car 5)")
check_raises("car of empty", "(car '())")
check_raises("cons bad 2nd arg", "(cons 1 2)")
check_raises("div by zero", "(/ 1 0)")
check_raises("wrong arg count", "((lambda (a b) a) 1)")
check_raises("unbalanced paren", "(+ 1 2")
check_raises("stray paren", "(+ 1 2))")
check_raises("empty application", "()")
check_raises("if wrong arity", "(if #t 1)")

# --- to_str printing -----------------------------------------------------------------------------------------------
check("print true", to_str(True), "#t")
check("print false", to_str(False), "#f")
check("print list", to_str([1, [2, 3]]), "(1 (2 3))")

# --- program file mode: `python3 lisp.py program.lisp` ------------------------------------------------------------------
with tempfile.NamedTemporaryFile("w", suffix=".lisp", delete=False) as f:
    f.write("; factorial program\n"
            "(define (fact n) (if (= n 0) 1 (* n (fact (- n 1)))))\n"
            "(fact 5)\n")
    prog = f.name
try:
    r = subprocess.run([sys.executable, os.path.join(HERE, "lisp.py"), prog],
                       capture_output=True, text=True, timeout=30)
    check("lisp.py file mode runs", r.returncode == 0, True)
    check("lisp.py file prints 120", r.stdout.strip().split()[-1], "120")
finally:
    os.unlink(prog)

print("\n%d passed, %d failed" % (passed, failed))
raise SystemExit(1 if failed else 0)
