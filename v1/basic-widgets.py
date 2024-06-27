from tkinter import *

master = Tk()

# Entry
Label(master, text='Enter the number of initial periods to be reported for verification: ').grid(row=0)
Label(master, text='Enter the minimum threshold for function length (microseconds): ').grid(row=1)
e1 = Entry(master)
e2 = Entry(master)
e1.grid(row=0, column=1)
e2.grid(row=1, column=1)

# CheckButton
var1 = IntVar()
Checkbutton(master, text='Saleae Live Capture', variable=var1).grid(row=2, sticky=W)
var2 = IntVar()
Checkbutton(master, text='Irregular Stats', variable=var2).grid(row=3, sticky=W)
mainloop()

mainloop()
