# 0.4.0

- rpm-shim now prefers the current interpreter for searching for the `rpm` module. (#22)

# 0.3.1

- Ignore extension suffixes if the interpreter is Python 2. (#18)

# 0.3.0

- rpm-shim now tries to directly import binary extensions with incompatible suffixes,
  for instance `_rpm.cpython-39-x86_64-linux-gnu.so`, that would normally fail to be imported
  automatically while importing `rpm`. (#15)

# 0.2.0

- rpm-shim now considers also system Python interpreter called `python{majorver}.{minorver}`
  when gathering the list of paths to try importing the system `rpm` module from.
  Peviously only `python{majorver}` and `platform-python` were considered. (#11)
