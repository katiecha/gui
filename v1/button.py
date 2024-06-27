import tkinter

r = tkinter.Tk()
r.title('Stop Button')
button = tkinter.Button(r, text='Stop', width=25, command=r.destroy)
button.pack()
r.mainloop()