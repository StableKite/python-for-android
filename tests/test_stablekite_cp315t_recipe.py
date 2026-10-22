"""Source-only acceptance checks for StableKite's CPython 3.15t p4a recipe.

These tests do not execute a native Android build or prove that free-threaded
third-party extension imports keep the GIL disabled.
"""
import ast
import copy
import os.path
import pathlib
import types
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
P = ROOT / 'pythonforandroid/recipes/python3/__init__.py'
H = ROOT / 'pythonforandroid/recipes/hostpython3/__init__.py'


def class_node(path, name):
    module = ast.parse(path.read_text('utf-8'))
    return next(n for n in module.body if isinstance(n, ast.ClassDef) and n.name == name)


def method(cls, name):
    return next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == name)


def isolated_method(cls, name):
    f = copy.deepcopy(method(cls, name))
    f.decorator_list = []
    f.name = 'isolated_' + name
    mod = ast.fix_missing_locations(ast.Module(body=[f], type_ignores=[]))
    namespace = {'join': os.path.join}
    exec(compile(mod, '<stablekite-recipes-test>', 'exec'), namespace)
    return namespace[f.name]


class StableKiteCP315tTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.py = class_node(P, 'Python3Recipe')
        cls.host = class_node(H, 'HostPython3Recipe')

    def test_target_version(self):
        self.assertEqual(next(n.value.value for n in self.py.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id=='version' for t in n.targets)), '3.15.0')

    def test_host_version_same(self):
        self.assertEqual(next(n.value.value for n in self.host.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id=='version' for t in n.targets)), '3.15.0')

    def test_free_threading_enabled(self):
        self.assertTrue(next(n.value.value for n in self.py.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id=='disable_gil' for t in n.targets)))

    def test_link_name_free_threaded(self):
        f=isolated_method(self.py,'link_version')
        self.assertEqual(f(types.SimpleNamespace(major_minor_version_string='3.15',disable_gil=True)),'3.15t')

    def test_link_name_standard_fallback(self):
        f=isolated_method(self.py,'link_version')
        self.assertEqual(f(types.SimpleNamespace(major_minor_version_string='3.15',disable_gil=False)),'3.15')

    def test_link_name_older(self):
        f=isolated_method(self.py,'link_version')
        self.assertEqual(f(types.SimpleNamespace(major_minor_version_string='3.7',disable_gil=False)),'3.7m')

    def test_installed_header_dir_315t(self):
        f=isolated_method(self.py,'include_root')
        target=types.SimpleNamespace(link_version='3.15t',get_build_dir=lambda arch: '/tmp/repro/'+arch)
        self.assertEqual(f(target,'arm64-v8a'),'/tmp/repro/arm64-v8a/android-build/android-root/include/python3.15t')

    def test_library_filename_and_instsoname(self):
        s=P.read_text('utf-8')
        self.assertIn("return 'libpython{link_version}.so'",s)
        self.assertIn("'INSTSONAME={lib_name}'.format(lib_name=self._libpython)",s)
        self.assertIn("python_lib_name = 'libpython' + self.link_version",s)

    def test_native_flag_conditional(self):
        s=P.read_text('utf-8')
        self.assertIn('if _p_version.minor >= 13 and self.disable_gil:',s)
        self.assertIn('self.configure_args.append("--disable-gil")',s)

    def test_no_forced_gil_environment(self):
        self.assertNotIn('PYTHON_GIL=0',P.read_text('utf-8'))

    def test_ast_parse_both(self):
        ast.parse(P.read_text('utf-8'))
        ast.parse(H.read_text('utf-8'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
