from phidias.Main import *
from phidias.Lib import *

from sensors import *
from actions import *



def_vars('X', 'Y', 'Z', 'T', 'W', 'K', 'J', 'M', 'N', "D", "I", "V", "L", "O", "E", "U")


# SIMULATING EVENTS

# simulating routines
r1() >> [+STT("turn off the lights in the living room, when the temperature is 25 and the time is 12.00")]
r2() >> [+STT("set the cooler in the bedroom to 25 degrees and cut the grass in the garden, when the time is 12.00")]

# simulating direct commands
d1() >> [+STT("set the cooler at 27 degrees in the bedroom")]
d2() >> [+STT("turn off the lights in the living room")]

# definite clauses for reasoning purposes
c1() >> [+STT("Nono is an hostile nation")]
c2() >> [+STT("Colonel West is American")]
c3() >> [+STT("missiles are weapons")]
c4() >> [+STT("Colonel West sells missiles to Nono")]
c5() >> [+STT("When an American sells weapons to a hostile nation, that American is a criminal")]

# Query
q() >> [+STT("Colonel West is a criminal")]


# simulating keywords
w() >> [+HOTWORD_DETECTED("ON")]
l() >> [+STT("listen")]
r() >> [+STT("reason")]

# simulating sensors
s1() >> [simulate_sensor("be", "time", "12.00")]
s2() >> [simulate_sensor("be", "temperature", "25")]

# test assertions
t() >> [go(), w(), l()]




# Front-End STT

# Start agent command
go() >> [show_line("Starting Caspar..."), set_wait(), HotwordDetect().start]

# show Clauses kb
s() >> [show_fol_kb()]
# initialize Clauses Kb
c() >> [clear_clauses_kb()]

# Hotwords processing
+HOTWORD_DETECTED("ON") / WAIT(W) >> [show_line("\n\nYes, I'm here!\n"), HotwordDetect().stop, UtteranceDetect().start, +WAKE("ON"), Timer(W).start]
+STT("listen") / (WAKE("ON") & WAIT(W)) >> [+LISTEN("ON"), show_line("\nWaiting for knowledge...\n"), Timer(W).start]
+STT("reason") / (WAKE("ON") & WAIT(W)) >> [+REASON("ON"), show_line("\nWaiting for query...\n"), Timer(W).start]

# Query KB
+STT(X) / (WAKE("ON") & REASON("ON")) >> [show_line("\nGot it.\n"), +GEN_MASK("FULL"), new_def_clause(X, "ONE", "NOMINAL")]

# Nominal clauses assertion --> single: FULL", "ONE" ---  multiple: "BASE", "MORE"
+STT(X) / (WAKE("ON") & LISTEN("ON")) >> [show_line("\nGot it.\n"), +GEN_MASK("BASE"), new_def_clause(X, "MORE", "NOMINAL"), process_rule()]
# processing rules --> single: FULL", "ONE" ---  multiple: "BASE", "MORE"
process_rule() / IS_RULE(X) >> [show_line("\n", X, " ----> is a rule!\n"), -IS_RULE(X), +GEN_MASK("BASE"), new_def_clause(X, "MORE", "RULE")]

# Generalization assertion
new_def_clause(X, M, T) / GEN_MASK("BASE") >> [-GEN_MASK("BASE"), preprocess_clause(X, "BASE", M, T), parse(), process_clause(), new_def_clause(X, M, T)]
new_def_clause(X, M, T) / GEN_MASK(Y) >> [-GEN_MASK(Y), preprocess_clause(X, Y, M, T), parse(), process_clause(), new_def_clause(X, M, T)]
new_def_clause(X, M, T) / WAIT(W) >> [show_line("\n------------- Done.\n"), Timer(W).start]


# Reactive Reasoning
+STT(X) / WAKE("ON") >> [UtteranceDetect().stop, -WAKE("ON"), show_line("\nProcessing domotic command...\n"), assert_command(X), parse_command(), parse_routine(), HotwordDetect().start]

+TIMEOUT("ON") / (WAKE("ON") & LISTEN("ON") & REASON("ON")) >> [show_line("\nReturning to idle state...\n"), -WAKE("ON"), -LISTEN("ON"), -REASON("ON"), UtteranceDetect().stop, HotwordDetect().start]
+TIMEOUT("ON") / (WAKE("ON") & REASON("ON")) >> [show_line("\nReturning to idle state...\n"), -REASON("ON"), -WAKE("ON"), UtteranceDetect().stop, HotwordDetect().start]
+TIMEOUT("ON") / (WAKE("ON") & LISTEN("ON")) >> [show_line("\nReturning to idle state...\n"), -LISTEN("ON"), -WAKE("ON"), UtteranceDetect().stop, HotwordDetect().start]
+TIMEOUT("ON") / WAKE("ON") >> [show_line("\nReturning to idle state...\n"), -WAKE("ON"), UtteranceDetect().stop, HotwordDetect().start]



# DEFINITE CLAUSES BUILDER

parse() >> [aggr_adj(), aggr_adv(), aggr_nouns(), mod_to_gnd(), gnd_prep_obj(), prep_to_gnd(), gnd_actions(), apply_adv(), actions_to_clauses(), finalize_gnd()]

# aggregate adjectives
aggr_adj() / (ADJ(I, X, L) & ADV(I, X, M)) >> [show_line("\naggregating adj-adv: ", L," - ", M), -ADJ(I, X, L), -ADV(I, X, M), aggregate("ADJ", I, X, L, M), aggr_adj()]
aggr_adj() / (ADJ(I, X, L) & ADJ(I, X, M) & neq(L, M)) >> [show_line("\naggregating adjectives: ", L," - ", M), -ADJ(I, X, L), -ADJ(I, X, M), aggregate("ADJ", I, X, L, M), aggr_adj()]
aggr_adj() / ADJ(I, X, L) >> [show_line("\nAdjectives aggregation done")]

# aggregate adverbs
aggr_adv() / (ADV(I, X, L) & ADV(I, X, M) & neq(L, M)) >> [show_line("\naggregating adverbs: ", L," - ", M), -ADV(I, X, L), -ADV(I, X, M), aggregate("ADV", I, X, L, M), aggr_adv()]
aggr_adv() / ADV(I, X, L) >> [show_line("\nAdverbs aggregation done")]

# aggregate compound nouns
aggr_nouns() / (GND(I, X, L) & GND(I, X, M) & neq(L, M)) >> [show_line("\naggregating nouns: ", L," - ", M), -GND(I, X, L), -GND(I, X, M), aggregate("NN", I, X, L, M), aggr_nouns()]
aggr_nouns() / GND(I, X, L) >> [show_line("\nNouns aggregation done.")]

# applying mods to grounds
mod_to_gnd() / (GND(I, X, L) & ADJ(I, X, M)) >> [show_line("\nadjective to ground: ", M," to ", L), -GND(I, X, L), -ADJ(I, X, M), merge(I, X, M, L), mod_to_gnd() ]
mod_to_gnd() / (GND(I, X, L) & PREP(I, D, W, X) & PREP(I, X, M, Y) & GND(I, Y, U)) >> [show_line("\nint preps...",M," - ",W), -GND(I, X, L), -PREP(I, X, M, Y), -GND(I, Y, U), int_preps_tognd(I, X, Y, M, U, L), mod_to_gnd()]
mod_to_gnd() / GND(I, X, L) >> [show_line("\nAdjective applications done.")]


# grounding object preps
gnd_prep_obj() / (PREP(I, X, L, O) & GND(I, O, M)) >> [show_line("\ngrounding object preps: ", L," <-- ", M), -PREP(I, X, L, O), -GND(I, O, M), ground_prep(I, X, L, O, M), gnd_prep_obj()]
gnd_prep_obj() / PREP(I, X, L, O) >> [show_line("\nPreposition ready: ", L)]

# applying PREP to ground
prep_to_gnd() / (PREP(I, X, L, O) & GND(I, X, M)) >> [show_line("\ngprep to ground: ", L," ---> ", M), -PREP(I, X, L, O), -GND(I, X, M), gprep_to_ground(I, X, L, O, M)]




# grounding actions

# adjective has to be applied before
gnd_actions() / (ACTION(I, V, D, X, Y) & ADJ(I, X, K) & GND(I, X, M)) >> [show_line("\nact subj not ready to be grounded (ground)..."),  mod_to_gnd(), gnd_actions()]
# prep is turned into a ground
gnd_actions() / (ACTION(I, V, D, X, Y) & PREP(I, X, L, O)) >> [show_line("\nact subj not ready to be grounded (prep)..."), prep_to_gnd(), gnd_actions()]
# applying grounds to actions object
gnd_actions() / (ACTION(I, V, D, X, Y) & GND(I, X, M)) >> [show_line("\ngrounds to actions subject: ", M), -ACTION(I, V, D, X, Y), ground_subj_act(I, V, D, X, Y, M), gnd_actions()]
gnd_actions() / (ACTION(I, V, D, X, Y) & ADJ(I, X, M)) >> [show_line("\n", M, " as subject of: ", V), -ACTION(I, V, D, X, Y), -ADJ(I, X, M), ground_subj_act(I, V, D, X, Y, M), gnd_actions()]

# adjective has to be applied before
gnd_actions() / (ACTION(I, V, D, X, Y) & ADJ(I, Y, K) & GND(I, Y, M)) >> [show_line("\nact obj not ready to be grounded..."), mod_to_gnd(), gnd_actions()]
# prep is turned into a ground
gnd_actions() / (ACTION(I, V, D, X, Y) & PREP(I, Y, L, O) & no_dav(Y)) >> [show_line("\nact obj not ready to be grounded (prep)..."), prep_to_gnd(), gnd_actions()]
# applying grounds to actions object
gnd_actions() / (ACTION(I, V, D, X, Y) & GND(I, Y, M)) >> [show_line("\ngrounds to actions object: ", M), -ACTION(I, V, D, X, Y), -GND(I, Y, M), ground_obj_act(I, V, D, X, Y, M), gnd_actions()]
gnd_actions() / (ACTION(I, V, D, X, Y) & ADJ(I, Y, M)) >> [show_line("\n", M, " as object of ", V), -ACTION(I, V, D, X, Y), -ADJ(I, Y, M), ground_obj_act(I, V, D, X, Y, M), gnd_actions()]
gnd_actions() >> [show_line("\ngrounding actions done.")]

# applying adverbs (if present) to actions label
apply_adv() / (ACTION(I, V, D, X, Y) & ADV(I, D, L)) >> [show_line("\napplying adverbs to actions label: ", L), -ACTION(I, V, D, X, Y), -ADV(I, D, L), adv_to_action(I, V, D, X, Y, L), apply_adv()]
apply_adv() / (ACTION(I, V, D, X, Y)) >> [show_line("\nadverbs application done.")]

# actions to clauses
actions_to_clauses() / (PRE_CROSS(I, D, K) & PREP(I, D, L, O)) >> [show_line("\nfeeding pre-cross: ", L), -PRE_CROSS(I, D, K), -PREP(I, D, L, O), feed_precross(I, D, K, L, O), actions_to_clauses()]
actions_to_clauses() / (ACTION(I, T, O, Y, Z) & ACTION(I, V, D, X, O) & PREP(I, O, L, K)) >> [show_line("\ncreating pre-cross: ", L),-ACTION(I, T, O, Y, Z), -PREP(I, O, L, K), create_precross(I, T, O, Y, Z, L, K), actions_to_clauses()]
actions_to_clauses() / (ACTION(I, V, D, X, O) & PRE_CROSS(I, O, K)) >> [show_line("\nmerging pre-cross: ", O), -ACTION(I, V, D, X, O), -PRE_CROSS(I, O, K), +ACTION(I, V, D, X, K), actions_to_clauses()]
actions_to_clauses() / (ACTION(I, T, O, Y, Z) & ACTION(I, V, D, X, O)) >> [show_line("\napplying action crossed dav: ", O), -ACTION(I, T, O, Y, Z), -ACTION(I, V, D, X, O), merge_act(I, T, Y, Z, V, D, X), actions_to_clauses()]
actions_to_clauses() / ACTION(I, V, D, X, Y) >> [show_line("\nturning action to clause: ", V), -ACTION(I, V, D, X, Y), act_to_clause(I, V, D, X, Y), actions_to_clauses()]
actions_to_clauses() >> [show_line("\nactions to clauses done. "), finalize_clause()]

# applying preps and finalization to clauses
finalize_clause() / (CLAUSE(I, D, X) & PREP(I, D, L, O)) >> [show_line("\napplying prep to clauses..."), -CLAUSE(I, D, X), -PREP(I, D, L, O), prep_to_clause(I, D, X, L, O), finalize_clause()]
finalize_clause() / CLAUSE(I, D, X) >> [show_line("\nfinalize clause..."), -CLAUSE(I, D, X), +CLAUSE(I, X), finalize_clause()]
finalize_clause() / (CLAUSE("LEFT", X) & CLAUSE("LEFT", Y) & neq(X, Y)) >> [show_line("\nleft conjunction..."), -CLAUSE("LEFT", X), -CLAUSE("LEFT", Y), conjunct_left_clauses(X, Y), finalize_clause()]
finalize_clause() / (LEFT_CLAUSE(X) & CLAUSE("LEFT", Y)) >> [show_line("\nleft conjunction..."), -LEFT_CLAUSE(X), -CLAUSE("LEFT", Y), conjunct_left_clauses(X, Y), finalize_clause()]

# remains management
finalize_gnd() / (GND(I, X, L) & CLAUSE(I, Y)) >> [show_line("\nretract unuseful grounds...", L), -GND(I, X, L), finalize_gnd()]
finalize_gnd() / (PREP(I, D, L, O) & CLAUSE(I, Y)) >> [show_line("\nretract unuseful preps...", L), -PREP(I, D, L, O), finalize_gnd()]
finalize_gnd() / REMAIN(I, K) >> [show_line("\nturning remain in half clause..."), -REMAIN(I, K), +CLAUSE(I, K), finalize_gnd()]
finalize_gnd() / GND(I, X, L) >> [show_line("\ncreating remain...", L), -GND(I, X, L), create_remain(I, X, L), finalize_gnd()]
finalize_gnd() >> [show_line("\nremains finalization done.")]

# creating merged definite clauses driven by subj-obj
process_clause() / (CLAUSE(I, X) & CLAUSE(I, Y) & neq(X, Y) & ACT_CROSS_VAR(I, Z, V)) >> [show_line("\njoining clauses with...", Z, " and ", V), -CLAUSE(I, X), -CLAUSE(I, Y), -ACT_CROSS_VAR(I, Z, V), join_clauses(X, Y, V), process_clause()]

# creating definite clauses with common left hand-side
process_clause() / (CLAUSE("RIGHT", X) & LEFT_CLAUSE(Y)) >> [show_line("\ncreating multiple definite clause..."), -CLAUSE("RIGHT", X), join_hand_sides(Y, X), process_clause()]

# create normal definite clauses
process_clause() / (CLAUSE("RIGHT", X) & CLAUSE("LEFT", Y)) >> [show_line("\ncreating normal definite clause..."), -CLAUSE("RIGHT", X), join_hand_sides(Y, X), process_clause()]
process_clause() / CLAUSE("FLAT", X) >> [show_line("\nGot R definite clause.\n"), -CLAUSE("FLAT", X), +DEF_CLAUSE(X), process_clause()]

process_clause() / (DEF_CLAUSE(X) & LEFT_CLAUSE(Y)) >> [show_line("\nProcessing definite clause WITH LEFT..."), -LEFT_CLAUSE(Y), process_clause()]
process_clause() / (DEF_CLAUSE(X) & CLAUSE("LEFT", Y)) >> [show_line("\nProcessing definite definite clause WITH CLAUSE LEFT..."), -CLAUSE("LEFT", Y), process_clause()]
process_clause() / CLAUSE("LEFT", Y) >> [show_line("\nRetracting unuseful LEFT clause..."), -CLAUSE("LEFT", Y), process_clause()]

process_clause() / (DEF_CLAUSE(X) & REASON("ON") & IS_RULE(Y)) >> [show_line("\nReasoning...............\n"), -DEF_CLAUSE(X), -LISTEN('ON'), -IS_RULE(Y), reason(X), process_clause()]
process_clause() / (DEF_CLAUSE(X) & REASON("ON")) >> [show_line("\nReasoning...............\n"), -DEF_CLAUSE(X), -LISTEN('ON'), reason(X), process_clause()]

process_clause() / (DEF_CLAUSE(X) & LISTEN("ON") & RETRACT("ON")) >> [show_line("\nRetracting clause."), -DEF_CLAUSE(X), -RETRACT("ON"), retract_clause(X), process_clause()]
process_clause() / (DEF_CLAUSE(X) & LISTEN("ON")) >> [show_line("\nAdding definite clause into Fol Kb."), -DEF_CLAUSE(X), new_clause(X), process_clause()]






# ROUTINES PARSER

parse_routine() >> [aggr_ent_conds(), produce_mod_conds(), produce_conds(), aggr_ent_rt(), produce_mod_rt(), produce_routine()]

# --------- conditional section ---------

# aggregate grounds terms sharing same arguments
aggr_ent_conds() / (COND_GROUND(M, X, Y) & COND_GROUND(N, X, Z) & gt(N, M)) >> [-COND_GROUND(M, X, Y), -COND_GROUND(N, X, Z), join_cond_grounds(X, Y, Z), aggr_ent_conds()]

# turning ground mod into action mod
produce_mod_conds() / (COND_PRE_MOD(Y, M, K) & COND_PRE_MOD(N, J, Y)) >> [-COND_PRE_MOD(Y, M, K), +COND_PRE_MOD(N, M, K), produce_mod_conds()]
produce_mod_conds() / (COND_PRE_MOD(Z, M, K) & PRE_COND(I, V, D, X, Z)) >> [-COND_PRE_MOD(Z, M, K), +COND_PRE_MOD(D, M, K), produce_mod_conds()]
# grounding mod terms
produce_mod_conds() / (COND_GROUND(M, Z, W) & COND_PRE_MOD(X, Y, Z)) >> [-COND_PRE_MOD(X, Y, Z), -COND_GROUND(M, Z, W), produce_mod_conds()]

# grounding pre-conditionals subject terms
produce_conds() / (PRE_COND(I, V, D, X, Y) & COND_GROUND(M, X, J)) >> [-COND_GROUND(M, X, J), -PRE_COND(I, V, D, X, Y), +PRE_COND(I, V, D, J, Y), produce_conds()]
# grounding pre-conditionals object terms
produce_conds() / (PRE_COND(I, V, D, X, Y) & COND_GROUND(M, Y, J)) >> [-COND_GROUND(M, Y, J), -PRE_COND(I, V, D, X, Y), +PRE_COND(I, V, D, X, J), produce_conds()]
# asserting conditionals
produce_conds() / PRE_COND(I, V, D, X, Y) >> [-PRE_COND(I, V, D, X, Y), +COND(I, V, X, Y), produce_conds()]

# --------- routines section ---------

# aggregate grounds terms sharing same arguments
aggr_ent_rt() / (ROUTINE_GROUND(M, X, Y) & ROUTINE_GROUND(N, X, Z) & gt(N, M)) >> [-ROUTINE_GROUND(M, X, Y), -ROUTINE_GROUND(N, X, Z), join_routine_grounds(X, Y, Z), aggr_ent_rt()]

# turning ground mod into action mod
produce_mod_rt() / (ROUTINE_PRE_MOD(X, M, K) & PRE_ROUTINE(I, V, D, X, L, T)) >> [-ROUTINE_PRE_MOD(X, M, K) , +ROUTINE_PRE_MOD(D, M, K), produce_mod_rt()]
# grounding mod terms
produce_mod_rt() / (ROUTINE_GROUND(M, Z, W) & ROUTINE_PRE_MOD(X, Y, Z)) >> [-ROUTINE_PRE_MOD(X, Y, Z), -ROUTINE_GROUND(M, Z, W), +ROUTINE_MOD(X, Y, W), produce_mod_rt()]

# grounding pre-routines terms
produce_routine() / (PRE_ROUTINE(I, V, D, X, L, T) & ROUTINE_GROUND(M, X, W)) >> [-ROUTINE_GROUND(M, X, W), -PRE_ROUTINE(I, V, D, X, L, T), +PRE_ROUTINE(I, V, D, W, L, T), produce_routine()]
# appending pre-routines parameters
produce_routine() / (PRE_ROUTINE(I, V, D, X, L, T) & ROUTINE_MOD(D, W, K)) >> [-PRE_ROUTINE(I, V, D, X, L, T), -ROUTINE_MOD(D, W, K), append_routine_params(I, V, D, X, W, K, L, T), produce_routine()]
# appending pre-routines modificators
produce_routine() / (PRE_ROUTINE(I, V, D, X, L, T) & ROUTINE_GROUND(M, D, K)) >> [-PRE_ROUTINE(I, V, D, X, L, T), -ROUTINE_GROUND(M, D, K), append_routine_mods(I, V, D, X, K, L, T), produce_routine()]
# asserting routines
produce_routine() / PRE_ROUTINE(I, V, D, X, L, T) >> [-PRE_ROUTINE(I, V, D, X, L, T), +ROUTINE(I, V, X, L, T), produce_routine()]



# DIRECT COMMAND PARSER

parse_command() >> [aggr_entities(), produce_mod(), produce_intent()]

# aggregate grounds terms sharing same arguments
aggr_entities() / (GROUND(M, X, Y) & GROUND(N, X, Z) & gt(N, M)) >> [-GROUND(M, X, Y), -GROUND(N, X, Z), join_grounds(X, Y, Z), aggr_entities()]

# turning ground mod into action mod
produce_mod() / (PRE_MOD(Y, M, K) & PRE_MOD(D, J, Y)) >> [-PRE_MOD(Y, M, K) , +PRE_MOD(D, M, K), produce_mod()]
produce_mod() / (PRE_MOD(X, M, K) & PRE_INTENT(V, D, X, L, T)) >> [-PRE_MOD(X, M, K) , +PRE_MOD(D, M, K), produce_mod()]
# grounding mod terms
produce_mod() / (PRE_MOD(X, Y, Z) & GROUND(M, Z, W)) >> [-PRE_MOD(X, Y, Z), -GROUND(M, Z, W), +MOD(X, Y, W), produce_mod()]

# grounding pre-actions terms
produce_intent() / (PRE_INTENT(V, D, X, L, T) & GROUND(M, X, W)) >> [-GROUND(M, X, W), -PRE_INTENT(V, D, X, L, T), +PRE_INTENT(V, D, W, L, T), produce_intent()]
# appending pre-action parameters
produce_intent() / (PRE_INTENT(V, D, X, L, T) & MOD(D, W, K)) >> [-PRE_INTENT(V, D, X, L, T), -MOD(D, W, K), append_intent_params(V, D, X, W, K, L, T), produce_intent()]
# appending pre-action modificators
produce_intent() / (PRE_INTENT(V, D, X, L, T) & GROUND(M, D, K)) >> [-PRE_INTENT(V, D, X, L, T), -GROUND(M, D, K), append_intent_mods(V, D, X, K, L, T), produce_intent()]
# asserting and executing actions
produce_intent() / PRE_INTENT(V, D, X, L, T) >> [-PRE_INTENT(V, D, X, L, T), +INTENT(V, X, L, T)]



# SMART ENVIRONMENT INTERFACE

+SENSOR(V, X, Y) >> [check_conds()]
check_conds() / (SENSOR(V, X, Y) & COND(I, V, X, Y) & ROUTINE(I, K, J, L, T)) >> [show_line("\nconditional met!"), -COND(I, V, X, Y), +START_ROUTINE(I), check_conds()]
check_conds() / SENSOR(V, X, Y) >> [show_line("\nbelief sensor not more needed..."), -SENSOR(V, X, Y)]

+START_ROUTINE(I) / (COND(I, V, X, Y) & ROUTINE(I, K, J, L, T)) >> [show_line("\nroutines not ready!")]
+START_ROUTINE(I) / ROUTINE(I, K, J, L, T) >> [show_line("\nexecuting routine..."), -ROUTINE(I, K, J, L, T), +INTENT(K, J, L, T), +START_ROUTINE(I)]


# turn off
+INTENT(X, "light", "living room", T) / lemma_in_syn(X, "change_state.v.01") >> [exec("change_state.v.01", "light", "living room", T)]
+INTENT(X, "alarm", "garage", T) / (lemma_in_syn(X, "change_state.v.01") & eval_cls("At_IN(Be_VBP(I_PRP(x1), __), Home_NN(x2))")) >> [exec("change_state.v.01", "alarm", "garage", T)]

# turn on
+INTENT(X, "light", "living room", T) / lemma_in_syn(X, "switch.v.03") >> [exec("switch.v.03", "light", "living room", T)]
+INTENT(X, "light", Y, T) / lemma_in_syn(X, "switch.v.03") >> [show_line("\n---- Result: failed to execute the command in the specified location")]

# open
+INTENT(X, "door", "living room", T) / lemma_in_syn(X, "open.v.01") >> [exec("open.v.01", "door", "living room", T)]
+INTENT(X, "door", "kitchen", T) / lemma_in_syn(X, "open.v.01") >> [exec("open.v.01", "door", "kitchen", T)]
+INTENT(X, "door", Y, T) / lemma_in_syn(X, "open.v.01") >> [show_line("\n---- Result: failed to execute the command in the specified location")]

# specify, set, determine, define, fix, limit
+INTENT(X, "cooler", "bedroom", T) / lemma_in_syn(X, "specify.v.02") >> [exec("specify.v.02", "cooler", "bedroom", T)]
+INTENT(X, "cooler", Y, T) / lemma_in_syn(X, "specify.v.02") >> [show_line("\n---- Result: failed to execute the command in the specified location")]

# cut
+INTENT(X, "grass", "garden", T) / lemma_in_syn(X, "cut.v.01",) >> [exec("cut.v.01", "grass", "garden", T)]
+INTENT(X, "cut.v.01", "grass", Y, T) / lemma_in_syn(X, "cut.v.01",) >> [show_line("\n---- Result: failed to execute the command in the specified location")]

# any other commands
+INTENT(V, X, L, T) >> [show_line("\n---- Result: failed to execute the command: ", V)]


# instantiate the engine
PHIDIAS.run()
# run the engine shell
PHIDIAS.shell(globals())
