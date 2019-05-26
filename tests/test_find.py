import pytest
from unittest import TestCase

wp = None

@pytest.fixture(scope="module", autouse=True)
def setup(scribe_class):
    global wp
    wp = scribe_class


class TestFind(TestCase):

    def setUp(self):
        wp.new()
        self.fd =  wp.find()
        self.rd = wp.replace()
        wp.text_editor.insert("1.0", "Some more more more")
        self.fd.inc = "1.0"
        self.fd.start = "1.0"
        self.fd.input.insert(0, "more")

    def tearDown(self):
        self.fd.destroy()
        wp.text_editor.delete("1.0", "end-1c")

    def test_find(self):
        self.fd.find()
        self.assertEqual(wp.text_editor.tag_ranges("sel")[0].string,
                         "1.5")
        self.assertEqual(wp.text_editor.tag_ranges("sel")[1].string,
                         "1.9")

    def test_find_next(self):
        first_loc = 5
        for x in range(3):
            self.fd.find()
            self.assertEqual(wp.text_editor.tag_ranges("sel")[0].string,
                             "1.{}".format(first_loc))
            first_loc += 5
        self.fd.find()
        self.assertEqual(wp.text_editor.tag_ranges("sel")[0].string, "1.5")

    def test_find_match_case_not_selected(self):
        self.fd.input.delete(0, "end")
        self.fd.input.insert(0, "MORE")
        self.fd.find()
        self.assertEqual(wp.text_editor.tag_ranges("sel")[0].string, "1.5")

    def test_find_match_case_selected(self):
        self.fd.var2.set(True)
        self.fd.input.insert(0, "MORE")
        self.fd.find()
        self.assertEqual(wp.text_editor.tag_ranges("sel"), ())

    def test_find_partial_word(self):
        self.fd.input.delete(0, "end")
        self.fd.input.insert(0, "or")
        self.fd.find()
        self.assertEqual(wp.text_editor.tag_ranges("sel")[0].string, "1.6")

    def test_find_partial_word_whole_word_selected(self):
        self.fd.input.delete(0, "end")
        self.fd.input.insert(0, "or")
        self.fd.var1.set("True")
        self.fd.find()
        self.assertEqual(wp.text_editor.tag_ranges("sel"), ())

    def test_replace(self):
        self.rd = wp.replace()
        self.rd.input.insert(0, "more")
        self.rd.replace_input.insert(0, "test")
        self.rd.replace()
        self.assertEqual(wp.text_editor.get("1.0", "end-1c"), "Some test more more")
        self.rd.destroy()

    def test_replace_all(self):
        self.rd = wp.replace()
        self.rd.input.insert(0, "more")
        self.rd.replace_input.insert(0, "test")
        self.rd.replace_all()
        self.assertEqual(wp.text_editor.get("1.0", "end-1c"), "Some test test test")
        self.rd.destroy()
