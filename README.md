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
This cognitive architecture is designed for implement more intelligent agents and also 
an agent itself. 

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
Even without entities and I/O interface definition, a testing can be done as it follows by
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
Beliefs Knowledge Base can be view with the command _kb_:
```sh
eShell: main > kb

COND('420548', 'be', 'temperature', '25')
COND('420548', 'be', 'time', '12.00')      
ROUTINE('420548', 'turn', 'light', 'living room', 'off')

eShell: main > 
```
The previous routine will wait for execution until the two beliefs COND are satisfied.
Let's simulate CONSs satisfaction by simulating two Sensors...
```sh
eShell: main > kb

COND('420548', 'be', 'temperature', '25')
COND('420548', 'be', 'time', '12.00')      
ROUTINE('420548', 'turn', 'light', 'living room', 'off')

eShell: main > 
```
Let's simulate CONDs satisfaction by simulating two Sensors...
 ```sh
eShell: main > s1()
eShell: main > Assertiong SENSOR('be','time','12.00')...

conditional triggered by a sensor...

Result: not all routine's conditionals are currently met!

eShell: main > s2()
eShell: main > Assertiong SENSOR('be','temperature','25')...

conditional triggered by a sensor...

executing routine...

---- Result: execution successful

Action: change_state.v.01
Object: light
Location: living room
Parameters: off
```
### Conceptual Reasoning
In order to distinguish working contexts, this reasoning will be triggered by two specific
hotwords (after the agent is awakened):
* _listen_: the agent will wait (until timeout) for utterances in natural language to be converted in definite clauses
and asserted in the Clauses Knowledge Base.
* _reson_: the agent will wait (until timeout) for one utterance in natural language to be converted in a
single positive literal for querying the Clauses Knowledge Base.

Next the Clauses Knowledge base will be fed with the following utterances:
* _Nono is an hostile nation_
* _Colonel West is American_
* _missiles are weapons_
* _Colonel West sells missiles to Nono_
* _When an American sells weapons to a hostile nation, that American is a criminal_






