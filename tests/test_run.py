from unittest import TestCase
import pytest
from tkScribe.run import Run


@pytest.mark.usefixtures("scribe_class")
class TestRun(TestCase):
    def setUp(self):
        self.run = Run(family="Times",
                       size=15,
                       weight="normal",
                       slant="italic",
                       underline=1,
                       overstrike=0,
                       foreground="yellow",
                       background="black")

    def test_init_attributes(self):
        self.assertEqual(self.run.family, "Times")

    def test_init_items(self):
        self.assertEqual(self.run["family"], "Times")

    def test_change_attr(self):
        self.run.family = "test"
        self.assertEqual(self.run.family, "test")
        self.assertEqual(self.run.cget("family"), "test")
        self.assertEqual(self.run["family"], "test")

    def test_change_item(self):
        self.run["family"] = "newtest"
        self.assertEqual(self.run.family, "newtest")
        self.assertEqual(self.run.cget("family"), "newtest")
        self.assertEqual(self.run["family"], "newtest")
        self.assertEqual(self.run.family, "newtest")

    def test_set_kwargs(self):
        run = Run()
        run.__setattr__("foreground", "pink")

    def test_make_dict(self):
        d = self.run.make_dict()
        self.assertEqual(d, {'background': 'black',
                             'family': 'Times',
                             'foreground': 'yellow',
                             'overstrike': 0,
                             'size': 15,
                             'slant': 'italic',
                             'underline': 1,
                             'weight': 'normal'})

    def test_copy(self):
        r = self.run.copy()
        for k, v in {'background': 'black',
                             'family': 'Times',
                             'foreground': 'yellow',
                             'overstrike': 0,
                             'size': 15,
                             'slant': 'italic',
                             'underline': 1,
                             'weight': 'normal'}.items():
            self.assertEqual(r.__getattribute__(k), v)
            self.assertNotEqual(r.name, self.run.name)

    def test__eq__(self):
        r = self.run.copy()
        self.assertTrue(r.__eq__(self.run))

    def test_not__eq__(self):
        r = self.run.copy()
        r.family = "Garamond"
        self.assertFalse(r.__eq__(self.run))



