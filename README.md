[![Codacy Badge](https://api.codacy.com/project/badge/Grade/04b15102ed9d4063ae6a34ea5498ac38)](https://app.codacy.com/app/neilbrownemail/tkScribe?utm_source=github.com&utm_medium=referral&utm_content=Neil-Brown/tkScribe&utm_campaign=Badge_Grade_Dashboard)
[![Build Status](https://travis-ci.org/Neil-Brown/tkScribe.svg?branch=master)](https://travis-ci.org/Neil-Brown/tkScribe)
[![Coverage Status](https://coveralls.io/repos/github/Neil-Brown/tkScribe/badge.svg?branch=master)](https://coveralls.io/github/Neil-Brown/tkScribe?branch=master)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)<br/><br/>
![image](https://github.com/Neil-Brown/tkScribe/blob/master/images/logo_small.png)<br/><br/>
Standalone or plugin wordprocessor for Tkinter applications.<br/>
* Fonts
* Bold 
* Italic
* Underline
* Strikethrough
* Font color
* Background color
* Text alignment

All formatting can be saved and reloaded. 

## Requirements

* Windows, Mac, Linux
* Python 3.x with tkinter and Pillow

## Installation

Available soon on pypi 27/05/2019
```pip install tkScribe```

## Documentation

#### Standalone Wordprocessor
From the command line
```
python tkScribe
```

#### Installing as part of an existing Tkinter application
Top Level Window
```
from tkScribe import Scribe
import tkinter as tk

root = tk.Tk()
root.title("Main Application")
launch_scribe_button = tk.Button(root, text="Scribe")
launch_scribe_button.pack(padx=20, pady=20, command = launch_scribe)

root.mainloop()

def launch_scribe():
    top = tk.Toplevel()
    scribe = Scribe(top)
   ```
Tkinter Frame

```
from tkScribe import Scribe 
import tkinter as tk

root = tk.Tk() 
root.title("Main Application")
scribe_window = tk.Frame(root)
scribe = Scribe(scribe_window)
scribe_window.pack()

root.mainloop()
```

#### Saving

If a tkinter root or toplevel window is provided as the parent to
Scribe, saving can be achieved from the drop down menus or hotkeys.

If a tkinter Frame is provided as the parent no dropdown menus will be
available. Saving can still be achieved from the hotkeys or by accessing
the methods directly. 

```
from tkScribe import Scribe 
import tkinter as tk

def save():
    scribe.save()
    
 def open()
    scribe.open()

root = tk.Tk() 
root.title("Main Application")
scribe_window = tk.Frame(root)
save_button = tk.Button(root, text="Save", command=save)
open_button = tk.Button(root, text="Open", command=open)

save_button.pack(side="left", padx=10, pady=10
open_button.pack(side="left", padx=10, pady=10
scribe_window.pack()

scribe = Scribe(scribe_window)

root.mainloop()
```
#### Shortcut Buttons


| Command       | Action        |
| ------------- |:------------:| 
| Control-c     | Copy      | 
| Control-v     | Paste     | 
| Control-s     | Save      | 
| Control-o     | Open      | 
| Control-b     | Bold      | 
| Control-i     | Italic    | 
| Control-u     | Underline | 

#### Contributing to Scribe

Bug fixes, feature additions, tests, documentation and more can be
contributed via [issues](https://github.com/Neil-Brown/tkScribe/issues)
and/or [pull requests](https://github.com/Neil-Brown/tkScribe/pulls).
All contributions are welcome. Please accompany any new code with tests.
* Fork the Scribe repository.
* Create a branch from master.
* Develop bug fixes, features, tests, etc.
* Create a pull request to pull the changes from your branch to the
  Scribe master. 
  



#### Reporting Issues

When reporting issues, please include code that replicates the issue,
(where possible) an image that demonstrates the issue.

* What did you do?
* What did you expect to happen?
* What actually happened?
* What versions of Pillow and Python are you using?




