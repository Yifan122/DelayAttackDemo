#! /usr/bin/env python
'''DNP3Crafter'''

import random
import threading
import time

from Config import config, DNP3PORT
from utils.Connection import Connection

dumpAttack = False
smartAttack = False


def delay_attack():
    global dumpAttack
    global smartAttack

    while(True):
        try:
            flag = input()
            if flag == 1:
                print '*'*33
                print "Start a dump attack, delay the next packets for {} cycles".format(delayCycles)
                print '*' * 33
                dumpAttack = True
            else:
                print '*' * 33
                print 'Start a smart attack'
                print '*' * 33
                smartAttack = True
        except:
            print "press 1 for dump attack.\npress 2 for smart attack"


def send_packet():
    print "start sending packets"
    global dumpAttack
    global smartAttack


    # Create connection
    connection = Connection(config.ipdst, DNP3PORT)
    connection.createConnection()

    for i in range(numPackets):
        # Generate random packets
        dnp3 = config.dnp3Packets[trace[i]]

        # Send packets
        connection.sendPacket(dnp3)

        print str(i) + '. Sent', config.dnp3Type[trace[i]]

        # Store the packets into the buffer
        # if buffer size is larger than delayCycles, discard it
        buffer.append(trace[i])
        if (len(buffer) > delayCycles):
            buffer.pop(0)

        time.sleep(config.normalTime)

        if dumpAttack:
            time.sleep(config.normalTime * 2)
            dumpAttack = False

        if smartAttack:
            print "################################################"
            print "# Delay the next coming packet by {} cycles".format(len(buffer))
            print "# Use the buffer packets to fulfill the gaps"
            print "################################################"

            # print out the buff
            print ""
            print '*' * 100
            print "The buff is: "
            for k in range(len(buffer)):
                print "#" + config.dnp3Type[buffer[k]] + "\t",
                if (k + 1) % 10 == 0:
                    print ""
            print ""
            print '*' * 100

            for j in range(len(buffer)):
                dnp3 = config.dnp3Packets[trace[i]]

                connection.sendPacket(dnp3)

                time.sleep(config.normalTime)

                print 'Sent buffer packets: ', config.dnp3Type[buffer[j]]

            i = i + len(buffer)

            smartAttack = False


    print 'Finished.\n'
    connection.close()


if __name__ == "__main__":
    print "##########################################"
    print "# This is the Demo for time delay Attack #"
    print "##########################################"
    print ""

    # The cycle time of AGC is 2 secs
    print "Assume the cycle time of AGC is {} secs\n".format(config.normalTime)

    numPackets = int(raw_input("Number of packets(default is 30): ") or "30")
    delayCycles = int(raw_input("How many cycles you want to delay(default is 5): ") or "5")

    trace = [random.randint(0, len(config.dnp3Packets) - 1) for i in range(numPackets)]

    # print out the trace
    print ""
    print '*' * 100
    print "The trace is: "
    for i in range(numPackets):
        print "#" + config.dnp3Type[trace[i]] + "\t",
        if (i + 1) % 10 == 0:
            print ""
    print '*' * 100

    print "\n"
    time.sleep(3)

    print "###############################################################"
    print "# AGC start to send packets      "
    print "# 1. Press 1 changing the next arriving packets by {} cycles".format(delayCycles)
    print "# 2. Press 2 time delay attack without changing time interval"
    print "#    but fulfill the gap using previous packets"
    print "###############################################################\n\n"

    time.sleep(5)
    print "Start to send the packets\n"
    time.sleep(2)

    buffer = []

    # creating thread
    t1 = threading.Thread(target=delay_attack, args=())
    t2 = threading.Thread(target=send_packet, args=())

    # starting thread 1
    t1.start()
    # starting thread 2
    t2.start()

    # wait until thread 1 is completely executed
    t1.join()
    # wait until thread 2 is completely executed
    t2.join()

    # both threads completely executed
    print("Done!")





