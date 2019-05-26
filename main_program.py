### Example usage

from PIL import Image, ImageTk
from pyscribe import Scribe
import tkinter as tk

class Main_Frame(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("Main Program")
        logo = Image.open("images//logo.png")
        logo.thumbnail((150, 150), Image.ANTIALIAS)
        self.logo = ImageTk.PhotoImage(logo)
        self.label = tk.Label(self, image=self.logo, background="#082947")
        self.left_frame = tk.Frame(self)
        self.right_frame = tk.Frame(self)
        graph = Image.open("images//graph.png")
        x = self.winfo_screenwidth() // 2
        graph.thumbnail((x, 600), Image.ANTIALIAS)
        self.graph_image = ImageTk.PhotoImage(graph)

        self.right_label = tk.Label(self.left_frame, image=self.graph_image)
        self.label.pack(fill="x", expand=True, ipady=20)
        self.right_label.pack()
        self.left_frame.pack(side="left")
        self.right_frame.pack(side="right")
        self.scribe = Scribe(self.right_frame, width=10)
        self.top_level_scribe = TopLevel()

class TopLevel(tk.Toplevel):
    def __init__(self):
        tk.Toplevel.__init__(self)
        self.title("Top Level Window")
        self.scribe = Scribe(self)


if __name__ == '__main__':
    main = Main_Frame()
    main.mainloop()