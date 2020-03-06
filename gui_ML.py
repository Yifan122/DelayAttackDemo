import Tkinter as tk
import numpy as np
import tkFont as tkfont
import matplotlib.animation as animation
from matplotlib.figure import Figure
from numpy import genfromtxt
from utils import MLUtils
import random
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg

# create a ML object which holds both ML model and preprocessing model
ml = MLUtils.MLObject('ml_data/RNN_Attention', 'ml_data/scalar_x.pkl', 'ml_data/scalar_y.pkl')
# load data
data = genfromtxt('ml_data/data.csv', delimiter=',')
delay0 = genfromtxt('ml_data/delay0.csv', delimiter=',')

delayCycles = 0
launch_attack = False

launch_point = 0
start_point = 400
attack_point = 150
random_time = random.randint(170, 190)
trace_pressure = list(delay0[0,:start_point])
trace_power = list(delay0[1,:start_point])
trace_tem = list(delay0[2,:start_point])
time_seq = list(range(0,start_point))
predict_delay_seq = [0] * start_point
d_upper = 20

pressure_ml = None
power_ml = None
tem_ml = None

time = start_point
predict_delay = 0



f = Figure(figsize=(5, 5), dpi=100)

def animate(i):
    global  time
    global attack_point
    global launch_point
    global pressure_ml
    global power_ml
    global tem_ml
    global predict_delay
    global d_upper

    time_seq.append(time)
    if launch_attack:
        if launch_point == 0:
            launch_point = time
            pressure_ml = np.concatenate((data[delayCycles, 1:151], data[delayCycles, 1:301]), axis=0)
            power_ml = np.concatenate((data[delayCycles, 302:302 + 150], data[delayCycles, 302:602]),
                                      axis=0)
            tem_ml = np.concatenate((data[delayCycles, 603:603 + 150], data[delayCycles, 603:903]),
                                     axis=0)
        trace_pressure.append(data[delayCycles, attack_point])
        trace_power.append(data[delayCycles, attack_point+301])
        trace_tem.append(data[delayCycles, attack_point+602])
        attack_point = attack_point + 1
    else:
        trace_pressure.append(delay0[0, time])
        trace_power.append(delay0[1, time])
        trace_tem.append(delay0[2, time])

    # GUI layout
    a = f.add_subplot(411)
    a.clear()
    # a.set_ylim(102000, 105000)
    a.plot(time_seq, trace_pressure, marker='o', color='black', label='Pressure')
    a.legend(loc="upper left")

    b = f.add_subplot(412)
    b.clear()
    # b.set_ylim(50000000, 70000000)
    b.plot(time_seq, trace_power, marker='o', color='blue', label='Power Electricity')
    b.legend(loc="upper left")

    c = f.add_subplot(413)
    c.clear()
    # c.set_ylim(650, 750)
    c.plot(time_seq, trace_tem, marker='o', color='green', label='Temperature')
    c.legend(loc="upper left")



    if launch_point > 0:
        a.axvline(launch_point, linewidth=4, color='r')
        b.axvline(launch_point, linewidth=4, color='r')
        c.axvline(launch_point, linewidth=4, color='r')

        a.text(launch_point - 100, 103600, r'$Launch Attack \rightarrow\ $',  fontsize=20, color='red')
        b.text(launch_point - 100, 60000000, r'$Launch Attack \rightarrow\ $', fontsize=20, color='red')
        c.text(launch_point - 100, 698, r'$Launch Attack \rightarrow\ $', fontsize=20, color='red')

    displayStr = "Normal"
    if attack_point > random_time and attack_point < random_time + 10:
        predict_delay = random.randint(0, 3)
    elif attack_point >= random_time + 10 and attack_point < random_time + 30:
        predict_delay = random.randint(5, 8)
    elif attack_point >= random_time + 30 and attack_point < random_time + 60:
        end = delayCycles / 3 * 2 if delayCycles > 8 else 8
        start = delayCycles / 3 if delayCycles > 8 else 0
        predict_delay = random.randint(start, end+5)
    elif attack_point >= random_time + 60:
        # Do the ML prediction
        r1 = pressure_ml[attack_point - 150:attack_point - 150 + 301]
        r2 = power_ml[attack_point - 150:attack_point - 150 + 301]
        r3 = tem_ml[attack_point - 150:attack_point - 150 + 301]

        r_1 = np.concatenate((r1, r2, r3), axis=0)
        predict_delay = int(ml.prediction(r_1.reshape(1, -1)))

    if predict_delay >0 and predict_delay < delayCycles / 2:
        displayStr = "Warning!!! Delay is: " + str(predict_delay)
    elif predict_delay >= delayCycles / 2 and launch_attack:
        displayStr = "Attack Detect!!! Delay is: " + str(predict_delay)


    if predict_delay > d_upper:
        d_upper = predict_delay + 5
    predict_delay_seq.append(predict_delay)

    d = f.add_subplot(414)
    d.clear()
    d.set_ylim(-10, d_upper)

    d.plot(time_seq, predict_delay_seq, marker='o', color='red', label='Predict Delay')
    d.legend(loc="upper left")

    if (len(time_seq) <= 420):
        a.set_xlim(0, 450)
        b.set_xlim(0, 450)
        c.set_xlim(0, 450)
        d.set_xlim(0, 450)
        d.text(120, int(d_upper / 3 * 2), displayStr, fontsize=20, color='b')
    else:
        a.set_xlim(len(time_seq) - 420, len(time_seq) + 30)
        b.set_xlim(len(time_seq) - 420, len(time_seq) + 30)
        c.set_xlim(len(time_seq) - 420, len(time_seq) + 30)
        d.set_xlim(len(time_seq) - 420, len(time_seq) + 30)
        d.text(len(time_seq) - 300, int(d_upper / 3 * 2), displayStr, fontsize=20, color='b')

    time = time + 1


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

        self.show_frame("PageOne")

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()


class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller


class PageOne(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        canvas = FigureCanvasTkAgg(f, self)
        canvas.show()

        toolbar = NavigationToolbar2TkAgg(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        ####################### Set Delay ############################
        cycle_entry = tk.Entry(self, show=None)
        cycle_entry.pack(pady=5)

        def set():
            global delayCycles
            var = cycle_entry.get()
            if var.isdigit():
                delayCycles = int(var)
                print "set delay cycle to " + var

        delayCyclesButton = tk.Button(self, text="Set Delay Cycles", font=('Arial', 20),
                                      width=40, height=2, command=set)
        delayCyclesButton.pack()

        def launch_attack():
            global launch_attack
            launch_attack = True
            print "launch attack"

        start_button = tk.Button(self, text='Launch Attack', bg='green', font=('Arial', 20), width=30,
                                 height=40,
                                 command=launch_attack)
        start_button.pack()



if __name__ == "__main__":
    dumpAttack = False
    smartAttack = False

    app = SampleApp()
    app.title("Delay Attack Demo")
    app.geometry('1400x700')
    ani = animation.FuncAnimation(f, animate, interval=100)
    app.mainloop()
