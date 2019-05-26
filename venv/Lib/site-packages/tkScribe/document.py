import datetime
import os

class Document:
    def __init__(self, directory):
        """Document class to be used to save and load all document
        information, including: text, runs. paragraphs, username,
        creationdate"""
        self.raw = ""
        self.filename = "Untitled.scribe"
        self.path = directory + self.filename
        self.name = None
        self.created_at = datetime.datetime.now()
        self.created_by = os.getlogin()
        self.runs = {}
        self.paragraphs = {}