Basic client for le.taxi
========================

This small script provides a basic client for le.taxi API.

Environment
-----------

You need a python 2.7 and pip, and it's better if you have virtualenv on your machine.

Settings
--------
If you want to have a default APIKEY you can generate the settings file by running:

```
python make_settings.py
```

You just need to enter your apikey.

Installation
------------

It's better if you have a virtual environment to run this client, but it's not 
mandatory.

You can install dependencies by running this command

```
 pip install -r requirements.txt
 ```

Running
-------

You can now run this command:
```
python run.py
```

Or if you have a config file:

```
BASIC_SETTINGS=my_settings.py python run.py
```
