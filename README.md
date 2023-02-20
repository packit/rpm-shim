# rpm-shim

Python RPM shim module for use in virtalenvs.

## Purpose

RPM Python bindings are tied to system RPM installation and are not available as a Python package (on PyPI or elsewhere). This shim module makes it possible to import and use the bindings in a virtualenv.

There is no point installing this shim module on a bare system, outside of a virtualenv. It should still work, but there is no benefit. If you want to do that anyway, pay attention not to overwrite installed RPM Python bindings.

## Example

Here is a scenario of how this module enables usage of RPM Python bindings in a newly created virtualenv. First commands are run on a host system.

```bash
# make sure RPM Python bindings are installed and functional
$ rpm -q python3-rpm
python3-rpm-4.18.0-1.fc37.x86_64

$ pip list
Package    Version
---------- -------
rpm        4.18.0

$ python -c "import rpm; print(rpm.__version__)"
4.18.0

# let's create a virtualenv
$ python -m venv env
$ source env/bin/activate

# the bindings are not accessible there
(env) $ python -c "import rpm; print(rpm.__version__)"
Traceback (most recent call last):
  File "<string>", line 1, in <module>
ModuleNotFoundError: No module named 'rpm'

# install the shim module from PyPI
(env) $ pip install rpm
...
Successfully installed rpm-0.1.0

# now we can import the bindings
(env) $ python -c "import rpm; print(rpm.__version__)"
4.18.0
```
