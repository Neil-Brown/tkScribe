import pytest
import tkinter as tk

from tkScribe.py_wordprocessor import WordProcessor

path = "..//..//"

@pytest.fixture(scope="session")
def scribe_class(request):
    root = tk.Tk()
    yield WordProcessor(parent = root, path=path)
    root.destroy()


