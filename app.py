from flask import Flask,flash,render_template, request, redirect, url_for,make_response,jsonify
import boto3
from boto3.s3.transfer import TransferConfig
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.utils import secure_filename
import logging
from guess_dog import guess_dog
import time
import os
from threading import Thread
from queue import Queue


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = '/app/static'

logging.basicConfig(level=logging.WARNING)
application = Flask(__name__)
application.wsgi_app = ProxyFix(
    application.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)
application.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
application.config['SESSION_TYPE'] = 'filesystem'
application.secret_key="anystringhere"

def get_time():
    return str(time.time_ns())

def upload_file_to_s3(file):
    file_ext = str(file.filename).split(".")[1]
    curr_time = get_time()
    new_file_name = curr_time + "." + file_ext
    # filename = secure_filename(file.filename)
    config = TransferConfig(multipart_threshold=1024*250, max_concurrency=10, multipart_chunksize=1024*250, use_threads=True)
    s3 = boto3.client('s3')
    try:
        print(f'attemtpting upload...')
        s3.upload_fileobj(
            file,
            'dogguesser',
            new_file_name,
            ExtraArgs={
                "ACL": "public-read",
                "ContentType": file.content_type
            },
            Config=config
        )
    except Exception as e:
        print(f'reached exception in upload')
        application.logger.warning(f'Something Happened: {e}')

    print(f'returning success')
    return "success"

def wrapper(func, arg, queue):
     queue.put(func(arg))

@application.route("/")
def index():
    return render_template('index.html', guess='N/A', visibility="hidden")

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def provide_dog_guess(guess: dict):
    return jsonify(guess)

@application.route("/change_label", methods=["POST"])
def change_label():
    if 'user_file' not in request.files:
        application.logger.warning(f'uh oh')
        flash('No user_file key in request.files')
        return redirect(url_for('index'))
    file = request.files['user_file']

    if file.filename == '':
        application.logger.warning(f'oh no')
        flash('No selected file')
        return redirect(url_for('index'))
    if file and allowed_file(file.filename):
        q1, q2 = Queue(), Queue()
        # output = upload_file_to_s3(file)
        print(f'starting first thread')
        Thread(target=wrapper, args=(upload_file_to_s3, file, q1)).start() 
        print(f'starting second thread')
        Thread(target=wrapper, args=(guess_dog, file, q2)).start()
        output = q1.get()
        dog_guessed = q2.get()
        return jsonify({"guess": dog_guessed, "visibility": "visible"})
    return jsonify({"guess": "None", "visibility": "visible"})



if __name__ == "__main__":
    # application.run()
    # application.run(port='8000')
    application.run(host='0.0.0.0', port='8000')
    #   application.run(host='0.0.0.0', port='8080', debug=True)