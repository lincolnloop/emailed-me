A mini-site for checking Google's GMail feed with Oauth. See a live example at http://emailed-me.appspot.com

Setup
-----

Copy ``secrets.py.example`` to ``secrets.py`` and fill in the necessary information.

* ``SECRET_KEY`` is used by Flask. Run ``import os; os.random(24)`` and paste its results
* ``CONSUMER_KEY`` and ``CONSUMER_SECRET`` will work as is, or you can `register your app and get a key/secret from Google <http://code.google.com/apis/accounts/docs/OAuth.html#prepRegister>`_
* ``TEST_GOOGLE_EMAIL`` and ``TEST_GOOGLE_PASSWORD`` can be used to test your application, but aren't required otherwise.


Run
---

To run using the `App Engine SDK <http://code.google.com/appengine/downloads.html#Google_App_Engine_SDK_for_Python>`_, simply run::

	dev_appserver.py .
	
within this directory.

To run outside of App Engine, either:

- add ``lib`` to your ``PYTHONPATH``, or
- ``pip install -r requirements.pip``

then run::

	python application.py


Test (optional)
---------------

Testing is done using Twill. It is easiest to install the requirements via ``pip install -r requirements.pip``, then run::

	python tests.py