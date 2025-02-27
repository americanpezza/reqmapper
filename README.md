ReqMapper
========
ReqMapper (Requirements Mapper) is a renderer for requirements written with a formal definition into a [XMind](http://www.xmind.net) readable mindmap.

Rationale
---------
Working with large implementation projects is a complex and scary endeavour. Despite many discussions about adopting Agile techniques fully, many of these projects are run using a mixture of traditional waterfall and modern Agile tools.

Requirements are a fundamental and often underestimated part of Project Management. As we tried to [describe in a LinkedIN article](https://www.linkedin.com/pulse/semi-serious-introduction-subtle-art-requirements-mario-beccia/), capturing requirements is a long and complex endeavour, but if often a mandatory step in large projects: this mindmap generator was built to work with the requirements capture logic described in the article.

In those situations, requirements are captured and managed using either basic tools (Excel spreadsheets?) or very sophisticated frameworks (es.: [IBM Rational DOORS](https://www.ibm.com/support/knowledgecenter/SSYQBZ_9.5.0/com.ibm.doors.requirements.doc/topics/c_welcome.html )).

If you don't own a licence for those tools, or simply you want to try to make sense of the captured requirements in a more visual way, reqmapper may help. 

It can generate a XMind map starting from the requirements contained in Excel spreadsheets, and has been tested with information exported from DOORS.

Logic
------
The mechanism followed in typical requirements capture tasks is simple:

1. Capture requirements following various methods (interviews, bibliography review, brainstorming, etc...)
2. Formulate requirements using shall statements, completed with specific attributes
3. Gather requirements using any tool capable of exporting into Excel spreadsheets
4. Export the requirements into 3 or more spreadsheets, structured into business/user/system requirements
5. Use reqmapper to generate a mindmap from the exported files
6. Open with XMind and enjoy!

More details on the process can be found in [this article](https://www.linkedin.com/pulse/semi-serious-introduction-subtle-art-requirements-mario-beccia/).

Features
---------
reqmapper can:

1. __produce mindmaps from spreadsheets__
2. support __various export structures__, as detailed in its configuration file (config.yml)
3. support the __rendering of requirement attributes as XMind markers__ (es.: 1,2,3 markers for a priority attribute)
4. perform various __syntax checks__ on the requirements structure (es.: find duplicate IDs, identify "orphaned" requirements, etc...)
5. scan all requirements to identify duplicates, using __semantic techniques__ (based on [NLTK](https://github.com/nltk/nltk), a python library for natural language processing)

Some of the above may look trivial at first, but if you happen to manage 100s (or 1000s) of requirements, these features can dramatically improve the way you work with them.

Installation
-----------
reqmapper was built using Python 3.7.3 on MacOS, but also tested with other Python 3.x distributions; it also works on Windows and Linux.

After cloning this repository, installation can be completed using pip:

`pip3 install -r requirements.txt`

The installation of NLTK and its own datasets can take a while, and will continue at the first execution of the script.

Use
----
After installation is complete, reqmapper can be run as a python script from the cloned directory:

`python3 ./reqmapper.py --help`

reqmapper expects the datafiles in a `sources` folder in the same directory as the main script; it also expects the data files to be excel spreadsheets named with a trailing "b" for business, "u" for user and "s" for system requirements.

Attributes and the way they are named in the `sources` can be managed from the `config.yaml` file.

To generate a mindmap from the data in the `sources` folder:

`python3 ./reqmapper.py` 

Adding `-v` produces more information on the console about possible syntax errors in the source files. This will produce a single mindmap with 4 sheets:

1. TopDown: a map that contains grouped business requirements, linked to user requirements which are then linked to system requirements
2. BottomUp: a map similar to the above, starting from system requirements and going all the way up to business requirements
3. Issues: a map containing identified issues, such as orphans (e.g. requirements that are not linked by any other requirement) or nolinks (e.g. requirements that are not linking to any other requirement)
4. Conventions: a map detailing the meaning of the symbols and other conventions used in the other ones

The map can grow easily with the number of requirements contained in the sources: if this becomes a problem, the script can produce 2 separate maps (topdown and bottomup).

To identify potential duplicate requirements:

`python3 ./reqmapper.py -k`

With the sample dataset included in the repository, this will report that requirements UREQ600 and UREQ800 have a similarity score of 1.0, e..g they're almost equal. If you look at the requirements text, they actually look different but their meaning is the same. In situations where you have several requirements, analyzing those with a high similarity score may simplifying identifying duplciates and improve the quality of the overall set. 

Code
----
The XMind rendering logic is based on a modified version of [mekk.xmind](https://pypi.org/project/mekk.xmind/), a XMind rendering package.

The NLTK checker is adapted from an article from [nlpforhackers.io](https://nlpforhackers.io/wordnet-sentence-similarity/).

