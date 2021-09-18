from flask import Flask, request, jsonify, render_template
from rcviz import visualize

app = Flask(__name__)

@app.route('/')
def app_index():
  return render_template('index.html')

@app.route('/visualize', methods=['GET'])
def app_visualize():
  function_definition = "@viz\n" + request.args.get('function_definition')
  function_call = request.args.get('function_call')
  svg = visualize(function_definition, function_call)
  svg = svg.decode("utf-8")
  return render_template('graph.html', svg=svg)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
