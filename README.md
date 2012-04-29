PACManager
==========

PACManager is a Django webapp designed to manage the monthly fees associated with running a PAC (Personal Alt Corp) within TEST Alliance.

Why?
----

Managing 20+ PACs became a pain the arse for everyone involved, and with our tax rules it usually ended up with corporations paying the bare minimum required, when actually they owed 5-6x more.

Installation
------------

1. Create a virtualenv, pip install requirements.
2. Setup your flavour of WSGI container and webserver (TEST uses uwsgi and Ngnix)
3. Schedule some crontabs to run the updatecorps and updatepayments management commands



