WARNING: this is a pre-release version of this module - use at your own risk
============================================================================

This is a port of the Ruby gem `everypolitician-popolo
<https://github.com/everypolitician/everypolitician-popolo>` to
Python.  Even this README is strongly based on that that gem.


Installation
------------

You can install this package with:

.. code:: bash

   pip install everypolitician-popolo


Usage
-----

You can download a Popolo file manually from
`EveryPolitician <http://everypolitician.org/>`__.

The following example uses `Åland Lagting
<https://github.com/everypolitician/everypolitician-data/raw/master/data/Aland/Lagting/ep-popolo-v1.0.json>`__
(which is the legislature of the Åland islands, available as
JSON data from the `EveryPolitician page for Åland
<http://everypolitician.org/aland/>`__).

First you'll need to require the library and read in a file from disk.

.. code:: python

    from popolo_data.importer import Popolo
    popolo = Popolo.from_filename('ep-popolo-v1.0.json')

All Popolo classes used by EveryPolitician are implemented:

-  `Person <http://www.popoloproject.com/specs/person.html>`__
-  `Organization <http://www.popoloproject.com/specs/organization.html>`__
-  `Area <http://www.popoloproject.com/specs/area.html>`__
-  `Event <http://www.popoloproject.com/specs/event.html>`__
-  `Membership <http://www.popoloproject.com/specs/membership.html>`__

There are methods defined for each property on a class, e.g. for a
Person:

::

    len(popolo.persons) # => 60
    person = popolo.persons.first
    person.id # => u'e3aab23e-a883-4763-be0d-92e5936024e2'
    person.name # => u'Aaltonen Carina'
    person.image # => u'http://www.lagtinget.ax/files/aaltonen_carina.jpg'
    person.wikidata # => u"Q4934081"

You can also find individual records or collections based on their
attributes:

.. code:: python

    popolo.persons.get(name="Aaltonen Carina")
        # => <Person: Aaltonen Carina>

    popolo.organizations.filter(classification="party")
        # => [<Organization: Liberalerna>,
        #     <Organization: Liberalerna på Åland r.f.>,
        #     <Organization: Moderat Samling>,
        #     <Organization: Moderat Samling på Åland r.f.>,
        #     <Organization: Moderat samling>,
        #     <Organization: Moderaterna på Åland>,
        #     <Organization: Obunden Samling>,
        #     <Organization: Obunden Samling på Åland>,
        #     <Organization: Ålands Framtid>,
        #     <Organization: Ålands Socialdemokrater>,
        #     <Organization: Ålands framtid>,
        #     <Organization: Ålands socialdemokrater>,
        #     <Organization: Åländsk Center>,
        #     <Organization: Åländsk Center r.f.>,
        #     <Organization: Åländsk Demokrati>,
        #     <Organization: Åländsk center>]

Development
-----------

After checking out the repo, install the dependencies with:

.. code:: bash

   pip install -r requirements.txt


You can then run the tests with:

.. code:: bash

   tox

To release a new version, update the version number in
``setup.py`` and add notes to the ``CHANGES.txt`` describing
the fixes or new features.


Contributing
------------

Bug reports and pull requests are welcome on GitHub at
`<https://github.com/everypolitician/everypolitician-popolo-python>`.


License
-------

The gem is available as open source under the terms of the `MIT
License <http://opensource.org/licenses/MIT>`__.
