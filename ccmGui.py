#! /usr/bin/env python

import tkinter as Tk # python 3

from ccmModel import Model
from ccmView import View


class Controller:
    def __init__(self):
        self.root = Tk.Tk()
        self.model = Model()
        self.view = View(self.root, self.model)

    def run(self):
        self.root.title("Command and Control")
        self.root.deiconify()
        self.root.mainloop()

    def cleanup(self):
        self.model.shutdown()

if __name__ == '__main__':
    c = Controller()
    c.run() # will terminate when the window is closed
    c.cleanup()
