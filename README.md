# pycaspar

This is the repository of the Python (3.7+) implementation of CASPAR (Cognitive Architecture System Planned and Reactive)
referred to the paper _CASPAR: towards Decision Making Helpers Agents for IoT, based on Natural Language and First Order
 Logic Reasoning_, published in ......................

# Installation

This repository has been tested with the following packages versions:

* [Phidias](https://github.com/corradosantoro/phidias) (release 1.3.4.alpha) 
* SpaCy (ver. 2.2.4)
* Natural Language Toolkit (ver. 3.5)


### Phidias

##### on all platforms
```sh
> git clone https://github.com/corradosantoro/phidias
> python setup.py install
```
##### additional package needed (Linux)
```sh
> python -pip install readline
```
##### additional package needed (Windows)
```sh
> python -pip install pyreadline
```

### SpaCy
```sh
> python -m pip install spacy
> python -m spacy download en_core_web_sm
```


### Natural Language Toolkit
```sh
> python -m pip install nltk
```



# Testing
This cognitive architecture is designed to implement more intelligent agents and also 
is an agent itself. Before starting the agent, Entities and Speech-To-Text Interfaces must be defined.

### Entities definition
Entities involved in reasoning must be defined in the Smart Environment Interface 
(line 1622 of caspar.py).

### Speech-To-Text Interfaces
SST Interfaces (for both hotwords and utterances) must be defined inside the Instances Sensors 
(line 1319 and 1337 of caspar.py).
 

### Starting Phidias Shell
```sh
> python caspar.py

          PHIDIAS Release 1.3.4.alpha (deepcopy-->clone,micropython,py3)
          Autonomous and Robotic Systems Laboratory
          Department of Mathematics and Informatics
          University of Catania, Italy (santoro@dmi.unict.it)
          
eShell: main >
```
### Starting agent
```sh
eShell: main > go()
eShell: main > Starting Caspar...

Starting Hotword detection...

eShell: main >
```
Even without entities and Speech-To-Text interfaces definition, an agent's testing can be done as it follows by
simulating vocal events:

### Waking agent
Here we suppose the agent recognizes a proper waking word (_caspar_ for example) and exits from its idle state:
```sh
eShell: main > w()
eShell: main > 

Yes, I'm here!

Stopping Hotword detection...

Starting utterance detection...
```
after ten seconds of inactivity:
```sh
Returning to idle state...

Stopping utterance detection...

Starting Hotword detection...
```

### IoT commands and routines
By the means of two testing procedure IoT direct commands can be tested, whose entities are defined
 in the Smart Enviroment interface:
* set the cooler at 27 degrees in the bedroom

```sh
eShell: main > d1()

Stopping utterance detection...

Processing domotic command...

set the cooler at 27 degrees in the bedroom

Starting Hotword detection...

---- Result: execution successful

Action: specify.v.02
Object: cooler
Location: bedroom
Parameters: at 27 degree
```
* turn off the lights in the living room
```sh
eShell: main > d2()

Stopping utterance detection...

Processing domotic command...

turn off the lights in the living room

Starting Hotword detection...

---- Result: execution successful

Action: change_state.v.01
Object: light
Location: living room
Parameters: off
```
Caspar is capable of parsing complex routines as it follow (the agent must be first awakened):

* turn off the lights in the living room, when the temperature is 25 and the time is 12.00
```sh
eShell: main > r1()

Stopping utterance detection...

Processing domotic command...

turn off the lights in the living room, when the temperature is 25 and the time is 12.00

Starting Hotword detection...

eShell: main > 
```
Now routines related beliefs are stored into Beliefs Knowledge Base, which can be view with the command _kb_:
```sh
eShell: main > kb

COND('420548', 'be', 'temperature', '25')
COND('420548', 'be', 'time', '12.00')      
ROUTINE('420548', 'turn', 'light', 'living room', 'off')

eShell: main > 
```
The routine will wait for execution, until the two beliefs COND are satisfied. Let's simulate CONDs 
satisfaction by simulating two Sensor detections, which let the agent decide on routine execution.
 ```sh
eShell: main > s1()

asserting SENSOR('be','time','12.00')...

conditional triggered by a sensor...

Result: not all routine's conditionals are currently met!
```
The time-related COND is satisfied, but it isn't enough for routine execution because 
it miss another COND satisfaction:
```sh
eShell: main > kb

COND('420548', 'be', 'temperature', '25')
ROUTINE('420548', 'turn', 'light', 'living room', 'off')

eShell: main > 
```
as another Sensor detection meet the temperature-related COND as well, the routine can be executed:
```sh
eShell: main > s2()

asserting SENSOR('be','temperature','25')...

conditional triggered by a sensor...

executing routine...

---- Result: execution successful

Action: change_state.v.01
Object: light
Location: living room
Parameters: off
```
### Conceptual Reasoning
All the Caspar's expressive capabilities are summarized [here](examples.md).
In order to distinguish working contexts, conceptual reasoning will be triggered by two specific
hotwords (after the agent is awakened):
* _listen_: the agent will wait (until timeout) for utterances in natural language to be converted in definite clauses
and asserted in the Clauses Knowledge Base.
* _reason_: the agent will wait (until timeout) for one utterance in natural language to be converted in a
single positive literal for querying the Clauses Knowledge Base.

Next the Clauses Knowledge base will be fed by the following utterances:
* _Nono is an hostile nation_
* _Colonel West is American_
* _missiles are weapons_
* _Colonel West sells missiles to Nono_
* _When an American sells weapons to a hostile nation, that American is a criminal_

and queried by:
* _Colonel West is a criminal?_

We will show (by the command s()) the Clauses Knowlegde Base content after every assertion simulation:
* _Nono is an hostile nation_
```sh
eShell: main > l()
eShell: main > 
Waiting for knowledge...

eShell: main > c1()
Got it.

------------- All generalizations asserted.


eShell: main > s()
eShell: main > 
4 clauses in Clauses kb:

Be(Nono(x1), Nation(x2))
Be(Nono(x1), Hostile(Nation(x2)))
(Nono(x) ==> Nation(x))
(Nono(x) ==> Hostile(Nation(x)))
```
* _Colonel West is American_
```sh
eShell: main > c2()
Got it.

------------- All generalizations asserted.


eShell: main > s()
6 clauses in Clauses kb:

Be(Nono(x1), Nation(x2))
Be(Nono(x1), Hostile(Nation(x2)))
(Nono(x) ==> Nation(x))
(Nono(x) ==> Hostile(Nation(x)))
Be(Colonel_West(x1), American(x2))
(Colonel_West(x) ==> American(x))
```
* _missiles are weapons_
```sh
eShell: main > c3()
Got it.

------------- All generalizations asserted.


eShell: main > s()
8 clauses in Clauses kb:

Be(Nono(x1), Nation(x2))
Be(Nono(x1), Hostile(Nation(x2)))
(Nono(x) ==> Nation(x))
(Nono(x) ==> Hostile(Nation(x)))
Be(Colonel_West(x1), American(x2))
(Colonel_West(x) ==> American(x))
Be(Missile(x1), Weapon(x2))
(Missile(x) ==> Weapon(x))
```
* _Colonel West sells missiles to Nono_
```sh
eShell: main > c4()
Got it.

------------- All generalizations asserted.


eShell: main > s()
24 clauses in Clauses kb:

Be(Nono(x1), Nation(x2))
Be(Nono(x1), Hostile(Nation(x2)))
(Nono(x) ==> Nation(x))
(Nono(x) ==> Hostile(Nation(x)))
Be(Colonel_West(x1), American(x2))
(Colonel_West(x) ==> American(x))
Be(Missile(x1), Weapon(x2))
(Missile(x) ==> Weapon(x))
(Sell(Colonel_West(x1), Missile(x2)) ==> Sell(American(x), Missile(x2)))
(Sell(Colonel_West(x1), Missile(x2)) ==> Sell(American(x), Weapon(x)))
(Sell(Colonel_West(x1), Missile(x2)) ==> Sell(Colonel_West(x1), Weapon(x)))
Sell(Colonel_West(x1), Missile(x2))
(To(Sell(Colonel_West(x1), Missile(x2)), Nono(x3)) ==> To(Sell(Colonel_West(x1), Missile(x2)), Nation(x)))
(To(Sell(Colonel_West(x1), Missile(x2)), Nono(x3)) ==> To(Sell(American(x), Missile(x2)), Nation(x)))
(To(Sell(Colonel_West(x1), Missile(x2)), Nono(x3)) ==> To(Sell(American(x), Weapon(x)), Nation(x)))
(To(Sell(Colonel_West(x1), Missile(x2)), Nono(x3)) ==> To(Sell(Colonel_West(x1), Weapon(x)), Nation(x)))
(To(Sell(Colonel_West(x1), Missile(x2)), Nono(x3)) ==> To(Sell(Colonel_West(x1), Missile(x2)), Hostile(Nation(x))))
(To(Sell(Colonel_West(x1), Missile(x2)), Nono(x3)) ==> To(Sell(American(x), Missile(x2)), Hostile(Nation(x))))
(To(Sell(Colonel_West(x1), Missile(x2)), Nono(x3)) ==> To(Sell(American(x), Weapon(x)), Hostile(Nation(x))))
(To(Sell(Colonel_West(x1), Missile(x2)), Nono(x3)) ==> To(Sell(Colonel_West(x1), Weapon(x)), Hostile(Nation(x))))
(To(Sell(Colonel_West(x1), Missile(x2)), Nono(x3)) ==> To(Sell(American(x), Missile(x2)), Nono(x3)))
(To(Sell(Colonel_West(x1), Missile(x2)), Nono(x3)) ==> To(Sell(American(x), Weapon(x)), Nono(x3)))
(To(Sell(Colonel_West(x1), Missile(x2)), Nono(x3)) ==> To(Sell(Colonel_West(x1), Weapon(x)), Nono(x3)))
To(Sell(Colonel_West(x1), Missile(x2)), Nono(x3))
```
* _When an American sells weapons to a hostile nation, that American is a criminal_
```sh
eShell: main > c5()
Got it.

------------- All generalizations asserted.


eShell: main > s()
25 clauses in Clauses kb:

Be(Nono(x1), Nation(x2))
Be(Nono(x1), Hostile(Nation(x2)))
(Nono(x) ==> Nation(x))
(Nono(x) ==> Hostile(Nation(x)))
Be(Colonel_West(x1), American(x2))
(Colonel_West(x) ==> American(x))
Be(Missile(x1), Weapon(x2))
(Missile(x) ==> Weapon(x))
(Sell(Colonel_West(x1), Missile(x2)) ==> Sell(American(x), Missile(x2)))
(Sell(Colonel_West(x1), Missile(x2)) ==> Sell(American(x), Weapon(x)))
(Sell(Colonel_West(x1), Missile(x2)) ==> Sell(Colonel_West(x1), Weapon(x)))
Sell(Colonel_West(x1), Missile(x2))
(To(Sell(Colonel_West(x1), Missile(x2)), Nono(x3)) ==> To(Sell(Colonel_West(x1), Missile(x2)), Nation(x)))
(To(Sell(Colonel_West(x1), Missile(x2)), Nono(x3)) ==> To(Sell(American(x), Missile(x2)), Nation(x)))
(To(Sell(Colonel_West(x1), Missile(x2)), Nono(x3)) ==> To(Sell(American(x), Weapon(x)), Nation(x)))
(To(Sell(Colonel_West(x1), Missile(x2)), Nono(x3)) ==> To(Sell(Colonel_West(x1), Weapon(x)), Nation(x)))
(To(Sell(Colonel_West(x1), Missile(x2)), Nono(x3)) ==> To(Sell(Colonel_West(x1), Missile(x2)), Hostile(Nation(x))))
(To(Sell(Colonel_West(x1), Missile(x2)), Nono(x3)) ==> To(Sell(American(x), Missile(x2)), Hostile(Nation(x))))
(To(Sell(Colonel_West(x1), Missile(x2)), Nono(x3)) ==> To(Sell(American(x), Weapon(x)), Hostile(Nation(x))))
(To(Sell(Colonel_West(x1), Missile(x2)), Nono(x3)) ==> To(Sell(Colonel_West(x1), Weapon(x)), Hostile(Nation(x))))
(To(Sell(Colonel_West(x1), Missile(x2)), Nono(x3)) ==> To(Sell(American(x), Missile(x2)), Nono(x3)))
(To(Sell(Colonel_West(x1), Missile(x2)), Nono(x3)) ==> To(Sell(American(x), Weapon(x)), Nono(x3)))
(To(Sell(Colonel_West(x1), Missile(x2)), Nono(x3)) ==> To(Sell(Colonel_West(x1), Weapon(x)), Nono(x3)))
To(Sell(Colonel_West(x1), Missile(x2)), Nono(x3))
(To(Sell(American(x1), Weapon(x2)), Hostile(Nation(x3))) ==> Be(American(x4), Criminal(x5)))
```
now it is time to query the Clauses Knowledge Base with the following utterance:
* _Colonel West is a criminal?_

```sh
eShell: main > r()
Waiting for query...

eShell: main > q()
Got it.

Reasoning...............

Query: Be(Colonel_West(x1), Criminal(x2))

 ---- NOMINAL REASONING ---

Result: False


 ---- NESTED REASONING ---

Result:  {v_353: v_83, v_354: x2, v_405: v_350, v_350: v_351, v_351: v_352, v_473: v_402, v_474: v_403, v_475: v_404}
```
Above are showed both results of Nominal Reasoning by the Backward-Chaining argorithm and Nested Reasoning.









