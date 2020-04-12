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

Features
---------
reqmapper can:

1. __produce mindmaps from spreadsheets__
2. support __various export structures__, as detailed in its configuration file (config.yml)
3. support the __rendering of requirement attributes as XMind markers__ (es.: 1,2,3 markers for a priority attribute)
4. perform various __syntax checks__ on the requirements structure (es.: find duplicate IDs, identify "orphaned" requirements, etc...)
5. scan all requirements to identify duplicates, using __semantic techniques__ (based on [NLTK](https://github.com/nltk/nltk), a python library for natural language processing)

Some of the above may look trivial at first, but if you happen to manage 100s (or 1000s) of requirements, these features can dramatically improve the way you work with them.

Use
----
reqmapper was built using Python 3.7.3 on MacOS, but also tested with other Python 3.x distributions; it also works on Windows and Linux.

After cloning this repository, It can be installed using pip:

`pip install -r requirements.txt`

The installation of NLTK and its own datasets can take a while, and will continue at the first execution of the script.

After installation is complete, reqmapper can be run as a python script from the cloned directory:

`python ./reqmapper.py --help`

reqmapper expects the datafiles in a `sources` folder in the same directory as the main script; it also expects the data files to be excel spreadsheets named with a trailing "b" for business, "u" for user and "s" for system requirements.

Attributes and the way they are named in the `sources` can be managed from the `config.yaml` file.

