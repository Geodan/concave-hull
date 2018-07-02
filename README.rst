============
Concave Hull
============

A python module of the concave hull algorithm described in this `Code Project article`_ written in C++, adapted for python using pybind11. Requires FLANN_.

.. _`Code Project article`: https://www.codeproject.com/Articles/1201438/The-Concave-Hull-of-a-Set-of-Points
.. _FLANN: https://www.cs.ubc.ca/research/flann/

Installation
============

FLANN
-----

Windows
^^^^^^^

Download FLANN 1.8 from here_ and build using a C++ compiler. Set the FLANN directory in the environment variables under the variable name FLANN_DIR.

.. code-block::

    set FLANN_DIR=path/to/flann/dir

Or set the environment variables via the control panel.

Ubuntu
^^^^^^

Install FLANN using apt:

.. code-block::

    sudo apt install libflann-dev

Or download the source_ and build.

.. code-block::

    mkdir build
    cd build
    cmake ..
    make
    make install

Set the environment variable.

.. code-block::

    export FLANN_DIR=/usr/include

.. _here: https://www.cs.ubc.ca/research/flann/
.. _source: https://github.com/mariusmuja/flann

Concave Hull
------------
With the FLANN_DIR variable set run the setup.py file using pip, by running the following command in the concave hull directory:

.. code-block::

    pip install .

Usage
=====

In python import the module and use the compute method to compute a concave hull.

.. code-block::python

    import numpy as np
    import concave_hull

    point = np.random(20, 2)
    hull = concave_hull.compute(points, 3)

Python doc
==========

Computes the concave hull of a set of points.

Parameters
----------
points : (Mx2) array
    The coordinates of the points.
k : int
    The initial k neighbors to search for.
iterate : bool
    If false the algorithm will stop after only one iteration of K, irrespective of result.

Returns
-------
hull : (Mx2) array
    The coordinates of the points of the concave hull
