## Compile options

python-sdbus has several compiling options which can be passed to setup.py
script using environment variables.

### PYTHON_SDBUS_USE_IGNORE_SYSTEMD_VERSION

By default setup.py will try to figure out the libsystemd version
using the `pkg-config` command to disable certain features if
the libsystemd version is too low. If you want to skip the check
and enable all features set this variable `1`.

### PYTHON_SDBUS_USE_STATIC_LINK

Link statically against libsystemd and libcap. This is mainly used for
PyPI package. Set this variable to `1` if you want to enable static
linking.

### PYTHON_SDBUS_USE_LIMITED_API

Use the [stable CPython API](https://docs.python.org/3/c-api/stable.html).
This will make the python package forward compatible with future python
versions without recompiling. The minimum python version will still be 3.7.
Stable API has around 5% lower performance.
Set this variable to `1` if you want to enable use of limited API.
