# recursive-visualizations

A way to visualize the call graph of recursive functions.

Uses Pyodide to run rcviz.py and then a WASM PyDot/GraphViz port to build an SVG graph.
Finally, some JavaScript adds a slider for stepping through the calls.

To run locally:

```python3 -m http.server```

To run Python tests:

```pytest```
