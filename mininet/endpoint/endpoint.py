"""
This is the implementation for a host that sends or receives UDP streams.

The protocol is simple, every second, a frame is sent containing an encapsulated sequence number. the sequence number
is increased in every frame. The receiver can detect losses as missing sequence numbers.

On startup, device.json is read.

Listeners are created for every receiving port. A listener reports every reception event, and every detected loss, to
a central observer.

Senders are created for every configured recipient.
"""
import json
import os
import random
import socket
import threading
import time
from threading import Thread


def encaps_data(seq_nr, frame_size=1024):
    """
    encapsulate a sequence number for a frame. add padding for constant size
    :param seq_nr: sequence number to encapsulate
    :return:
    """
    d = str(seq_nr)
    return d+"".join((" " for _ in range(frame_size-len(d))))

def decaps_data(data):
    return int(data)


class Observer(object):

    __slots__ = ()

    def received(self, stream_id, seq_nr):
        pass

    def missed(self, stream_id, seq_nr):
        pass

    def finish(self):
        pass

class DirectPrintObserver(Observer):
    def __init__(self, show_positive):
        self.show_positive = show_positive

    def received(self, stream_id, seq_nr):
        if self.show_positive:
            print "%d: + %d" % (stream_id, seq_nr)

    def missed(self, stream_id, seq_nr):
        print "%d: -     %d" % (stream_id, seq_nr)

class SummaryPrintObserver(Observer):

    __slots__ = ("streams", "was_finished", "lock")

    def __init__(self):
        self.streams = {}
        self.was_finished = False
        self.lock = threading.Lock()

    def received(self, stream_id, seq_nr):
        with self.lock:
            if stream_id in self.streams:
                self.streams[stream_id]["max"] = max(seq_nr, self.streams[stream_id]["max"])
                self.streams[stream_id]["min"] = min(seq_nr, self.streams[stream_id]["min"])
            else:
                self.streams[stream_id] = {
                    "min": seq_nr,
                    "max": seq_nr,
                    "misses": 0
                }

    def missed(self, stream_id, seq_nr):
        with self.lock:
            if stream_id in self.streams:
                self.streams[stream_id]["max"] = max(seq_nr, self.streams[stream_id]["max"])
                self.streams[stream_id]["min"] = min(seq_nr, self.streams[stream_id]["min"])
                self.streams[stream_id]["misses"] += 1
            else:
                self.streams[stream_id] = {
                    "min": seq_nr,
                    "max": seq_nr,
                    "misses": 1
                }

    def finish(self):
        with self.lock:
            if self.was_finished:
                return
            self.was_finished = True
            for stream_id in sorted(self.streams.iterkeys()):
                stats = self.streams[stream_id]
                total_packets = stats["max"] + 1 - stats["min"]
                print "Stream %d" % stream_id
                print "  %d to %d observed (%d packets)" % (stats["min"], stats["max"], total_packets)
                print "  %d dropped (%d%s loss)" % (stats["misses"], int(100.0*float(stats["misses"])/float(total_packets)), "%")


class Listener(object):

    __slots__ = ("port", "last_seq_nr", "observer", "socket", "_is_running", "thread")

    def __init__(self, port, observer):
        self.port = port
        self.last_seq_nr = None
        self.observer = observer
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(1)
        self.socket.bind(("0.0.0.0", port))
        self._is_running = True
        self.thread = Thread(target=self.loop)
        self.thread.daemon = True
        self.thread.start()

    def shutdown(self):
        self._is_running = False
        self.socket.close()
        self.observer.finish()

    def loop(self):
        while self._is_running:
            try:
                data, _ = self.socket.recvfrom(1124)
                seq_nr = decaps_data(data)
                if self.last_seq_nr:
                    if seq_nr > self.last_seq_nr:
                        while seq_nr > self.last_seq_nr:
                            self.last_seq_nr += 1
                            if seq_nr != self.last_seq_nr:
                                self.observer.missed(self.port, self.last_seq_nr)
                    else:
                        continue
                else:
                    self.last_seq_nr = seq_nr
                self.observer.received(self.port, seq_nr)
            except socket.timeout:
                pass  # this is actually only used so that program end can be detected.

class Sender(object):

    __slots__ = ("target", "socket", "_is_running", "thread", "framesize", "interarrival_time",

                 "send_fun")

    def __init__(self, receiver_addr, dest_port, source_port, framesize, interarrival_time, lossy):
        self.target = (receiver_addr, dest_port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(("0.0.0.0", source_port))  # fixme: doesn't work. use different source port per stream
        self._is_running = True
        self.framesize = framesize
        self.interarrival_time = interarrival_time


        if lossy:
            rnd = random.random
            sendto = self.socket.sendto
            target = self.target
            def send_fun(seq_nr):
                if rnd() > 0.5:
                    sendto(encaps_data(seq_nr, framesize), target)
            self.send_fun =send_fun
        else:
            sendto = self.socket.sendto
            target = self.target
            def send_fun(seq_nr):
                sendto(encaps_data(seq_nr, framesize), target)
            self.send_fun =send_fun

        self.thread = Thread(target=self.loop)
        self.thread.daemon = True
        self.thread.start()

    def shutdown(self):
        self._is_running = False
        self.socket.close()

    def loop(self):
        next_wakeup = time.time()
        iit = self.interarrival_time  # performance
        tf = time.time  # performance
        send_fun = self.send_fun
        seq_nr = 0
        send_fun(seq_nr)
        while self._is_running:
            seq_nr += 1
            next_wakeup += iit
            time.sleep(next_wakeup - tf())
            send_fun(seq_nr)


if __name__ == "__main__":

    with open("device.json", "r") as f:
        config = json.loads(f.read())

    observer = SummaryPrintObserver()#config["config"]["show_positive"])

    listeners = [Listener(
        port,
        observer
    ) for port in config["receive"]]

    senders = [Sender(
        target["host"],
        target["dest_port"],
        target["source_port"],
        target["size"],
        target["interval"]/float(1000000000),
        config["config"]["lossy"]
    ) for target in config["send"]]

    try:
        while os.path.exists(os.path.join("/tmp", "endpoints_active")):
            time.sleep(2)
    except:
        pass

    for l in listeners:
        l.shutdown()
    for s in senders:
        s.shutdown()
    time.sleep(2)
