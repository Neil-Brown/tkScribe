from tkinter import Frame, Label

class Button(Frame):
    """Buttons to be used in the control panel"""
    def __init__(self, master, **kwargs):
        """Construct the button and set default attributes or user defined
        attributes"""
        Frame.__init__(self, master)
        self.default_attributes = {
            "text": "",
            "inactive_background": "#698EB8",
            "inactive_border": "#97B5D6",
            "active_background": "#63BAA0",
            "active_border": "#93D7C2",
            "border_width": 2,
            "font": ("Arial", 20),
            "inactive_foreground": "#2D5887",
            "active_foreground": "#C7EFE3",
            "compound": "top",
            "stay_active": False,
            "image": None,
            "highlightthickness": 0
        }

        for key, value in self.default_attributes.items():
            if key not in kwargs:
                setattr(self, key, value)
        for key, value in kwargs.items():
            setattr(self, key, value)
        # assert 0
        self.label = Label(self, compound=self.compound, text=self.text,
                              image=self.image, font=self.font, cursor="hand2")
        self.label.pack(fill="both", expand=True, padx=self.border_width,
                        pady=self.border_width, ipady=0)
        self.bind("<Enter>", self.enter)
        self.bind("<Leave>", self.leave)
        self.label.bind("<Button-1>", self.clicked)
        self.active = False
        self.leave()

    def enter(self, *event):
        self.label.configure(background=self.active_background,
                             foreground=self.active_foreground)
        self.configure(background=self.active_border)

    def leave(self, *event):
        if not self.active:
            self.label.configure(background=self.inactive_background,
                                 foreground=self.inactive_foreground)
            self.configure(background=self.inactive_border)

    def clicked(self, *event):
        if self.stay_active:
            if self.active:
                self.active = False
            else:
                self.active = True
        self.command()
