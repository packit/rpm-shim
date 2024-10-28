# 0.3.0

- rpm-shim now tries to directly import binary extensions with incompatible suffixes,
  for instance `_rpm.cpython-39-x86_64-linux-gnu.so`, that would normally fail to be imported
  automatically while importing `rpm`. (#15)

# 0.2.0

- rpm-shim now considers also system Python interpreter called `python{majorver}.{minorver}`
  when gathering the list of paths to try importing the system `rpm` module from.
  Peviously only `python{majorver}` and `platform-python` were considered. (#11)
