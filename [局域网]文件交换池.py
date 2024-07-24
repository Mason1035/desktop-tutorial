from flask import Flask, request, send_from_directory, redirect, url_for, render_template_string, session
import os

app = Flask(__name__)
app.secret_key = 'key'  # 用于会话加密，需替换为你自己的密钥
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 定义正确的密码
CORRECT_PASSWORD = input('设置一个密码: ')  # 替换为你想要设置的密码

# HTML模板，用于上传和管理文件
upload_page = '''
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <title>上传文件</title>
</head>
<body>
  <h1>上传新文件</h1>
  <form method=post enctype=multipart/form-data>
    <input type=file name=file>
    <input type=submit value=上传>
  </form>
  <h2>文件列表:</h2>
  <ul>
  {% for filename in files %}
    <li>
      <a href="{{ url_for('download_file', filename=filename) }}">{{ filename }}</a>
      <form method="post" action="{{ url_for('delete_file', filename=filename) }}" style="display:inline;">
        <input type="submit" value="删除">
      </form>
    </li>
  {% endfor %}
  </ul>
</body>
</html>
'''

# HTML模板，用于密码验证页面
login_page = '''
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <title>登录</title>
</head>
<body>
  <h1>请输入密码访问</h1>
  <form method=post action="{{ url_for('login') }}">
    <input type=password name=password>
    <input type=submit value=登录>
  </form>
  {% if error %}
  <p style="color:red;">{{ error }}</p>
  {% endif %}
</body>
</html>
'''


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('upload_file'))
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template_string(upload_page, files=files)


@app.route('/uploads/<filename>')
def download_file(filename):
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    return redirect(url_for('upload_file'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['password'] == CORRECT_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('upload_file'))
        else:
            error = '密码错误，请重试。'
    return render_template_string(login_page, error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    port = input('指定一个端口: ')
    app.run(host='0.0.0.0', port=port)