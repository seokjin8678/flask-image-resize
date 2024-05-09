import datetime
import uuid
from io import BytesIO
import requests
from PIL import Image
from flask import Flask, request, redirect, render_template, session, send_file

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
    img.save(output_stream, format='webp', optimize=True, quality=85)
    output_stream.seek(0)

    return send_file(output_stream, mimetype='image/webp', as_attachment=True, download_name=f'{file.filename}.webp')


@app.post('/combine-9')
def combine_9():
    images = [Image.open(request.files.get(f'image{i}')) for i in range(9)]
    new_image = combine_images(images)

    output_stream = BytesIO()
    new_image.save(output_stream, format="webp")
    output_stream.seek(0)

    return send_file(output_stream, mimetype='image/webp', as_attachment=True,
                     download_name=f'combine12_{datetime.datetime.now()}.webp')


def combine_images(images):
    width, height = images[0].size
    total_width = width * 3
    print(len(images) // 3)
    total_height = height * (len(images) // 3)
    new_image = Image.new('RGB', (total_width, total_height), (0, 0, 0))
    i, j = 0, 0
    for image in images:
        new_image.paste(image, box=(i * width, j * height))
        i += 1
        if i >= 3:
            i = 0
            j += 1
    return new_image


@app.post('/combine-12')
def combine_12():
    images = [Image.open(request.files.get(f'image{i}')) for i in range(12)]
    new_image = combine_images(images)

    output_stream = BytesIO()
    new_image.save(output_stream, format="webp")
    output_stream.seek(0)

    return send_file(output_stream, mimetype='image/webp', as_attachment=True,
                     download_name=f'combine12_{datetime.datetime.now()}.webp')


if __name__ == '__main__':
    app.run()
