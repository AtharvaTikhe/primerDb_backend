from flask import Flask, render_template, request, jsonify
from src.pick_primers.run_primer3 import GenerateP3Input


app = Flask(__name__)


@app.route('/pick_primers', methods = ['GET', 'POST'])
def send_pick_primers():
    seq_id = request.form['seq_id']
    Chr = request.form['chr']
    coords = request.form['coords']
    flanks = request.form['flanks']
    num_ret = request.form['num_ret']
    seq_target = request.form['seq_target']
    obj = GenerateP3Input(Chr, coords, flanks, seq_id, seq_target, num_ret)
    primer_pairs, full_output = obj.run_primer3()
    print(primer_pairs)
    return jsonify(primer_pairs)



@app.route('/')
def send_home_page():
    return render_template('index.html')


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8080, debug=True)
