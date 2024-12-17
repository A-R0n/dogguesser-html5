from flask import Flask, flash, render_template, request, redirect, url_for, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix
import logging
from guess_dog import guess_dog
from upload_file_to_s3 import upload_file_to_s3
from threading import Thread
import toml
import os
from multiprocessing import Process
import io
import shutil

logging.basicConfig(level=logging.WARNING)
application = Flask(__name__)
application.wsgi_app = ProxyFix(
    application.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)

# p ='config.toml'
p ="/home/ec2-user/app/config.toml"
with open(p, "r") as f:
    config = toml.load(f)

application.config.from_object(config)
application.config.secret_key = os.urandom(24)


def copy_stream(input_stream):
    buffer = io.BytesIO()  # Or io.StringIO() for text data
    shutil.copyfileobj(input_stream, buffer)
    buffer.seek(0)  # Reset the buffer position to the beginning
    return buffer


def wrapper(func, arg, queue):
     queue.put(func(arg))

@application.route("/")
def index():
    return render_template('index.html', guess='N/A', visibility="hidden")

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in config['app']['allowed_extensions']

def provide_dog_guess(guess: dict):
    return jsonify(guess)

def runInParallel(*fns):
    proc = []
    for fn in fns:
        p = Process(target=fn)
        p.start()
        proc.append(p)
    for p in proc:
        p.join()

@application.route("/change_label", methods=["POST"])
def change_label():
    if 'user_file' not in request.files:
        application.logger.warning(f'uh oh')
        flash('No user_file key in request.files')
        return redirect(url_for('index'))
    file = request.files['user_file']
    filename = file.filename
    file.save(filename)

    if file.filename == '':
        application.logger.warning(f'oh no')
        flash('No selected file')
        return redirect(url_for('index'))


    if file and allowed_file(file.filename):
        with open(f'{filename}', 'rb') as input_file:
            copy = copy_stream(input_file)

        file2 = copy.read()
        thread = Thread(target=upload_file_to_s3, args=(file2,))
        dog_guessed = guess_dog(file)
        print(f'starting thread')
        thread.start()
        print(f'returning json')
        return jsonify({"guess": dog_guessed, "visibility": "visible"})
    return jsonify({"guess": "None", "visibility": "visible"})



if __name__ == "__main__":
    application.run(host=config['app']['host'], port=config['app']['port'])
    # application.run(host=config['app']['host'], port=config['app']['port'], debug=True)
