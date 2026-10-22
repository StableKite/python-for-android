# StableKite CPython 3.15.0t Android work branch

This branch starts at upstream `kivy/python-for-android:develop`
`8ef9d1dbbf769d2c14681dbc3c116c85e2e93bae`.

It sets both `python3` and `hostpython3` recipes to CPython **3.15.0**,
enables target `--disable-gil` and uses the **t** ABI suffix in target
`libpython3.15t.so` and installed Python headers (`include/python3.15t`).
The host-side Python tools for StableKiteApp remain independently pinned to
Python 3.14.2 / Buildozer 1.6.0 / Cython 0.29.33; recipe `hostpython3`
is the build helper for the CPython 3.15.0 *target*, not the host-tools venv.

### Scope / required acceptance

`python3 -m unittest -v tests/test_stablekite_cp315t_recipe.py` verifies
recipe source settings only. A successful source test is **not** an Android
CPython 3.15t build. Before adopting any commit for an APK, require actual
Android ARM64 NDK compile/link and the matching header/libs/JNI/SDL/bootstrap
and SONAME/SOABI evidence (`cpython-315t`), then on device verify `sys._is_gil_enabled()`
remains **False** after the PySide6/Shiboken6/pygame/lxml/PyAV imports and
Android Activity. Never use `PYTHON_GIL=0` to manufacture a pass.

The StableKiteApp legacy Python 3.14.2 build must retain its separate original
pinned `python-for-android` revision and recipes until a tested, explicit
opt-in replaces it. Do not merge to `develop` or claim Android release GO from
these source-only assertions. External pygame/PySide compatibility remains
owned by their separate projects.
