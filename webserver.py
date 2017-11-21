from flask import Flask, request
import json
import os
import nltk_tools
app = Flask(__name__)

@app.route('/')
def hello_world():
        return 'Hello, World!'

@app.route('/algorithms')
def request_algorithms():
        return json.dumps(nltk_tools.get_algorithms())

@app.route('/file=<file>')
def request_file(file):
        return json.dumps(json.load(open(os.path.join(os.path.join(os.getcwd(), 'preeclampsia'), file), 'r')))

@app.route('/files')
def request_files():
        files = []
        for file in os.listdir('preeclampsia'):
                if not os.path.isdir(os.path.join('preeclampsia', file)):
                        files.append(file)
        return json.dumps(files)

@app.route('/compare/votes')
def requestCompareVotes():
        return json.dumps(nltk_tools.get_votes_comparison(json.loads(request.args.get('file')), request.args.get('algorithms').split(','), request.args.get('algorithm')))

@app.route('/compare/algorithms')
def requestCompareAlgorithms():
        return json.dumps(nltk_tools.get_algorithms_comparison(json.loads(request.args.get('file')), request.args.get('algorithms').split(',')))
                          
if __name__ == '__main__':
        app.run()
            
