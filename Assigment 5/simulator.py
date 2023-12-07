import argparse
from copy import deepcopy
from enum import Enum, auto
import random
import sys
import time

# Constants
BIDIRECTIONAL = 0
TIMER_INTERRUPT = 0
FROM_LAYER5 = 1
FROM_LAYER3 = 2
OFF = 0
ON = 1
A = 0
B = 1

# Data structures
class Msg:
    def __init__(self, data):
        self.data = data

class Packet:
    def __init__(self, seqnum, acknum, checksum, payload):
        self.seqnum = seqnum
        self.acknum = acknum
        self.checksum = checksum
        self.payload = payload

# Global variables
expectedSeqNumA = 0
lastPacketA = None
expectedSeqNumB = 0
lastPacketB = None
lastAckNumB = 0

# Event structures
class Event:
    def __init__(self, evtime, evtype, eventity, pktptr):
        self.evtime = evtime
        self.evtype = evtype
        self.eventity = eventity
        self.pktptr = pktptr
        self.prev = None
        self.next = None

evlist = None

# Network parameters
TRACE = 1
nsim = 0
nsimmax = 0
time = 0.0
lossprob = 0.0
corruptprob = 0.0
lambda_val = 0.0
ntolayer3 = 0
nlost = 0
ncorrupt = 0

# Main functions
def A_output(message):
    global expectedSeqNumA, lastPacketA
    packet = Packet(expectedSeqNumA, 0, 0, message.data[:20])
    packet.checksum = calculate_checksum(packet)
    lastPacketA = packet
    tolayer3(A, packet)
    start_timer(A, 30.0)

def B_output(message):
    global expectedSeqNumB, lastPacketB
    packet = Packet(expectedSeqNumB, 0, 0, message.data[:20])
    packet.checksum = calculate_checksum(packet)
    lastPacketB = packet
    tolayer3(B, packet)
    start_timer(B, 30.0)

def A_input(packet):
    global lastPacketA
    if calculate_checksum(packet) == packet.checksum and packet.acknum == lastPacketA.seqnum:
        stoptimer(A)

def A_timerinterrupt():
    global lastPacketA
    tolayer3(A, lastPacketA)
    start_timer(A, 30.0)

def calculate_checksum(packet):
    checksum = packet.seqnum + packet.acknum
    for char in packet.payload:
        checksum += ord(char)
    return checksum

def B_input(packet):
    global expectedSeqNumB, lastAckNumB
    if calculate_checksum(packet) == packet.checksum and packet.seqnum == expectedSeqNumB:
        tolayer5(B, packet.payload)
        ack_pkt = Packet(0, packet.seqnum, 0, "")
        ack_pkt.checksum = calculate_checksum(ack_pkt)
        tolayer3(B, ack_pkt)
        expectedSeqNumB = 1 - expectedSeqNumB
    else:
        ack_pkt = Packet(0, lastAckNumB, 0, "")
        ack_pkt.checksum = calculate_checksum(ack_pkt)
        tolayer3(B, ack_pkt)

def B_timerinterrupt():
    pass

def B_init():
    pass

def tolayer3(AorB, packet):
    global ntolayer3, nlost, ncorrupt
    ntolayer3 += 1

    if random.random() < lossprob:
        nlost += 1
        if TRACE > 0:
            print("TOLAYER3: packet being lost")
        return

    if random.random() < corruptprob:
        ncorrupt += 1
        x = random.random()
        if x < 0.75:
            packet.payload = 'Z'
        elif x < 0.875:
            packet.seqnum = 999999
        else:
            packet.acknum = 999999
        if TRACE > 0:
            print("TOLAYER3: packet being corrupted")

    evptr = Event(0.0, FROM_LAYER3, (AorB + 1) % 2, packet)
    lastime = time

    for q in evlist:
        if q.evtype == FROM_LAYER3 and q.eventity == evptr.eventity:
            lastime = q.evtime

    evptr.evtime = lastime + 1 + 9 * random.random()

    if TRACE > 2:
        print("TOLAYER3: scheduling arrival on the other side")

    insertevent(evptr)

def tolayer5(AorB, datasent):
    if TRACE > 2:
        print("TOLAYER5: data received:", ''.join(datasent))

def stoptimer(AorB):
    global evlist
    for q in evlist:
        if q.evtype == TIMER_INTERRUPT and q.eventity == AorB:
            evlist.remove(q)
            return

def start_timer(AorB, increment):
    global evlist

    # Verificar si ya hay un temporizador para la entidad AorB
    timer_exists = any(q.evtype == TIMER_INTERRUPT and q.eventity == AorB for q in [evlist])

    if not timer_exists:
        evptr = Event(time + increment, TIMER_INTERRUPT, AorB, None)
        insertevent(evptr)


def generate_next_arrival():
    global time, evlist
    x = lambda_val * random.random() * 2
    evptr = Event(time + x, FROM_LAYER5, B if BIDIRECTIONAL and random.random() > 0.5 else A, None)
    insertevent(evptr)

def insertevent(evptr):
    global evlist
    if evlist is None:
        evlist = evptr
        evptr.next = None
        evptr.prev = None
    else:
        q = evlist
        qold = q
        while q is not None and evptr.evtime > q.evtime:
            qold = q
            q = q.next

        if q is None:
            qold.next = evptr
            evptr.prev = qold
            evptr.next = None
        elif q == evlist:
            evptr.next = evlist
            evptr.prev = None
            evlist.prev = evptr
            evlist = evptr
        else:
            evptr.next = q
            evptr.prev = q.prev
            q.prev.next = evptr
            q.prev = evptr

def printevlist():
    global evlist
    print("--------------\nEvent List Follows:")
    q = evlist
    while q is not None:
        print(f"Event time: {q.evtime}, type: {q.evtype}, entity: {q.eventity}")
        q = q.next
    print("--------------")

def jimsrand():
    return random.random()

def init():
    global nsimmax, lossprob, corruptprob, lambda_val, TRACE, nsim, time, ntolayer3, nlost, ncorrupt

    print("-----  Stop and Wait Network Simulator Version 1.1 -------- \n")
    nsimmax = int(input("Enter the number of messages to simulate: "))
    lossprob = float(input("Enter packet loss probability [enter 0.0 for no loss]: "))
    corruptprob = float(input("Enter packet corruption probability [0.0 for no corruption]: "))
    lambda_val = float(input("Enter average time between messages from sender's layer5 [ > 0.0]: "))
    TRACE = int(input("Enter TRACE: "))

    random.seed(9999)
    sum_val = 0.0

    for _ in range(1000):
        sum_val += jimsrand()

    avg = sum_val / 1000.0

    if avg < 0.25 or avg > 0.75:
        print("It is likely that random number generation on your machine\n"
              "is different from what this emulator expects.  Please take\n"
              "a look at the routine jimsrand() in the emulator code. Sorry.")
        exit()

    ntolayer3 = 0
    nlost = 0
    ncorrupt = 0

    time = 0.0
    generate_next_arrival()

def main():
    global evlist, nsim, time

    init()

    while True:
        eventptr = evlist

        if eventptr is None:
            break

        evlist = evlist.next

        if evlist is not None:
            evlist.prev = None

        if TRACE >= 2:
            print(f"\nEVENT time: {eventptr.evtime}, type: {eventptr.evtype}", end="")
            if eventptr.evtype == 0:
                print(", timerinterrupt  ", end="")
            elif eventptr.evtype == 1:
                print(", fromlayer5 ", end="")
            else:
                print(", fromlayer3 ", end="")
            print(f" entity: {eventptr.eventity}\n")

        time = eventptr.evtime

        if nsim == nsimmax:
            break

        if eventptr.evtype == FROM_LAYER5:
            generate_next_arrival()
            j = nsim % 26
            msg2give = Msg(''.join([chr(97 + j)] * 20))
            if TRACE > 2:
                print("          MAINLOOP: data given to student: ", end="")
                for char in msg2give.data:
                    print(char, end="")
                print("\n")
            nsim += 1

            if eventptr.eventity == A:
                A_output(msg2give)
            else:
                B_output(msg2give)

        elif eventptr.evtype == FROM_LAYER3:
            pkt2give = Packet(eventptr.pktptr.seqnum, eventptr.pktptr.acknum, eventptr.pktptr.checksum,
                              eventptr.pktptr.payload)
            if eventptr.eventity == A:
                A_input(pkt2give)
            else:
                B_input(pkt2give)

        elif eventptr.evtype == TIMER_INTERRUPT:
            if eventptr.eventity == A:
                A_timerinterrupt()
            else:
                B_timerinterrupt()

        else:
            print("INTERNAL PANIC: unknown event type\n")

    print(f" Simulator terminated at time {time}\n after sending {nsim} msgs from layer5\n")


if __name__ == "__main__":
    main()