import uuid
from io import BytesIO
from PIL import Image
from flask import Flask, request, redirect, render_template, Response, session

app = Flask(__name__)
app.secret_key = uuid.uuid4().__str__()

users = {
    'festago': 'vptmxkrh'
}


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
    if username in users and users[username] == password:
        session['username'] = username
        return redirect('/')
    return redirect('/login')


@app.post('/resize')
def resize():
    file = request.files['image']
    width = int(request.form['width'])
    height = int(request.form['height'])
    img = Image.open(file.stream)
    resize_img = img.resize((width, height))

    output_stream = BytesIO()
    resize_img.save(output_stream, format=img.format)

    response = Response(
        output_stream.getvalue(),
        mimetype=file.mimetype,
        content_type='application/octet-stream',
    )
    response.headers["Content-Disposition"] = f"attachment; filename=new_{file.filename}"
    return response


if __name__ == '__main__':
    app.run()
