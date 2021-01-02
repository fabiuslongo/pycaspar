# pycaspar

This is the repository of the Python (3.7+) implementation of CASPAR (Cognitive Architecture System Planned and Reactive)
referred to the paper: [A Reactive Cognitive Architecture based on Natural Language Processing for the task of Decision-Making
using a Rich Semantic](http://ceur-ws.org/Vol-2706/paper2.pdf), presented in WOA 2020: Workshop “From Objects to Agents”, September 14–16, 2020, Bologna, Italy.

![Image 1](https://github.com/fabiuslongo/pycaspar/blob/master/images/Caspar.JPG)

# Installation


This repository has been tested on Raspberry Pi 4B with the following packages versions:

* [Phidias](https://github.com/corradosantoro/phidias) (release 1.3.4.alpha) 
* SpaCy (ver. 2.3.0)
* Natural Language Toolkit (ver. 3.5)
* [Snowboy](https://github.com/Kitt-AI/snowboy)
* [Google Speech-to-Text] (https://cloud.google.com/speech-to-text/docs/libraries#client-libraries-install-python)


### Phidias


```sh
> git clone https://github.com/corradosantoro/phidias
> python setup.py install
> python -pip install parse
```

### spaCy

---------------

```sh
> sudo apt-get update
> sudo apt-get install --reinstall build-essential
> BLIS_ARCH=generic pip install spacy=2.3.0 --no-binary=blis
> python -m spacy download en_core_web_lg
```


### Natural Language Toolkit

---------------

from prompt:
```sh
> python -m pip install nltk
```
from python console:
```sh
> import nltk
> nltk.download('wordnet')
```

### Festival Text-to-Speech

Install Festival with:

---------------
 
```sh
> sudo apt-get install festival
```


# Testing
This cognitive architecture is designed to implement more intelligent agents and also 
is an agent itself. Before starting the agent, Entities and Speech-To-Text Interfaces must be defined.

### Entities definition

---------------

Entities involved in reasoning must be defined in the Smart Environment Interface (smart_env_int.py).

### Speech-To-Text Interfaces

---------------

SST Interfaces (for both hotwords and utterances) must be defined inside the Instances Sensors (HotwordDetect and UtteranceDetect classes of sensors_snow_google.py).



### Starting Phidias Shell

---------------

```sh
> python caspar.py

          PHIDIAS Release 1.3.4.alpha (deepcopy-->clone,micropython,py3)
          Autonomous and Robotic Systems Laboratory
          Department of Mathematics and Informatics
          University of Catania, Italy (santoro@dmi.unict.it)
          
eShell: main >
```
### Starting agent

---------------

```sh
eShell: main > go()
eShell: main > Starting Caspar...

Starting Hotword detection...

eShell: main >
```
Even without entities and Speech-To-Text interfaces definition, an agent's testing can be done as it follows by
simulating vocal events:

### Waking agent

---------------

After the waking word _caspar_ is recognized the agent will exits from its idle state:

```sh
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
the amount of waiting seconds can be changed in the AGENT section of the config.ini file (WAIT_TIME).

### IoT commands and routines

---------------

By the means of two testing procedure IoT direct commands can be tested, whose entities are defined
 in the Smart Enviroment interface:
 
* _set the cooler at 27 degrees in the bedroom_

Stopping utterance detection...

Processing domotic command...

set the cooler at 27 degrees in the bedroom

Starting Hotword detection...

---- Result: execution successful

Action: specify.v.02
Object: cooler
Location: bedroom
Parameters: at 27 degree

* _turn off the lights in the living room_

```sh
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

* _turn off the lights in the living room, when the temperature is 25 and the time is 12.00_

```sh

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
eShell: main > +SENSOR('be','time','12.00')

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
eShell: main > +SENSOR('be','temperature','25')

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

---------------

All the Caspar's expressive capabilities are summarized [here](examples.md).
In order to distinguish working contexts, conceptual reasoning will be triggered by two specific
hotwords (after the agent is awakened):
* _listen_: the agent will wait (until timeout) for utterances in natural language to be converted in definite clauses
and asserted in the Clauses Knowledge Base.
* _reason_: the agent will wait (until timeout) for one utterance in natural language to be converted in a
single positive literal for querying the Clauses Knowledge Base.

Next the Clauses Knowledge base will be fed by the following utterances:
* _Cuba is an hostile nation_
* _Colonel West is American_
* _missiles are weapons_
* _Colonel West sells missiles to Cuba_
* _When an American sells weapons to a hostile nation, that American is a criminal_

and queried by:
* _Colonel West is a criminal?_

We will show (by the command s()) the Clauses Knowlegde Base content after every assertion simulation:
* _Nono is an hostile nation_

```sh

Waiting for knowledge...

eShell: main > +STT("Cuba is an hostile nation")
Got it.

------------- All generalizations asserted.


eShell: main > s()
eShell: main > 
4 clauses in Clauses kb:

Be(Cuba(x1), Nation(x2))
Be(Cuba(x1), Hostile(Nation(x2)))
(Cuba(x) ==> Nation(x))
(Cuba(x) ==> Hostile(Nation(x)))
```
* _Colonel West is American_
```sh
eShell: main > +STT("Colonel West is American")
Got it.

------------- All generalizations asserted.


eShell: main > s()
6 clauses in Clauses kb:

Be(Cuba(x1), Nation(x2))
Be(Cuba(x1), Hostile(Nation(x2)))
(Cuba(x) ==> Nation(x))
(Cuba(x) ==> Hostile(Nation(x)))
Be(Colonel_West(x1), American(x2))
(Colonel_West(x) ==> American(x))
```
* _missiles are weapons_
```sh
eShell: main > +STT("missiles are weapons")
Got it.

------------- All generalizations asserted.


eShell: main > s()
8 clauses in Clauses kb:

Be(Cuba(x1), Nation(x2))
Be(Cuba(x1), Hostile(Nation(x2)))
(Cuba(x) ==> Nation(x))
(Cuba(x) ==> Hostile(Nation(x)))
Be(Colonel_West(x1), American(x2))
(Colonel_West(x) ==> American(x))
Be(Missile(x1), Weapon(x2))
(Missile(x) ==> Weapon(x))
```
* _Colonel West sells missiles to Cuba_
```sh
eShell: main > +STT("Colonel West sells missiles to Cuba")
Got it.

------------- All generalizations asserted.


eShell: main > s()
24 clauses in Clauses kb:

Be(Cuba(x1), Nation(x2))
Be(Cuba(x1), Hostile(Nation(x2)))
(Cuba(x) ==> Nation(x))
(Cuba(x) ==> Hostile(Nation(x)))
Be(Colonel_West(x1), American(x2))
(Colonel_West(x) ==> American(x))
Be(Missile(x1), Weapon(x2))
(Missile(x) ==> Weapon(x))
(Sell(Colonel_West(x1), Missile(x2)) ==> Sell(American(v_0), Missile(x2)))
(Sell(Colonel_West(x1), Missile(x2)) ==> Sell(American(x), Weapon(v_1)))
(Sell(Colonel_West(x1), Missile(x2)) ==> Sell(Colonel_West(x1), Weapon(v_2)))
Sell(Colonel_West(x1), Missile(x2))
(To(Sell(Colonel_West(x1), Missile(x2)), Cuba(x3)) ==> To(Sell(Colonel_West(x1), Missile(x2)), Nation(v_4)))
(To(Sell(Colonel_West(x1), Missile(x2)), Cuba(x3)) ==> To(Sell(American(v_5), Missile(v_6)), Nation(x)))
(To(Sell(Colonel_West(x1), Missile(x2)), Cuba(x3)) ==> To(Sell(American(v_7), Weapon(v_8)), Nation(x)))
(To(Sell(Colonel_West(x1), Missile(x2)), Cuba(x3)) ==> To(Sell(Colonel_West(v_9), Weapon(v_10)), Nation(x)))
(To(Sell(Colonel_West(x1), Missile(x2)), Cuba(x3)) ==> To(Sell(Colonel_West(x1), Missile(x2)), Hostile(Nation(v_11))))
(To(Sell(Colonel_West(x1), Missile(x2)), Cuba(x3)) ==> To(Sell(American(v_12), Missile(v_13)), Hostile(Nation(x))))
(To(Sell(Colonel_West(x1), Missile(x2)), Cuba(x3)) ==> To(Sell(American(v_14), Weapon(v_15)), Hostile(Nation(x))))
(To(Sell(Colonel_West(x1), Missile(x2)), Cuba(x3)) ==> To(Sell(Colonel_West(v_16), Weapon(v_17)), Hostile(Nation(x))))
(To(Sell(Colonel_West(x1), Missile(x2)), Cuba(x3)) ==> To(Sell(American(v_18), Missile(v_19)), Cuba(x3)))
(To(Sell(Colonel_West(x1), Missile(x2)), Cuba(x3)) ==> To(Sell(American(v_22), Weapon(v_23)), Cuba(x3)))
(To(Sell(Colonel_West(x1), Missile(x2)), Cuba(x3)) ==> To(Sell(Colonel_West(v_26), Weapon(v_27)), Cuba(x3)))
To(Sell(Colonel_West(x1), Missile(x2)), Cuba(x3))
```
* _When an American sells weapons to a hostile nation, that American is a criminal_
```sh
eShell: main > +STT("When an American sells weapons to a hostile nation, that American is a criminal")
Got it.

------------- All generalizations asserted.


eShell: main > s()
25 clauses in Clauses kb:

Be(Cuba(x1), Nation(x2))
Be(Cuba(x1), Hostile(Nation(x2)))
(Cuba(x) ==> Nation(x))
(Cuba(x) ==> Hostile(Nation(x)))
Be(Colonel_West(x1), American(x2))
(Colonel_West(x) ==> American(x))
Be(Missile(x1), Weapon(x2))
(Missile(x) ==> Weapon(x))
(Sell(Colonel_West(x1), Missile(x2)) ==> Sell(American(v_0), Missile(x2)))
(Sell(Colonel_West(x1), Missile(x2)) ==> Sell(American(x), Weapon(v_1)))
(Sell(Colonel_West(x1), Missile(x2)) ==> Sell(Colonel_West(x1), Weapon(v_2)))
Sell(Colonel_West(x1), Missile(x2))
(To(Sell(Colonel_West(x1), Missile(x2)), Cuba(x3)) ==> To(Sell(Colonel_West(x1), Missile(x2)), Nation(v_4)))
(To(Sell(Colonel_West(x1), Missile(x2)), Cuba(x3)) ==> To(Sell(American(v_5), Missile(v_6)), Nation(x)))
(To(Sell(Colonel_West(x1), Missile(x2)), Cuba(x3)) ==> To(Sell(American(v_7), Weapon(v_8)), Nation(x)))
(To(Sell(Colonel_West(x1), Missile(x2)), Cuba(x3)) ==> To(Sell(Colonel_West(v_9), Weapon(v_10)), Nation(x)))
(To(Sell(Colonel_West(x1), Missile(x2)), Cuba(x3)) ==> To(Sell(Colonel_West(x1), Missile(x2)), Hostile(Nation(v_11))))
(To(Sell(Colonel_West(x1), Missile(x2)), Cuba(x3)) ==> To(Sell(American(v_12), Missile(v_13)), Hostile(Nation(x))))
(To(Sell(Colonel_West(x1), Missile(x2)), Cuba(x3)) ==> To(Sell(American(v_14), Weapon(v_15)), Hostile(Nation(x))))
(To(Sell(Colonel_West(x1), Missile(x2)), Cuba(x3)) ==> To(Sell(Colonel_West(v_16), Weapon(v_17)), Hostile(Nation(x))))
(To(Sell(Colonel_West(x1), Missile(x2)), Cuba(x3)) ==> To(Sell(American(v_18), Missile(v_19)), Cuba(x3)))
(To(Sell(Colonel_West(x1), Missile(x2)), Cuba(x3)) ==> To(Sell(American(v_22), Weapon(v_23)), Cuba(x3)))
(To(Sell(Colonel_West(x1), Missile(x2)), Cuba(x3)) ==> To(Sell(Colonel_West(v_26), Weapon(v_27)), Cuba(x3)))
To(Sell(Colonel_West(x1), Missile(x2)), Cuba(x3))
(To(Sell(American(x1), Weapon(x2)), Hostile(Nation(x3))) ==> Be(American(x4), Criminal(x5)))
```
now it is time to query the Clauses Knowledge Base with the following utterance:
* _Colonel West is a criminal?_

```sh
eShell: main > +STT("reason")
Waiting for query...

eShell: main > +STT("Colonel West is a criminal")
Got it.

Reasoning...............

Query: Be(Colonel_West(x1), Criminal(x2))

 ---- NOMINAL REASONING ---

Result: False


 ---- NESTED REASONING ---

Result:  {v_219: v_129, v_220: x2, v_280: v_216, v_281: v_217, v_282: v_218, v_366: v_277, v_367: v_278, v_368: v_279}
```
Above are showen both results of Nominal Reasoning by the Backward-Chaining argorithm and Nested Reasoning.


### Word Sense Disambiguation

---------------

In order to obtain a disambiguation between labels containing the same lemma, depending on the context of
the sentence, instead of the lemma it is possible to encode labels with synsets by changing the value of DIS_ACTIVE in the
DISAMBIGUATION section of config.ini. It is also possible to specify the Parts-Of-Speech whom will be encoded. Such
encoding take in account of different word2vect similarity (provided by spaCy) combinations, between the sentence ***S*** in exam and the text fields (gloss and examples) within 
 each synset comprising each lemmatized word ***l*** in ***S***.
 
![Image 2](https://github.com/fabiuslongo/pycaspar/blob/master/images/metrics.JPG)

For instance, considering the following sentences sharing the word "bass" and their encoding:

* He likes to eat a bass
```sh
> Like.v.05:VBZ_Feed.v.06:VB(He:PRP(x1), Sea_bass.n.01:NN(x2))
```
Where the gloss of the synset "Sea_bass.n.01" is: "the lean flesh of a saltwater fish of the family Serranidae"

* He likes to play the bass
```sh
> Wish.v.02:VBZ_Play.v.18:VB(He:PRP(x1), Bass.n.07:NN(x2))
```
Where the gloss of the synset "Bass.n.07" is:"the member with the lowest range of a family of musical instruments"

Another two examples sharing the word "bank", more in detail:

* Three masked men stolen all cash money from the bank

```sh
> From_IN(Steal.v.01_VBD(Masked.s.02_JJ(Three_CD_Man.n.01_NNS(x1)), Cash.n.01_NN_Money.n.01_NN(x2)), Depository_financial_institution.n.01_NN(x3))
```

where (DIS_METRIC_COMPARISON = COMBINED):

* steal.v.01: "take without the owner's consent"
* masked.s.02: "having markings suggestive of a mask"
* money.n.02: "wealth reckoned in terms of money"
* cash.n.01: "money in the form of bills or coins"
* **depository_financial_institution.n.01: "a financial institution that accepts deposits and channels the money into lending activities"**


An the other sentence:

* The boy leapt from the bank into the cold water

```sh
> Into_IN(From_IN(Jump.v.08_VBD(Boy.n.04_NN(x1), __), Bank.n.01_NN(x3)), Cold.a.01_JJ(Body_of_water.n.01_NN(x4)))
```

where (DIS_METRIC_COMPARISON = COMBINED):

* boy.n.02: a friendly informal reference to a grown man
* jump.v.08: jump down from an elevated point
* **bank.n.01: sloping land (especially the slope beside a body of water)**
* cold.a.01: having a low or inadequate temperature or feeling a sensation of coldness or having been made cold by e.g. ice or refrigeration
* body_of_water.n.01: the part of the earth's surface covered with water (such as a river or lake or ocean)


### Grounded Meaning Context

---------------

In the scope of a distinct session, during a normal conversation, it is most likely that words with same
lemmas are considered to have the same meaning. Since slight differences in the POS classification and/or synset choice might
 lead also to unsuccessful reasoning, by setting GMC_ACTIVE = true in the section GROUNDED_MEANING_CONTEXT, it is possible
  to set all labels with the same lemma to the first synset value encountered of them, in the scope of the same session.
