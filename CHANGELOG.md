# 0.2.0

- rpm-shim now considers also system Python interpreter called `python{majorver}.{minorver}`
  when gathering the list of paths to try importing the system `rpm` module from.
  Peviously only `python{majorver}` and `platform-python` were considered. (#11)
