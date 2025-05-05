from flask import Flask, render_template, request, redirect, url_for
from opinion_engine import *

app = Flask(__name__)

board_store = {"nodes": [], "links": []}


@app.route('/')
def input_page():
    return render_template('input.html')


@app.route('/submit', methods=['POST'])
def submit():
    arg1 = request.form['user_input_1']
    arg2 = request.form['user_input_2']

    ops1 = parse_bullets(extract_opinions(arg1))
    ops2 = parse_bullets(extract_opinions(arg2))
    matches = match_opinions(ops1, ops2)

    nodes, links = build_graph(matches)

    board_store["nodes"] = nodes
    board_store["links"] = links

    return redirect(url_for('whiteboard'))


@app.route('/whiteboard')
def whiteboard():
    # retrieve data and send into template
    return render_template('whiteboard.html',
                           nodes=board_store["nodes"],
                           links=board_store["links"])


if __name__ == '__main__':
    app.run(debug=True)
