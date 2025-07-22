from flask import Flask, request, send_from_directory, redirect, url_for, render_template_string, session
import os
import hashlib
import time
import sqlite3
import uuid
import sys
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024 * 1024  # 限制100GB


# 数据库初始化
def init_db():
    conn = sqlite3.connect('file_manager.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS files
                 (id TEXT PRIMARY KEY,
                  real_name TEXT,
                  stored_name TEXT,
                  size INTEGER,
                  md5 TEXT,
                  upload_time TIMESTAMP)''')
    conn.commit()
    conn.close()


init_db()

# 从环境变量获取密码
CORRECT_PASSWORD = os.environ.get('FILE_MANAGER_PASSWORD')
if not CORRECT_PASSWORD and not getattr(sys, 'frozen', False):
    CORRECT_PASSWORD = input('设置一个密码: ')
    if not CORRECT_PASSWORD:
        print("错误：密码不能为空！")
        sys.exit(1)

user_port = input('设置一个端口(例如“8080”): ')

upload_html = """
<!doctype html>
<html lang='zh-CN'>
<head>
  <meta charset='UTF-8'>
  <title>文件交换池</title>
  <style>
    body { font-family: Arial, sans-serif; padding: 40px; background: #f4f4f4; }
    h1 { color: #333; }
    table { border-collapse: collapse; width: 100%; margin-top: 20px; background: white; }
    th, td { border: 1px solid #ccc; padding: 12px; text-align: center; }
    th { background-color: #eee; }
    form { display: inline; }
    .btn { padding: 5px 12px; margin: 4px; background-color: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
    .btn:hover { background-color: #0056b3; }
    .btn-danger { background-color: #dc3545; }
    .btn-danger:hover { background-color: #bd2130; }
    #drop-zone {
      border: 2px dashed #999;
      border-radius: 10px;
      padding: 30px;
      text-align: center;
      color: #666;
      background: #fff;
      margin-top: 20px;
    }
    #progress-container {
      margin-top: 20px;
    }
    .progress-bar {
      width: 0%;
      height: 20px;
      background-color: #28a745;
      text-align: center;
      color: white;
      font-size: 12px;
      border-radius: 4px;
      margin-top: 4px;
    }
    .logout-container {
      position: absolute;
      top: 20px;
      right: 20px;
    }
  </style>
</head>
<body>
  <div class='logout-container'>
    <form method='post' action='{{ url_for("logout") }}'>
      <input type='submit' class='btn' value='登出'>
    </form>
  </div>
  <h1>文件管理中心</h1>

  <form method='post' action='{{ url_for("reset_all_files") }}' onsubmit="return confirm('⚠️ 确定要删除所有文件？此操作不可恢复！');">
    <input type='submit' class='btn btn-danger' value='⚠️ 一键重置所有文件'>
  </form>

  <div id='drop-zone'>
    拖拽文件到这里上传<br>或点击选择：
    <input type='file' id='file-input' multiple>
    <button onclick='uploadFiles()' class='btn'>上传</button>
  </div>

  <div id='progress-container'></div>

  {% if files %}
  <table>
    <thead>
      <tr>
        <th>文件名</th>
        <th>大小</th>
        <th>上传时间</th>
        <th>MD5</th>
        <th>操作</th>
      </tr>
    </thead>
    <tbody>
      {% for file in files %}
      <tr>
        <td><a href='{{ url_for("download_file", file_id=file.id) }}'>{{ file.real_name }}</a></td>
        <td>{{ file.size }}</td>
        <td>{{ file.upload_time }}</td>
        <td style='font-family: monospace;'>{{ file.md5 }}</td>
        <td>
          <form method='post' action='{{ url_for("delete_file", file_id=file.id) }}' onsubmit="return confirm('确定删除 {{ file.real_name }}？');">
            <input type='submit' class='btn btn-danger' value='删除'>
          </form>
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
  {% else %}
  <p>暂无文件</p>
  {% endif %}

<script>
  const dropZone = document.getElementById('drop-zone');
  const fileInput = document.getElementById('file-input');
  const progressContainer = document.getElementById('progress-container');

  dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.style.background = '#e8f0fe';
  });

  dropZone.addEventListener('dragleave', () => {
    dropZone.style.background = '#fff';
  });

  dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.style.background = '#fff';
    fileInput.files = e.dataTransfer.files;
  });

  function uploadFiles() {
    const files = fileInput.files;
    if (!files.length) return alert("请选择文件");

    // 清除之前的进度条
    progressContainer.innerHTML = '';

    for (let i = 0; i < files.length; i++) {
      const formData = new FormData();
      formData.append('file', files[i]);

      const progressBar = document.createElement('div');
      progressBar.className = 'progress-bar';
      progressBar.innerText = `上传中: ${files[i].name}`;
      progressContainer.appendChild(progressBar);

      const xhr = new XMLHttpRequest();
      xhr.open('POST', '/ajax-upload', true);

      xhr.upload.onprogress = function(e) {
        if (e.lengthComputable) {
          let percent = (e.loaded / e.total) * 100;
          progressBar.style.width = percent + '%';
          progressBar.innerText = `${files[i].name} ${percent.toFixed(0)}%`;
        }
      };

      xhr.onload = function() {
        if (xhr.status === 200) {
          progressBar.innerText = `✅ 已完成: ${files[i].name}`;
          progressBar.style.backgroundColor = '#17a2b8';
          if (i === files.length - 1) {
            setTimeout(() => location.reload(), 800);
          }
        } else {
          progressBar.innerText = `❌ 上传失败: ${files[i].name}`;
          progressBar.style.backgroundColor = '#dc3545';
        }
      };

      xhr.onerror = function() {
        progressBar.innerText = `❌ 网络错误: ${files[i].name}`;
        progressBar.style.backgroundColor = '#dc3545';
      };

      xhr.send(formData);
    }
  }
</script>
</body>
</html>
"""

login_html = """
<!doctype html>
<html lang='zh-CN'>
<head>
  <meta charset='UTF-8'>
  <title>文件交换池</title>
  <style>
    body { font-family: Arial, sans-serif; background: #fafafa; padding: 100px; text-align: center; }
    input[type=password], input[type=submit] {
      padding: 10px; font-size: 16px; margin: 10px; border-radius: 5px; border: 1px solid #ccc;
    }
    input[type=submit] {
      background-color: #007bff; color: white; cursor: pointer;
    }
    input[type=submit]:hover {
      background-color: #0056b3;
    }
    p { color: red; }
    .container {
      max-width: 400px;
      margin: 0 auto;
      padding: 20px;
      background: white;
      border-radius: 10px;
      box-shadow: 0 0 10px rgba(0,0,0,0.1);
    }
  </style>
</head>
<body>
  <div class='container'>
    <h1>输入密码登陆</h1>
    <form method='post' action='{{ url_for("login") }}'>
      <input type='password' name='password' required autofocus>
      <input type='submit' value='确认'>
    </form>
    {% if error %}
      <p>{{ error }}</p>
    {% endif %}
  </div>
<div id="footer">

<p id="p2">
<a target="_blank" href="https://github.com/Mason1035/desktop-tutorial">源码下载_文件交换池2.0</a>
</p>
</div>

</body>
</html>
"""


def get_md5(filepath):
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def format_size(bytes_size):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} TB"


@app.route('/', methods=['GET'])
def upload_file():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect('file_manager.db')
    c = conn.cursor()
    c.execute("SELECT id, real_name, size, upload_time, md5 FROM files ORDER BY upload_time DESC")
    files = []
    for row in c.fetchall():
        files.append({
            'id': row[0],
            'real_name': row[1],
            'size': format_size(row[2]),
            'upload_time': datetime.fromtimestamp(row[3]).strftime('%Y-%m-%d %H:%M:%S'),
            'md5': row[4]
        })
    conn.close()

    return render_template_string(upload_html, files=files)


@app.route('/ajax-upload', methods=['POST'])
def ajax_upload():
    if 'logged_in' not in session:
        return '未登录', 403

    file = request.files.get('file')
    if not file or not file.filename:
        return '上传失败', 400

    # 生成存储文件名
    file_id = str(uuid.uuid4())
    stored_name = file_id + os.path.splitext(file.filename)[1]
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], stored_name)

    # 保存文件
    file.save(file_path)

    # 计算文件信息
    file_size = os.path.getsize(file_path)
    file_md5 = get_md5(file_path)

    # 存储到数据库
    conn = sqlite3.connect('file_manager.db')
    c = conn.cursor()
    c.execute("INSERT INTO files VALUES (?, ?, ?, ?, ?, ?)",
              (file_id, file.filename, stored_name, file_size, file_md5, time.time()))
    conn.commit()
    conn.close()

    return 'OK', 200


@app.route('/download/<file_id>')
def download_file(file_id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect('file_manager.db')
    c = conn.cursor()
    c.execute("SELECT real_name, stored_name FROM files WHERE id=?", (file_id,))
    file = c.fetchone()
    conn.close()

    if file:
        return send_from_directory(
            app.config['UPLOAD_FOLDER'],
            file[1],
            as_attachment=True,
            download_name=file[0]  # 保持原始文件名下载
        )
    return "文件不存在", 404


@app.route('/delete/<file_id>', methods=['POST'])
def delete_file(file_id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect('file_manager.db')
    c = conn.cursor()

    # 获取存储文件名
    c.execute("SELECT stored_name FROM files WHERE id=?", (file_id,))
    result = c.fetchone()

    if result:
        stored_name = result[0]
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], stored_name)

        # 删除物理文件
        if os.path.exists(file_path):
            os.remove(file_path)

        # 删除数据库记录
        c.execute("DELETE FROM files WHERE id=?", (file_id,))
        conn.commit()

    conn.close()
    return redirect(url_for('upload_file'))


@app.route('/reset', methods=['POST'])
def reset_all_files():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect('file_manager.db')
    c = conn.cursor()

    # 获取所有文件
    c.execute("SELECT stored_name FROM files")
    files = c.fetchall()

    # 删除物理文件
    for file in files:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file[0])
        if os.path.exists(file_path):
            os.remove(file_path)

    # 清空数据库
    c.execute("DELETE FROM files")
    conn.commit()
    conn.close()

    return redirect(url_for('upload_file'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if not CORRECT_PASSWORD:
        return "管理员未设置密码，请联系管理员", 500

    error = None
    if request.method == 'POST':
        if request.form['password'] == CORRECT_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('upload_file'))
        else:
            error = '密码错误，请重试。'
    return render_template_string(login_html, error=error)


@app.route('/logout', methods=['POST'])
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    port = int(os.environ.get('PORT', user_port))
    host = os.environ.get('HOST', '0.0.0.0')

    if not CORRECT_PASSWORD:
        print("错误：未设置密码！请通过环境变量 FILE_MANAGER_PASSWORD 设置")
        sys.exit(1)

    print(f"文件管理服务启动在 {host}:{port}")
    print(f"上传目录: {os.path.abspath(UPLOAD_FOLDER)}")
    print(f"数据库文件: {os.path.abspath('file_manager.db')}")
    app.run(host=host, port=port)