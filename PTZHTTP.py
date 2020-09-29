import logging
import requests


def driveAction(pan='', tilt='', *args, **kwargs):
    action = ''
    if pan == 'drive_left':
        action += 'left'
    elif pan == 'drive_right':
        action += 'right'

    if tilt == 'drive_up':
        action += 'up'
    elif tilt == 'drive_down':
        action += 'down'

    if not action:
        action = 'ptzstop'

    return action


_ACTIONS = dict(
    drive=driveAction
)

_PARAMS = dict(
    drive=('pan_speed', 'tilt_speed')
)


class PTZHTTP:
    def __init__(self, ip: str):
        self.ip = ip
        self.last_url = ''

    def _action(self, action: str, *args, **kwargs):
        action = _ACTIONS.get(action, lambda: action)(*args, **kwargs)

        params: list
        if action in _PARAMS:
            params = [kwargs[arg] for arg in _PARAMS[action]]
        else:
            params = [*args, (arg for arg in kwargs.values())]

        url = f"http://{self.ip}//cgi-bin/ptzctrl.cgi?ptzcmd&{action}"
        for p in params:
            url += f"&{p}"

        if self.last_url == url:
            return

        self.last_url = url
        logging.info(url)
        try:
            requests.get(url)
        except Exception:
            logging.error("Request failed")
            logging.error(dict(
                action=action,
                args=args,
                kwargs=kwargs,
                url=url))
