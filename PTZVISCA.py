import socket
import logging

_ACTIONS = dict(
    zoom="81 01 04 07 {dir:=1x}{speed:=1x} FF",
    drive="81 01 06 01 {pan_speed:=2x} {tilt_speed:=2x} {pan:=2x} {tilt:=2x} FF",
    preset="81 01 04 3F 0{mode:=1x} {preset:=2x} FF"
)

_CONSTANTS = dict(
    zoom_in=2,
    zoom_out=3,
    zoom_set=0,
    focus_near=3,
    focus_far=2,
    focus_lock=2,
    focus_unlock=3,
    drive_up=1,
    drive_down=2,
    drive_left=1,
    drive_right=2,
    drive_stop=3
)


class PTZVISCA:
    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port
        self.sock = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.last_message = ''

    def _action(self, action: str, **kwargs):
        spec = {k: _CONSTANTS.get(v, v) for k, v in kwargs.items()}
        msg = _ACTIONS.get(action, '').format(**spec)

        if msg == self.last_message:
            return
        self.sock.sendto(msg, (self.ip, self.port))
        recvMsg = 0
        while True:
            nextBytes = self.sock.recv(50)
            recvMsg = int(nextBytes.hex(), 16)
            if 9461759 >= recvMsg >= 9457919:
                recvMsg = 0
                continue
            elif 9457663 >= recvMsg >= 9453823:
                self.last_message = msg
                break
