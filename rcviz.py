# rcviz : a small recursion call graph vizualization decorator
# Copyright (c) Ran Dugal 2014
# Licensed under the GPLv2, which is available at
# http://www.gnu.org/licenses/gpl-2.0.html
from time import time
import inspect
import copy
from typing import Dict, List, Any

import pydot

class TooManyFramesError(Exception):
    pass

class TooMuchTimeError(Exception):
    pass

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
    def render():
      dotgraph = pydot.Dot("rc-graph", graph_type="digraph", strict=False)
      
      # Create nodes
      for frame_id, node in callgraph._callers.items():
        aux_str = ''
        for param, val in node.auxdata.items():
          aux_str += " | %s: %s" % (param, val)
        label = "{ %s(%s) %s}" % (
                    node.fn_name, node.argstr(), aux_str)
        dotgraph.add_node(pydot.Node(frame_id, label=label, shape='Mrecord'))
      
      # Create edges
      for frame_id, node in callgraph._callers.items():
        child_nodes = []
        for child_id, counter, unwind_counter in node.child_methods:
          child_nodes.append(child_id)
          label = "(#%s)" % (counter)
          dotgraph.add_edge(pydot.Edge(frame_id, child_id, color="black", label=label))
          
        # Order edges left to right
        if len(child_nodes) > 1:
          subgraph = pydot.Subgraph(rank='same')
          prev_node = None
          for child_node in child_nodes:
            subgraph.add_node(pydot.Node(child_node))
            if prev_node:
              subgraph.add_edge(pydot.Edge(prev_node, child_node))
            prev_node = child_node
          dotgraph.add_subgraph(subgraph)
      
      parent_frame = None
      for frame_id, node in callgraph._callers.items():
        for child_id, counter, unwind_counter in node.child_methods:
          child_node = callgraph._callers.get(child_id)
          if child_node and child_node.ret is not None:
            ret_label = f'{child_node.ret} (#{child_node.ret_step})'
            dotgraph.add_edge(pydot.Edge(frame_id, child_id, dir="back", label=ret_label, color="green", headport="c"))
        if parent_frame is None:
          parent_frame = frame_id
          if node.ret is not None:
            ret_label = f'{node.ret} (#{node.ret_step})'
            dotgraph.add_node(pydot.Node(99999999, shape='Mrecord', label='Result'))
            dotgraph.add_edge(pydot.Edge(99999999, frame_id, dir="back", label=ret_label, color="Green", headport="c"))
         
      return dotgraph.to_string() 

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
        s_args = ", ".join([str(arg) for arg in self.args])
        s_kwargs = ", ".join([(str(k), str(v))
                             for (k, v) in self.kwargs.items()])
        return "%s%s" % (s_args, s_kwargs)


class viz(object):
    ''' decorator to construct the call graph with args and return values as labels '''

    def __init__(self, wrapped):
        self.wrapped = wrapped
        self.max_frames = 1000 
        self.max_time = 10 # in seconds
        self.start_time = time()

    def __call__(self, *args, **kwargs):

        g_callers = callgraph.get_callers()
        g_frames = callgraph.get_frames()

        # find the caller frame, and add self as a child node
        caller_frame_id = None

        fullstack = inspect.stack()

        this_frame_id = id(fullstack[0][0])
        if fullstack[2].function == '__call__':
          caller_frame_id = id(fullstack[2][0])

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

        if len(g_frames) > self.max_frames:
          raise TooManyFramesError(f"Encountered more than ${self.max_frames} while executing function")
        if (time() - self.start_time) > self.max_time:
          raise TooMuchTimeError(f"Took more than ${self.max_time} seconds to run function")
          
        # Invoke the wrapped
        ret = self.wrapped(*args, **kwargs)

        g_callers[this_frame_id].ret_step = callgraph._step

        if edgeinfo:
            edgeinfo.append(callgraph.get_unwindcounter())
            callgraph.increment_unwind()

        g_callers[this_frame_id].ret = copy.deepcopy(ret)

        return ret


def decorate_funcs(func_source: str):
    outlines = []
    for line in func_source.split("\n"):
        if line.startswith("def "):
            outlines.append("@viz")
        outlines.append(line)
    return "\n".join(outlines)


def visualize(function_definition, function_call):
  """Either returns generated SVG or generates an error."""
  callgraph.reset()
  function_definition=decorate_funcs(function_definition)
  exec(function_definition, globals())
  eval(function_call)
  return callgraph.render()
