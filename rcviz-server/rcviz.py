# rcviz : a small recursion call graph vizualization decorator
# Copyright (c) Ran Dugal 2014
# Licensed under the GPLv2, which is available at
# http://www.gnu.org/licenses/gpl-2.0.html

import inspect
import pygraphviz as gviz
import copy
from typing import Dict, List, Any

class callgraph(object):
    '''singleton class that stores global graph data
       draw graph using pygraphviz
    '''

    _callers: Dict[int, Any] = {}  # caller_fn_id : node_data
    _counter = 1  # track call order
    _unwindcounter = 1  # track unwind order
    _step = 1 # track overall steps
    _frames: List[int] = []  # keep frame objects reference

    @staticmethod
    def reset():
        callgraph._callers = {}
        callgraph._counter = 1
        callgraph._frames = []
        callgraph._unwindcounter = 1
        callgraph._step = 1

    @staticmethod
    def get_callers():
        return callgraph._callers

    @staticmethod
    def get_counter():
        return callgraph._counter

    @staticmethod
    def get_unwindcounter():
        return callgraph._unwindcounter

    @staticmethod
    def increment():
        callgraph._counter += 1
        callgraph._step += 1

    @staticmethod
    def increment_unwind():
        callgraph._unwindcounter += 1
        callgraph._step += 1

    @staticmethod
    def get_frames():
        return callgraph._frames

    @staticmethod
    def render(show_null_returns=True):

        g = gviz.AGraph(strict=False, directed=True)

        # create nodes
        for frame_id, node in callgraph._callers.items():

            auxstr = ""
            for param, val in node.auxdata.items():
                auxstr += " | %s: %s" % (param, val)

            if not show_null_returns and node.ret is None:
                label = "{ %s(%s) %s }" % (node.fn_name, node.argstr(), auxstr)
            else:
                label = "{ %s(%s) %s | ret: %s (#%s)}" % (
                    node.fn_name, node.argstr(), auxstr, node.ret, node.ret_step)
            g.add_node(frame_id, shape='Mrecord', label=label,
                       fontsize=13, labelfontsize=13)

        # edge colors
        step = 200 / callgraph._counter
        cur_color = 0

        # create edges
        for frame_id, node in callgraph._callers.items():
            child_nodes = []
            for child_id, counter, unwind_counter in node.child_methods:
                child_nodes.append(child_id)
                cur_color = step * counter
                color = "#%2x%2x%2x" % (
                    int(cur_color), int(cur_color), int(cur_color))
                label = "%s" % (counter)
                g.add_edge(frame_id, child_id, label=label, color="black",
                           fontsize=8, labelfontsize=8, fontcolor="#999999")

            # order edges l to r
            if len(child_nodes) > 1:
                sg = g.add_subgraph(child_nodes, rank='same')
                sg.graph_attr['rank'] = 'same'
                prev_node = None
                for child_node in child_nodes:
                    if prev_node:
                        sg.add_edge(prev_node, child_node, color="#ffffff")
                    prev_node = child_node

        g.layout()
        return g.draw(prog='dot', format='svg')


class node_data(object):

    def __init__(self, _args=None, _kwargs=None, _fnname="", _ret=None, _childmethods=[]):
        self.args = _args
        self.kwargs = _kwargs
        self.fn_name = _fnname
        self.ret = _ret
        self.child_methods = _childmethods  # [ (method, gcounter) ]

        self.auxdata = {}  # user assigned track data

    def __str__(self):
        return "%s -> child_methods: %s" % (self.nodestr(), self.child_methods)

    def nodestr(self):
        return "%s = %s(%s)" % (self.ret, self.fn_name, self.argstr())

    def argstr(self):
        s_args = ",".join([str(arg) for arg in self.args])
        s_kwargs = ",".join([(str(k), str(v))
                             for (k, v) in self.kwargs.items()])
        return "%s%s" % (s_args, s_kwargs)


class viz(object):
    ''' decorator to construct the call graph with args and return values as labels '''

    def __init__(self, wrapped):
        self.wrapped = wrapped

    def __call__(self, *args, **kwargs):

        g_callers = callgraph.get_callers()
        g_frames = callgraph.get_frames()

        # find the caller frame, and add self as a child node
        caller_frame_id = None

        fullstack = inspect.stack()


        if len(fullstack) > 2 and not fullstack[2].code_context[0].startswith("  eval("):
            print(fullstack[2])
            print(fullstack[3])
            caller_frame_id = id(fullstack[2][0])

        this_frame_id = id(fullstack[0][0])

        if this_frame_id not in g_frames:
            g_frames.append(fullstack[0][0])

        if this_frame_id not in g_callers.keys():
            g_callers[this_frame_id] = node_data(
                args, kwargs, self.wrapped.__name__, None, [])

        edgeinfo = None
        if caller_frame_id:
            edgeinfo = [this_frame_id, callgraph._step]
            g_callers[caller_frame_id].child_methods.append(edgeinfo)
            callgraph.increment()

        # invoke wraped
        ret = self.wrapped(*args, **kwargs)


        g_callers[this_frame_id].ret_step = callgraph._step

        if edgeinfo:
            edgeinfo.append(callgraph.get_unwindcounter())
            callgraph.increment_unwind()

        g_callers[this_frame_id].ret = copy.deepcopy(ret)

        return ret


def visualize(function_definition, function_call):
  callgraph.reset()
  exec(function_definition, globals())
  eval(function_call)
  return callgraph.render()
