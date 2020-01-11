import Tkinter as tk
import tkFont as tkfont
import random
import threading
import time

from Config import config, DNP3PORT
from utils.Connection import Connection
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation

# https://pythonprogramming.net/embedding-live-matplotlib-graph-tkinter-gui/?completed=/how-to-embed-matplotlib-graph-tkinter-gui/

numPackets = 30
delayCycles = 5

# trace generated
trace = []
trace_seq = []
trace_show = []

# trace already sent
trace_seq_sent = []
trace_show_sent = []

trace_str = None

dumpAttack = False
smartAttack = False

starting = False

attack_point_normal = []
attack_point_smart = []


f = Figure(figsize=(5, 5), dpi=100)

def animate(i):
    a = f.add_subplot(211)
    a.clear()
    a.plot(trace_seq, trace_show, linestyle=':', marker='o', color='gray')
    a.set_xlim(0, len(trace_seq)+1)
    a.set_ylim(-1,1)
    a.set_title("Generated Trace:")


    b = f.add_subplot(212)
    b.clear()
    b.plot(trace_seq_sent, trace_show_sent, linestyle=':', marker='o', color='red')
    b.set_xlim(0, len(trace_seq)+1)
    b.set_ylim(-1, 1)
    b.set_title("Trace sent: ")
    if len(attack_point_smart) > 0:
        for point in attack_point_smart:
            b.axvline(point, linewidth=4, color='r')
            b.text(point+0.1, 0.3, r'$\leftarrow\ Attack$', fontsize=20, color='red')

    if len(attack_point_normal) > 0:
        for point in attack_point_normal:
            b.axvline(point, linewidth=4, color='b')
            b.axvline(point+delayCycles, linewidth=4, color='b')
            # b.text(point+0.1, 30, r'$\leftarrow\ Missing Packets$', fontsize=20, color='b')
            b.text(point+0.1, 0.5, 'Missing Packets', fontsize=20, color='blue')

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
        number_label = tk.Label(self, text="Number of packets", font=('Arial', 28), width=40, height=2)
        number_label.pack()

        number_entry = tk.Entry(self, show=None)
        number_entry.pack()

        cycle_label = tk.Label(self, text="how many cycles you want to delay: ", font=('Arial', 28),
                               width=40, height=2)
        cycle_label.pack()

        cycle_entry = tk.Entry(self, show=None)
        cycle_entry.pack()

        def set():
            global numPackets
            global delayCycles
            global trace
            global trace_seq
            global trace_show

            var1 = number_entry.get()
            var2 = cycle_entry.get()
            if var1.isdigit() and var2.isdigit():
                numPackets = int(var1)
                delayCycles = int(var2)
                print "Set the number of packets successfully"
                # trace = [random.randint(0, len(config.dnp3Packets) - 1) for i in range(numPackets)]
                for i in range(numPackets):
                    trace.append(random.randint(0, len(config.dnp3Packets) - 1))
                    trace_seq.append(i+1)
                    trace_show.append(random.randint(1, 40)/20.0 - 1.0)
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
        global trace_seq
        global trace_show

        canvas = FigureCanvasTkAgg(f, self)
        canvas.show()
        # canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        # canvas.get_tk_widget().pack

        toolbar = NavigationToolbar2TkAgg(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        start_button = tk.Button(self, text='Start sending packets', bg='green', width=15, height=2, command=self.startSendPackets)
        start_button.pack()

        normal_delay = tk.Button(self, text='Normal Delay', bg='green', width=15, height=2,
                                 command=self.normal_delay)
        normal_delay.pack()

        smart_delay = tk.Button(self, text='Smart Delay', bg='green', width=15, height=2,
                                 command=self.smart_delay)
        smart_delay.pack()

        t = threading.Thread(target=self.sendPackets, args=())
        t.start()


    def sendPackets(self):
        global starting
        global dumpAttack
        global smartAttack

        while(starting is False):
            time.sleep(0.3)
            continue

        buffer = []

        # Create connection
        connection = Connection(config.ipdst, DNP3PORT)
        connection.createConnection()

        i = 0
        while i < numPackets:
            trace_show_sent.append(trace_show[i])
            trace_seq_sent.append(i+1)

            # Generate random packets
            dnp3 = config.dnp3Packets[trace[i]]

            # Send packets
            connection.sendPacket(dnp3)

            time.sleep(config.normalTime)

            if dumpAttack:
                attack_point_normal.append(i+1)
                for j in range(delayCycles):
                    time.sleep(config.normalTime)
                    i = i + 1
                dumpAttack = False
            else:
                i = i + 1

            if smartAttack:
                attack_point_smart.append(i+1)
                attack_time = i
                for k in range(delayCycles+1, 1, -1):
                    trace_show_sent.append(trace_show[attack_time - k])
                    trace_seq_sent.append(i + 1)
                    i = i+1

                    # Send packets
                    connection.sendPacket(dnp3)

                    time.sleep(config.normalTime)

                smartAttack = False


    def startSendPackets(self):
        global starting
        starting = True

    def normal_delay(self):
        global dumpAttack
        dumpAttack = True

    def smart_delay(self):
        global smartAttack
        smartAttack = True


if __name__ == "__main__":

    dumpAttack = False
    smartAttack = False

    app = SampleApp()
    app.title("Delay Attack Demo")
    app.geometry('1400x700')
    ani = animation.FuncAnimation(f, animate, interval=1000)
    app.mainloop()
