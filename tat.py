import sys
import os
import matplotlib.pyplot as plt
import numpy
import tkinter as tk
from tkinter import filedialog
from datetime import datetime


if len(sys.argv) > 1:
    files = sys.argv[1:]
else:
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilenames(initialdir=os.path.abspath(os.getcwd()))
    files = [a for a in file_path]


def generate_file(filename):
    logname = filename
    num = 1
    while logname in os.listdir():
        if num > 1:
            logname[-1] = str(num)
        else:
            logname += str(num)
        logname += 1

    file_location = os.getcwd()    
    filename_ = file_location + "\\" + logname + ".txt"
    file = open(filename_, 'w')
    file.write(datetime.now().strftime("%m_%d_%Y, %H-%M-%S"))
    file.close()

for i in range(len(files)):
    filename = files[i]
    if filename[-3:] == "txt":
        print("Starting analysis...")            
        generate_file(filename)
        print("Done. PDF generated \n")
print("Building comparison...") 
print("Done. PDF generated \n")


