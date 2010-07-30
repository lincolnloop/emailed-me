A mini-site for checking Google's GMail feed with Oauth. See a live example at http://emailed-me.appspot.com

To run on App Engine, simply run::

	dev_appserver.py .
	
within this directory.

To run outside of App Engine, either:

- add ``lib`` to your ``PYTHONPATH``, or
- ``pip install -r requirements.pip``

then run::

	python application.py