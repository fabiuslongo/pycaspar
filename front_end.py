from phidias.Lib import *
from actions import *
from sensors import *


# Front-End STT

# SIMULATING EVENTS

# simulating routines
r1() >> [+STT("turn off the lights in the living room, when the temperature is 25 and the time is 12.00")]
r2() >> [+STT("set the cooler in the bedroom to 25 degrees and cut the grass in the garden, when the time is 12.00")]

# simulating direct commands
d1() >> [+STT("set the cooler at 27 degrees in the bedroom")]
d2() >> [+STT("turn off the alarm in the garage")]

# definite clauses for reasoning purposes
c1() >> [+STT("Cuba is an hostile nation")]
c2() >> [+STT("Colonel West is American")]
c3() >> [+STT("missiles are weapons")]
c4() >> [+STT("Colonel West sells missiles to Cuba")]
c5() >> [+STT("When an American sells weapons to a hostile nation, that American is a criminal")]

# open issues

# testing disambiguation: He likes to eat bass, He likes to play the bass

# relcl
# I just want a simple way to get my discount -----> unsolved!
# I lived the experience THAT you told to me: Yes! --- I lived the experience WHICH you told to me: Yes!
# I lived the experience THAT you told me: No! --- I lived the experience WHICH you told me: No!
# I saw the man that you love: Yes! --- I saw the man you love: No!

# mark: unwanted conditionals
# I want to see the issues like he sees them, I want to see the issues as he sees them

# dobj
# What she bought to me were these books: YES!
# What she bought me were these books

# Query
q() >> [+STT("Colonel West is a criminal")]



# Start agent command
go() >> [show_line("Starting Caspar..."), set_wait(), HotwordDetect().start]

# show Clauses kb
s() >> [show_fol_kb()]
# initialize Clauses Kb
c() >> [clear_clauses_kb()]

# simulating keywords
w() >> [+HOTWORD_DETECTED("ON")]
l() >> [+STT("listen")]
r() >> [+STT("reason")]

# simulating sensors
s1() >> [simulate_sensor("Be", "Time", "12.00")]
s2() >> [simulate_sensor("Be", "Temperature", "25")]

# test assertions
t() >> [go(), w(), l()]


# Hotwords processing
+HOTWORD_DETECTED("ON") / WAIT(W) >> [show_line("\n\nYes, I'm here!\n"), HotwordDetect().stop, UtteranceDetect().start, +WAKE("ON"), Timer(W).start]
+STT("listen") / (WAKE("ON") & WAIT(W)) >> [+LISTEN("ON"), show_line("\nWaiting for knowledge...\n"), Timer(W).start]
+STT("reason") / (WAKE("ON") & WAIT(W)) >> [+REASON("ON"), show_line("\nWaiting for query...\n"), Timer(W).start]

+STT(X) / (WAKE("ON") & LISTEN("ON")) >> [reset_ct(), parse_rules(X,"DISOK"), parse_deps(), feed_mst(), +PROCESS_STORED_MST("OK"), Timer(W).start]
+STT(X) / (WAKE("ON") & REASON("ON")) >> [reset_ct(), parse_rules(X, "DISOK"), parse_deps(), feed_mst(), +PROCESS_STORED_MST("OK"), Timer(W).start]


# Query KB
+PROCESS_STORED_MST("OK") / (WAKE("ON") & REASON("ON")) >> [show_line("\nGot it.\n"), +GEN_MASK("FULL"), new_def_clause("ONE", "NOMINAL")]

# Nominal clauses assertion --> single: FULL", "ONE" ---  multiple: "BASE", "MORE"
+PROCESS_STORED_MST("OK") / (WAKE("ON") & LISTEN("ON")) >> [show_line("\nGot it.\n"), +GEN_MASK("BASE"), new_def_clause("MORE", "NOMINAL"), process_rule()]
# processing rules --> single: FULL", "ONE" ---  multiple: "BASE", "MORE"
process_rule() / IS_RULE("TRUE") >> [show_line("\n------> rule detected!\n"), -IS_RULE("TRUE"), +GEN_MASK("BASE"), new_def_clause("MORE", "RULE")]

# Generalization assertion
new_def_clause(M, T) / GEN_MASK("BASE") >> [-GEN_MASK("BASE"), preprocess_clause("BASE", M, T), parse(), process_clause(), new_def_clause(M, T)]
new_def_clause(M, T) / GEN_MASK(Y) >> [-GEN_MASK(Y), preprocess_clause(Y, M, T), parse(), process_clause(), new_def_clause(M, T)]
new_def_clause(M, T) / WAIT(W) >> [show_line("\n------------- Done.\n"), Timer(W).start]


# Reactive Reasoning
+STT(X) / WAKE("ON") >> [reset_ct(), UtteranceDetect().stop, -WAKE("ON"), show_line("\nProcessing domotic command...\n"), parse_rules(X, "NODIS"), parse_deps(), feed_mst(), assert_command(X), parse_command(), parse_routine(), HotwordDetect().start]

+TIMEOUT("ON") / (WAKE("ON") & LISTEN("ON") & REASON("ON")) >> [show_line("\nReturning to idle state...\n"), -WAKE("ON"), -LISTEN("ON"), -REASON("ON"), UtteranceDetect().stop, HotwordDetect().start]
+TIMEOUT("ON") / (WAKE("ON") & REASON("ON")) >> [show_line("\nReturning to idle state...\n"), -REASON("ON"), -WAKE("ON"), UtteranceDetect().stop, HotwordDetect().start]
+TIMEOUT("ON") / (WAKE("ON") & LISTEN("ON")) >> [show_line("\nReturning to idle state...\n"), -LISTEN("ON"), -WAKE("ON"), UtteranceDetect().stop, HotwordDetect().start]
+TIMEOUT("ON") / WAKE("ON") >> [show_line("\nReturning to idle state...\n"), -WAKE("ON"), UtteranceDetect().stop, HotwordDetect().start]


