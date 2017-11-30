from flask import Flask, request, Response
import json
import os
import nltk_tools
app = Flask(__name__)

@app.route('/algorithms')
def request_algorithms():
        rtn = Response(json.dumps(nltk_tools.get_algorithms()))
        rtn.headers['Access-Control-Allow-Origin'] = '*'
        return rtn

@app.route('/file=<file>')
def request_file(file):
        rtn = Response(json.dumps(json.load(open(os.path.join(os.path.join(os.getcwd(), 'downloaded_pages'), file), 'r'))))
        rtn.headers['Access-Control-Allow-Origin'] = '*'
        return rtn

@app.route('/files')
def request_files():
        files = []
        for file in os.listdir('downloaded_pages'):
                if not os.path.isdir(os.path.join('downloaded_pages', file)):
                        files.append(file)
        rtn = Response(json.dumps(files))
        rtn.headers['Access-Control-Allow-Origin'] = '*'
        return rtn

@app.route('/compare/votes')
def requestCompareVotes():
        rtn = Response(json.dumps(nltk_tools.get_votes_comparison(json.loads(request.args.get('file')), request.args.get('algorithms').split(','), request.args.get('algorithm'))))
        rtn.headers['Access-Control-Allow-Origin'] = '*'
        return rtn

@app.route('/compare/algorithms')
def requestCompareAlgorithms():
        rtn = Response(json.dumps(nltk_tools.get_algorithms_comparison(json.loads(request.args.get('file')), request.args.get('algorithms').split(','))))
        rtn.headers['Access-Control-Allow-Origin'] = '*'
        return rtn

if __name__ == '__main__':
        app.run()
