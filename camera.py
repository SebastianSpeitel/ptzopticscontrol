import requests
import logging
import socket
from enum import Enum

from PTZHTTP import PTZHTTP

logging.basicConfig(level=logging.INFO)


def toHex(num: int):
    return hex(num)[2:].zfill(2)


class Camera(PTZHTTP):
    class ZOOM(Enum):
        TELE = 'zoom_in'
        IN = 'zoom_in'
        WIDE = 'zoom_out'
        OUT = 'zoom_out'
        DIRECT = 'zoom_set'

    class FOCUS(Enum):
        NEAR = 'focus_near'
        FAR = 'focus_far'
        LOCK = 'focus_lock'
        UNLOCK = 'focus_unlock'

    class DRIVE(Enum):
        UP = 'drive_up'
        DOWN = 'drive_down'
        LEFT = 'drive_left'
        RIGHT = 'drive_right'
        STOP = 'drive_stop'

    defaults = dict(
        pan_speed=10,
        tilt_speed=10,
        zoom_speed=5
    )

    def __init__(self, defaults: dict = dict(), **kwargs):
        self.defaults = {**self.defaults, **defaults}
        super().__init__(**kwargs)

    def __getattr__(self, name):
        def cmd(*args, **kwargs):
            for k, v in kwargs.items():
                if v is None:
                    kwargs[k] = self.defaults.get(k)

            super()._action(name, *args, **kwargs)

        return cmd

    def move(self, panSpeed: int = 0, tiltSpeed: int = 0):
        pan: Camera.DRIVE = Camera.DRIVE.STOP
        tilt: Camera.DRIVE = Camera.DRIVE.STOP

        if tiltSpeed:
            tilt = Camera.DRIVE.DOWN if tiltSpeed > 0 else Camera.DRIVE.UP
            tiltSpeed = abs(tiltSpeed)

        if panSpeed:
            pan = Camera.DRIVE.LEFT if panSpeed < 0 else Camera.DRIVE.RIGHT
            panSpeed = abs(panSpeed)

        super()._action(
            action='drive',
            pan=pan,
            tilt=tilt,
            pan_speed=panSpeed,
            tilt_speed=tiltSpeed)

    def zoom(self, action, zoomspeed):
        if zoomspeed == None:
            zoomspeed = self.defaults["zoom_speed"]
        act = Camera.actions.get(action, Camera.actions.get(
            action, Camera.actions["zoomstop"]))

        msg = bytearray.fromhex(f"81 01 04 07 {act}{zoomspeed} FF")
        self.send(msg)

    def set_preset(self, preset: int):
        msg = bytearray.fromhex(f"81 01 04 3F 01 {toHex(preset)} FF")
        self.send(msg)

    def call_preset(self, preset: int):
        msg = bytearray.fromhex(f"81 01 04 3F 02 {toHex(preset)} FF")
        self.send(msg)


if __name__ == "__main__":
    cam = Camera('')
    cam.move(0, 0)
