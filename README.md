distrowatch
===========

Distrowatch is a simple tool to see how out of date your pinned requirements.txt
packages are, as compared to pypi. All packages are saved to a json file, which 
can be served however you wish (I prefer mine medium-rare).

This is intended to be as pure python as possible, so that it's agnostic with 
regards to platform. The only outside library is pip, which you should have 
anyway.

To run
------

Run get_versions.py. I prefer to run this through a cronjob.

Requires
--------

This script uses the json library, so it requires Python 2.6 or later.
