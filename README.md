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

## Using RPM bindings with a different Python version than the system Python

On many systems, the shim module will be able to find the system-installed RPM bindings, even if you use a different version of Python (e.g. Fedora 38 ships with Python 3.11 by default, but the shim will also work in a Python 3.10 virtualenv).

On some distributions (especially Debian/Ubuntu ones), it will not work and raise a `ModuleNotFoundError: No module named 'rpm._rpm'`. This is because those distributions encode the Python version in the name of the `_rpm.so` file: `_rpm.cpython-38-x86_64-linux-gnu.so`.

You can make the shim module work on such systems by creating a symlink to the generic `_rpm.so` name:

```bash
for file in /usr/lib/python3/dist-packages/rpm/_rpm*.cpython-*.so; do
  sudo ln -s ${file} $(echo ${file} | sed 's/\.cpython[^.]*//');
done
```
