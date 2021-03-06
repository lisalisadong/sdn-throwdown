# This file provided by Facebook is for non-commercial testing and evaluation
# purposes only. Facebook reserves all rights not expressly granted.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# FACEBOOK BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import json
import os
import sys
import threading
import time
sys.path.insert(0, 'backend')
from states import NetworkStateService
from flask import Flask, Response, request

app = Flask(__name__, static_url_path='', static_folder='public')
app.add_url_rule('/', 'root', lambda: app.send_static_file('index.html'))

@app.route('/api/comments', methods=['GET', 'POST'])
def comments_handler():

    with open('database/comments.json', 'r') as file:
        comments = json.loads(file.read())

    if request.method == 'POST':
        newComment = request.form.to_dict()
        newComment['id'] = int(time.time() * 1000)
        comments.append(newComment)

        with open('database/comments.json', 'w') as file:
            file.write(json.dumps(comments, indent=4, separators=(',', ': ')))

    return Response(json.dumps(comments), mimetype='application/json', headers={'Cache-Control': 'no-cache', 'Access-Control-Allow-Origin': '*'})

@app.route('/api/sqls', methods=['GET', 'POST'])
def sqls_handler():

    with open('database/sqls.json', 'r') as file:
        sqls = json.loads(file.read())

    if request.method == 'POST':
        newSql = request.form.to_dict()
        newSql['id'] = int(time.time() * 1000)
        sqls.append(newSql)

        with open('database/sqls.json', 'w') as file:
            file.write(json.dumps(sqls, indent=4, separators=(',', ': ')))

    return Response(json.dumps(sqls), mimetype='application/json', headers={'Cache-Control': 'no-cache', 'Access-Control-Allow-Origin': '*'})


@app.route('/api/graphs', methods=['GET', 'POST'])
def graphs_handler():

    with open('database/graphs.json', 'r') as file:
        graphs = json.loads(file.read())

    if request.method == 'POST':
        newGraph = request.form.to_dict()
        newGraph['id'] = int(time.time() * 1000)
        graphs.append(newGraph)

        with open('database/graphs.json', 'w') as file:
            file.write(json.dumps(graphs, indent=4, separators=(',', ': ')))

    return Response(json.dumps(graphs), mimetype='application/json', headers={'Cache-Control': 'no-cache', 'Access-Control-Allow-Origin': '*'})


@app.route('/api/sql', methods=['GET'])
def sql_handler():
    query_string = request.args.get('query');
    query_type = request.args.get('type');

    print "evaluating: " + query_string;
    nss = NetworkStateService("database/states.db");
    data = nss.query(query_string, query_type);
    nss.close();
    #result = {};
    #result['time'] = 1;

    return Response(json.dumps(data), mimetype='application/json', headers={'Cache-Control': 'no-cache', 'Access-Control-Allow-Origin': '*'})


@app.route('/api/topology', methods=['GET'])
def get_topology():
    with open('database/topology.json', 'r') as file:
        topology = json.loads(file.read())

    return Response(json.dumps(topology), mimetype='application/json', headers={'Cache-Control': 'no-cache', 'Access-Control-Allow-Origin': '*'})

if __name__ == '__main__':
    app.run(host= '0.0.0.0', port=int(os.environ.get("PORT",3000)), debug=True)



