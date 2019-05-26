import copy
import os
import pytest
from unittest import TestCase
from unittest.mock import MagicMock

from tkScribe.py_wordprocessor import basecolor, bordercolor

foreground = "#082947"
basecolor = "#f0f0f0"
path="..//"

@pytest.fixture(scope="module", autouse=True)
def setup(scribe_class):
    global wp
    wp = scribe_class


class TestInnit(TestCase):
    def test_font_color(self):
        self.assertEqual(wp.default_run.foreground, foreground)

    def test_background_color(self):
        wp.background_color = "white"
        self.assertEqual(wp.background_color, "white")

    def test_file_menu(self):
        self.assertIn(wp.file, wp.menu.winfo_children())
        self.assertIn(wp.edit, wp.menu.winfo_children())
        self.assertIn(wp.format, wp.menu.winfo_children())


class TestMinimize(TestCase):

    def setUp(self):
        self.initital_width = wp.frame.winfo_width()
        self.min = wp.format_min_width

    def tearDown(self):
        wp.minwidth = 0

    def test_resize_to_smaller_versions_of_windows_forgets_original(self):
        wp.frame.event_generate("<Configure>", width=self.min-10)
        self.assertEqual(len(wp.minimized_frames), 4)

    def test_no_frames_after_minimize_below_minwidth(self):
        wp.frame.event_generate("<Configure>", width=self.min - 10)
        wp.minimized = True
        wp.frame.event_generate("<Configure>", width=wp.minwidth - 10)
        frames = wp.get_frames()
        self.assertEqual(frames, [])

    def test_minimized_windows_restored_after_maximize(self):
        wp.frame.event_generate("<Configure>", width=self.min - 10)
        wp.minimized = True
        wp.frame.event_generate("<Configure>", width=wp.minwidth - 10)
        wp.frame.event_generate("<Configure>", width=wp.minwidth + 10)
        self.assertEqual(len(wp.get_frames()), 4)

    def test_maximize_to_normal_format_windows(self):
        wp.frame.event_generate("<Configure>", width=self.min - 10)
        wp.minimized = True
        wp.frame.event_generate("<Configure>", width=self.min + 10)
        self.assertEqual(len(wp.get_frames()), 8)


class TestMinDropdown(TestCase):
    def setUp(self):
        wp.frame.event_generate("<Configure>", width=wp.format_min_width - 10)
        wp.minimized = True

    def test_show_min_dropdown(self):
        id = 1
        wp.show_min_dropdown(1)
        for x, f in enumerate(wp.frame_list):
            if (x * 2) == id:
                self.assertTrue(f.winfo_ismapped())
            else:
                self.assertFalse(f.winfo_ismapped())

    def test_remove_frames(self):
        frames = wp.get_frames()
        wp.remove_frames()
        self.assertEqual(wp.get_frames(), [])
        for f in frames:
            self.assertFalse(f.winfo_ismapped())


class Dropdowns(TestCase):
    def setUp(self):
        self.fonts = wp.font_dropdown.get("1.0", "end-1c").split("\n")

    def tearDown(self):
        wp.hide_all_dropdowns()

    def test_call_populate_fonts(self):
        wp.populate_font_dropdown()
        self.assertNotEqual(wp.font_dropdown.get("1.0", "end-1c"), "")

    def test_font_size_exists(self):
        self.assertFalse(wp.font_size_dropdown.winfo_ismapped())

    def test_font_size_poopulated(self):
        self.assertNotEqual(wp.font_size_dropdown.get("1.0", "end-1c"), "")

    def test_linespacing_dropdown_exists(self):
        self.assertFalse(wp.line_spacing_dropdown.winfo_ismapped())

    def test_linespacing_dropdown(self):
        self.assertNotEqual(wp.line_spacing_dropdown.get("1.0", "end-1c"), "")

    def test_tab_dropdown_exists(self):
        self.assertFalse(wp.tab_dropdown.winfo_ismapped())

    def test_tab_dropdown_populated(self):
        self.assertNotEqual(wp.tab_dropdown.get("1.0", "end-1c"), "")

    def test_duplicate_text(self):
        pass

    def test_show_dropdown(self):
        for dp in [wp.font_dropdown, wp.font_size_dropdown, wp.tab_dropdown,
                   wp.line_spacing_dropdown]:
            wp.show_dropdown(dp, wp.font_selector)
            wp.update_idletasks()
            self.assertTrue(dp.winfo_ismapped())

    def test_scroll(self):
        idx = wp.font_dropdown.tag_ranges(self.fonts[-2].replace(" ", ""))[0]
        wp.scroll(wp.font_dropdown, self.fonts[-2])
        self.assertIsNotNone(wp.font_dropdown.bbox(idx))

    def test_highlight(self):
        tag = self.fonts[10].replace(" ", "")
        wp.highlight(wp.font_dropdown, tag)
        self.assertEqual(wp.font_dropdown.tag_cget(tag, "background"), basecolor)
        self.assertEqual(wp.font_dropdown.cget("state"), "disabled")

    def test_remove_highlight(self):
        tag = self.fonts[-2].replace(" ", "")
        wp.remove_highlight(wp.font_dropdown, tag)
        self.assertEqual(wp.font_dropdown.tag_cget(tag, "background"), "white")
        self.assertEqual(wp.font_dropdown.cget("state"), "disabled")


class TestPositionChangeParagraph(TestCase):
    def setUp(self):
        wp.new()
        for x in ["left", "center", "right"]:
            wp.justify(x)
            for char in "Some text\n":
                wp.text_editor.insert("insert", char)

    def test_check_pos_correct_paragraph1(self):
        for x in range(1, 4):
            wp.text_editor.mark_set("insert", "{}.2".format(x))
            wp.check_pos()
            self.assertEqual(wp.current_paragraph, "p{}".format(x))

    def test_format_buttons(self):
        for x, just in enumerate(["left", "center", "right"]):
            wp.text_editor.mark_set("insert", "{}.2".format(x+1))
            wp.check_pos()
            self.assertEqual(wp.paragraph_buttons[just]["button"].cget(
                "background"), bordercolor)
            self.assertEqual(wp.paragraph_buttons[just][
                "button"].label.cget("background"), basecolor)


class TestPositionChangeRun(TestCase):
    def setUp(self):
        wp.new()
        for char in "Some text ":
            wp.text_editor.insert("insert", char)
        wp.run_config("weight")
        for char in "Bold text":
            wp.text_editor.insert("insert", char)

    def test_buttonpress_changes_insert_to_current(self):
        self.assertEqual(wp.current_run, "r2")
        wp.text_editor.mark_set("current", "1.2")
        wp.text_editor.event_generate("<Button-1>")
        self.assertEqual(wp.current_run, "r1")

    def test_check_pos_correct_run(self):
        wp.text_editor.mark_set("insert", "1.4")
        wp.check_pos()
        self.assertEqual(wp.current_run, "r1")

    def test_check_pos_correct_second_run(self):
        wp.text_editor.mark_set("insert", "1.13")
        wp.check_pos()
        self.assertEqual(wp.current_run, "r2")

    def test_check_buttons_no_format(self):
        wp.text_editor.mark_set("insert", "1.4")
        wp.check_pos()
        self.assertEqual(wp.font_buttons["weight"]["button"].cget(
                         "background"), basecolor)

    def test_check_buttons_without_format(self):
        for b in ["slant", "underline", "overstrike"]:
            wp.text_editor.mark_set("insert", "1.14")
            wp.check_pos()
            wp.set_format_buttons()
            self.assertEqual(wp.font_buttons[b]["button"].cget(
                             "background"), basecolor)
            self.assertEqual(wp.font_buttons[b]["button"].label.cget(
                "background"), basecolor)

    def test_check_buttons_with_format(self):
        wp.text_editor.mark_set("insert", "1.14")
        wp.check_pos()
        wp.set_format_buttons()
        self.assertEqual(wp.font_buttons["weight"]["button"].cget(
            "background"), bordercolor)
        self.assertEqual(wp.font_buttons["weight"]["button"].label.cget(
            "background"), basecolor)

    def test_format_button_removed_when_pos_changed(self):
        wp.text_editor.mark_set("insert", "1.2")
        wp.check_pos()
        wp.set_format_buttons()
        self.assertEqual(wp.font_buttons["weight"]["button"].cget(
            "background"), basecolor)
        self.assertEqual(wp.font_buttons["weight"]["button"].label.cget(
            "background"), basecolor)


class TestWordProcessor(TestCase):

    def setUp(self):
        wp.new()

    def test_delete_updates_wordcount(self):
        for char in "test":
            wp.text_editor.insert("insert", char)
        wp.text_editor.delete("1.2", "end-1c")
        self.assertEqual(wp.char_num_label.cget("text"),
                         "1 words - 2 chars")

    def test_italic_no_extra_space(self):
        wp.text_editor.update()
        wp.text_editor.event_generate("<Control-i>")
        self.assertEqual(wp.text_editor.index("insert"), "1.0")

    def test_find_current(self):
        self.assertEqual(wp.find_current("r"), "r1")
        self.assertEqual(wp.find_current("p"), "p1")

        self.assertEqual(wp.find_current("r", "10.12"), "r1")
        self.assertEqual(wp.find_current("p", "end"), "p1")
        self.assertEqual(wp.find_current("r", "insert"), "r1")
        self.assertEqual(wp.find_current("r", "current"), "r1")

        self.assertRaises(AttributeError, wp.find_current, "p", "1.0")

    # Paragraph configuration
    def test_set_mark(self):
        self.assertEqual(wp.set_mark("r", "index"), "r2")
        self.assertEqual(wp.set_mark("p", "index"), "p2")

    def test_set_tab(self):
        wp.set_tab(5)
        self.assertEqual(wp.current_paragraph, "p1")
        self.assertTrue(wp.text_editor.tag_cget("p1", "tabs"), (5,))
        wp.current_paragraph = "p10"
        wp.set_tab(10)
        self.assertEqual(wp.current_paragraph, "p2")

    def test_linespacing_config(self):
        wp.linespacing_config("BEFORE_3.0")
        self.assertEqual(wp.text_editor.tag_cget("p1", "spacing1"),
                         "3.0")
        wp.linespacing_config("DURING_10.0")
        self.assertEqual(wp.text_editor.tag_cget("p1", "spacing2"),
                         "10.0")
        wp.linespacing_config("AFTER_3.0")
        self.assertEqual(wp.text_editor.tag_cget("p1", "spacing3"),
                         "3.0")

    def test_check_new_paragraph(self):
        wp.check_new_paragraph()
        self.assertEqual(wp.current_paragraph, "p1")
        wp.check_new_paragraph("insert linestart")
        self.assertEqual(wp.current_paragraph, "p1")

    def test_paragraph_init(self):
        self.assertEqual(wp.text_editor.tag_cget("p1", "justify"), "left")

    def test_update_entry(self):
        w = wp.font_selector
        wp.update_entry("test", w)
        self.assertEqual(w.get(), "test")

    def test_help_text(self):
        wp.help_text(wp.font_buttons["weight"]["button"])
        wp.update_idletasks()
        self.assertTrue(wp.help_text_label.winfo_ismapped())
        self.assertEqual(wp.help_text_label.get("1.0", "end-1c"),
                         "\n\n".join(wp.font_buttons["weight"][
                                         "button"].help_text)+"\n\n")
        wp.text_editor.mark_set("current", "1.0")

    def test_remove_help_text(self):
        wp.help_text(wp.font_buttons["weight"]["button"])
        wp.update_idletasks()
        self.assertTrue(wp.help_text_label.winfo_ismapped())
        wp.remove_help_text()
        self.assertFalse(wp.help_text_label.winfo_ismapped())

    # New
    def test_first_run(self):

        self.assertTrue("r1" in wp.text_editor.mark_names())
        self.assertTrue("p1" in wp.text_editor.mark_names())

    def test_r0_applied_from_start(self):
        self.assertNotEqual(wp.text_editor.tag_cget("r1", "font"), "")
        self.assertEqual(wp.text_editor.tag_cget("r1", "foreground"),
                         foreground)
        self.assertEqual(wp.text_editor.tag_cget("r1", "background"), "white")

    def test_p0_applied_from_start(self):
        self.assertEqual(wp.text_editor.tag_cget("p1", "justify"), "left")
        self.assertEqual(wp.text_editor.tag_cget("p1", "spacing1"), "0")
        self.assertEqual(wp.text_editor.tag_cget("p1", "spacing2"), "0")
        self.assertEqual(wp.text_editor.tag_cget("p1", "spacing3"), "0")

    def test_variables(self):
        self.assertFalse("r_BEFORE" in wp.text_editor.tag_names())

    def test_fonts_deleted(self):
        wp.text_editor.insert("1.0", "text")
        wp.run_config("weight")
        wp.new()
        self.assertEqual(len(wp.runs), 1)

    def test_delete_fonts(self):
        wp.delete_runs()
        self.assertEqual(len(wp.runs), 1)
        self.assertTrue("r1" in wp.runs.keys())
        for param in wp.preferences["font"]:
            self.assertEqual(wp.runs["r1"].cget(param), wp.preferences["font"][
                param])

    def test_button_reset(self):
        buttons = ["weight", "slant", "underline", "overstrike"]
        for button in buttons:
            wp.font_buttons[button]["button"].label.configure(background="red")
        wp.new()
        for button in buttons:
            self.assertEqual(wp.font_buttons[button]["button"].label.cget(
                "background"), basecolor)
            self.assertEqual(wp.font_buttons[button]["button"].cget(
                "background"), basecolor)

    def test_format_button_reset(self):
        wp.new()
        self.assertEqual(wp.paragraph_buttons["left"]["button"].label.cget(
            "background"), wp.paragraph_buttons["left"][
            "button"].active_background)
        self.assertEqual(wp.paragraph_buttons["left"]["button"].cget(
            "background"), wp.paragraph_buttons["left"][
            "button"].active_border)

    def test_set_new_font_glitch(self):
        pass

    def test_font_dict_equals_run_marks(self):
        runs = [run for run in wp.text_editor.mark_names() if
                run.startswith("r") and run != "right"]
        keys = list(wp.runs.keys())
        self.assertEqual(runs, keys)

    def test_ext_handling_no_period(self):
        wp.document.path = "test"
        wp.ext_handling()
        self.assertEqual(wp.document.path, "test.scribe")

    def test_get_paragraph_no_text(self):
        wp.new()
        p = wp.get_paragraphs()
        self.assertEqual(p, {'p1': {'index': ('1.0', '1.0'), 'justify': 'left',
                                 'spacing1': '0', 'spacing2': '0',
                                   'spacing3': "0", "tabs": "20"}})

    def test_save_formatting(self):
        wp.get_runs()
        for run in wp.document.runs:
            self.assertEqual(run[0], "r")
            int(run[1:])

        for p in wp.document.paragraphs:
            self.assertEqual(p[0], "p")
            int(p[1:])

    def test_set_justification_buttons(self):
        wp.set_justification_buttons("center")
        self.assertEqual(wp.paragraph_buttons["center"]["button"].cget(
            "background"), wp.paragraph_buttons["center"][
            "button"].active_border)
        self.assertEqual(wp.paragraph_buttons["center"][
                             "button"].label.cget("background"),
                         wp.paragraph_buttons["center"][
                             "button"].active_background)

        self.assertEqual(wp.paragraph_buttons["left"][
                             "button"].label.cget("background"),
                         wp.paragraph_buttons["left"][
                             "button"].inactive_background)
        self.assertEqual(wp.paragraph_buttons["right"][
                             "button"].label.cget("background"),
                         wp.paragraph_buttons["right"][
                             "button"].inactive_background)

    def test_find_current(self):

        wp.find_current("r")
        self.assertEqual(wp.current_run, "r1")
        wp.find_current("p")
        self.assertEqual(wp.current_paragraph, "p1")

    def test_set_mark_same_line_dif_pos(self):
        wp.set_mark("p", "index linestart")
        self.assertEqual(wp.current_paragraph, "p1")

    def test_set_mark_diff_line_dif_pos(self):
        wp.set_mark("p", "2.5 linestart")
        self.assertEqual(wp.current_paragraph, "p1")

    # Save

@pytest.mark.creates_dialogue
class open_save(TestCase):
    def setUp(self):
        wp.new()
        for char in "Testing":
            wp.text_editor.insert("insert", char)
        wp.save(False, wp.preferences["dir"]+"test.scribe")

    def tearDown(self):
        wp.new()
        os.remove(wp.preferences["dir"]+"test.scribe")

    def test_open_no_filepath(self):
        wp.open()

    def test_open_with_pickling_error(self):
        wp.open("{}images//logo.ico".format(path))

    def test_save_no_filename(self):
        wp.save()

    def test_save_as_txt(self):
        wp.save(False, wp.preferences["dir"] + "test.txt")
        self.assertTrue(os.path.exists(wp.preferences["dir"] + "test.txt"))
        os.remove(wp.preferences["dir"] + "test.txt")


class TestFont(TestCase):
    def setUp(self):
        wp.new()

    def test_check_create_new_run_start(self):
        wp.set_mark("insert", "1.0")
        res = wp.check_create_new_format(wp.current_run)
        self.assertEqual(res, False)

    def test_check_create_new_run_end(self):
        for char in "text":
            wp.text_editor.insert("insert", char)
        res = wp.check_create_new_format(wp.current_run)
        self.assertEqual(res, True)

    def test_check_create_new_run_middle(self):
        for char in "text":
            wp.text_editor.insert("insert", char)
        wp.text_editor.mark_set("insert", "1.2")
        res = wp.check_create_new_format(wp.current_run)
        self.assertEqual(res, True)

    def test_check_create_new_run_selected_all(self):
        for char in "text":
            wp.text_editor.insert("insert", char)
        wp.text_editor.tag_add("sel", "1.0", "1.4")
        res = wp.check_create_new_format(wp.current_run)
        self.assertEqual(res, False)

    def test_check_create_new_start_selected_all(self):
        for char in "text":
            wp.text_editor.insert("insert", char)
        wp.text_editor.tag_add("sel", "1.0", "1.2")
        res = wp.check_create_new_format(wp.current_run)
        self.assertEqual(res, True)

    def test_toggle_font_values(self):
        before = wp.runs[wp.current_run].weight
        wp.toggle_font_values(wp.runs[wp.current_run], "weight")
        self.assertNotEqual(wp.runs[wp.current_run].weight, before)

    def test_toggle_fonts_default_run_not_changed(self):
        wp.toggle_font_values(wp.runs[wp.current_run], "weight")
        self.assertEqual(wp.default_run.weight, "normal")

    def test_run_config_args_same_run(self):
        wp.run_config("weight")
        self.assertNotIn("r2", wp.runs.keys())
        self.assertEqual(wp.runs["r1"].weight, "bold")

    def test_run_config_args_new_run(self):
        wp.text_editor.insert("insert", "t")
        wp.run_config("weight")
        self.assertEqual(len(wp.runs), 2)
        self.assertEqual(wp.runs[wp.current_run].weight, "bold")

    def test_config_run_tag(self):
        wp.text_editor.insert("insert", "t")
        wp.run_config("slant")
        self.assertIn("r2", wp.text_editor.tag_names())

    # Changes default run
    def test_font_config(self):
        wp.run_config(family="Courier", size="25")
        self.assertEqual(wp.runs[wp.current_run].cget("family"), "Courier")
        self.assertEqual(wp.runs[wp.current_run].cget("size"), 25)
        wp.run_config("weight")
        self.assertEqual(wp.runs[wp.current_run].cget("weight"), "bold")

        wp.run_config("slant")
        self.assertEqual(wp.runs[wp.current_run].cget("slant"), "italic")

    def test_font_config_not_removed_current_from_selected_all(self):
        cr = wp.current_run
        for _ in range(3):
            wp.text_editor.insert("insert", "g")
        wp.text_editor.tag_add("sel", "1.0", "1.3")
        wp.run_config("weight")
        self.assertEqual(wp.text_editor.tag_ranges(cr)[0].string, "1.0")
        self.assertEqual(wp.text_editor.tag_ranges(cr)[1].string, "1.3")

    def test_font_config_removed_current_from_selected_start(self):
        cr = wp.current_run
        for _ in range(3):
            wp.text_editor.insert("insert", "g")
        wp.text_editor.tag_add("sel", "1.0", "1.1")
        wp.run_config("weight")
        self.assertEqual(wp.text_editor.tag_ranges(cr)[0].string, "1.1")
        self.assertEqual(wp.text_editor.tag_ranges(cr)[1].string, "1.3")

    def test_font_config_removed_current_from_selected_middle(self):
        for _ in range(3):
            wp.text_editor.insert("insert", "g")
        wp.text_editor.tag_add("sel", "1.1", "1.2")
        wp.run_config("weight")
        self.assertEqual(wp.text_editor.tag_ranges("r1")[0].string, "1.0")
        self.assertEqual(wp.text_editor.tag_ranges("r1")[1].string, "1.1")
        self.assertEqual(wp.text_editor.tag_ranges("r1")[2].string, "1.2")
        self.assertEqual(wp.text_editor.tag_ranges("r1")[3].string, "1.3")

    def test_font_config_removed_current_from_selected_end(self):
        for _ in range(3):
            wp.text_editor.insert("insert", "g")
        wp.text_editor.tag_add("sel", "1.2", "1.3")
        wp.run_config("weight")
        self.assertEqual(wp.text_editor.tag_ranges("r1")[0].string, "1.0")
        self.assertEqual(wp.text_editor.tag_ranges("r1")[1].string, "1.2")

    def test_font_config_selected_run_created_start(self):
        for _ in range(3):
            wp.text_editor.insert("insert", "g")
        wp.text_editor.tag_add("sel", "1.0", "1.1")
        wp.run_config("weight")
        self.assertEqual(wp.text_editor.tag_ranges("r2")[0].string, "1.0")
        self.assertEqual(wp.text_editor.tag_ranges("r2")[1].string, "1.1")
        self.assertEqual(wp.runs["r2"].weight, "bold")

    def test_run_font_color(self):
        wp.run_config(foreground="pink")
        self.assertEqual(wp.runs["r1"].foreground, "pink")

    def test_tag_font_color(self):
        wp.run_config(foreground="pink")
        self.assertEqual(wp.text_editor.tag_cget("r1", "foreground"), "pink")

    def test_run_background_color(self):
        wp.run_config(background="pink")
        self.assertEqual(wp.runs["r1"].background, "pink")

    def test_tag_font_color(self):
        wp.run_config(background="pink")
        self.assertEqual(wp.text_editor.tag_cget("r1", "background"), "pink")

    @pytest.mark.creates_dialogue
    def test_foreground_changes_run(self):
        wp.foreground(color="#ffc0cb")
        self.assertEqual(wp.runs[wp.current_run].foreground, "#ffc0cb")

    @pytest.mark.creates_dialogue
    def test_fbackground_changes_run(self):
        wp.background(color="#ffc0cb")
        self.assertEqual(wp.runs[wp.current_run].background, "#ffc0cb")


class TestParagraph(TestCase):

    def setUp(self):
        wp.new()
        for char in "Some text":
            wp.text_editor.insert("insert", char)

    def test_paragraph_index(self):
        self.assertEqual(wp.text_editor.tag_ranges("p1")[0].string, "1.0")
        self.assertEqual(wp.text_editor.tag_ranges("p1")[1].string, "1.9")

    def test_new_paragraph_not_added_on_same_line(self):
        wp.justify("center")
        self.assertFalse("p2" in wp.text_editor.tag_names())

    def test_new_justification_applied(self):
        wp.justify("right")
        self.assertEqual(wp.text_editor.tag_cget("p1", "justify"), "right")

    def test_paragraph_marks_equal_paragraph_tags(self):
        marks = [m for m in wp.text_editor.mark_names() if m.startswith("p")]
        tags = [t for t in wp.text_editor.tag_names() if t.startswith("p")]
        self.assertEqual(marks, tags)

    def test_new_line_doesnt_equal_new_paragraph(self):
        wp.justify("center")
        wp.text_editor.insert("insert", "\nc")
        self.assertEqual(wp.text_editor.index("insert linestart"), "2.0")
        self.assertNotIn("p2", wp.text_editor.tag_names())

    def test_new_line_does_equal_new_paragraph(self):
        wp.text_editor.insert("insert", "\nc")
        wp.justify("center")
        self.assertIn("p1", wp.text_editor.tag_names())

@pytest.mark.creates_dialogue
class TestParagraphs_saved_and_loaded(TestCase):
    def setUp(self):
        wp.new()
        wp.justify("center")
        for char in "test\n":
            wp.text_editor.insert("insert", char)
        wp.justify("left")
        for char in "test\n":
            wp.text_editor.insert("insert", char)
        wp.justify("right")
        for char in "test\n":
            wp.text_editor.insert("insert", char)
        wp.save(False, "test.scribe")
        wp.new()
        wp.open("test.scribe")

    def test_center_tag_loaded(self):
        self.assertEqual(wp.text_editor.tag_cget("p1", "justify"), "center")

    def test_left_tag_loaded(self):
        self.assertEqual(wp.text_editor.tag_cget("p2", "justify"), "left")

    def test_right_tag_loaded(self):
        self.assertEqual(wp.text_editor.tag_cget("p3", "justify"), "right")

    def test_center_tag_range(self):
        self.assertEqual(wp.text_editor.tag_ranges("p1")[0].string, "1.0")

    def test_left_tag_range(self):
        self.assertEqual(wp.text_editor.tag_ranges("p2")[0].string, "2.0")

    def test_right_tag_range(self):
        self.assertEqual(wp.text_editor.tag_ranges("p3")[0].string, "3.0")


class Test_Font_Selected(TestCase):
    def setUp(self):
        wp.new()
        self.txt = "Some text"
        for char in self.txt:
            wp.text_editor.insert("insert", char)

    def tearDown(self):
        wp.new()

    def test_select_all(self):
        wp.text_editor.tag_add("sel", "1.0", "end-1c")
        wp.run_config("weight")
        self.assertEqual(wp.text_editor.tag_ranges("r1")[0].string, "1.0")
        self.assertEqual(wp.text_editor.tag_ranges("r1")[1].string, "1.9")
        self.assertEqual(wp.runs["r1"].cget("weight"), "bold")

    def test_select_beginning(self):
        wp.text_editor.tag_add("sel", "1.0", "1.5")
        wp.run_config("slant")
        self.assertEqual(wp.text_editor.tag_ranges("r2")[0].string, "1.0")
        self.assertEqual(wp.text_editor.tag_ranges("r2")[1].string, "1.5")
        self.assertEqual(wp.runs["r2"].cget("slant"), "italic")
#
        self.assertEqual(wp.text_editor.tag_ranges("r1")[0].string, "1.5")
        self.assertEqual(wp.text_editor.tag_ranges("r1")[1].string, "1.9")
        self.assertEqual(wp.runs["r1"].cget("slant"), "roman")

    def test_select_middle(self):
        wp.text_editor.tag_add("sel", "1.5", "1.8")
        wp.run_config("underline")
        self.assertEqual(wp.text_editor.tag_ranges("r1")[0].string, "1.0")
        self.assertEqual(wp.text_editor.tag_ranges("r1")[1].string, "1.5")
        self.assertEqual(wp.runs["r1"].cget("underline"), 0)

        self.assertEqual(wp.text_editor.tag_ranges("r2")[0].string, "1.5")
        self.assertEqual(wp.text_editor.tag_ranges("r2")[1].string, "1.8")
        self.assertEqual(wp.runs["r2"].cget("underline"), 1)

        self.assertEqual(wp.text_editor.tag_ranges("r1")[2].string, "1.8")
        self.assertEqual(wp.text_editor.tag_ranges("r1")[3].string, "1.9")
        self.assertEqual(wp.runs["r1"].cget("underline"), 0)


class Test_Selected_Justify(TestCase):
    def setUp(self):
        wp.new()
        wp.text_editor.tag_remove("sel", "1.0")
        for char in "Some text":
            wp.text_editor.insert("insert", char)
            wp.text_editor.insert("insert", "\n")

    def test_setUp(self):
        self.assertEqual(wp.text_editor.index("end-1c"), "10.0")
        self.assertEqual(len(wp.text_editor.tag_ranges("p1")), 2)

    def test_para_start(self):
        self.assertEqual(wp.text_editor.tag_ranges("p1")[0].string, "1.0")

    def test_para_end(self):
        self.assertEqual(wp.text_editor.tag_ranges("p1")[1].string, "10.0")

    def test_split_paragraph_same_start_same_end(self):
        wp.text_editor.tag_add("sel", "1.0", "10.0")
        wp.split_paragraph("center")
        self.assertIn("p1", wp.text_editor.tag_names("1.0"))
        self.assertIn("p1", wp.text_editor.tag_names("3.8"))
        self.assertIn("p1", wp.text_editor.tag_names("9.0"))

    def test_split_paragraph_same_start_smaller_end(self):
        wp.text_editor.tag_add("sel", "1.0", "5.0")
        wp.split_paragraph("center")
        self.assertNotIn("p1", wp.text_editor.tag_names("2.5"))
        self.assertIn("p1", wp.text_editor.tag_names("6.0"))
        self.assertIn("p2", wp.text_editor.tag_names("3.5"))
        self.assertNotIn("p3", wp.text_editor.tag_names())

    def test_split_paragraph_diff_start_same_end(self):
        wp.text_editor.tag_add("sel", "4.0", "10.0")
        wp.split_paragraph("center")
        self.assertIn("p1", wp.text_editor.tag_names("2.3"))
        self.assertNotIn("p1", wp.text_editor.tag_names("5.0"))
        self.assertIn("p2", wp.text_editor.tag_names("5.3"))
        self.assertNotIn("p3", wp.text_editor.tag_names())

    def test_split_paragraph_dif_start_diff_end(self):
        wp.text_editor.tag_add("sel", "3.0", "7.0")
        wp.split_paragraph("center")
        self.assertIn("p1", wp.text_editor.tag_names("2.3"))
        self.assertNotIn("p1", wp.text_editor.tag_names("4.5"))
        self.assertIn("p2", wp.text_editor.tag_names("6.2"))
        self.assertNotIn("p2", wp.text_editor.tag_names("2.2"))
        self.assertIn("p1", wp.text_editor.tag_names("8.2"))
        self.assertNotIn("p2", wp.text_editor.tag_names("9.3"))

    def test_justify_all(self):
        wp.text_editor.tag_add("sel", "1.0", "end-1c")
        wp.justify("right")
        self.assertEqual(wp.text_editor.tag_cget("p1", "justify"), "right")

    def test_justify_beginning(self):
        wp.text_editor.tag_add("sel", "1.0", "4.0")
        wp.justify("center")
        self.assertEqual(wp.text_editor.tag_cget("p1", "justify"), "left")
        self.assertEqual(wp.text_editor.tag_cget("p2", "justify"), "center")

    def test_justify_end(self):
        wp.text_editor.tag_add("sel", "5.0", "11.0")
        wp.justify("center")
        self.assertEqual(wp.text_editor.tag_cget("p1", "justify"), "left")
        self.assertEqual(wp.text_editor.tag_cget("p2", "justify"), "center")

    def test_justify_middle(self):
        wp.text_editor.tag_add("sel", "2.0", "7.5")
        wp.justify("right")
        self.assertEqual(wp.text_editor.tag_cget("p1", "justify"), "left")
        self.assertEqual(wp.text_editor.tag_cget("p2", "justify"), "right")


# Clipboard
class TestSelectAll(TestCase):
    def setUp(self):
        wp.new()
        for x in range(10):
            wp.text_editor.insert("insert", "a")

    def tearDown(self):
        wp.new()

    def test_select_all(self):
        wp.select_all()
        self.assertEqual(len(wp.text_editor.get("sel.first", "sel.last")), 10)

    def test_cut(self):
        wp.text_editor.tag_add("sel", "1.0", "end-1c")
        wp.cut()
        self.assertEqual(wp.text_editor.get("1.0", "end-1c"), "")


class TestCopy(TestCase):
    def setUp(self):
        wp.new()
        for word in ["normal", " bold ", "normal"]:
            for char in word:
                wp.text_editor.insert("insert", char)
            wp.run_config("weight")

    def tearDown(self):
        wp.new()

    def test_set_up(self):
        self.assertEqual(wp.text_editor.get("1.0", "end-1c"),
                         "normal bold normal")
        self.assertIn("r1", wp.text_editor.tag_names("1.1"))
        self.assertIn("r2", wp.text_editor.tag_names("1.8"))
        self.assertIn("r3", wp.text_editor.tag_names("1.15"))

    def test_get_tags_in_range_start(self):
        wp.text_editor.tag_add("sel", "1.0", "1.2")
        wp.copy()

    def test_get_tags_in_range_all(self):
        wp.text_editor.tag_add("sel", "1.0", "end-1c")
        tags = wp.get_tags_in_range()
        self.assertEqual(tags, [
                                ['n', 'r1', 'p1'],
                                ['o', 'r1', 'p1'],
                                ['r', 'r1', 'p1'],
                                ['m', 'r1', 'p1'],
                                ['a', 'r1', 'p1'],
                                ['l', 'r1', 'p1'],
                                [' ', 'r2', 'p1'],
                                ['b', 'r2', 'p1'],
                                ['o', 'r2', 'p1'],
                                ['l', 'r2', 'p1'],
                                ['d', 'r2', 'p1'],
                                [' ', 'r2', 'p1'],
                                ['n', 'r3', 'p1'],
                                ['o', 'r3', 'p1'],
                                ['r', 'r3', 'p1'],
                                ['m', 'r3', 'p1'],
                                ['a', 'r3', 'p1'],
                                ['l', 'r3', 'p1']])

    def test_ctrc_content(self):
        wp.text_editor.tag_add("sel", "1.0", "1.1")
        wp.update()
        wp.text_editor.event_generate("<Control-c>")
        self.assertEqual(wp.copied_runs, [["n", "r1", "p1"]])


class TestPaste(TestCase):
    def setUp(self):
        wp.new()
        for char in "normal ":
            wp.text_editor.insert("insert", char)
        wp.run_config("weight")
        for char in "bold":
            wp.text_editor.insert("insert", char)
        wp.text_editor.tag_add("sel", "1.7", "1.11")
        wp.copy()
        wp.text_editor.mark_set("insert", "1.0")
        wp.current_run = wp.find_current("r")
        wp.paste()

    def tearDown(self):
        wp.new()

    def test_hotkey_no_duplication(self):
        wp.new()
        wp.text_editor.insert("1.0", "a")
        wp.text_editor.tag_add("sel", "1.0", "1.1")
        wp.text_editor.update()
        wp.text_editor.event_generate("<Control-c>")
        wp.text_editor.event_generate("<Control-v>")
        self.assertEqual(wp.text_editor.get("1.0", "end-1c"), "aa")



    def test_text(self):
        self.assertEqual(wp.text_editor.get("1.0", "end-1c"), "boldnormal bold")

    def test_r1_range(self):
        self.assertEqual(wp.text_editor.tag_ranges("r1")[0].string, "1.4")
        self.assertEqual(wp.text_editor.tag_ranges("r1")[1].string, "1.11")
        self.assertEqual(len(wp.text_editor.tag_ranges("r1")), 2)

    def test_r2_range(self):
        self.assertEqual(wp.text_editor.tag_ranges("r2")[0].string, "1.11")
        self.assertEqual(wp.text_editor.tag_ranges("r2")[1].string, "1.15")
        self.assertEqual(len(wp.text_editor.tag_ranges("r2")), 2)

    def test_r3_range(self):
        self.assertEqual(wp.text_editor.tag_ranges("r3")[0].string, "1.0")
        self.assertEqual(wp.text_editor.tag_ranges("r3")[1].string, "1.4")
        self.assertEqual(len(wp.text_editor.tag_ranges("r3")), 2)

    def test_no_r4(self):
        self.assertNotIn("r4", wp.text_editor.tag_names())

    def test_r1_weight(self):
        self.assertEqual(wp.runs["r1"].cget("weight"), "normal")

    def test_r1_mark(self):
        self.assertEqual(wp.text_editor.tag_ranges("r1")[0].string,
                         wp.text_editor.index("r1"))


class TestPasteMiddle(TestCase):
    def setUp(self):
        for char in "normal ":
            wp.text_editor.insert("insert", char)
        wp.run_config("weight")
        for char in "bold":
            wp.text_editor.insert("insert", char)
        wp.text_editor.tag_add("sel", "1.7", "1.11")
        wp.copy()
        wp.text_editor.mark_set("insert", "1.2")
        wp.current_run = wp.find_current("r")
        wp.paste()

    def tearDown(self):
        wp.new()

    def test_text(self):
        self.assertEqual(wp.text_editor.get("1.0", "end-1c"),
                         'noboldrmal bold')

    def test_r1_range(self):
        self.assertEqual(wp.text_editor.get("1.0", "1.2"), "no")
        self.assertEqual(wp.text_editor.tag_ranges("r1")[0].string, "1.0")
        self.assertEqual(wp.text_editor.tag_ranges("r1")[1].string, "1.1")
        self.assertEqual(len(wp.text_editor.tag_ranges("r1")), 2)
        self.assertEqual(wp.text_editor.tag_ranges("r1")[0].string,
                         wp.text_editor.index("r1"))

    def test_r3_range(self):
        self.assertEqual(wp.text_editor.get("1.6", "1.10"), "rmal")
        self.assertEqual(wp.text_editor.tag_ranges("r3")[0].string, "1.6")
        self.assertEqual(wp.text_editor.tag_ranges("r3")[1].string, "1.11")

    def test_r4_range(self):
        self.assertEqual(wp.text_editor.get("1.2", "1.6"), "bold")
        self.assertEqual(wp.text_editor.tag_ranges("r4")[0].string, "1.2")
        self.assertEqual(wp.text_editor.tag_ranges("r4")[1].string, "1.6")


class TestSplit(TestCase):
    def setUp(self):
        for char in "one ":
            wp.text_editor.insert("insert", char)
        wp.run_config("weight")
        for char in "two":
            wp.text_editor.insert("insert", char)

    def tearDown(self):
        wp.new()

    def test_setup(self):
        self.assertEqual(wp.text_editor.get("1.0", "end-1c"), "one two")
        self.assertEqual(wp.text_editor.tag_ranges("r1")[0].string, "1.0")
        self.assertEqual(wp.text_editor.tag_ranges("r1")[1].string, "1.4")
        self.assertEqual(wp.text_editor.tag_ranges("r2")[0].string, "1.4")
        self.assertEqual(wp.text_editor.tag_ranges("r2")[1].string, "1.7")
        self.assertNotIn("r3", wp.text_editor.tag_names())

    def test_insert_at_start_r1(self):
        wp.text_editor.mark_set("insert", "1.0")
        wp.split("r")
        self.assertEqual(wp.text_editor.tag_ranges("r1")[0].string, "1.0")
        self.assertEqual(wp.text_editor.tag_ranges("r1")[1].string, "1.4")
        self.assertNotIn("r3", wp.text_editor.tag_names())

    def test_insert_at_middle_r1(self):
        wp.text_editor.mark_set("insert", "1.2")
        wp.split("r")
        self.assertEqual(wp.text_editor.tag_ranges("r1")[0].string, "1.0")
        self.assertEqual(wp.text_editor.tag_ranges("r1")[1].string, "1.1")

    def test_insert_at_middle_r3(self):
        wp.text_editor.mark_set("insert", "1.2")
        wp.split("r")
        self.assertEqual(wp.text_editor.tag_ranges("r3")[0].string, "1.2")
        self.assertEqual(wp.text_editor.tag_ranges("r3")[1].string, "1.4")

    def test_insert_at_end_r1(self):
        wp.text_editor.mark_set("insert", "1.4")
        wp.split("r")
        self.assertEqual(wp.text_editor.tag_ranges("r1")[0].string, "1.0")
        self.assertEqual(wp.text_editor.tag_ranges("r1")[1].string, "1.4")


class TestGetParagraph(TestCase):
    def setUp(self):
        wp.new()
        wp.justify("center")
        wp.text_editor.insert("insert", "center\n")
        wp.justify("right")
        wp.text_editor.insert("insert", "right\n")
        wp.justify("left")
        wp.text_editor.insert("insert", "left")

    def test_setup(self):
        self.assertEqual(wp.text_editor.get("1.0", "end-1c"),
                         "center\nright\nleft")
        self.assertIn("p3", wp.text_editor.tag_names())

    def test_get_paragraphs(self):
        self.assertEqual(wp.get_paragraphs(), {'p1': {'index': ('1.6', '2.0'),
                                                      'justify': 'center',
                                                      'spacing1': '0',
                                                      'spacing2': '0',
                                                      'spacing3': '0',
                                                      'tabs': '20'},
                                                'p2': {'index': ('2.5', '3.0'),
                                                       'justify': 'right',
                                                       'spacing1': '0',
                                                       'spacing2': '0',
                                                       'spacing3': '0',
                                                       'tabs': '20'},
                                                'p3': {'index': ('3.3', '3.4'),
                                                       'justify': 'left',
                                                       'spacing1': '0',
                                                       'spacing2': '0',
                                                       'spacing3': '0',
                                                       'tabs': '20'}})

# This class needs to be last as it creates mocks of many methods that would
# cause subsequent tests to fail
class TestHotKeys(TestCase):

    def test_copy(self):
        wp.copy = MagicMock()
        wp.text_editor.update()
        wp.text_editor.event_generate("<Control-c>")
        self.assertTrue(wp.copy.called)
#
    def test_paste(self):
        wp.paste = MagicMock()
        wp.text_editor.update()
        wp.text_editor.event_generate("<Control-v>")
        self.assertTrue(wp.paste.called)

    def test_open(self):
        wp.open = MagicMock()
        wp.text_editor.update()
        wp.text_editor.event_generate("<Control-o>")
        self.assertTrue(wp.open.called)

    def test_save(self):
        wp.save = MagicMock()
        wp.text_editor.update()
        wp.text_editor.event_generate("<Control-s>")
        self.assertTrue(wp.save.called)

    def test_new(self):
        wp.new = MagicMock()
        wp.text_editor.update()
        wp.text_editor.event_generate("<Control-n>")
        self.assertTrue(wp.new.called)

    def test_bold(self):
        wp.run_config = MagicMock()
        wp.text_editor.update()
        wp.text_editor.event_generate("<Control-b>")
        wp.run_config.assert_called_with("weight")

    def test_italic(self):
        wp.run_config = MagicMock()
        wp.text_editor.update()
        wp.text_editor.event_generate("<Control-i>")
        wp.run_config.assert_called_with("slant")

    def test_underline(self):
        wp.run_config = MagicMock()
        wp.text_editor.update()
        wp.text_editor.event_generate("<Control-u>")
        wp.run_config.assert_called_with("underline")
