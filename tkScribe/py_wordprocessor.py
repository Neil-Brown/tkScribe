import os
import pickle

from PIL import Image, ImageTk
import tkinter as tk
from tkinter import (ttk,
                     messagebox,
                     filedialog as fd,
                     scrolledtext as st,
                     colorchooser)

from tkScribe.button import Button
from tkScribe.document import Document
from tkScribe.find import Find, Replace
from tkScribe.run import *

filetypes = [
    ("Scribe files", "*.{}".format("scribe")),
    ("Text files", "*.txt"),
    ("All files", "*"),
]

basecolor = "#f0f0f0"
bordercolor = "#ACA5F0"

class WordProcessor(tk.Frame):
    def __init__(self, parent, path="", **kwargs):
        """Set up the GUI
        Initialize all variables"""
        tk.Frame.__init__(self)
        self.parent = parent
        self.path = path
        print("path", path)
        try:
            self.parent.iconbitmap("{}images//logo.ico".format(path))
        except: # Parent is not top level
            pass
        self.configure_kwargs(kwargs)
        self.title_txt = "Untitled"
        self.minimized_frames = []
        self.copied_runs = []
        self.minimized = False
        self.minwidth = 0
        self.preferences = {
            'dir': "C:\\Users\\{}\\Documents\\".format(os.getlogin()),
            'font': dict(family="Arial", size=12, weight="normal",
                         slant="roman", underline=False, overstrike=False),
            'foreground': "black",
            'button_active_color': "#0078d7", 'background_color': "white",
            'default_ext': "scribe"
        }
        self.default_run = Run(family=self.preferences["font"]["family"],
                               size=self.preferences["font"]["size"],
                               weight=self.preferences["font"]["weight"],
                               slant=self.preferences["font"]["slant"],
                               underline=self.preferences["font"][
                                   "underline"],
                               overstrike=self.preferences["font"][
                                   "overstrike"],
                               foreground="#082947",
                               background="white")

        # Main Windows
        self.frame = tk.Frame(self.parent)
        self.clipboard_frame = tk.Frame(self.frame, name="clipboard")
        self.font_frame = tk.Frame(self.frame, name="font")
        self.font_button_frame = tk.Frame(self.font_frame, name="font")
        self.paragraph_frame = tk.Frame(self.frame, name="paragraph")
        self.editing_frame = tk.Frame(self.frame, name="editing")
        self.editing_frame_sub = tk.Frame()

        # File Menu
        self.menu = tk.Menu(self.parent)
        self.file = tk.Menu(self.menu, tearoff=False)
        self.edit = tk.Menu(self.menu, tearoff=False)
        self.format = tk.Menu(self.menu, tearoff=False)
        self.file_menu_setup()
        try:
            self.parent.configure(menu=self.menu)
            self.parent.title(self.title_txt)
            self.center_window()
        except tk.TclError: # Parent is not top-level
            pass

        # Control Panel
        self.font_selector = ttk.Entry(self.font_frame)
        self.font_selector_image = ImageTk.PhotoImage(
            Image.open("{}images//down-arrow.png".format(path)))
        self.font_button = Button(master=self.font_selector,
                                  image=self.font_selector_image,
                                  inactive_background="white",
                                  inactive_border="white",
                                  active_background="white",
                                  active_border="white",
                                  command=lambda:
                                  self.show_dropdown(
                                      dropdown=self.font_dropdown,
                                      target=self.font_selector
                                  ))
        self.font_size_selector = ttk.Entry(self.font_frame, width=6)
        self.font_size_button = Button(self.font_size_selector,
                                       image=self.font_selector_image,
                                       inactive_background="white",
                                       inactive_border="white",
                                       active_background="white",
                                       active_border="white",
                                       command=lambda:
                                       self.show_dropdown(
                                           dropdown=self.font_size_dropdown,
                                           target=self.font_size_selector
                                       ))

        self.clipboard_buttons = {
            "paste": {
                "method": self.paste,
                "help_text": ["Paste (Ctr+v)",
                              "Paste the contents of the clipboard"],
                "coords": [0, 0, 2]
            },
            "copy": {
                "method": self.copy,
                "help_text": ["Copy (Ctr+c)",
                              "Copy selected text to the clipboard"],
                "coords": [0, 1, 1]
            },
            "cut": {
                "method": self.cut,
                "help_text": ["Cut (Ctr+x)",
                              "Cut selected text from document"],
                "coords": [1, 1, 1]
            }
        }

        self.font_buttons = {
            'weight': {
                "method": lambda f="weight": self.run_config(f),
                "param": ["normal", "bold"],
                "help_text": ["Bold (Ctr+b)",
                              "Make the current font heavier"],
                "coords": [0, 1, 1]
            },
            'slant': {
                "method": lambda formatting="slant": self.run_config(
                    formatting),
                "param": ["roman", "italic"],
                "help_text": ["Italic",
                              "Change to an italic font"],
                "coords": [1, 1, 1]
            },
            'underline': {
                "method": lambda formatting="underline": self.run_config(
                    formatting),
                "param": [False, True],
                "help_text": ["Underline",
                              "Draw a line under the text"],
                "coords": [2, 1, 1]
            },
            'overstrike': {
                "method": lambda formatting="overstrike": self.run_config(
                    formatting),
                "param": [False, True],
                "help_text": ["Strikethrough",
                              "Draw a line through the text"],
                "coords": [3, 1, 1]
            },
            'foreground': {
                "method": self.foreground,
                "param": None,
                "help_text": ["Foreground",
                              "Change the text colour"],
                "coords": [4, 1, 1]
            },
            'background': {
                "method": self.background,
                "param": None,
                "help_text": ["Background",
                              "Change the color of the text backgrond"],
                "coords": [5, 1, 1]
            }
        }
        self.paragraph_buttons = {
            "line_spacing": {
                "method": lambda: self.show_dropdown(
                    dropdown=self.line_spacing_dropdown,
                    target=self.paragraph_buttons["line_spacing"]["button"]),
                "param": [None],
                "help_text": ["Line Spacing",
                              "Configure the spacing between lines"],
                "coords": [0, 0, 1]
            },
            "tab": {
                "method": lambda: self.show_dropdown(
                    dropdown=self.tab_dropdown,
                    target=self.paragraph_buttons["tab"]["button"]),
                "param": [None],
                "help_text": ["Tab Size",
                              "Configure the indent size of tabs"],
                "coords": [1, 0, 1]
            },
            "left": {
                "method": lambda just="left": self.justify(just),
                "param": [False, True],
                "help_text": ["Justify Left",
                              "Align text to the left"],
                "coords": [0, 1, 1]
            },
            "center": {
                "method": lambda just="center": self.justify(just),
                "param": [False, True],
                "help_text": ["Justify Center",
                              "Align text in the center"],
                "coords": [1, 1, 1]
            },
            "right": {
                "method": lambda just="right": self.justify(just),
                "param": [False, True],
                "help_text": ["Justify Right",
                              "Align text to the right"],
                "coords": [2, 1, 1]
            },
        }
        self.editing_buttons = {
            'find': {
                'method': self.find,
                'param': [None],
                "help_text": ["Find",
                              "Find text in the document"],
                "coords": [0, 0, 2]
            },
            'replace': {
                "method": self.replace,
                "param": [None],
                "help_text": ["Replace",
                              "Replace text in the document"],
                "coords": [0, 1, 1]
            },
            'select_all': {
                "method": self.select_all,
                "param": [None],
                "help_text": ["Select All (Ctr+a)",
                              "Select all text in the document"],
                "coords": [1, 1, 1],
            },
        }

        # Editor
        self.editor_window = tk.Frame(self.parent, background="#ACA5F0",
                                      relief="raised", width=50)
        self.text_editor = st.ScrolledText(self.editor_window, wrap="word")
        self.char_num_label = tk.Label(self.parent, text="")

        self.control_panel_setup()
        self.text_editor_setup()
        self.help_text_label = tk.Text(background="#d4d0fb",
                                       wrap="word",
                                       height=3,
                                       font=("Arial", 10),
                                       foreground="#082947",
                                       borderwidth=2,
                                       relief="ridge"
                                       )
        self.help_text_label.tag_configure("bold",
                                           foreground="#082947",
                                           font=("Arial", 10, "bold"))
        self.help_text_label.tag_add("bold", "1.0", "1.0 lineend")

        # Drop Downs
        self.font_dropdown = self.build_dropdown(has_scroll=True)
        self.populate_font_dropdown()

        self.font_size_dropdown = self.build_dropdown()
        self.populate_font_size_dropdown()
        self.font_size_dropdown.configure(width=5, height=16)

        self.line_spacing_dropdown = self.build_dropdown()
        self.populate_linespacing_dropdown()
        self.line_spacing_dropdown.configure(width=23, height=18)

        self.tab_dropdown = self.build_dropdown()
        self.populate_tab_dropdown()
        self.tab_dropdown.configure(width=3, height=20)

        # Sub Frames
        self.delete_label = Button(
            self.frame,
            inactive_background=basecolor,
            inactive_border=basecolor,
            active_border=bordercolor,
            active_background=basecolor,
            image=ImageTk.PhotoImage(Image.open("{}images\\x.png".format(
                self.path))),
            command=self.restore_mins)

        # Proxy and generate callback when Text is modified
        self._orig = self._w + "_orig"
        self.parent.tk.call("rename", self.text_editor._w, self._orig)
        self.parent.tk.createcommand(self.text_editor._w, self.proxy)
        self.text_editor.bind("<<TextModified>>", self.callback)

        # Control resize events
        self.frame_list = self.get_frames()
        self.format_min_width = self.frame.winfo_reqwidth()
        self.frame.bind("<Configure>", self.resize)

        # Document
        self.document = Document(directory=self.preferences["dir"])
        self.hot_keys()
        self.new()

    def center_window(self):
        """Center the application window in screen"""
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.parent.geometry("{}x{}+{}+{}".format(
            sw // 2,
            sh // 2,
            (sw // 2) - ((sw // 2) // 2),
            (sh // 2) - ((sh // 2) // 2),
        ))
        self.parent.deiconify()

    # Handle Control panel Resize events
    def get_frames(self):
        """ Returns a list of currently packed frames in control panel"""
        return [x for x in self.frame.pack_slaves()]

    def resize(self, event):
        """ Receive a resize event and depending on the width of self.frame (
        Control Panel) outsources to relevant method / function. """
        if event.width < self.format_min_width and not self.minimized:
            self.remove_frames()
            self.minimize_frames()
        elif event.width > self.format_min_width and self.minimized:
            self.maximize_frame()
        elif event.width < self.minwidth:
            self.remove_frames()
        elif event.width > self.minwidth and not self.get_frames():
            self.restore_mins()

    def remove_frames(self):
        """ Forgets all currently packed formatting windows"""
        for frame in self.get_frames():
            frame.pack_forget()

    def minimize_frames(self):
        """ Minimizes all formatting frames in self.frame
        """
        self.minimized = True
        if self.minimized_frames:
            self.restore_mins()
            return
        min_width = 0
        for x, win in enumerate(["clipboard", "font", "paragraph",
                                 "editing"]):
            self.minimized_frames.append(tk.Frame(self.frame))
            im = self.get_main_images_for_minimized_windows(
                getattr(self, "{}_buttons".format(win)))[0]
            tk.Label(self.minimized_frames[-1],
                     image=im,
                     text=im._name.title(), compound="top").pack()
            expand_button = Button(
                self.minimized_frames[-1],
                image=self.font_selector_image,
                inactive_background=basecolor,
                inactive_border=basecolor,
                active_border=bordercolor,
                active_background=basecolor,
                command=lambda idx=x: self.show_min_dropdown(idx))

            expand_button.pack()
            self.minimized_frames[-1].pack(side="left", fill="y",
                                           expand=False)
            self.frame.update()
            #self.minimized_frames[-1].update() # Without this the
            # mini windows are not removed on further resize
            min_width += self.minimized_frames[-1].winfo_reqwidth()
        self.minwidth = min_width

    def show_min_dropdown(self, idx):
        """ Show a frame with all the option butttons available in that
            control panel frame"""
        self.remove_frames()
        self.frame_list[idx * 2].pack(side="left", fill="y", expand=False)
        self.delete_label.pack(side="left", fill=None, expand=None, anchor="n")

    def restore_mins(self):
        """ Packs already created minimized versions of formatting frames. """
        self.remove_frames()
        for x in self.minimized_frames:
            x.pack(side="left", fill="y", expand=False)

    def maximize_frame(self):
        """ Remove minimized frames and re-packs original formatting frames."""
        self.remove_frames()
        for frame in self.frame_list:
            frame.pack(side="left", fill="y", expand=False)
        self.minimized = False

    def configure_kwargs(self, kwargs):
        """Configures user diplay options parameters"""
        for k, v in kwargs.items():
            if k == "iconbitmap":
                self.parent.iconbitmap(v)
            self.__setattr__(k, v)

    #  Setup Widgets
    def file_menu_setup(self):
        """ Creates and packs the menu widgets """
        self.file.add_command(label="New     Ctr+N", command=self.new)
        self.file.add_command(label="Open     Ctr+O", command=self.open)
        self.file.add_separator()
        self.file.add_command(label="Save     Ctr+S",
                              command=lambda askfile=False: self.save(
                                  askfile=askfile))
        self.file.add_command(label="Save As", command=self.save)
        self.file.add_separator()
        self.file.add_command(label="Exit")

        self.edit.add_command(label="Copy          Ctrl+c", command=self.copy)
        self.edit.add_command(label="Paste          Ctrl+p", command=self.paste)
        self.edit.add_command(label="Cut             Ctrl+x", command=self.cut)
        self.edit.add_command(label="Find            Ctrl+f", command=self.find)
        self.edit.add_command(label="Replace      Ctrl+r",
                              command=self.replace)

        self.format.add_command(label="Bold                   Ctr+B",
                                command=lambda: self.run_config("weight"))
        self.format.add_command(label="Italic                   Ctr+I",
                                command=lambda: self.run_config("slant"))
        self.format.add_command(label="Underline          Ctr+U",
                                command=lambda: self.run_config("underline"))
        self.format.add_command(label="Strikethrough  ",
                                command=lambda: self.run_config("overstrike"))

        self.format.add_command(label="Justify Left  ", command=lambda
                                j="left": self.justify(j))
        self.format.add_command(label="Justify Center", command=lambda
                                j="center": self.justify(j))
        self.format.add_command(label="Justify Right ", command=lambda
                                j="right": self.justify(j))
        self.menu.add_cascade(label="File", menu=self.file)
        self.menu.add_cascade(label="Edit", menu=self.edit)
        self.menu.add_cascade(label="Format", menu=self.format)


    def control_panel_setup(self):
        """ Creates and packs the widgets for the formatting window"""

        tk.Label(self.clipboard_frame, text="Clipboard",
                 foreground="#082947").grid(column=0, row=3, columnspan=2)
        self.clipboard_frame.pack(side="left", fill="y", expand=False, padx=5)
        ttk.Separator(self.frame, orient="vertical").pack(side="left", fill="y",
                                                          expand=False)

        tk.Label(self.font_frame, text="Font",
                 foreground="#082947").grid(column=0, row=3, columnspan=6)
        self.font_frame.pack(side="left", fill="y", expand=False, padx=5)
        ttk.Separator(self.frame, orient="vertical").pack(side="left", fill="y",
                                                          expand=False)

        tk.Label(self.paragraph_frame, text="Paragraph",
                 foreground="#082947").grid(column=0, row=3, columnspan=3)
        self.paragraph_frame.pack(side="left", fill="y", expand=False,
                                  padx=(0, 5))
        ttk.Separator(self.frame, orient="vertical").pack(side="left", fill="y",
                                                          expand=False)
        tk.Label(self.editing_frame, text="Editing",
                 foreground="#082947").grid(column=0, row=3, columnspan=2)
        self.editing_frame.pack(side="left", fill="y", expand=False, )
        ttk.Separator(self.frame, orient="vertical").pack(side="left", fill="y",
                                                          expand=False)

        self.font_selector.type = "family"
        self.font_size_selector.type = "size"
        self.font_selector.grid(column=0, row=0, columnspan=4, sticky="EW",
                                pady=(5, 0), ipady=2, ipadx=4)
        self.font_button.place(in_=self.font_selector, relx=0.96,
                               rely=0.1, anchor="ne")
        self.font_size_selector.grid(column=4, row=0, columnspan=2, sticky="EW",
                                     pady=(5, 0), ipady=2)
        self.font_size_button.place(in_=self.font_size_selector, relx=0.96,
                                    rely=0.1, anchor="ne")

        self.button_packer(win=self.clipboard_frame, d=self.clipboard_buttons)
        self.font_button_frame.grid(column=0, row=1, columnspan=6, sticky="SEW")

        self.button_packer(win=self.font_button_frame,
                           d=self.font_buttons,
                           stay_active=True)

        self.button_packer(self.paragraph_frame,
                           self.paragraph_buttons)

        # self.button_packer(win=self.paragraph_frame,
        #                    d=self.justification_buttons, stay_active=True,
        #                    row=1,
        #                    label_text="Paragraph")
        self.button_packer(win=self.editing_frame, d=self.editing_buttons)

        self.frame.pack(fill="x")

        for frame in [self.clipboard_frame,
                      self.font_frame,
                      self.paragraph_frame,
                      self.editing_frame]:
            frame.update_idletasks()
        self.frame.full_size_width = self.frame.winfo_reqwidth()

    def text_editor_setup(self):
        """Creates and packs the text widget. Sets the formatting tags"""
        self.text_editor.configure(font=self.preferences["font"], width=90)
        self.editor_window.configure(width=self.text_editor.winfo_width() + 50)
        self.editor_window.pack(fill="both", expand=True, ipadx=25)
        self.text_editor.pack(fill="y", expand=True)
        self.char_num_label.pack()
        self.text_editor.tag_configure("highlight", background=basecolor)
        self.text_editor.tag_configure("sel", selectbackground="white")

        # Bind movement buttons to track which paragraph / run the cursor us at
        for x in ["Button-1", "Left", "Right", "Up", "Down"]:
            self.text_editor.bind("<{}>".format(x), self.check_pos)

    def check_pos(self, *event):
        """ Sets the current run / paragraph based on the cursor location
        Calls methods to highlight the correct buttons for the current run
        and paragraph"""
        if event and event[0].type._name_ == "ButtonPress":
            self.text_editor.mark_set("insert", "current")
        self.current_run = self.find_current("r")
        self.current_paragraph = self.find_current("p")
        self.set_format_buttons()
        self.set_justification_buttons(
            self.text_editor.tag_cget(self.current_paragraph, "justify"))

    def set_format_buttons(self):
        """ Set format button color to match current run at insert pos"""
        for p in ["weight", "slant", "underline", "overstrike"]:
            if self.runs[self.current_run].cget(p) in ["bold", "italic"] or \
                    self.runs[self.current_run].cget(p) == 1:
                c1 = bordercolor
                c2 = basecolor
            else:
                c1 = basecolor
                c2 = basecolor
            self.font_buttons[p]["button"].configure(background=c1)
            self.font_buttons[p]["button"].label.configure(
                background=c2)

    # Callback
    def proxy(self, command, *args):
        """Generates a TextModified event in the event of insertion
        Updates wordcount in the event of insertion or deletion"""
        cmd = (self._orig, command) + args
        try:
            result = self.parent.tk.call(cmd)
        except tk.TclError:
            return
        if command in ("insert", "replace"):
            self.text_editor.event_generate("<<TextModified>>")
        elif command == "delete":
            self.update_word_count()
        return result

    def callback(self, *args):
        """ Adds run and paragraph tags to the last character entered"""
        self.update_word_count()
        self.text_editor.tag_add(self.current_run, "insert-1c")
        self.text_editor.tag_add(self.current_paragraph, "insert-1c")

    def update_word_count(self):
        """ Calculates the number of words and characters in the document
        and updates the label"""
        s = self.text_editor.get("1.0", "end-1c")
        self.char_num_label.configure(
            text="{} words - {} chars".format(len(s.split()), len(s)))

    def find_current(self, string, mark="insert"):
        """ accept 'r' or 'p' and return previous mark for runs or paragraphs
        respectively """
        while not mark.startswith(string[0]):
            mark = self.text_editor.mark_previous(mark)
        return mark

    def update_entry(self, value, widget):
        """Called when an option from a drop down window is selected
        Receives the widget to be updated i.e. font, the value to update it
        with. Hides ALL dropdowns."""
        widget.delete(0, "end")
        widget.insert(0, value)
        self.hide_all_dropdowns()
        self.run_config(
            family=self.font_selector.get(),
            size=self.font_size_selector.get())

    def hot_keys(self):
        """ Binds shorcut keys to relevent methods"""
        self.text_editor.unbind_all("<Control-i>")
        self.text_editor.bind("<Control-o>", lambda event: self.open())
        self.text_editor.bind("<Control-s>", lambda event, b=False: self.save(
            askfile=b))
        self.text_editor.bind("<Control-n>", lambda event: self.new())
        self.text_editor.bind("<Control-b>", lambda event: self.run_config(
            "weight"))
        self.text_editor.bind("<Control-i>", lambda event: self.run_config(
            "slant"))
        self.text_editor.bind("<Control-u>", lambda event: self.run_config(
            "underline"))
        self.text_editor.bind("<Control-c>", lambda event: self.copy())
        self.text_editor.bind("<Control-v>", lambda event: self.paste())

    def get_start_and_end(self):
        """Return start and end coordinates"""
        if self.text_editor.tag_ranges("sel"):
            start = self.text_editor.tag_ranges("sel")[0].string
            end = self.text_editor.tag_ranges("sel")[1].string
        else:
            start = self.text_editor.index("insert")
            end = start
        return start, end

    # Clipboard
    def paste(self):
        """Inserts each character in copied_runs setting current run to a
        copy of the copied run"""
        self.text_editor.clipboard_clear()
        if self.current_run != self.copied_runs[0][1]:
            self.split("r")
            # noinspection PyAttributeOutsideInit
            self.current_run = self.copy_run(self.copied_runs[0][1])
        for entry in self.copied_runs:
            self.text_editor.insert("insert", entry[0])
        self.reset_marks()

    def reset_marks(self):
        """Reset marks to tag position after pasting"""
        for t in [t for t in self.text_editor.tag_names() if t.startswith("r")]:
            self.text_editor.mark_set(t, self.text_editor.tag_ranges(t)[0])

    def split(self, string, loc="insert"):
        """ Reset tags"""
        tag = self.find_current(string)
        orig_start = self.text_editor.tag_ranges(tag)[0].string
        orig_end = self.text_editor.tag_ranges(tag)[1].string

        # Remove tag
        self.text_editor.tag_remove(tag, "1.0", "end")

        # Add original tag before loc
        if self.text_editor.compare(orig_start, "<", loc):
            self.text_editor.tag_add(tag, orig_start, loc + "-1c")
            if self.text_editor.compare(orig_end, ">", loc):
                new_tag = self.copy_run(tag)
                self.text_editor.tag_add(new_tag, loc, orig_end)
        else:
            if self.text_editor.compare(orig_end, ">", loc):
                self.text_editor.tag_add(tag, loc, orig_end)

    def copy_run(self, run):
        """Creates a new run name and a new tag which is a copy of the run
        passed in. Returns the new run name"""
        new_run = self.set_mark(run[0])
        self.runs[new_run] = self.runs[run].copy()
        self.text_editor.tag_configure(
            new_run,
            font=self.runs[new_run],
            foreground=self.runs[new_run].foreground,
            background=self.runs[new_run].background)
        return new_run

    def cut(self):
        """Delete selected text"""
        self.text_editor.delete("sel.first", "sel.last")

    def get_tag_at_location(self, string, index):
        """ Return tag name if it exisrs at index and begins with the string"""
        for tag in self.text_editor.tag_names(index):
            if tag.startswith(string):
                return tag

    def get_tags_in_range(self, first="sel.first", last="sel.last"):
        """ Return a list of lists, comprised of text, run tag, and paragraph
            i.e. [["a", "r1", p1"], ["b", "r2", "pw"]]"""
        tags = []
        x = 0
        while self.text_editor.compare(first + "+{}c".format(x), "<", last):
            tags.append([self.text_editor.get(first + "+{}c".format(x)),
                         self.get_tag_at_location("r",
                                                  first + "+{}c".format(x)),
                         self.get_tag_at_location("p",
                                                  first + "+{}c".format(x)),
                         ])
            x += 1

        return tags

    def copy(self):
        """If text is selected, overrides the default clipboard and calls
        new method to deal with the copy"""
        if self.text_editor.tag_ranges("sel"):
            self.text_editor.clipboard_clear()
            self.copied_runs = self.get_tags_in_range()

    # Font

    def foreground(self, color="red"):
        """ Gets hex color from colorchooser"""
        self.run_config(foreground=colorchooser.askcolor(color)[1])

    def background(self, color="white"):
        """ Gets hex color from colorchooser"""
        self.run_config(background=colorchooser.askcolor(color)[1])

    def check_create_new_format(self, unit):
        """ Takes a run or paragraph and returns a boolean depending on
        whether a new instance is required"""
        srt, end = self.get_start_and_end()
        try:
            if self.text_editor.compare(
                    self.text_editor.tag_ranges(unit)[0], "==", srt):
                if self.text_editor.compare(
                        self.text_editor.tag_ranges(unit)[1], "==", end):
                    return False
        except IndexError:  # No text in run
            return False
        return True

    def run_config(self, *args, **kwargs):
        """ Configures current or new run object
            *args binary pairs to be toggled i.e. 'normal'>'bold'
            *kwargs config font family and size args
        """
        run = self.runs[self.current_run]
        prev = self.current_run
        if self.check_create_new_format(self.current_run):
            run = self.runs[self.current_run].copy()
            self.current_run = self.set_mark("r", "insert")
        if args:
            self.toggle_font_values(run, args[0])
        if kwargs:
            for key, value in kwargs.items():
                run.__setattr__(key, value)
        # run = self.check_font_exists(run)
        self.config_run_tag(run)
        if self.text_editor.tag_ranges("sel"):
            self.text_editor.tag_remove(prev, "sel.first", "sel.last")
            self.text_editor.tag_add(self.current_run, "sel.first", "sel.last")
        self.set_format_buttons()
        return "break" # Overrides the default binding on Ctrl-i for tab

    def config_run_tag(self, run):
        self.runs[self.current_run] = run
        self.text_editor.tag_configure(
            self.current_run,
            font=run,
            foreground=run.foreground,
            background=run.background,
            selectbackground=basecolor,
            selectforeground="pink")
        self.text_editor.focus_force()

    def toggle_font_values(self, run, formatting):
        """ Toggles binary options of paramter passed in
        'normal' > 'bold' on the font object"""
        if run.cget(formatting) == self.font_buttons[formatting]["param"][0]:
            attr = self.font_buttons[formatting]["param"][1]
        else:
            attr = self.font_buttons[formatting]["param"][0]
        run[formatting] = attr

    def set_mark(self, string, index="insert"):
        """ Accept 'r' or 'p', sets a new mark at index and returns the name"""
        num = max([int(x[1::]) for x in self.text_editor.mark_names()
                   if x not in ["insert", "tk::anchor1", "current"]]) + 1
        name = "{}{}".format(string, num)
        self.text_editor.mark_set(name, index)
        self.text_editor.mark_gravity(name, "left")
        return name

    # Paragraph
    def justify(self, just):
        """Removes any previous justification tags, applies new justification
        rules and highlights the relevant button"""
        if self.text_editor.tag_ranges("sel"):
            self.split_paragraph(just)
            return
        if self.text_editor.index(self.current_paragraph + " linestart") != \
                self.text_editor.index("insert linestart"):
            self.check_new_paragraph()
        self.text_editor.tag_configure(self.current_paragraph,
                                       justify=just)
        self.set_justification_buttons(just)
        self.text_editor.focus_force()

    def split_paragraph(self, just):
        """ Remove paragraph from location paragraph and divide into number
        of relevent paragraphs """
        self.text_editor.tag_remove(self.current_paragraph, "sel.first",
                                    "sel.last")
        if self.check_create_new_format(self.current_paragraph):
            # noinspection PyAttributeOutsideInit
            self.current_paragraph = self.set_mark("p", "sel.first")
        self.text_editor.tag_configure(self.current_paragraph, justify=just)
        self.text_editor.tag_add(self.current_paragraph, "sel.first",
                                 "sel.last")

    def set_justification_buttons(self, just):
        """Sets the correct justification button to be highlighted based ont
        he current paragraph"""
        for key in self.paragraph_buttons:
            if key != just:
                self.paragraph_buttons[key]["button"].active = False
                self.paragraph_buttons[key]["button"].leave()
            else:
                self.paragraph_buttons[key]["button"].active = True
                self.paragraph_buttons[key]["button"].enter()

    def linespacing_config(self, tag):
        """ Take 'BEFORE_2.5' and apply line spacing of 2.5 before the
        paragraph. """
        self.check_new_paragraph()
        tag = tag.split("_")
        if tag[0] == "BEFORE":
            self.text_editor.tag_configure(self.current_paragraph,
                                           spacing1=float(tag[1]))
        if tag[0] == "DURING":
            self.text_editor.tag_configure(self.current_paragraph,
                                           spacing2=float(tag[1]))
        else:
            self.text_editor.tag_configure(self.current_paragraph,
                                           spacing3=float(tag[1]))
        self.hide_all_dropdowns()
        self.text_editor.focus_force()

    def check_new_paragraph(self, index="insert"):
        """ Creates a new paragraph with the same paramters as the previous"""
        if self.text_editor.index(index) == self.text_editor.index(
                self.current_paragraph):
            return
        old_para = self.current_paragraph
        # noinspection PyAttributeOutsideInit
        self.current_paragraph = self.set_mark("p")
        self.text_editor.tag_configure(self.current_paragraph,
                                       justify=self.text_editor.tag_cget(
                                           old_para, "justify"),
                                       spacing1=self.text_editor.tag_cget(
                                           old_para, "spacing1"),
                                       spacing2=self.text_editor.tag_cget(
                                           old_para, "spacing2"),
                                       spacing3=self.text_editor.tag_cget(
                                           old_para, "spacing3"),
                                       tabs=self.text_editor.tag_cget(old_para,
                                                                      "tabs")
                                       )

    def set_tab(self, tag):
        """Configures the current paragraphs tab length based on the current
        font"""
        self.check_new_paragraph()
        tab_width = self.runs[self.current_run].measure(" " * tag)
        self.text_editor.tag_configure(self.current_paragraph,
                                       tabs=(tab_width,))
        self.hide_all_dropdowns()
        self.text_editor.focus_force()

    # Widgets
    def populate_font_dropdown(self):
        """Inserts font name in the correct font in the font family drop down
        window, with relevent tag"""
        for font_name in font.families():
            tag = font_name.replace(" ", "")
            self.font_dropdown.tag_configure(tag, font=(font_name, 10))
            self.set_scroll_tags(
                self.font_dropdown, tag,
                lambda event, x=font_name: self.update_entry(
                                                        x, self.font_selector))
            self.font_dropdown.insert("insert", "{}\n".format(font_name), tag)

    def populate_font_size_dropdown(self):
        """Inserts size options for font size drop down."""
        for size in ["8", "9", "10", "11", "12", "14", "16", "18", "20",
                     "22", "24", "26", "28", "36", "48", "72"]:
            self.font_size_dropdown.tag_configure(size)
            self.set_scroll_tags(
                self.font_size_dropdown,
                size,
                lambda event,
                            x=size: self.update_entry(
                                                    x, self.font_size_selector))
            self.font_size_dropdown.insert("insert", "{}\n".format(size), size)

    def populate_linespacing_dropdown(self):
        """Inserts options for the linespacing dropdown"""
        txt = "Spacing {} paragraph\n"
        for line in ["BEFORE", "DURING", "AFTER"]:
            self.line_spacing_dropdown.insert("insert", txt.format(line))
            for size in ["1.0", "1.5", "2.0", "2.5", "3.0"]:
                tag = "{}_{}".format(line, size)
                self.line_spacing_dropdown.tag_configure(tag)
                self.set_scroll_tags(
                    self.line_spacing_dropdown,
                    tag,
                    lambda event, t=tag:
                    self.linespacing_config(t))
                self.line_spacing_dropdown.insert("insert", "{}\n".format(size),
                                                  tag)
        self.line_spacing_dropdown.configure(state="disabled")

    def populate_tab_dropdown(self):
        """Inserts options for the tab dropdown menu"""
        for x in range(0, 105, 5):
            self.tab_dropdown.tag_configure(x)
            self.set_scroll_tags(
                self.tab_dropdown,
                x,
                lambda event, t=x: self.set_tab(t))
            self.tab_dropdown.insert("insert", "{}\n".format(x), x)
        self.tab_dropdown.configure(state="disabled")

    def set_scroll_tags(self, dropdown, tag_name, func):
        """Binds each option in a dropdown with a highlight tag to create a
        scroll effect"""
        dropdown.tag_bind(
            tag_name,
            "<Enter>",
            lambda event, t=tag_name: self.highlight(dropdown, t))

        dropdown.tag_bind(
            tag_name,
            "<Leave>",
            lambda event, t=tag_name: self.remove_highlight(dropdown, t))
        dropdown.tag_bind(tag_name, "<Button-1>", func)

    def show_dropdown(self, dropdown, target, anchor="nw"):
        """ Place dropdown at the coordinates of the target widget"""
        self.hide_all_dropdowns()
        x, y = self.get_coords(target)
        dropdown.place(in_=target.master, x=x,
                       y=y + target.winfo_height(), anchor=anchor,
                       bordermode="outside")
        self.b = self.text_editor.bind("<Button-1>",
                                       lambda event: self.forget_dropdown(
                                           dropdown), "+")

    def hide_all_dropdowns(self):
        """ Geometry manager 'place' forgets all drop down windows"""
        for d in (self.font_dropdown, self.font_size_dropdown,
                  self.line_spacing_dropdown, self.tab_dropdown):
            self.forget_dropdown(d)

    def delete_runs(self):
        """Delete all runs and revert back to r1 with default parameters"""
        # noinspection PyAttributeOutsideInit
        self.runs = {"r1": self.default_run.copy()}

    def delete_tag_marks(self):
        """ Deletes all user defined tags and marks """
        for tag in self.text_editor.mark_names():
            if tag not in ["insert", "tk::anchor1", "current"]:
                self.text_editor.mark_unset(tag)
                self.text_editor.tag_delete(tag)

    def select_all(self):
        """Selects all text"""
        self.text_editor.tag_add("sel", "1.0", "end-1c")

    #  File IO
    def open(self, filepath=None):
        """ Tries to read the document as a text file. If unable
            it tries to unpickle the file. If this fails raise an error or
            call render_doc"""
        if not filepath:
            filepath = self.get_file_path()
        if filepath:
            try:
                with open(filepath, "r") as f:
                    self.document.raw = f.read()
            except UnicodeDecodeError:
                try:
                    with open(filepath, "rb") as f:
                        self.document = pickle.load(f)
                except pickle.UnpicklingError as e:
                    messagebox.showerror("File Error",
                                         "Could not decode {}\n\nError: {}"
                                         .format(filepath, e))
                    return
            self.render_doc()

    def get_file_path(self):
        f = fd.askopenfile(
            initialdir=self.preferences["dir"],
            title="Open",
            filetypes=filetypes,
            initialfile=self.document.filename,
            defaultextension=".scribe"
        )
        return f.name

    def new(self):
        """ Restores file to natural state."""
        self.text_editor.delete("1.0", tk.END + "-1c")
        self.font_selector.delete(0, tk.END)
        self.font_selector.insert(0, self.preferences["font"]["family"])
        self.font_size_selector.delete(0, tk.END)
        self.font_size_selector.insert(0, self.preferences["font"]["size"])
        if hasattr(self.parent, "title"):
            self.parent.title("Untitled")
        self.delete_runs()
        self.delete_tag_marks()
        # noinspection PyAttributeOutsideInit
        self.current_run = "r1"
        # noinspection PyAttributeOutsideInit
        self.current_paragraph = "p1"
        self.text_editor.mark_set("r1", "1.0")
        self.text_editor.mark_set("p1", "1.0")
        self.text_editor.mark_gravity("r1", "left")
        self.text_editor.mark_gravity("p1", "left")
        self.text_editor.tag_configure("r1", font=self.runs["r1"],
                                       foreground="#082947",
                                       background="white",
                                       selectbackground="#d4d0fb",
                                       selectforeground="black")
        self.text_editor.tag_configure("p1",
                                       justify="left",
                                       spacing1=0,
                                       spacing2=0,
                                       spacing3=0,
                                       tabs=(self.runs["r1"].measure(
                                                                    " " * 5),))
        self.reset_font_buttons()
        self.set_justification_buttons("left")
        self.text_editor.clipboard_clear()
        self.text_editor.tag_remove("sel", "1.0")
        self.copied_runs = []
        self.text_editor.focus_force()

    def reset_font_buttons(self):
        """ Set all font button's color to basecolor"""
        for item in self.font_buttons.items():
            item[1]["button"].label.configure(background=basecolor)
            item[1]["button"].configure(background=basecolor)

    def render_doc(self):
        """Sets document title. Inserts text and calls methods to apply run
        and paragrapg tags"""
        self.text_editor.insert("1.0", self.document.raw)
        self.parent.title(self.document.filename)
        self.apply_runs()
        self.apply_paragraphs()

    def apply_runs(self):
        """ Apply document.runs to raw text """
        for key, dic in self.document.runs.items():
            f = font.Font()
            for item in self.preferences["font"].keys():
                f.__setitem__(item, dic[item])
            f.foreground = dic["foreground"]
            f.background = dic["background"]
            self.runs[key] = f
            self.text_editor.mark_set(key, self.document.runs[key]["index"])
            self.text_editor.tag_configure(key,
                                           font=self.runs[key],
                                           foreground=self.document.runs[key][
                                               "foreground"],
                                           background=self.document.runs[key][
                                               "background"],
                                           selectbackground=basecolor,
                                           selectforeground="black"
                                           )
            self.text_editor.tag_add(key, self.document.runs[key]["index"][0],
                                     self.document.runs[key]["index"][1])

    def apply_paragraphs(self):
        """ Apply document.paragraphs to raw text """
        for key in self.document.paragraphs:
            self.text_editor.tag_delete(key)
            self.text_editor.mark_set(key, self.document.paragraphs[key][
                "index"][0])
            self.text_editor.tag_configure(
                key,
                justify=self.document.paragraphs[key]["justify"],
                spacing1=self.document.paragraphs[key]["spacing1"],
                spacing2=self.document.paragraphs[key]["spacing2"],
                spacing3=self.document.paragraphs[key]["spacing3"],
                tabs=self.document.paragraphs[key]["tabs"], )
            self.text_editor.tag_add(
                key,
                self.document.paragraphs[key]["index"][0])

    def save(self, askfile=True, filepath=None):
        """ If Save As opens a file dialogue and puts path in document.
            Calls ext_handlingsave method based on file extension
            Updates GUI title with filename
        """
        if not filepath:
            filepath = fd.asksaveasfilename(initialdir=self.preferences["dir"],
                                            title="Save as",
                                            filetypes=filetypes,
                                            filename=filepath,
                                            initialfile=self.document.filename,
                                            defaultextension=".scribe")
        if filepath:
            self.document.path = filepath
            self.ext_handling()
            if self.document.filename.split(".")[1] == "txt":
                self.save_txt()
            else:
                self.document.raw = self.text_editor.get("1.0", "end-1c")
                self.document.runs = self.get_runs()
                self.document.paragraphs = self.get_paragraphs()
                self.pickle_doc()
            self.parent.title(self.document.filename)

    def ext_handling(self):
        """Determines how to save the file by extension"""
        if "." not in self.document.path:
            self.document.path += ".{}".format(self.preferences["default_ext"])
        self.document.filename = os.path.basename(self.document.path)

    # Save as txt
    def save_txt(self):
        """  Saves text as .txt file - formatting will be lost"""
        if not messagebox.askyesno("Save", "All formatting will be "
                                          "lost\nProceed?",
                               icon="warning", default="no"):
            return
        with open(self.document.path, "w") as f:
            f.write(self.text_editor.get("1.0", tk.END + "-1c"))
        messagebox.showinfo("Save",
                            "Document saved to\n" + self.document.path)

    def get_runs(self):
        """ Return dictionary. Key = tag names i.e. 'r0'.
         Contains tag range, font, foreground and background"""
        runs = {}
        for name, run in self.runs.items():
            runs[name] = run.make_dict()
            try:
                runs[name]["index"] = (
                    self.text_editor.tag_ranges(name)[0].string,
                    self.text_editor.tag_ranges(name)[1].string)
            except IndexError:  # No text in run
                if name == "r1": # Blank document
                    runs[name]["index"] = ("1.0", "1.0")
        return runs

    def get_paragraphs(self):
        """ Return dict. Key = tag i.e. 'p0'.
            Contains index. justify, spacing1, spacing2, spacing3, tabs"""
        paragraphs = {}
        paras = [t for t in self.text_editor.tag_names() if t.startswith("p")]
        for para in paras:
            paragraphs[para] = {}
            try:
                paragraphs[para]["index"] = (self.text_editor.tag_ranges(para)[
                                                 0].string,
                                             self.text_editor.tag_ranges(para)[
                                                 1].string,
                                             )
            except IndexError:  # No text in paragraph
                if para == "p1": # Blank document
                    paragraphs[para]["index"] = ("1.0", "1.0")
            for item in ["justify", "spacing1", "spacing2", "spacing3"]:
                paragraphs[para][item] = self.text_editor.tag_cget(para, item)
            paragraphs[para]["tabs"] = self.text_editor.tag_cget(para, "tabs")[
                0].string
        return paragraphs

    def pickle_doc(self):
        """Converts the Document instance to a pickle file and saves it at
            path in its path attribute."""
        with open(self.document.path, "wb") as f:
            pickle.dump(self.document,
                        f,
                        protocol=pickle.HIGHEST_PROTOCOL)

        messagebox.showinfo("Save", "Document saved to\n" + self.document.path)

    # Edit commands
    def find(self):
        return Find(self.text_editor, path=self.path)

    def replace(self):
        return Replace(self.text_editor, path=self.path)

    def button_packer(self, win, d, stay_active=False):
        """Receives a window and a dictionary containing packing information
        and packs the buttons into the relevant frame of the control panel"""
        for x, key in enumerate(d.keys()):
            d[key]["image"] = ImageTk.PhotoImage(
                Image.open("{}images//{}.png".format(self.path, key)))
            d[key]["image"]._name = win._name
            d[key]["button"] = Button(win,
                                      image=d[key]["image"],
                                      command=d[key]["method"],
                                      inactive_background=basecolor,
                                      inactive_border=basecolor,
                                      active_background=basecolor,
                                      active_border=bordercolor,
                                      borderwidth=2,
                                      stay_active=stay_active,
                                      help_text=d[key]["help_text"])

            d[key]['button'].grid(column=d[key]["coords"][0],
                                  row=d[key]["coords"][1],
                                  columnspan=d[key]["coords"][2],
                                  pady=(3, 0),
                                  sticky="NEWS")
            win.columnconfigure(d[key]["coords"][0], weight=1)
            d[key]["button"].bind(
                                "<Enter>", lambda event,
                                b=d[key]['button']: self.help_text(b))
            d[key]["button"].bind("<Leave>", lambda event:
            self.remove_help_text())

    def help_text(self, button):
        """Places help text relevant to the received buttons position.
        Help text content is an attribute of the button"""
        self.help_text_label.configure(width=len(button.help_text[1]))
        self.help_text_label.insert("insert", button.help_text[0], "bold")
        self.help_text_label.insert("insert",
                                    "\n\n" + button.help_text[1] + "\n\n")
        x, y = self.get_coords(button)
        self.help_text_label.place(in_=button.master, x=x,
                                   rely=1, anchor="nw",
                                   bordermode="outside")

    def remove_help_text(self):
        """Removes text from the help text label and place forgets the label"""
        self.help_text_label.delete("1.0", "end-1c")
        self.help_text_label.place_forget()

    @staticmethod
    def build_dropdown(has_scroll=False):
        """
        Returns either a Text or Scrolled Text widget to be used as a
        dropdown menu
        """
        if has_scroll:
            dropdown = st.ScrolledText()
        else:
            dropdown = tk.Text()
        dropdown.configure(font=("Arial", 8),
                           background="white",
                           cursor="hand2",
                           relief="groove",
                           borderwidth=2,
                           wrap="word", )
        return dropdown

    @staticmethod
    def scroll(text_widget, item):
        """ Receives a Text widget and scrolls to and highlights that
        location """
        idx = text_widget.search(item, "1.0")
        text_widget.see(idx)
        text_widget.tag_configure(item.replace(" ", ""),
                                  background=bordercolor)
        text_widget.focus_set()

    @staticmethod
    def remove_highlight(obj, t):
        """Receives a drop down widget and tag and configures the tags
        background to be white"""
        obj.configure(state="normal")
        obj.tag_configure(t, background="white")
        obj.configure(state="disabled")

    @staticmethod
    def forget_dropdown(dropdown):
        """Receives a dropdown and Place forgets it"""
        dropdown.place_forget()

    @staticmethod
    def highlight(obj, tag):
        """Receives a dropdown widget and tag and configures the tag
        background to be the basecolor"""
        obj.configure(state="normal")
        obj.tag_configure(tag, background=basecolor)
        obj.configure(state = "disabled")

    @staticmethod
    def get_coords(widget):
        """ Receives a widget and returns the x, y coordinates of the widget"""
        return widget.winfo_x(), widget.winfo_y()

    @staticmethod
    def get_main_images_for_minimized_windows(win_dict):
        """Returns the images to be used in the minimized windows after
        parent is resized"""
        return [win_dict[x]["image"] for x in win_dict.keys() if x in
                ["foreground", "left", "find", "paste"]]


