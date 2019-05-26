import os
import tkinter as tk
from tkinter import ttk, messagebox

DEBUG = True

class Find(tk.Toplevel):

    def __init__(self, editor, path=""):
        tk.Toplevel.__init__(self)
        """Initiaize a Toplevel window as a Find dialogue and as the basis 
        of the Replace dialog"""
        self.editor = editor
        self.path = path
        self.title("Find")
        if "nt" == os.name:
            self.iconbitmap("{}images//logo.ico".format(self.path))
        else:
            self.iconbitmap("@{}images//logo.xbm".format(self.path))
        tk.Label(self, text="Find what:").grid(column=0, row=0, sticky="W",
                                               padx=(5, 0), pady=(5, 0))
        self.countVar = tk.StringVar()
        self.var1 = tk.BooleanVar()
        self.var2 = tk.BooleanVar()
        self.var1.set(False)
        self.var2.set(False)
        self.input = ttk.Entry(self, width=30)
        self.check1 = ttk.Checkbutton(self, text="Match whole word",
                                      variable=self.var1)
        self.check2 = ttk.Checkbutton(self, text="Match case",
                                      variable=self.var2)
        self.find_next_button = ttk.Button(self, text="Find next",
                                           command=self.find)
        self.cancel_button = ttk.Button(self, text="Cancel",
                                        command=self.destroy_toplevel)
        self.check1.grid(column=0, row=2, sticky="W", padx=(5, 0))
        self.check2.grid(column=0, row=3, sticky="W", padx=(5, 0), pady=(0, 5))
        self.input.grid(column=1, row=0, sticky="EW", padx=5, pady=(5, 0))
        self.find_next_button.grid(column=3, row=0, sticky="EW", pady=2.0,
                                   padx=(0, 5))
        self.cancel_button.grid(column=3, row=3, sticky="NEW", padx=(0, 5),
                                pady=2)
        self.position()
        if self.editor.tag_ranges("sel"):
            self.start = self.editor.index("sel.first")
            self.end = self.editor.index("sel.last")
        else:
            self.start = "1.0"
            self.end = "end"
        self.inc = self.start

    def find(self):
        """ Search text widget based on the search criteria"""

        # Remove any existing selection
        self.editor.tag_remove("sel",
                               self.start,
                               self.end)
        search_string, regex = self.make_search_string()

        # If match case
        nocase = 1
        if self.var2.get():
            nocase = 0

        # noinspection PyAttributeOutsideInit
        self.pos = self.editor.search(search_string,
                                      self.inc,
                                      count=self.countVar,
                                      exact=True,
                                      nocase=nocase,
                                      regexp=regex)

        self.editor.tag_add("sel", self.pos,
                            self.pos + "+{}c".format(self.countVar.get()))
        self.editor.see(self.pos)
        self.inc = self.pos + "+1c"

    def make_search_string(self):
        """Return the user entered search term or rgex"""
        search_string = self.input.get()
        regex = False
        if self.var1.get():
            regex = True  # If match whole word
            search_string = r"(^|\s){}(\s|$)".format(self.input.get())
        return search_string, regex

    def destroy_toplevel(self):
        """Remove select from the main Text widget and destroy itself"""
        self.editor.tag_remove("highlight", "1.0", self.end)
        self.destroy()

    def position(self):
        """Set Find window adjacent to the text editor"""
        x = self.editor.winfo_rootx()
        y = self.editor.winfo_rooty()
        self.geometry("+{}+{}".format(x, y))


class Replace(Find):
    def __init__(self, editor, path=""):
        """Inherits from Find class to construct a Toplevel Replace dialog"""
        super(Replace, self).__init__(editor, path)
        self.title("Replace")
        tk.Label(self, text="Replace with:").grid(column=0, row=1, sticky="W")
        self.replace_button = ttk.Button(self, text="Replace",
                                         command=self.replace)
        self.replace_all_button = ttk.Button(self, text="Replace All",
                                             command=self.replace_all)

        self.replace_input = ttk.Entry(self, width=30)
        self.replace_button.grid(column=3, row=1, sticky="NEW", padx=(0, 5),
                                 pady=2)
        self.replace_all_button.grid(column=3, row=2, sticky="NEW",
                                     padx=(0, 5), pady=2)

        self.replace_input.grid(column=1, row=1, sticky="EW", padx=5,
                                pady=(5, 0))
        self.pos = "1.0"
        self.tab_order()

    def replace(self):
        """Calls parents find method, to get index of search criteria,
        deletes text between these indices, and inserts the replacement text"""
        self.find()
        self.editor.delete(self.pos, self.pos + "+{}c".format(
            self.countVar.get()))
        self.editor.insert(self.pos, self.replace_input.get())

    def replace_all(self):
        """Replaces all instances of the search criteria and calls the
        replace method on each instance"""
        replacements = 0
        while self.pos:
            self.replace()
            if self.pos:
                replacements += 1
        if not DEBUG:
            messagebox.showinfo("Replace", "Replaced {} items".format(replacements))

    def tab_order(self):
        """Corrects the tab select order inherited from parent"""
        self.replace_input.tkraise(self.input)
        self.replace_button.tkraise(self.find_next_button)
        self.replace_all_button.tkraise(self.replace_button)