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

# Flags
starting = False
dumpAttack = False
smartAttack = False

# Default delay cycles
delayCycles = 3

# Display trace
generated_trace = []
generated_seq = []

send_trace = []
send_seq = []

attack_trace = [[]]
attack_seq = [[]]

# Attack Counter
smartAttackCounter = 0
dumpAttackCounter = 0

normalDelayPoints = []
smartDelayPoints = []

f = Figure(figsize=(5, 5), dpi=100)


def animate(i):
    a = f.add_subplot(211)
    a.clear()
    a.set_ylim(-1, 1)
    a.plot(generated_seq, generated_trace, linestyle=':', marker='o', color='gray')
    a.set_title("Generated Trace:")

    b = f.add_subplot(212)
    b.clear()
    b.set_ylim(-1, 1)
    b.set_title("Trace sent: ")
    b.plot(send_seq, send_trace, linestyle=':', marker='o', color='gray')

    for j in range(len(attack_seq)):
        b.plot(attack_seq[j], attack_trace[j], linestyle=':', marker='o', color='red')

    if len(smartDelayPoints) > 0:
        for point in smartDelayPoints:
            b.axvline(point, linewidth=4, color='r')
            b.text(point + 0.1, 0.3, r'$\leftarrow\ Attack$', fontsize=20, color='red')

    if len(normalDelayPoints) > 0:
        for point in normalDelayPoints:
            b.axvline(point, linewidth=4, color='b')
            b.text(point + 0.1, 0.5, 'Missing Packets', fontsize=20, color='blue')

    if len(generated_seq) < 40:
        a.set_xlim(0, 40)
        b.set_xlim(0, 40)
        b.text(1, 0.75, 'Delay Cycles:' + str(delayCycles), fontsize=16, color='red')
    else:
        a.set_xlim(len(generated_seq) - 40, len(generated_seq))
        b.set_xlim(len(generated_seq) - 40, len(generated_seq))
        b.text(len(generated_seq) - 40 + 1, 0.75, 'Delay Cycles:' + str(delayCycles), fontsize=16, color='red')


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
        number_label = tk.Label(self, text="Number of packets", font=('Arial', 28), width=40, height=2)
        number_label.pack()

        number_entry = tk.Entry(self, show=None)
        number_entry.pack()

        cycle_label = tk.Label(self, text="how many cycles you want to delay: ", font=('Arial', 28),
                               width=40, height=2)
        cycle_label.pack()

        cycle_entry = tk.Entry(self, show=None)
        cycle_entry.pack()


class PageOne(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        global trace_seq
        global trace_show

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

        start_button = tk.Button(self, text='Start sending packets', bg='green', font=('Arial', 20), width=30,
                                 height=40,
                                 command=self.startSendPackets)
        start_button.pack(padx=40, side=tk.LEFT)

        normal_delay = tk.Button(self, text='Normal Delay', bg='green', font=('Arial', 20), width=30, height=40,
                                 command=self.normal_delay)
        normal_delay.pack(padx=40, side=tk.LEFT)

        smart_delay = tk.Button(self, text='Smart Delay', bg='green', font=('Arial', 20), width=30, height=40,
                                command=self.smart_delay)
        smart_delay.pack(padx=40, side=tk.LEFT)

        t = threading.Thread(target=self.sendPackets, args=())
        t.start()

    def sendPackets(self):
        global starting
        global dumpAttack
        global smartAttack
        global generated_trace
        global generated_seq
        global send_trace
        global send_seq
        global attack_trace
        global attack_seq
        global dumpAttackCounter
        global smartAttackCounter

        while (starting is False):
            time.sleep(0.3)
            continue

        # Create connection
        # connection = Connection(config.ipdst, DNP3PORT)
        # connection.createConnection()

        i = 0
        while True:
            # Generate random packets
            dnp3 = config.dnp3Packets[random.randint(0, len(config.dnp3Packets) - 1)]

            generated_trace.append(random.randint(0, 20) / 10.0 - 1)
            generated_seq.append(i)

            if dumpAttackCounter > 0:
                dumpAttackCounter = dumpAttackCounter - 1

            elif smartAttackCounter > 0:
                maliciousPacket = generated_trace[smartDelayPoints[len(smartDelayPoints) - 1] - smartAttackCounter]
                smartAttackCounter = smartAttackCounter - 1
                send_seq.append(generated_seq[i])
                send_trace.append(maliciousPacket)

                attack_seq[len(attack_trace) - 1].append(generated_seq[i])
                attack_trace[len(attack_trace) - 1].append(maliciousPacket)

                if smartAttackCounter == 0:
                    attack_seq.append([])
                    attack_trace.append([])

                # Send packets
                # connection.sendPacket(dnp3)

            else:
                send_trace.append(generated_trace[i])
                send_seq.append(generated_seq[i])
                # Send packets
                # connection.sendPacket(dnp3)

            i = i + 1

            time.sleep(config.normalTime)

    def startSendPackets(self):
        global starting
        starting = True

    def normal_delay(self):
        global dumpAttack
        global dumpAttackCounter
        global normalDelayPoints
        dumpAttack = True
        dumpAttackCounter = delayCycles
        normalDelayPoints.append(len(generated_trace) - 1)

    def smart_delay(self):
        global smartAttack
        global smartAttackCounter
        global generated_trace
        global smartDelayPoints
        smartAttack = True
        smartAttackCounter = delayCycles
        smartDelayPoints.append(len(generated_trace) - 1)


if __name__ == "__main__":
    dumpAttack = False
    smartAttack = False

    app = SampleApp()
    app.title("Delay Attack Demo")
    app.geometry('1400x900')
    ani = animation.FuncAnimation(f, animate, interval=1000)
    app.mainloop()
