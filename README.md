# pycaspar

This is the repository of the Python (3.7+) implementation of CASPAR (Cognitive Architecture System Planned and Reactive)
referred to the paper _CASPAR: towards Decision Making Helpers Agents for IoT, based on Natural Language and First Order
 Logic Reasoning_, published in ......................

# Installation

For running Caspar you need to install the following packages:

* [Phidias](https://github.com/corradosantoro/phidias) 
* SpaCy
* Natural Language Toolkit


### Phidias

##### All platforms
```sh
$ git clone https://github.com/corradosantoro/phidias
$ python setup.py install
```
##### Linux
```sh
$ python -pip install readline
```
##### Windows
```sh
$ python -pip install pyreadline
```

### SpaCy
```sh
$ python -m pip install spacy
$ python -m spacy download en_core_web_sm
```


### Natural Language Toolkit
```sh
$ python -m pip install nltk
```



# Testing
This cognitive architecture is designed for implement more intelligent agents and also 
an agent itself. 

### Starting Phidias Shell
```sh
$ python caspar.py

NLP engine instantiating...

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
Caspar is capable of parsing complex routines as it follow (the agent must be awakened):

* turn off the lights in the living room, when the temperature is 25 and the time is 12
```sh
eShell: main > r1()

Stopping utterance detection...

Processing domotic command...

turn off the lights in the living room, when the temperature is 25 and the time is 12

Starting Hotword detection...

eShell: main > 
```
Beliefs Knowledge Base can be view with the command _kb_:
```sh
eShell: main > kb

COND('420548', 'be', 'temperature', '25')
COND('420548', 'be', 'time', '12')      
ROUTINE('420548', 'turn', 'light', 'living room', 'off')

eShell: main > 
```
The previous routine will wait for execution until the two beliefs COND are satisfied. 

