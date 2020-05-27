

from utils import (
    first, issequence, Expr, expr, subexpressions
)

import itertools
import copy

# ______________________________________________________________________________


class KB:

    """A knowledge base to which you can tell and ask sentences.
    To create a KB, first subclass this class and implement
    tell, ask_generator, and retract.  Why ask_generator instead of ask?
    The book is a bit vague on what ask means --
    For a Propositional Logic KB, ask(P & Q) returns True or False, but for an
    FOL KB, something like ask(Brother(x, y)) might return many substitutions
    such as {x: Cain, y: Abel}, {x: Abel, y: Cain}, {x: George, y: Jeb}, etc.
    So ask_generator generates these one at a time, and ask either returns the
    first one or returns False."""

    def __init__(self, sentence=None):
        raise NotImplementedError

    def tell(self, sentence):
        """Add the sentence to the KB."""
        raise NotImplementedError

    def ask(self, query):
        """Return a substitution that makes the query true, or, failing that, return False."""
        return first(self.ask_generator(query), default=False)

    def ask_generator(self, query):
        """Yield all the substitutions that make query true."""
        raise NotImplementedError

    def retract(self, sentence):
        """Remove sentence from the KB."""
        raise NotImplementedError



def KB_AgentProgram(KB):
    """A generic logical knowledge-based agent program. [Figure 7.1]"""
    steps = itertools.count()

    def program(percept):
        t = next(steps)
        KB.tell(make_percept_sentence(percept, t))
        action = KB.ask(make_action_query(t))
        KB.tell(make_action_sentence(action, t))
        return action

    def make_percept_sentence(percept, t):
        return Expr("Percept")(percept, t)

    def make_action_query(t):
        return expr("ShouldDo(action, {})".format(t))

    def make_action_sentence(action, t):
        return Expr("Did")(action[expr('action')], t)

    return program


def is_symbol(s):
    """A string s is a symbol if it starts with an alphabetic char.
    >>> is_symbol('R2D2')
    True
    """
    return isinstance(s, str) and s[:1].isalpha()


def is_var_symbol(s):
    """A logic variable symbol is an initial-lowercase string.
    >>> is_var_symbol('EXE')
    False
    """
    return is_symbol(s) and s[0].islower()


def is_prop_symbol(s):
    """A proposition logic symbol is an initial-uppercase string.
    >>> is_prop_symbol('exe')
    False
    """
    return is_symbol(s) and s[0].isupper()


def variables(s):
    """Return a set of the variables in expression s.
    >>> variables(expr('F(x, x) & G(x, y) & H(y, z) & R(A, z, 2)')) == {x, y, z}
    True
    """
    return {x for x in subexpressions(s) if is_variable(x)}


def is_definite_clause(s):
    """Returns True for exprs s of the form A & B & ... & C ==> D,
    where all literals are positive.  In clause form, this is
    ~A | ~B | ... | ~C | D, where exactly one clause is positive.
    >>> is_definite_clause(expr('Farmer(Mac)'))
    True
    """
    if is_symbol(s.op):
        return True
    elif s.op == '==>':
        antecedent, consequent = s.args
        return (is_symbol(consequent.op) and
                all(is_symbol(arg.op) for arg in conjuncts(antecedent)))
    else:
        return False


def parse_definite_clause(s):
    """Return the antecedents and the consequent of a definite clause."""
    assert is_definite_clause(s)
    if is_symbol(s.op):
        return [], s
    else:
        antecedent, consequent = s.args
        return conjuncts(antecedent), consequent




def dissociate(op, args):
    """Given an associative op, return a flattened list result such
    that Expr(op, *result) means the same as Expr(op, *args).
    >>> dissociate('&', [A & B])
    [A, B]
    """
    result = []

    def collect(subargs):
        for arg in subargs:
            if arg.op == op:
                collect(arg.args)
            else:
                result.append(arg)
    collect(args)
    return result


def conjuncts(s):
    """Return a list of the conjuncts in the sentence s.
    >>> conjuncts(A & B)
    [A, B]
    >>> conjuncts(A | B)
    [(A | B)]
    """
    return dissociate('&', [s])





def unify(x, y, s={}):
    """Unify expressions x,y with substitution s; return a substitution that
    would make x,y equal, or None if x,y can not unify. x and y can be
    variables (e.g. Expr('x')), constants, lists, or Exprs. [Figure 9.1]
    >>> unify(x, 3, {})
    {x: 3}
    """
    if s is None:
        return None
    elif x == y:
        return s
    elif is_variable(x):
        return unify_var(x, y, s)
    elif is_variable(y):
        return unify_var(y, x, s)
    elif isinstance(x, Expr) and isinstance(y, Expr):
        return unify(x.args, y.args, unify(x.op, y.op, s))
    elif isinstance(x, str) or isinstance(y, str):
        return None
    elif issequence(x) and issequence(y) and len(x) == len(y):
        if not x:
            return s
        return unify(x[1:], y[1:], unify(x[0], y[0], s))
    else:
        return None


def is_variable(x):
    """A variable is an Expr with no args and a lowercase symbol as the op."""
    return isinstance(x, Expr) and not x.args and x.op[0].islower()


def unify_var(var, x, s):
    if var in s:
        return unify(s[var], x, s)
    elif x in s:
        return unify(var, s[x], s)
    elif occur_check(var, x, s):
        return None
    else:
        return extend(s, var, x)


def occur_check(var, x, s):
    """Return true if variable var occurs anywhere in x
    (or in subst(s, x), if s has a binding for x)."""
    if var == x:
        return True
    elif is_variable(x) and x in s:
        return occur_check(var, s[x], s)
    elif isinstance(x, Expr):
        return (occur_check(var, x.op, s) or
                occur_check(var, x.args, s))
    elif isinstance(x, (list, tuple)):
        return first(e for e in x if occur_check(var, e, s))
    else:
        return False


def extend(s, var, val):
    """Copy the substitution s and extend it by setting var to val; return copy.
    >>> extend({x: 1}, y, 2) == {x: 1, y: 2}
    True
    """
    s2 = s.copy()
    s2[var] = val
    return s2


def subst(s, x):
    """Substitute the substitution s into the expression x.
    >>> subst({x: 42, y:0}, F(x) + y)
    (F(42) + 0)
    """
    if isinstance(x, list):
        return [subst(s, xi) for xi in x]
    elif isinstance(x, tuple):
        return tuple([subst(s, xi) for xi in x])
    elif not isinstance(x, Expr):
        return x
    elif is_var_symbol(x.op):
        return s.get(x, x)
    else:
        return Expr(x.op, *[subst(s, arg) for arg in x.args])


def standardize_variables(sentence, dic=None):
    """Replace all the variables in sentence with new variables."""
    if dic is None:
        dic = {}
    if not isinstance(sentence, Expr):
        return sentence
    elif is_var_symbol(sentence.op):
        if sentence in dic:
            return dic[sentence]
        else:
            v = Expr('v_{}'.format(next(standardize_variables.counter)))
            dic[sentence] = v
            return v
    else:
        return Expr(sentence.op,
                    *[standardize_variables(a, dic) for a in sentence.args])


standardize_variables.counter = itertools.count()

# ______________________________________________________________________________


class FolKB(KB):

    def __init__(self, initial_clauses=None):
        self.clauses = []  # inefficient: no indexing
        if initial_clauses:
            for clause in initial_clauses:
                self.tell(clause)

    def tell(self, sentence):
        if is_definite_clause(sentence):
            self.clauses.append(sentence)
        else:
            raise Exception("Not a definite clause: {}".format(sentence))

    def ask_generator(self, query):
        return fol_bc_ask(self, query)

    def retract(self, sentence):
        self.clauses.remove(sentence)

    def fetch_rules_for_goal(self, goal):
        return self.clauses

    def fetch_rules(self):
        return self.clauses

    def produce_goals_complete(self, goal, candidates, depth, number_of_calls):
        return produce_goals_inner_complete(self, goal, candidates, depth, number_of_calls)

    def produce_goals_sound(self, goal, candidates, depth, number_of_calls):
        return produce_goals_inner_sound(self, goal, candidates, depth, number_of_calls)

    def nested_tell(self, def_clause):
        return nested_tell_inner(self, def_clause)




def nested_tell_inner(KB, def_clause):
    if def_clause not in KB.clauses:

        candidates = []
        number_of_calls = 0

        # produce_clauses applied only to single positive literals
        if len(str(def_clause).split("==>")) == 1:
            KB.produce_goals_complete(def_clause, candidates, 0, number_of_calls)
            for cand in candidates:
                if cand != def_clause:
                    print("\nDerived literale: ", cand)
                    new_implication = str(def_clause) + " ==> " + str(cand)
                    print("\nDerived implication: ", new_implication)
                    KB.tell(expr(new_implication))

        KB.tell(def_clause)

        print("\nDone.\n")
    else:
        print("\nDefinite clause already present in the kb.\n")




def expr_to_string(e):
    str = ""
    for i in range(len(e)):
        if i == 0:
            str = e[i]
        else:
            str = str + ", " + e[i]
    return str


def produce_goals_inner_complete(KB, goal, candidates, depth, number_of_calls):

    print("\n\n")
    print("My goal is ", goal)
    print("My candidates is ", candidates)
    print("My depth is ", depth)
    number_of_calls = number_of_calls + 1
    print("Number of calls till now ", number_of_calls)

    if goal not in KB.clauses:
        print("\n")

        print("Goal not in KB!")
        for q in KB.clauses:
            print("\nConsidering clause ", q)
            lhs, rhs = parse_definite_clause(q)
            print("\twhose lhs is ", lhs)
            print("\twhose rhs is ", rhs)
            print("\t\tGoal is", goal)
            args_list = list(goal.args)
            for n, arg in enumerate(args_list):
                print("\t\t\tConsidering argument ", arg)
                lhs_str = expr_to_string(lhs)
                if unify(lhs_str, arg) is not None:
                    print("\t\t\t\tUnify with", lhs_str, "is not None")
                    args_list[n] = rhs
                    new_goal = copy.deepcopy(goal)
                    new_goal.args = tuple(args_list)
                    print("\t\t\t\t\tNew goal is ", new_goal)
                    print("\t\t\t\t\tCandidates is ", candidates)
                    if new_goal not in candidates:
                        print("\t\t\t\t\tNew goal", new_goal, "is not in candidates")
                        candidates.append(new_goal)
                        print("\t\t\t\t\tNow candidates is ", candidates)
                        produce_goals_inner_complete(KB, new_goal, candidates, depth + 1, number_of_calls)
                else:
                    print("\t\t\t\tUnify is None.")
        print("All clauses analyzed!")


def produce_goals_inner_sound(KB, goal, candidates, depth, number_of_calls):

    print("\n\n")
    print("My goal is ", goal)
    print("My candidates is ", candidates)
    print("My depth is ", depth)
    number_of_calls = number_of_calls + 1
    print("Number of calls till now ", number_of_calls)

    if goal not in KB.clauses:
        print("\n")

        print("Goal not in KB!")
        for q in KB.clauses:
            print("\nConsidering clause ", q)
            lhs, rhs = parse_definite_clause(standardize_variables(q))
            print("\twhose lhs is ", lhs)
            print("\twhose rhs is ", rhs)
            print("\t\tGoal is", goal)
            args_list = list(goal.args)
            for n, arg in enumerate(args_list):
                print("\t\t\tConsidering argument ", arg)
                lhs_str = expr_to_string(lhs)
                if unify(lhs_str, arg) is not None:
                    print("\t\t\t\tUnify with", lhs_str, "is not None")
                    args_list[n] = rhs
                    new_goal = copy.deepcopy(goal)
                    new_goal.args = tuple(args_list)
                    print("\t\t\t\t\tNew goal is ", new_goal)
                    print("\t\t\t\t\tCandidates is ", candidates)
                    if new_goal not in candidates:
                        print("\t\t\t\t\tNew goal", new_goal, "is not in candidates")
                        candidates.append(new_goal)
                        print("\t\t\t\t\tNow candidates is ", candidates)
                        if (KB.ask(expr(new_goal)) != False):
                            return str(KB.ask(expr(new_goal)))
                        else:
                            return produce_goals_inner_sound(KB, new_goal, candidates, depth + 1,
                                                                     number_of_calls)
                else:
                    print("\t\t\t\tUnify is None.")
        print("All clauses analyzed!")
        return False;



def fol_bc_ask(KB, query):
    """A simple backward-chaining algorithm for first-order logic. [Figure 9.6]
    KB should be an instance of FolKB, and query an atomic sentence."""
    return fol_bc_or(KB, query, {})


def fol_bc_or(KB, goal, theta):
    for rule in KB.fetch_rules_for_goal(goal):
        lhs, rhs = parse_definite_clause(standardize_variables(rule))
        for theta1 in fol_bc_and(KB, lhs, unify(rhs, goal, theta)):
            yield theta1


def fol_bc_and(KB, goals, theta):
    if theta is None:
        pass
    elif not goals:
        yield theta
    else:
        first, rest = goals[0], goals[1:]
        for theta1 in fol_bc_or(KB, subst(theta, first), theta):
            for theta2 in fol_bc_and(KB, rest, theta1):
                yield theta2







