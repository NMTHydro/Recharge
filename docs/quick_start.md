Quick Start
===========

In order to complete an ETRM simulation:

1. Download Anaconda [(version 2.x)](https://www.continuum.io/downloads), read the 
beginner's guide [here](https://wiki.python.org/moin/BeginnersGuide).
From the Anaconda site: "Anaconda is a free, easy-to-install package manager,
environment manager, Python distribution, and collection of over 720 open
source packages with free community support. Hundreds more open source
packages and their dependencies can be installed with a simple ```
conda install [packagename]```.
It’s platform-agnostic, can be used on Windows, OS X and Linux."

2. Get [git](https://git-scm.com/downloads). Read the [documentation](https://git-scm.com/doc).
Consider [GitHub Desktop](https://desktop.github.com/) if you like desktop GUI.

3. Create an env  using these [helpful instructions](https://uoa-eresearch.github.io/eresearch-cookbook/recipe/2014/11/20/conda/).
Conda envs (much like virtual envs)  create a python environment with a python executable
and install all the packages ETRM needs, isolated from other projects and
their dependencies.  For example, ETRM uses GDAL, Numpy, Pandas, and a number
of other packages.  If you have another project (say, using ArcPy), you can
have another set of packages with their dependencies and they won't interfere
with your new project. Right click and save the environment.yml 
from GitHub, use ```conda env create -f environment.yml```.
For extra info and how to get started see {official docs](http://conda.pydata.org/docs/index.html)
and a ["test drive"](http://conda.pydata.org/docs/test-drive.html).

4. Get [PyCharm IDE](https://www.jetbrains.com/pycharm/download/).
Read their [quick start guide](https://www.jetbrains.com/help/pycharm/2016.2/quick-start-guide.html).
Set the [project interpreter](https://www.jetbrains.com/help/pycharm/2016.2/quick-start-guide.html#interpreter)
to your ETRM interpreter (i.e., your new Conda env).


5. Clone our latest Recharge project from [GitHub](https://github.com/NMTHydro/Recharge).

6. Ready, set, go.

