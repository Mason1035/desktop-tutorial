from flask import Flask, request, send_from_directory, redirect, url_for, render_template_string, session, send_file
import os
import hashlib
import time
import sqlite3
import uuid
import sys
from io import BytesIO
import qrcode
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)

# 上传目录 & 大小限制
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024 * 1024  # 100GB

# 从环境变量或交互获取密码
CORRECT_PASSWORD = os.environ.get('FILE_MANAGER_PASSWORD')
if not CORRECT_PASSWORD and not getattr(sys, 'frozen', False):
    CORRECT_PASSWORD = input('设置一个密码: ')
    if not CORRECT_PASSWORD:
        print("错误：密码不能为空！")
        sys.exit(1)

user_port = input('设置一个端口(例如“8080”): ')

# 初始化数据库
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

# 计算 MD5
def get_md5(filepath):
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

# 格式化文件大小
def format_size(bytes_size):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} TB"

# 模板：带二维码的上传页面
upload_html = """
<!doctype html>
<html lang='zh-CN'>
<head>
  <meta charset='UTF-8'>
  <title>文件交换池</title>
  <style>
    body { font-family: Arial, sans-serif; padding: 20px; background: #f4f4f4; }
    .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
    h1 { margin: 0; color: #333; }
    .logout-container form { display: inline; }
    .breadcrumb { margin-bottom: 10px; color: #555; }
    .breadcrumb a { color: #007bff; text-decoration: none; }
    .breadcrumb a:hover { text-decoration: underline; }
    .controls { margin-bottom: 20px; }
    .controls .btn, .controls .btn-danger { margin-right: 10px; }

    .layout { display: flex; }
    .main { flex: 1; }
    .sidebar { width: 300px; margin-left: 20px; }

    .panel { background: #fff; border: 1px solid #ddd; border-radius: 5px; margin-bottom: 20px; }
    .panel h2 { margin: 0; padding: 10px 15px; background: #f7f7f7; font-size: 16px; border-bottom: 1px solid #ddd; }
    .panel .content { padding: 10px 15px; font-size: 14px; }
    .panel .content p, .panel .content li { margin: 5px 0; }
    .panel .content ul { padding-left: 20px; }

    table { border-collapse: collapse; width: 100%; background: #fff; }
    th, td { border: 1px solid #ccc; padding: 12px; text-align: center; }
    th { background-color: #eee; }
    .btn { padding: 5px 12px; background-color: #007bff; color: #fff; border: none; border-radius: 5px; cursor: pointer; }
    .btn:hover { background-color: #0056b3; }
    .btn-danger { background-color: #dc3545; }
    .btn-danger:hover { background-color: #bd2130; }

    #drop-zone { border: 2px dashed #999; border-radius: 10px; padding: 20px; text-align: center; color: #666; background: #fff; }
    #drop-zone.hover { background: #e8f0fe; }
    #drop-zone .btn { margin-top: 10px; }

    #progress-container { margin-top: 20px; }
    .progress-bar { width: 0%; height: 20px; background-color: #28a745; text-align: center; color: #fff; font-size: 12px; border-radius: 4px; margin-top: 4px; }
  </style>
</head>
<body>
  <div class="header">
    <h1>文件管理中心</h1>
    <div class="logout-container">
      <form method="post" action="{{ url_for('logout') }}">
        <input type="submit" class="btn" value="登出">
      </form>
    </div>
  </div>

  <div class="breadcrumb">
    位置：<a href="{{ url_for('upload_file') }}">根目录</a>
  </div>

  <div class="controls">
    <form method="post" action="{{ url_for('reset_all_files') }}" onsubmit="return confirm('⚠️ 确定要删除所有文件？此操作不可恢复！');" style="display:inline-block;">
      <input type="submit" class="btn btn-danger" value="⚠️ 重置所有文件">
    </form>
  </div>

  <div class="layout">
    <div class="main">
      <div id="drop-zone">
        拖拽文件或文件夹到这里上传<br>
        <button id="select-files-btn" class="btn">选择文件</button>
        <button id="select-folder-btn" class="btn">选择文件夹</button>
        <input type="file" id="file-input" multiple style="display:none">
        <input type="file" id="folder-input" webkitdirectory directory mozdirectory multiple style="display:none">
      </div>
      <div id="progress-container"></div>

      {% if files %}
      <table>
        <thead>
          <tr>
            <th>文件名</th>
            <th>二维码</th>
            <th>大小</th>
            <th>上传时间</th>
            <th>MD5</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          {% for file in files %}
          <tr>
            <td><a href="{{ url_for('download_file', file_id=file.id) }}">{{ file.real_name }}</a></td>
            <td><img src="{{ url_for('serve_qrcode', file_id=file.id) }}" alt="二维码" width="80" height="80"></td>
            <td>{{ file.size }}</td>
            <td>{{ file.upload_time }}</td>
            <td style="font-family: monospace;">{{ file.md5 }}</td>
            <td>
              <form method="post" action="{{ url_for('delete_file', file_id=file.id) }}" onsubmit="return confirm('确定删除 {{ file.real_name }}？');">
                <input type="submit" class="btn btn-danger" value="删除">
              </form>
            </td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
      {% else %}
      <p>暂无文件</p>
      {% endif %}
    </div>

    <div class="sidebar">
      <div class="panel">
        <h2>下载源码</h2>
        <div class="content">
          <a target="_blank" href="https://github.com/Mason1035/desktop-tutorial">源码下载_文件交换池2.0</a>
        </div>
      </div>
      <div class="panel">
        <h2>依赖库</h2>
        <div class="content">
          <ul>
            <li>flask</li>
            <li>qrcode</li>
            <li>werkzeug</li>
          </ul>
        </div>
      </div>
    </div>
  </div>

<script>
  const dropZone = document.getElementById('drop-zone');
  const fileInput = document.getElementById('file-input');
  const folderInput = document.getElementById('folder-input');
  const progressContainer = document.getElementById('progress-container');
  const selectFilesBtn = document.getElementById('select-files-btn');
  const selectFolderBtn = document.getElementById('select-folder-btn');

  selectFilesBtn.addEventListener('click', () => fileInput.click());
  selectFolderBtn.addEventListener('click', () => folderInput.click());

  ['dragover','dragenter'].forEach(evt => {
    dropZone.addEventListener(evt, e => { e.preventDefault(); dropZone.classList.add('hover'); });
  });
  ['dragleave','drop'].forEach(evt => {
    dropZone.addEventListener(evt, e => { e.preventDefault(); dropZone.classList.remove('hover'); });
  });
  dropZone.addEventListener('drop', e => { fileInput.files = e.dataTransfer.files; folderInput.value = null; uploadFiles(); });

  fileInput.addEventListener('change', uploadFiles);
  folderInput.addEventListener('change', uploadFiles);

  function uploadFiles() {
    const files = [...(fileInput.files||[]), ...(folderInput.files||[])];
    if (!files.length) return alert("请选择文件或文件夹");
    progressContainer.innerHTML = '';
    files.forEach((f,i) => {
      const formData = new FormData();
      formData.append('file', f);
      const bar = document.createElement('div'); bar.className='progress-bar'; bar.innerText=`上传中: ${f.name}`;
      progressContainer.appendChild(bar);
      const xhr = new XMLHttpRequest(); xhr.open('POST','/ajax-upload');
      xhr.upload.onprogress = e => {
        if (e.lengthComputable) {
          const pct = (e.loaded/e.total)*100;
          bar.style.width=pct+'%'; bar.innerText=`${f.name} ${pct.toFixed(0)}%`;
        }
      };
      xhr.onload = () => {
        if (xhr.status===200) { bar.innerText=`✅ 完成: ${f.name}`; bar.style.background='#17a2b8'; }
        else { bar.innerText=`❌ 失败: ${f.name}`; bar.style.background='#dc3545'; }
        if (i===files.length-1) setTimeout(()=>location.reload(),800);
      };
      xhr.onerror = () => { bar.innerText=`❌ 网络错误: ${f.name}`; bar.style.background='#dc3545'; };
      xhr.send(formData);
    });
    fileInput.value=folderInput.value='';
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

@app.route('/public/<file_id>')
def public_download(file_id):
    conn = sqlite3.connect('file_manager.db')
    c = conn.cursor()
    c.execute("SELECT real_name, stored_name FROM files WHERE id=?", (file_id,))
    file = c.fetchone()
    conn.close()

    if not file:
        return "文件不存在", 404

    return send_from_directory(
        app.config['UPLOAD_FOLDER'],
        file[1],
        as_attachment=True,
        download_name=file[0]
    )

# -------------------------
# 原始受保护下载接口
# -------------------------
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
            download_name=file[0]
        )
    return "文件不存在", 404

# -------------------------
# 生成二维码，指向公开下载
# -------------------------
@app.route('/qrcode/<file_id>')
def serve_qrcode(file_id):
    # 二维码链接改为 /public/<file_id>
    download_url = url_for('public_download', file_id=file_id, _external=True)
    img = qrcode.make(download_url)
    buf = BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return send_file(buf, mimetype='image/png')

# --------- 其余现有路由 ---------

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

    file_id = str(uuid.uuid4())
    stored_name = file_id + os.path.splitext(secure_filename(file.filename))[1]
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], stored_name)
    file.save(file_path)

    file_size = os.path.getsize(file_path)
    file_md5 = get_md5(file_path)

    conn = sqlite3.connect('file_manager.db')
    c = conn.cursor()
    c.execute("INSERT INTO files VALUES (?, ?, ?, ?, ?, ?)",
              (file_id, file.filename, stored_name, file_size, file_md5, time.time()))
    conn.commit()
    conn.close()

    return 'OK', 200

@app.route('/delete/<file_id>', methods=['POST'])
def delete_file(file_id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect('file_manager.db')
    c = conn.cursor()
    c.execute("SELECT stored_name FROM files WHERE id=?", (file_id,))
    result = c.fetchone()
    if result:
        path = os.path.join(app.config['UPLOAD_FOLDER'], result[0])
        if os.path.exists(path):
            os.remove(path)
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
    c.execute("SELECT stored_name FROM files")
    for (name,) in c.fetchall():
        p = os.path.join(app.config['UPLOAD_FOLDER'], name)
        if os.path.exists(p):
            os.remove(p)
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
    print(f"文件管理服务启动在 {host}:{port}")
    print(f"上传目录: {os.path.abspath(UPLOAD_FOLDER)}")
    print(f"数据库文件: {os.path.abspath('file_manager.db')}")
    app.run(host=host, port=port)


