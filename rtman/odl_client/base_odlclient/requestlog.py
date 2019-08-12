"""
Logging of JSON requests to ODL
Data is stored only every x seconds to limit resource usage
"""
import base64
import json
import logging
import time
from Queue import Queue
from threading import Thread, Event

from ieee802dot1qcc.status import Status
from ieee802dot1qcc.talker import Talker

# in seconds
LOG_WAIT_BEFORE_SAVE = 7.0


class NoLogger(object):
    def __init__(self):
        pass

    def log_request(self, r, request_ts, request_json_data=None):
        pass

    def add_logentry(self, log_entry):
        pass

    def stop(self):
        pass


class LogEntry(object):
    @property
    def json(self):
        return {"type": None}


class UNILogEntry(object):
    __slots__ = (
        "timestamp",
        "talker",
        "listener",
        "status",
        "request_type"
    )

    TYPE_ADD = "register"
    TYPE_REMOVE = "remove"
    TYPE_STATUS = "status"

    def __init__(self, timestamp, uni_object, request_type):
        super(UNILogEntry, self).__init__()
        self.timestamp = timestamp

        if isinstance(uni_object, Status):
            self.status = uni_object
            uni_object = uni_object.associated_talker_or_listener
        else:
            self.status = None

        if isinstance(uni_object, Talker):
            self.talker = uni_object
            self.listener = None
        else:
            self.listener = uni_object
            self.talker = None

        self.request_type = request_type

    @property
    def json(self):
        return {
            "type": "uni",
            "request_type": self.request_type,
            "talker": self.talker.json() if self.talker else None,
            "listener": self.listener.json() if self.listener else None,
            "status": self.status.json() if self.status else None
        }


class RequestLogEntry(LogEntry):
    __slots__ = (
        "timestamp", "path", "url", "method", "headers", "body"
    )

    def __init__(self, timestamp, path, url=None, method=None, headers=None, body=None):
        super(RequestLogEntry, self).__init__()
        self.timestamp = timestamp
        self.path = path
        self.url = url
        self.method = method
        self.headers = headers
        self.body = body

    @property
    def json(self):
        return {
            "timestamp": self.timestamp,
            "path": self.path,
            "url": self.url,
            "method": self.method,
            "headers": self.headers,
            "body": self.body
        }


class ResponseLogEntry(LogEntry):
    __slots__ = ("timestamp", "status_code", "headers", "body")

    def __init__(self, timestamp, status_code=None, headers=None, body=None):
        super(ResponseLogEntry, self).__init__()
        self.timestamp = timestamp
        self.status_code = status_code
        self.headers = headers
        self.body = body

    @property
    def json(self):
        return {
            "timestamp": self.timestamp,
            "status_code": self.status_code,
            "headers": self.headers,
            "body": self.body
        }


class HTTPLogEntry(LogEntry):
    __slots__ = (
        "request", "response"
    )

    def __init__(self, request, response=None):
        super(HTTPLogEntry, self).__init__()
        self.request = request
        self.response = response

    @property
    def json(self):
        return {
            "request": self.request.json,
            "response": self.response.json if self.response else {},
            "type": "request"
        }


class RTmanStartEntry(LogEntry):
    __slots__ = ("timestamp",)

    def __init__(self, timestamp):
        super(RTmanStartEntry, self).__init__()
        self.timestamp = timestamp

    @property
    def json(self):
        return {
            "timestamp": self.timestamp,
            "type": "RTman_start"
        }


class RTmanStopEntry(LogEntry):
    __slots__ = ("timestamp",)

    def __init__(self, timestamp):
        super(RTmanStopEntry, self).__init__()
        self.timestamp = timestamp

    @property
    def json(self):
        return {
            "timestamp": self.timestamp,
            "type": "RTman_stop"
        }


class JSONLogger(NoLogger):
    __slots__ = ("_log_entry_queue", "_storing_thread", "_filename", "_write_event", "_is_running")

    def __init__(self, log_filename):
        self._is_running = True
        super(JSONLogger, self).__init__()
        self._filename = log_filename
        logging.info("writing request log to %s" % self._filename)
        self._write_event = Event()
        self._log_entry_queue = Queue()
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
        request_log_entry = RequestLogEntry(
            timestamp=self._time_to_millis(request_ts),
            path=r.request.path_url,
            url=r.request.url,
            method=r.request.method,
            headers={key: value for key, value in r.request.headers.iteritems()},
            body=request_body_dict
        )

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
        response_log_entry = ResponseLogEntry(
            timestamp=self._current_time_millis(),
            status_code=r.status_code,
            headers={key: value for key, value in r.headers.iteritems()},
            body=response_body_dict
        )

        log_entry = HTTPLogEntry(request=request_log_entry, response=response_log_entry)
        self.add_logentry(log_entry)

    def add_logentry(self, log_entry):
        self._log_entry_queue.put(log_entry)
        self._write_event.set()

    def stop(self):
        self._is_running = False
        self._write_event.set()

    def _current_time_millis(self):
        return self._time_to_millis(time.time())

    def _save_log(self):
        with open(self._filename, 'w') as f:
            f.write("[" + json.dumps(RTmanStartEntry(self._current_time_millis()).json))
            while self._is_running:
                self._write_event.wait(LOG_WAIT_BEFORE_SAVE)
                self._write_event.clear()
                while not self._log_entry_queue.empty():
                    entry_json = json.dumps(self._log_entry_queue.get().json)
                    f.write("," + entry_json)
                f.flush()
            f.write("," + json.dumps(RTmanStopEntry(self._current_time_millis()).json) + "]")

    @staticmethod
    def _time_to_millis(t):
        return int(round(t * 1000))
