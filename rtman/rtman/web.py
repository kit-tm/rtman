import json
import re
import traceback
from SocketServer import TCPServer
import BaseHTTPServer
from threading import Thread

from base_odlclient.node import ODLNode, Switch

from jinja2 import Environment, PackageLoader, select_autoescape

from irt_odlclient.schedule import TransmissionPoint
from reserving_odlclient.stream import MultiStream

env = Environment(
    loader=PackageLoader('rtman', 'templates'),
    autoescape=select_autoescape(['html', 'xml'])
)

def flatten_dict(d, separator="/"):
    """
    flatten a dict, preserving key paths. For example,

    {
      a: {
        b: 3,
        c: {
          d: 4
        }
      }
    }

    becomes
    {
      a/b: 3,
      a/c/d: 4
    }

    :param any d: dict to flatten
    :param str separator: separator to combine keys ("/" in the example above)
    :return:
    """
    result = {}
    if isinstance(d, list):
        d = {i:d[i] for i in range(len(d))}
    for k, v in d.iteritems():
        if isinstance(v, dict) or isinstance(v, list):
            for vk, vv in flatten_dict(v).iteritems():
                result["%s%s%s" % (k, separator, vk)] = vv
        else:
            result[k] = v
    return result

class RTmanWebHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    """
    BaseHTTPRequestHandler to use for RTmanWebServer.
    Uses RTmanWeb's respond_by_urls function to respond to requests.
    """

    def _use_rtmanweb(self, method):
        res = self.server.rtmanweb.respond_by_urls(path=self.path, method=method)
        body, status, headers = res
        self.send_response(status)
        for k, v in headers.iteritems():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        """
        this is how HTTPServer handles a GET request
        :return:
        """
        self._use_rtmanweb(method="GET")

    def do_POST(self):
        """
        this is how HTTPServer handles a POST request
        :return:
        """
        self._use_rtmanweb(method="POST")

    def do_PUT(self):
        """
        this is how HTTPServer handles a PUT request
        :return:
        """
        self._use_rtmanweb(method="PUT")

    def do_DELETE(self):
        """
        this is how HTTPServer handles a DELETE request
        :return:
        """
        self._use_rtmanweb(method="DELETE")

    def log_request(self, code='-', size='-'):
        """
        this is how HTTPServer logs.
        this implementation simply does not log anything anywhere.
        """
        return

class RTmanWebServer(BaseHTTPServer.HTTPServer):
    """
    HTTPServer that is aware of an RTmanWeb instance.
    """

    # noinspection PyPep8Naming
    def __init__(self, rtmanweb, server_address, RequestHandlerClass=RTmanWebHandler, bind_and_activate=True):
        TCPServer.__init__(self, server_address, RequestHandlerClass, bind_and_activate)
        self.rtmanweb = rtmanweb

class RTmanWeb(object):
    """
    Opens an HTTPServer and provides a method for handling requests.
    """

    __slots__ = ("_rtman", "_urls", "_webserver")

    def __init__(self, rtman):
        self._rtman = rtman

        # define urls like in django's urls.py
        self._urls = (
            (r'^$', "GET", self._index),
            (r'^/switch$', "GET", self._switches),
            (r'^/switch/(?P<switch>[a-zA-Z0-9:;_]*)/flows$', "GET", self._switch_flows),
            (r'^/graph$', "GET", self._graph),
            (r'^/graph/topology.json$', "GET", self._graph_topology_json)
        )

    def start(self, hostname="localhost", port=8080):
        """
        called to start the webserver

        :param str hostname: hostname to bind to
        :param int port: tcp port to bind to
        :return:
        """
        self._webserver = RTmanWebServer(self, (hostname, port))
        t = Thread(target=self._webserver.serve_forever)
        t.daemon = True
        t.start()

    def stop(self):
        """
        stop the webserver
        :return:
        """
        self._webserver.server_close()

    def _index(self):
        return env.get_template("index.html").render(
            stream_count=len(self._rtman.odl_client.partialstreams),
            switch_count=len(self._rtman.odl_client.switches),
            flow_count=len(self._rtman.odl_client.flows)
        ), None, None

    def _switches(self):
        return env.get_template("switch_list.html").render(
            switches=[{"name": node_id} for node_id in self._rtman.odl_client.switches.iterkeys()]
        ), None, None


    def _switch_flows(self, switch):
        flows = []
        try:
            switch_obj = self._rtman.odl_client.get_node(switch)
            for flow in switch_obj._flows:
                flowentry = {"others": {}}
                for k, v in flow._odl_inventory().iteritems():
                    if k == "id":
                        flowentry["id"] = v
                    elif k == "instructions":
                        instructions = []
                        for vk, vv in sorted(flatten_dict(v.get("instruction", {})).iteritems(), key=lambda (x, y): x):
                            if not vk.endswith("order"):
                                instructions.append(("instruction/%s" % vk, vv))
                        flowentry["instructions"] = instructions
                    elif k == "match":
                        matches = []
                        for vk, vv in sorted(flatten_dict(v).iteritems(), key=lambda (x, y): x):
                            if not vk.endswith("order"):
                                matches.append(("match/%s" % vk, vv))
                        flowentry["match"] = matches
                    else:
                        flowentry["others"][k] = v
                flows.append(flowentry)
        except KeyError:
            traceback.print_exc()
            return "Switch does not exist", 404, None

        return env.get_template("switch_flows.html").render(
            switch_name=switch,
            flows=flows
        ), None, None

    def _graph(self):
        """
        the graph document is just the web-based program that displays the topology.
        Data is added when it loads graph/topology.json.

        Here, we simply define some parameters for the program.
        """
        return env.get_template("graph.html").render(
            streamcolors=[  # colors used for stream display. Just some default graph colors.
                "3366CC",
                "DC3912",
                "FF9900",
                "109618",
                "990099",
                "3B3EAC",
                "0099C6",
                "DD4477",
                "66AA00",
                "B82E2E",
                "316395",
                "994499",
                "22AA99",
                "AAAA11",
                "6633CC",
                "E67300",
                "8B0707",
                "329262",
                "5574A6",
                "3B3EAC"
            ],
            node_size=7,  # size of node circles
            linkdistance=5,  # distance of switch-switch links (note: this is a target, and is affected by node gravity)
            linkdistance_hostlink=1,  # distance of host-switch links (note: again just a target, see gravity)
            gravity=-800,  # force that pulls nodes away from each other (yes, this is negative gravity)
            color_switches="#88f",  # color for switch nodes
            color_hosts="#888"  # color for host nodes
        ), None, None

    def _graph_topology_json(self):
        """

        :return: all the data needed by graph.html
        """

        # for nodes, we simply need to know their ids (to reference them in links, and for display) and
        # whether or not they are hosts (if not a host: it's a switch!)
        # and while we are iterating all hosts, we can use their neighbor lists to get all the links as well.
        links = set()
        nodes = []
        for node in self._rtman.odl_client.nodes.itervalues():  # type: ODLNode
            nodes.append({
                "id": node.node_id,
                "is_host": not isinstance(node, Switch)
            })
            for neighbor in node.get_neighbors():
                links.add(tuple(sorted((node, neighbor))))  # sort so that we have a fixed order to eliminate duplicates

        # for links, we need to know
        #   - source and destination,
        #   - if it's a host link (it's much easier to find that out here)
        #   - and the costs in bost directions
        links_topology = [{
            "source": s.node_id,
            "target": t.node_id,
            "is_host_link": (not isinstance(s, Switch)) or (not isinstance(t, Switch)),
            "cost_a": None,
            "cost_b": None
        } for s, t in links]

        # for streams, we need a list of used links. for each link, we need both hosts, and the stream name
        #  (the stream name is for easier adding in graph.html)
        # what we want is to have all links for any given stream
        streams = {}  # :type: dict[str, list[dict]}

        for multistream_tps in self._rtman.odl_client.schedule.transmission_points_by_multistream.values():
            multistream = next(iter(next(iter(multistream_tps)).partialstreams)).parent  # type: MultiStream

            # since hops (and thus multistream.links) only covers switches, we need to add the host/switch connections
            # manually. Start with the sender
            links_stream = [{
                "source": multistream.sender.node_id,
                "target": multistream.sender.get_connector().target.parent.node_id,
                "stream": multistream.name
            }]

            # each transmission point indicates a sending form a switch to a switch or a receiver.
            for tp in multistream_tps:  # type: TransmissionPoint
                connector = tp.switch_connector
                links_stream.append({
                    "source": connector.parent.node_id,
                    "target": connector.target.parent.node_id,
                    "stream": multistream.name
                })

            streams[multistream.name] = links_stream

        return json.dumps({
            "links": links_topology,
            "nodes": nodes,
            "streams": streams
        }), 200, {"Content-Type": "application/json"}

    def respond_by_urls(self, path, method):
        """
        use self._urls (see constructor) to forward this to a method and get a response.
        called by RTmanWebHandler to handle an HTTP request.

        :param str path: HTTP Path
        :param str method: HTTP Method (GET, POST, PUSH, ...)
        :return: tuple: HTTP Response Body, status code, additional HTTP Headers
        :rtype: tuple[str, int, dict[str, str]]
        """
        path = path.rstrip("/")
        # iterate over self._urls (see constructor) until we find a matching path
        for regex, method_, callback in self._urls:
            # what we want to match: method, path
            if method_ == method:
                match = re.match(regex, path)
                if match is not None:
                    # we have a match! pass regex variables as kwargs to the callback function.
                    response = callback(**match.groupdict())

                    # get some defaults for None responses of the callback function
                    if response is None:
                        return None
                    body, status, headers = response
                    if status is None:
                        status = 200
                    if headers is None:
                        headers = {"Content-Type": "text/html"}

                    # aaand return the filled-with-defaults response
                    return body, status, headers

        # this is only reached when we haven't found a match in self._urls
        return "URL not found", 404, {"Content-Type": "text/txt"}
