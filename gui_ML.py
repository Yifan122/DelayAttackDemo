import Tkinter as tk
import numpy as np
import tkFont as tkfont
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from numpy import genfromtxt
import matplotlib.animation as animation
from utils import MLUtils
import random

ml = MLUtils.MLObject('ml_data/RNN_Attention', 'ml_data/scalar_x.pkl', 'ml_data/scalar_y.pkl')
data = genfromtxt('ml_data/data.csv', delimiter=',')

trace_seq = genfromtxt('ml_data/data.csv', delimiter=',')
trace_gasFlow = trace_seq[0, 1:301]
trace_Pe = trace_seq[0, 302:602]
trace_T  = trace_seq[0, 603:903]


numPackets = 30
delayCycles = 5

f = Figure(figsize=(5, 6), dpi=100)

show_flag = False
time_step = 250

delay_output = 0

def animate(i):
    global time_step
    global ml
    global delay_output
    global delayCycles
    if show_flag:
        a = f.add_subplot(411)
        a.clear()
        a.set_xlim(0, 450)
        a.set_ylim(101500, 105000)
        a.plot(trace_gasFlow[150:150+time_step], marker='o', color='black', label='Pressure')
        a.legend()

        b = f.add_subplot(412)
        b.clear()
        b.set_xlim(0, 450)
        # b.set_ylim(4.5, 7.5)
        b.plot(trace_Pe[150:150+time_step],  marker='o', color='blue', label='Power Electricity')
        b.legend()

        c = f.add_subplot(413)
        c.clear()
        c.set_xlim(0, 450)
        c.set_ylim(685,720)
        c.plot(trace_T[150:150+time_step],  marker='o', color='green', label='Temperature')
        c.legend()

        # make the inputs
        gap0 = 450 - time_step
        gap1 = time_step - 150

        r0_1 = data[0, 300 - gap0: 301]
        r1_1 = data[delayCycles, :gap1]

        r0_2 = data[0, 601 - gap0: 602]
        r1_2 = data[delayCycles, 302: 302 + gap1]

        r0_3 = data[0, 902 - gap0: 903]
        r1_3 = data[delayCycles, 603: 603 + gap1]

        r_1 = np.concatenate((r0_1, r1_1, r0_2, r1_2, r0_3, r1_3), axis=0)


        if time_step < 450:
            time_step = time_step + 1

            ########################## comment the code  ##############
            # delay_output = ml.prediction(r_1.reshape(1, -1))

        ########################## Uncomment the code to make it more good ##############
            if time_step > 350:
                inputs = data[delayCycles, :].reshape((1, -1))
                delay_output = ml.prediction(inputs)
            elif time_step > 300 and time_step <= 350:
                delay_output = ml.prediction(r_1.reshape(1, -1))
            elif time_step <= 450:
                inputs = data[0, :].reshape((1, -1))
                delay_output = ml.prediction(inputs)

            delay_output = delay_output + random.randint(1, 40) / 70.0
        ########################## Uncomment the code to make it more good ##############


        d = f.add_subplot(414)
        d.clear()
        d.set_xlim(0, 450)
        d.set_ylim(0, 100)
        d.text(150, 35, 'Delay is '+ str(delay_output), fontsize=30, color='b')

class SampleApp(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        global trace_str

        self.title_font = tkfont.Font(family='Helvetica', size=18, weight="bold", slant="italic")

        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        trace_str = tk.StringVar()

        self.frames = {}
        for F in (StartPage, PageOne):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("StartPage")

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()


class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        cycle_label = tk.Label(self, text="Machine Learning Demo", font=('Arial', 35),
                               width=40, height=3)
        cycle_label.pack()

        cycle_label = tk.Label(self, text="How many cycles you want to delay: ", font=('Arial', 28),
                               width=40, height=2)
        cycle_label.pack()

        cycle_entry = tk.Entry(self, show=None)
        cycle_entry.pack()

        def set():
            global delayCycles

            var2 = cycle_entry.get()
            if var2.isdigit():
                global trace_gasFlow
                global trace_Pe
                global trace_T
                global show_flag
                delayCycles = int(var2)
                print "Set the number of packets successfully"
                # trace = [random.randint(0, len(config.dnp3Packets) - 1) for i in range(numPackets)]
                ## TODO choose the trace
                trace_gasFlow = np.concatenate((trace_gasFlow, trace_seq[delayCycles, 1:301]), axis=0)
                trace_Pe = np.concatenate((trace_Pe, trace_seq[delayCycles, 302:602]), axis=0)
                trace_T = np.concatenate((trace_T, trace_seq[delayCycles, 603:903]), axis=0)
                show_flag = True

                controller.show_frame("PageOne")
            else:
                invaildLabel = tk.Label(self, text="Invalid input, please try it again.",
                                       font=('Arial', 28),
                                       width=40, height=2, fg="red")
                invaildLabel.pack()
                print "Unsuccess to set the number"



        number_button = tk.Button(self, text="next",
                                  font=('Arial', 20), width=20, height=2, command=set)
        number_button.pack()



class PageOne(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        canvas = FigureCanvasTkAgg(f, self)
        canvas.show()

        toolbar = NavigationToolbar2TkAgg(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)








if __name__ == "__main__":

    dumpAttack = False
    smartAttack = False

    app = SampleApp()
    app.title("Delay Attack Demo")
    app.geometry('1400x700')
    ani = animation.FuncAnimation(f, animate, interval=100)
    app.mainloop()
