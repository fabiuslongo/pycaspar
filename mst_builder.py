from phidias.Lib import *
from actions import *



# MST components creations

parse_deps() / DEP("nsubj", X, Y) >> [show_line("\nprocessing nsubj..."), -DEP("nsubj", X, Y), create_MST_ACT(X, Y), parse_deps()]
parse_deps() / DEP("nsubjpass", X, Y) >> [show_line("\nprocessing nsubjpass..."), -DEP("nsubjpass", X, Y), create_MST_ACT_PASS(X, Y), parse_deps()]

parse_deps() / (MST_ACT(X, D, Y, Z) & DEP("xcomp", T, K)) >> [show_line("\nprocessing xcomp...", T), +MST_ACT(K, D, Y, Z), -DEP("xcomp", T, K), parse_deps()]

parse_deps() / (MST_ACT(X, D, Y, Z) & MST_VAR(Z, "?") & DEP("attr", X, K)) >> [show_line("\nprocessing attr..."), -DEP("attr", X, K), -MST_VAR(Z, "?"), +MST_VAR(Z, K), parse_deps()]
parse_deps() / (MST_ACT(X, D, Y, Z) & MST_VAR(Z, "?") & DEP("acomp", X, K)) >> [show_line("\nprocessing acomp..."), -DEP("acomp", X, K), -MST_VAR(Z, "?"), +MST_VAR(Z, K), parse_deps()]
parse_deps() / (MST_ACT(X, D, Y, Z) & MST_VAR(Z, "?") & DEP("dobj", X, K)) >> [show_line("\nprocessing dobj..."), -DEP("dobj", X, K), -MST_VAR(Z, "?"), +MST_VAR(Z, K), parse_deps()]
parse_deps() / (MST_ACT(X, D, Y, Z) & MST_VAR(Z, O) & DEP("oprd", X, K)) >> [show_line("\nprocessing oprd..."), -DEP("oprd", X, K), +MST_BIND(O, K), parse_deps()]
parse_deps() / (MST_ACT(X, D, Y, Z) & DEP("dative", X, K)) >> [show_line("\nprocessing dative..."), -DEP("dative", X, K), create_MST_PREP(D, K), parse_deps()]
parse_deps() / (MST_ACT(X, D, Y, Z) & DEP("prep", X, K)) >> [show_line("\nprocessing action prep..."), -DEP("prep", X, K), create_MST_PREP(D, K), parse_deps()]



parse_deps() / (MST_VAR(V, X) & DEP("compound", X, Y)) >> [show_line("\nprocessing compound..."), -DEP("compound", X, Y), +MST_COMP(X, Y), parse_deps()]
parse_deps() / (MST_VAR(V, X) & DEP("amod", X, Y)) >> [show_line("\nprocessing amod..."), -DEP("amod", X, Y), +MST_BIND(X, Y), parse_deps()]

parse_deps() / (MST_VAR(V, X) & MST_BIND(X, Y) & DEP("prep", Y, K)) >> [show_line("\nprocessing bind prep..."), -DEP("prep", Y, K), create_MST_PREP(V, K), parse_deps()]
parse_deps() / (MST_VAR(V, X) & DEP("prep", X, K)) >> [show_line("\nprocessing prep..."), -DEP("prep", X, K), create_MST_PREP(V, K), parse_deps()]

parse_deps() / (MST_PREP(X, Y, Z) & DEP("pobj", X, O) & MST_VAR(Z, "?")) >> [show_line("\nprocessing pobj..."), -MST_VAR(Z, "?"), -DEP("pobj", X, O), +MST_VAR(Z, O), parse_deps()]

# Conditionals/Adverbs
parse_deps() / (MST_ACT(X, D, Y, Z) & DEP("advmod", X, K) & COND_WORD(K)) >> [show_line("\nprocessing conditional..."), -DEP("advmod", X, K), +MST_COND(D), parse_deps()]
parse_deps() / (MST_ACT(X, D, Y, Z) & DEP("advmod", X, K)) >> [show_line("\nprocessing advmod..."), -DEP("advmod", X, K), +MST_VAR(D, K), parse_deps()]
parse_deps() / (MST_ACT(X, D, Y, Z) & DEP("npadvmod", X, K)) >> [show_line("\nprocessing npadvmod..."), -DEP("npadvmod", X, K), +MST_VAR(D, K), parse_deps()]
parse_deps() / (MST_ACT(X, D, Y, Z) & DEP("neg", X, K)) >> [show_line("\nprocessing neg..."), -DEP("neg", X, K), +MST_VAR(D, K), parse_deps()]


parse_deps() / (MST_ACT(X, D, Y, Z) & DEP("mark", X, K) & NBW(K)) >> [show_line("\nprocessing mark..."), -DEP("mark", X, K), +MST_COND(D), parse_deps()]

parse_deps() / (MST_ACT(X, D, Y, Z) & MST_VAR(Y, "?") & DEP("agent", X, K) & DEP("pobj", K, O)) >> [show_line("\nprocessing agent..."), -MST_VAR(Y, "?"), -DEP("agent", X, K), -DEP("pobj", K, O), +MST_VAR(Y, O), parse_deps()]


parse_deps() / (MST_ACT(X, D, Y, Z) & MST_ACT(T, E, W, K) & DEP("ccomp", X, T)) >> [show_line("\nprocessing ccomp..."), -DEP("ccomp", X, T), -MST_ACT(X, D, Y, Z), +MST_ACT(X, D, Y, E), parse_deps()]
parse_deps() / (DEP("ccomp", X, Y)) >> [show_line("\nprocessing ccomp as nsubj..."), -DEP("ccomp", X, Y), create_MST_ACT(X, Y), parse_deps()]


parse_deps() / (MST_ACT(X, D, Y, Z) & MST_ACT(T, D, Y, Z) & neq(X, T)) >> [show_line("\nconcat composite verbals..."), -MST_ACT(X, D, Y, Z), -MST_ACT(T, D, Y, Z), concat_mst_verbs(X, T, D, Y, Z), parse_deps()]

parse_deps() / (MST_ACT(X, D, Y, Z) & MST_VAR(W, K) & DEP("relcl", K, X) & Past_Part(X)) >> [show_line("\nprocessing relcl pp..."), -DEP("relcl", K, X), -MST_ACT(X, D, Y, Z), +MST_ACT(X, D, Y, W), parse_deps()]
parse_deps() / (MST_ACT(X, D, Y, Z) & MST_VAR(W, K) & MST_VAR(Z, U) & DEP("relcl", K, X) & Wh_Det(U)) >> [show_line("\nprocessing relcl wh..."), -DEP("relcl", K, X), -MST_ACT(X, D, Y, Z), +MST_ACT(X, D, Y, W), parse_deps()]
parse_deps() / (MST_ACT(X, D, Y, Z) & MST_VAR(W, K) & DEP("relcl", K, X)) >> [show_line("\nprocessing relcl..."), -DEP("relcl", K, X), -MST_ACT(X, D, Y, Z), +MST_ACT(X, D, W, Z), parse_deps()]

parse_deps() / (DEP("relcl", X, Y) & MST_VAR(W, X) & MST_ACT(T, D, U, W)) >> [show_line("\nprocessing relcl as nsubj..."), -DEP("relcl", X, Y), +MST_ACT(Y, D, U, W), parse_deps()]

parse_deps() / (MST_ACT(X, D, Y, Z) & MST_ACT(T, D, Y, Z) & neq(X, T)) >> [show_line("\nconcat composite verbals..."), -MST_ACT(X, D, Y, Z), -MST_ACT(T, D, Y, Z), concat_mst_verbs(X, T, D, Y, Z), parse_deps()]


parse_deps() / DEP("ROOT", X, X) >> [show_line("\nremoving ROOT..."), -DEP("ROOT", X, X), parse_deps()]
parse_deps() / DEP(Z, X, Y) >> [show_line("\nremoving ", Z), -DEP(Z, X, Y), parse_deps()]


"""
# Feeding parser's MST components section
feed_mst() / MST_ACT(X, Y, Z, T) >> [show_line("\nfeeding MST with an action..."), -MST_ACT(X, Y, Z, T), feed_mst_actions_parser(X, Y, Z, T), feed_mst()]
feed_mst() / MST_VAR(X, Y) >> [show_line("\nfeeding MST with a var..."), -MST_VAR(X, Y), feed_mst_vars_parser(X, Y), feed_mst()]
feed_mst() / MST_BIND(X, Y) >> [show_line("\nfeeding MST with a bind..."), -MST_BIND(X, Y), feed_mst_binds_parser(X, Y), feed_mst()]
feed_mst() / MST_PREP(X, Y, Z) >> [show_line("\nfeeding MST with a prep..."), -MST_PREP(X, Y, Z), feed_mst_preps_parser(X, Y, Z), feed_mst()]
feed_mst() / MST_COMP(X, Y) >> [show_line("\nfeeding MST a comp..."), -MST_COMP(X, Y), feed_mst_comps_parser(X, Y), feed_mst()]
feed_mst() / MST_COND(X) >> [show_line("\nfeeding MST with a cond..."), -MST_COND(X), feed_mst_conds_parser(X), feed_mst()]
"""



