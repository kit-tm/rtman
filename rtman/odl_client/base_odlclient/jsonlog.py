"""
Logging of JSON requests to ODL
Data is stored only every x seconds to limit resource usage
"""
import base64
import datetime
import json
import time
from threading import Lock, Thread, Event

# in seconds
LOG_WAIT_BEFORE_SAVE = 7.0


class ODLJSONLogger(object):
    __slots__ = ("_log_entries", "_storing_lock", "_storing_thread", "_filename", "_stop_event", "_data_changed")

    def __init__(self):
        self._log_entries = []
        self._storing_lock = Lock()
        self._filename = "odl_log_" + datetime.datetime.now().replace(microsecond=0).isoformat() + ".json"
        self._stop_event = Event()
        self._data_changed = False
        self._storing_thread = Thread(target=self._save_log)
        self._storing_thread.start()

    def log_request(self, r, request_ts, request_json_data=None):
        """
        :type r: requests.Response
        :type request_ts: float
        :type request_json_data: dict
        """
        # collecting request information
        request_body_dict = {}
        if not r.request.body:
            request_body_dict["empty"] = True
        else:
            request_body_dict["empty"] = False
            request_body_dict["is_json"] = request_json_data is not None
            if request_json_data is not None:
                request_body_dict["content"] = request_json_data
            else:
                request_body_dict["content"] = base64.b64encode(r.request.body)
        request_dict = {"timestamp": self._time_to_millis(request_ts),
                        "path": r.request.path_url,
                        "url": r.request.url,
                        "method": r.request.method,
                        "headers": {key: value for key, value in r.request.headers.iteritems()},
                        "body": request_body_dict}
        # collecting response information
        response_body_dict = {}
        if not r.content:
            response_body_dict["empty"] = True
        else:
            response_body_dict["empty"] = False
            try:
                response_body_dict["content"] = r.json()
                response_body_dict["is_json"] = True
            except ValueError:
                response_body_dict["content"] = base64.b64encode(r.content)
                response_body_dict["is_json"] = False
        response_dict = {"timestamp": self._current_time_millis(),
                         "status_code": r.status_code,
                         "headers": {key: value for key, value in r.headers.iteritems()},
                         "body": response_body_dict}
        log_entry = {"request": request_dict, "response": response_dict}
        self._log_entries.append(log_entry)
        # making sure we don't miss any data while saving
        with self._storing_lock:
            self._data_changed = True

    def stop(self):
        self._stop_event.set()

    def _current_time_millis(self):
        return self._time_to_millis(time.time())

    def _save_log(self):
        while True:
            stop = self._stop_event.wait(LOG_WAIT_BEFORE_SAVE)
            with self._storing_lock:
                if self._data_changed:
                    with open(self._filename, 'w') as f:
                        json.dump(self._log_entries, f, sort_keys=True, indent=2)
                    self._data_changed = False
            if stop:
                return

    @staticmethod
    def _time_to_millis(t):
        return int(round(t * 1000))
