from flask import Flask, render_template, request
import json
import boto3
from werkzeug.middleware.proxy_fix import ProxyFix


app = Flask(__name__)
app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)

@app.route("/")
def index():
    return "<h1 style='color:blue'> A very simple Flask server!</h1>"

@app.route("/")
def index():
    return render_template('index.html')

@app.route('/sign_s3/')
def sign_s3():
  S3_BUCKET = 'dogguesser'

  file_name = request.args.get('file_name')
  print(f'file name sign s3 {file_name}')
  file_type = request.args.get('file_type')
  print("initiating boto client")
  s3 = boto3.client('s3')
  print("attempting to presign post")

  presigned_post = s3.generate_presigned_post(
    Bucket = S3_BUCKET,
    Key = file_name,
    Fields = {"acl": "public-read", "Content-Type": file_type},
    Conditions = [
      {"acl": "public-read"},
      {"Content-Type": file_type}
    ],
    ExpiresIn = 3600
  )
  print(f'presigned post {presigned_post}')
  url = 'https://%s.s3.amazonaws.com/%s' % (S3_BUCKET, file_name)
  print(f'new url is {url}')
  return json.dumps({
    'data': presigned_post,
    'url': url
  })
  

# def main():
#    app.run(debug=False)

# if __name__ ==  '__main__':
#    main()
if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080, url_scheme='https')