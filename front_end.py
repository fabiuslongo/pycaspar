from phidias.Lib import *
from actions import *

#from sensors import *
#from sensors_azure import *
from sensors_google import *

# Clauses KB manual feeding beliefs
class FEED(Reactor): pass
class QUERY(Reactor): pass

# Front-End STT

# SIMULATING EVENTS

# simulating routines
r1() >> [+WAKE("TEST"), +STT("turn off the lights in the living room, when the temperature is 25 and the time is 12")]
r2() >> [+WAKE("TEST"), +STT("set the cooler in the bedroom to 25 degrees and cut the grass in the garden, when the time is 12")]

# simulating direct commands
d1() >> [+WAKE("TEST"), +STT("set the cooler at 27 degrees in the bedroom")]
d2() >> [+WAKE("TEST"), +STT("turn off the alarm in the garage")]

# sentences for reasoning purposes
c1() >> [+FEED("Cuba is a hostile nation")]
c2() >> [+FEED("The Colonel West is American")]
c3() >> [+FEED("missiles are weapons")]
c4() >> [+FEED("the Colonel West sells missiles to Cuba")]
c5() >> [+FEED("When an American sells weapons to a hostile nation, that American is a criminal")]

# Query
q() >> [+QUERY("The Colonel West is a criminal")]


# Start agent command
go() >> [show_line("Starting Caspar..."), set_wait(), HotwordDetect().start, say("system ready")]

# show Clauses kb
s() >> [show_fol_kb()]
# initialize Clauses Kb
c() >> [clear_clauses_kb()]

# Azure
#l() >> [+STT("Listen.")]
#r() >> [+STT("Reason.")]
#d() >> [+STT("Done.")]

# simulating sensors
s1() >> [simulate_sensor("Be", "Time", "12")]
s2() >> [simulate_sensor("Be", "Temperature", "25")]

# testing rules
+FEED(X) >> [reset_ct(), parse_rules(X, "DISOK"), parse_deps(), feed_mst(), +PROCESS_STORED_MST("OK"), log("Feed",X), show_ct(), +LISTEN("TEST")]
+QUERY(X) >> [reset_ct(), parse_rules(X, "DISOK"), parse_deps(), feed_mst(), +PROCESS_STORED_MST("OK"), log("Query",X), show_ct(), +REASON("TEST")]
+PROCESS_STORED_MST("OK") / LISTEN("TEST") >> [show_line("\nGot it.\n"), +GEN_MASK("BASE"), new_def_clause("MORE", "NOMINAL"), process_rule(), -LISTEN("TEST")]
+PROCESS_STORED_MST("OK") / REASON("TEST") >> [show_line("\nGot it.\n"), +GEN_MASK("FULL"), new_def_clause("ONE", "NOMINAL"), -REASON("TEST")]


# Hotwords processing
+HOTWORD_DETECTED("ON") / WAIT(W) >> [show_line("\n\nYes, I'm here!\n"), HotwordDetect().stop, beep(), UtteranceDetect().start, +WAKE("ON"), Timer(W).start]

# Google STT
+STT("listen") / (WAKE("ON") & WAIT(W)) >> [-REASON("ON"), +LISTEN("ON"), show_line("\nWaiting for knowledge...\n"), UtteranceDetect().stop, say("Waiting for knowledge..."), UtteranceDetect().start, Timer(W).start]
+STT("reason") / (WAKE("ON") & WAIT(W)) >> [-LISTEN("ON"), +REASON("ON"), show_line("\nWaiting for query...\n"), UtteranceDetect().stop, say("Waiting for query..."), UtteranceDetect().start, Timer(W).start]
+STT("done") / (WAKE("ON") & WAIT(W)) >> [-LISTEN("ON"), -REASON("ON"), show_line("\nExiting from cognitive phase...\n"), UtteranceDetect().stop, say("Exiting from cognitive phase..."), HotwordDetect().start, Timer(W).start]

# Azure STT
#+STT("Listen.") / (WAKE("ON") & WAIT(W)) >> [-REASON("ON"), +LISTEN("ON"), show_line("\nWaiting for knowledge...\n"), UtteranceDetect().start, Timer(W).start]
#+STT("Reason.") / (WAKE("ON") & WAIT(W)) >> [-LISTEN("ON"), +REASON("ON"), show_line("\nWaiting for query...\n"), UtteranceDetect().start, Timer(W).start]
#+STT("Done.") / (WAKE("ON") & WAIT(W)) >> [-LISTEN("ON"), -REASON("ON"), show_line("\nExiting from cognitive phase...\n"), UtteranceDetect().stop, HotwordDetect().start, Timer(W).start]

+STT(X) / (WAKE("ON") & LISTEN("ON")) >> [reset_ct(), parse_rules(X, "DISOK"), parse_deps(), feed_mst(), +PROCESS_STORED_MST("OK"), show_ct(), +ANSWER(X), Timer(W).start]
+STT(X) / (WAKE("ON") & REASON("ON")) >> [reset_ct(), parse_rules(X, "DISOK"), parse_deps(), feed_mst(), +PROCESS_STORED_MST("OK"), show_ct(), Timer(W).start]

+ANSWER(X) / (WAKE("ON")) >> [UtteranceDetect().stop, say(X), UtteranceDetect().start]

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
+STT(X) / WAKE("TEST") >> [reset_ct(), -WAKE("TEST"), show_line("\nProcessing domotic command...\n"), parse_rules(X, "NODIS"), parse_deps(), feed_mst(), assert_command(X), parse_command(), parse_routine()]

+TIMEOUT("ON") / (WAKE("ON") & LISTEN("ON") & REASON("ON")) >> [show_line("\nReturning to idle state...\n"), -WAKE("ON"), -LISTEN("ON"), -REASON("ON"), UtteranceDetect().stop, HotwordDetect().start]
+TIMEOUT("ON") / (WAKE("ON") & REASON("ON")) >> [show_line("\nReturning to idle state...\n"), -REASON("ON"), -WAKE("ON"), UtteranceDetect().stop, HotwordDetect().start]
+TIMEOUT("ON") / (WAKE("ON") & LISTEN("ON")) >> [show_line("\nReturning to idle state...\n"), -LISTEN("ON"), -WAKE("ON"), UtteranceDetect().stop, HotwordDetect().start]

+TIMEOUT("ON") / WAKE("ON") >> [show_line("\nReturning to idle state...\n"), -WAKE("ON"), UtteranceDetect().stop, HotwordDetect().start]


