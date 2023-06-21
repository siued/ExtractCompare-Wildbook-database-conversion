from tkinter import Tk, messagebox


# use tk for this because it's easier
def show_message(title, text):
    Tk().withdraw()  # Hide the main window
    messagebox.showinfo(title, text)


# sort strings, but put alphabetic strings before numeric strings
def custom_sort(item):
    if all(c.isalpha() or c.isspace() for c in item):
        return 0, item
    else:
        return 1, item