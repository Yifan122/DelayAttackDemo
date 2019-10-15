import Tkinter as tk
import tkFont as tkfont
import random
import ScrolledText as tkst
import threading
import time

from Config import config, DNP3PORT
from utils.Connection import Connection

numPackets = 30
delayCycles = 5

trace = []
trace_str = None

dumpAttack = False
smartAttack = False

starting = False

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

        cycle_label = tk.Label(self, text="ow many cycles you want to delay: ", font=('Arial', 28),
                               width=40, height=2)
        cycle_label.pack()

        cycle_entry = tk.Entry(self, show=None)
        cycle_entry.pack()

        def set():
            global numPackets
            global delayCycles
            global trace
            var1 = number_entry.get()
            var2 = cycle_entry.get()
            if var1.isdigit() and var2.isdigit():
                numPackets = int(var1)
                delayCycles = int(var2)
                print "Set the number of packets successfully"
                # trace = [random.randint(0, len(config.dnp3Packets) - 1) for i in range(numPackets)]
                for i in range(numPackets):
                    trace.append(random.randint(0, len(config.dnp3Packets) - 1))
                self.generateTraceStr()
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


    def generateTraceStr(self):
        global trace
        global trace_str
        global numPackets

        tmp = []
        tmp.append("The trace of the packets is: \n")
        tmp.append('*' * 110);
        tmp.append('\n')
        for i in range(numPackets):
            tmp.append(str(i + 1) + ". " + config.dnp3Type[trace[i]] + "\t")
            if (i + 1) % 5 == 0:
                tmp.append("\n")
        tmp.append('*' * 110)

        tmp = ''.join(tmp)
        trace_str.set(tmp)



class PageOne(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        global trace_str

        trace_label = tk.Label(self, textvariable=trace_str, font=('Arial', 18), width=120, height=10, justify=tk.LEFT)
        trace_label.pack()

        self.st = tkst.ScrolledText(self, font=('Arial', 18), width=120, height=20)
        self.st.pack()

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

        self.st.insert(tk.END, "*"*80 + "\n")
        self.st.insert(tk.END, "   Start sending packets \n")
        self.st.insert(tk.END, "*" * 80 + "\n")
        # Create connection
        connection = Connection(config.ipdst, DNP3PORT)
        connection.createConnection()

        for i in range(numPackets):
            # Generate random packets
            dnp3 = config.dnp3Packets[trace[i]]

            # Send packets
            connection.sendPacket(dnp3)
            self.st.insert(tk.END, str(i+1) + ". Sent \"" +config.dnp3Type[trace[i]] + "\"\n")

            buffer.append(trace[i])
            if (len(buffer) > delayCycles):
                buffer.pop(0)

            time.sleep(config.normalTime)

            if dumpAttack:
                for _ in range(delayCycles):
                    self.st.insert(tk.END, "no packet for this cycle\n")
                    time.sleep(config.normalTime)

                dumpAttack = False

            if smartAttack:
                self.st.insert(tk.END, "################################################\n")
                self.st.insert(tk.END, "# Delay the next coming packet by {} cycles\n".format(len(buffer)))
                self.st.insert(tk.END, "# Use the buffer packets to fulfill the gaps\n")
                self.st.insert(tk.END, "################################################\n")

                # print out the buff



                for j in range(len(buffer)):
                    dnp3 = config.dnp3Packets[trace[i]]

                    connection.sendPacket(dnp3)

                    time.sleep(config.normalTime)

                    self.st.insert(tk.END, "Sent buffer packets: "+config.dnp3Type[buffer[j]]+ "\n")

                self.st.insert(tk.END, "################################################\n")

                i = i + len(buffer)

                smartAttack = False


    def startSendPackets(self):
        global starting
        starting = True

    def normal_delay(self):
        global dumpAttack
        global delayCycles
        dumpAttack = True
        self.st.insert(tk.END, "*" * 80 + "\n")
        self.st.insert(tk.END, "Start a dump attack, delay the next packets for {} cycles\n".format(delayCycles))
        self.st.insert(tk.END, "*" * 80 + "\n")

    def smart_delay(self):
        global smartAttack
        global delayCycles
        smartAttack = True
        self.st.insert(tk.END, "*" * 80 + "\n")
        self.st.insert(tk.END, "Start a smart attack\n")
        self.st.insert(tk.END, "*" * 80 + "\n")

if __name__ == "__main__":

    dumpAttack = False
    smartAttack = False

    app = SampleApp()
    app.title("Delay Attack Demo")
    app.geometry('1400x700')
    app.mainloop()
