from tofpipe.connection import conn_zmq, conn_socket, conn_base
from tofpipe.protocol.protobuf import Protocol, proto_base
from tofpipe.protocol.message import Status, ResponseType
from model import DeviceInfo, UseCase

import threading
import time
import queue


conn_types = {
    'tcp_socket': conn_socket.Client,
    'zmq': conn_zmq.Client,
}


class TCPSocket:
    MAX_QUEUE_SIZE = 10

    def __init__(self, address="127.0.0.1", port=5000, conn_type='zmq'):
        self._address = address
        self._port = port
        self._conn_type = conn_type

        self._protocol = Protocol()
        self._socket = None

        # define autoexposure control
        self._auto_exp = None
        self._auto_exp_en = False
        self._expo_time = 100

        # define receiving thread
        self._recv_loop: threading.Thread = None
        self._recv_loop_evt: threading.Event = threading.Event()
        # frame queue for incoming data
        self._depth_frames = queue.Queue(self.MAX_QUEUE_SIZE)
        self._ampl_frames = queue.Queue(self.MAX_QUEUE_SIZE)

        # status event
        self._status_evt = threading.Event()
        # status information
        self._device_info: DeviceInfo = DeviceInfo()
        self._use_cases: list[UseCase] = list()
        self._curr_uc = 0

        self.use_case_changed_evt: threading.Event = threading.Event()

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def open(self):
        """Open socket to pre-defined address/port"""
        self._socket: conn_base.Client = conn_types[self._conn_type](protocol=self._protocol)

        print("connecting to ", self._address, self._port)
        self._socket.connect(self._address, port=self._port)
        # setting a timeout somehow does not connect 
        # self._socket.set_timeout(5000)

        self._recv_loop = threading.Thread(target=self.__evt_loop, daemon=True)
        self._recv_loop.start()

    def close(self):
        self._recv_loop_evt.set()
        self._recv_loop.join()

        """Close active connection"""
        if self._socket is not None:
            self._socket.close()
            self._socket: conn_base.Client = conn_zmq.Client(protocol=self._protocol)

    def refresh_status(self, timeout_s: int = 1):
        # clear previous messages
        self._status_evt.clear()

        req = self._protocol.request()
        req.info = True

        if self._socket is not None:
            self._socket.send(req)

            start = time.time()
            while not self._status_evt.is_set() and time.time() - start < timeout_s:
                pass

            if self._status_evt.is_set():
                self._status_evt.clear()
            else:
                raise TimeoutError("No Status message received!")

    def get_image(self):
        try:
            phase = self._depth_frames.get(timeout=100e-3)
            intensity = self._ampl_frames.get(timeout=100e-3)
            self._depth_frames.task_done()
            self._ampl_frames.task_done()
        except queue.Empty as ex:
            raise ex

        phase_img = phase[1]
        phase_meta = phase[2]
        intensity_img = intensity[1]
        intensity_meta = intensity[2]

        if self._auto_exp_en:
            new_expo_time = int(self._auto_exp.calc(intensity_img))

            if new_expo_time != self._expo_time:
                self.set_exposure(new_expo_time)
                print(new_expo_time)

        return phase_img, intensity_img, phase_meta, intensity_meta

    def set_exposure(self, expo_time_us=80):
        self._expo_time = expo_time_us

        req = self._protocol.request()
        req.exposure = expo_time_us

        self._socket.send(req)

    def set_usecase(self, num=0):
        if self._use_cases[num].max_expo_us < self._expo_time:
            self.set_exposure(self._use_cases[num].max_expo_us)

        req = self._protocol.request()
        req.use_case = num
        self._socket.send(req)

        time.sleep(0.5)
        self.refresh_status()

    def disable_auto_exp(self):
        self._auto_exp_en = False

    def set_config(self, config):
        self._address = config["ip_address"]
        self._port = config["port"]
        self._conn_type = config["conn_type"]

    def get_config(self):
        config = {
            "ip_address": self._address,
            "port": self._port,
            "conn_type": self._conn_type
        }
        return config

    @property
    def device_info(self) -> DeviceInfo:
        return self._device_info

    @property
    def use_cases(self) -> (int, list[UseCase]):
        return self._curr_uc, self._use_cases

    def __set_device_status(self, status: Status):
        self._device_info = DeviceInfo(
            driver_name=status.driver_info.driver,
            driver_version=status.driver_info.version,
            hw=status.driver_info.card,
        )
        self._use_cases.clear()
        for use_case in status.use_cases:
            self._use_cases.append(
                UseCase(
                    num=use_case.num,
                    desc=use_case.description,
                    fmod1=use_case.fmod1,
                    fmod2=use_case.fmod2,
                    nr_frames=use_case.nr_frames,
                    max_expo_us=use_case.max_expo,
                )
            )

        if status.curr_uc != self._curr_uc:
            self._curr_uc = status.curr_uc
            self.use_case_changed_evt.set()

    def __evt_loop(self):
        while not self._recv_loop_evt.is_set():
            response: proto_base.Response = self._socket.recv()

            msg_type = response.response_type
            if msg_type == ResponseType.FRAMEDATA:
                frame = response.frame

                if frame[0] == proto_base.FrameType.PHASE:
                    if self._depth_frames.full():
                        # queue is full - remove first element and enqueue
                        self._depth_frames.get()
                        self._depth_frames.task_done()
                    self._depth_frames.put(frame)
                elif frame[0] == proto_base.FrameType.INTENSITY:
                    if self._ampl_frames.full():
                        # queue is full - remove first element and enqueue
                        self._ampl_frames.get()
                        self._ampl_frames.task_done()
                    self._ampl_frames.put(frame)
                else:
                    print("Unknown frame type received")
            elif msg_type == ResponseType.STATUS:
                print("Received Status Message!")
                self.__set_device_status(response.status)
                self._status_evt.set()
            elif msg_type == ResponseType.READREG:
                pass

        self._recv_loop_evt.clear()     # event loop stopped, clear event
