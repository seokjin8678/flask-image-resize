import uuid
from io import BytesIO
from PIL import Image
from flask import Flask, request, redirect, render_template, Response, session, send_file
import requests

app = Flask(__name__)
app.secret_key = uuid.uuid4().__str__()
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB


@app.before_request
def check_user_logged_in():
    if request.path in ['/login']:
        return

    if 'username' not in session:
        return redirect('/login')


@app.get('/')
def index():
    return render_template('index.html')


@app.get('/login')
def login_view():
    return render_template('login.html')


@app.post('/login')
def login():
    username = request.form['username']
    password = request.form['password']
    response = requests.post("https://festago.org/admin/api/v1/auth/login",
                             json={'username': username, 'password': password})
    if response.status_code == 200:
        session['username'] = username
        return redirect('/')
    return redirect('/login')


@app.post('/resize-fixed')
def resize_fixed():
    file = request.files['image']
    width = int(request.form['width'])
    height = int(request.form['height'])
    img = Image.open(file.stream)
    resize_img = img.resize((width, height))

    output_stream = BytesIO()
    resize_img.save(output_stream, format=img.format)
    output_stream.seek(0)

    return send_file(output_stream, mimetype=file.mimetype, as_attachment=True, download_name=f'new_{file.filename}')


@app.post('/resize-ratio')
def resize_ratio():
    file = request.files['image']
    ratio = int(request.form['ratio'])
    img = Image.open(file.stream)
    original_width, original_height = img.size

    new_width = int(original_width * (ratio / 100))
    new_height = int(original_height * (ratio / 100))
    resize_img = img.resize((new_width, new_height))

    output_stream = BytesIO()
    resize_img.save(output_stream, format=img.format)
    output_stream.seek(0)

    return send_file(output_stream, mimetype=file.mimetype, as_attachment=True, download_name=f'new_{file.filename}')


@app.post('/convert-webp')
def convert():
    file = request.files['image']
    img = Image.open(file.stream)
    img = img.convert('RGB')

    output_stream = BytesIO()
    img.save(output_stream, 'webp', optimize=True, quality=85)
    output_stream.seek(0)

    return send_file(output_stream, mimetype='image/webp', as_attachment=True, download_name=f'{file.filename}.webp')


if __name__ == '__main__':
    app.run()
