from flask import Flask, render_template, request, redirect, url_for, session
import os
import zipfile
import subprocess
import signal
import shutil

app = Flask(__name__)
app.secret_key = "mr_ghost_secret_key_123"

UPLOAD_FOLDER = "uploads"
MAX_RUNNING = 5
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
processes = {}

# ---------- Helper Functions ----------

def get_user_upload_path():
    user_dir = os.path.join(UPLOAD_FOLDER, session['username'])
    os.makedirs(user_dir, exist_ok=True)
    return user_dir

def extract_zip(zip_path, extract_to):
    with zipfile.ZipFile(zip_path, 'r') as z:
        z.extractall(extract_to)

def install_requirements(path):
    req = os.path.join(path, "requirements.txt")
    if os.path.exists(req):
        subprocess.call(["pip", "install", "-r", req])

def find_main_file(path):
    for f in ["main.py", "app.py", "bot.py"]:
        if os.path.exists(os.path.join(path, f)):
            return f
    return None

def start_app(app_name):
    user_dir = get_user_upload_path()
    app_dir = os.path.join(user_dir, app_name)
    zip_path = os.path.join(app_dir, "app.zip")
    extract_dir = os.path.join(app_dir, "extracted")
    log_path = os.path.join(app_dir, "logs.txt")

    if not os.path.exists(extract_dir):
        if os.path.exists(zip_path):
            extract_zip(zip_path, extract_dir)
            install_requirements(extract_dir)
        else:
            return

    main_file = find_main_file(extract_dir)
    if not main_file:
        return

    # আগের লগ ডিলিট করে নতুন লগ শুরু করা
    open(log_path, "w").close() 
    
    log = open(log_path, "a")
    p = subprocess.Popen(
        ["python3", main_file],
        cwd=extract_dir,
        stdout=log,
        stderr=log
    )
    processes[(session['username'], app_name)] = p

def stop_app(app_name):
    key = (session['username'], app_name)
    p = processes.get(key)
    if p:
        try:
            p.terminate() # সফটলি বন্ধ করা
            p.wait(timeout=2)
        except:
            p.kill() # জোর করে বন্ধ করা
        processes.pop(key, None)

# ---------- Routes ----------

@app.route("/set_theme/<int:theme_id>")
def set_theme(theme_id):
    session['theme'] = theme_id
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        if username:
            session['username'] = username 
            return redirect(url_for("index"))
    
    current_theme = session.get('theme', 1)
    
    return f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>NAYEM OFCL - Private Portal</title>
        <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@900&family=Montserrat:wght@400;700&family=Poppins:wght@300;500&display=swap" rel="stylesheet">
        
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: 'Poppins', sans-serif; height: 100vh; display: flex; flex-direction: column; align-items: center; justify-content: center; overflow: hidden; }}
            body.theme-1 {{ background: linear-gradient(-45deg, #0f0c29, #302b63, #24243e); background-size: 400% 400%; animation: grad 15s ease infinite; }}
            body.theme-2 {{ background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab); background-size: 400% 400%; animation: grad 5s ease infinite; }}
            body.theme-3 {{ background: linear-gradient(90deg, #FC466B 0%, #3F5EFB 100%); background-size: 400% 400%; animation: grad 3s linear infinite; }}
            body.theme-4 {{ background: radial-gradient(circle, #1e3c72, #2a5298); animation: pulse 4s infinite; }}
            body.theme-5 {{ background: linear-gradient(-45deg, #f093fb 0%, #f5576c 100%); background-size: 400% 400%; animation: grad 8s ease-in-out infinite; }}
            body.theme-6 {{ background: linear-gradient(to right, #000000, #434343); background-size: 400% 400%; animation: grad 10s infinite; }}
            body.theme-7 {{ background: linear-gradient(-45deg, #00dbde 0%, #fc00ff 100%); background-size: 400% 400%; animation: grad 2s ease infinite; }}
            body.theme-8 {{ background: linear-gradient(45deg, #85FFBD 0%, #FFFB7D 100%); background-size: 400% 400%; animation: grad 12s ease infinite; }}
            body.theme-9 {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); background-size: 400% 400%; animation: grad 7s infinite alternate; }}
            body.theme-10 {{ background: linear-gradient(-45deg, #ff0000, #ffff00, #00ff00, #00ffff, #0000ff, #ff00ff); background-size: 600% 600%; animation: grad 4s linear infinite; }}

            @keyframes grad {{
                0% {{ background-position: 0% 50%; }}
                50% {{ background-position: 100% 50%; }}
                100% {{ background-position: 0% 50%; }}
            }}
            @keyframes pulse {{
                0% {{ transform: scale(1); }}
                50% {{ transform: scale(1.05); }}
                100% {{ transform: scale(1); }}
            }}

            .theme-switcher {{
                position: absolute; bottom: 20px; display: flex; gap: 10px;
                background: rgba(255,255,255,0.1); padding: 10px; border-radius: 50px;
                backdrop-filter: blur(5px); z-index: 100; border: 1px solid rgba(255,255,255,0.2);
            }}
            .theme-btn {{ width: 25px; height: 25px; border-radius: 50%; border: 2px solid #fff; cursor: pointer; transition: 0.3s; }}
            .theme-btn:hover {{ transform: scale(1.2); }}

            .header-title {{ position: absolute; top: 10%; text-align: center; width: 100%; }}
            .jubayer-text {{
                font-family: 'Orbitron', sans-serif;
                font-size: clamp(40px, 8vw, 100px);
                font-weight: 900; text-transform: uppercase;
                letter-spacing: clamp(10px, 2vw, 30px);
                background: linear-gradient(to bottom, #ffffff, #00d2ff);
                -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                filter: drop-shadow(0 0 15px rgba(0, 210, 255, 0.5));
                animation: floating 3s ease-in-out infinite; user-select: none;
            }}

            @keyframes floating {{
                0%, 100% {{ transform: translateY(0); opacity: 0.8; }}
                50% {{ transform: translateY(-15px); opacity: 1; }}
            }}

            .login-box {{
                background: rgba(255, 255, 255, 0.08); padding: 40px; border-radius: 25px;
                border: 1px solid rgba(255, 255, 255, 0.2); box-shadow: 0 25px 50px rgba(0, 0, 0, 0.3);
                backdrop-filter: blur(15px); width: 90%; max-width: 380px; text-align: center; z-index: 10;
            }}

            h2 {{ 
                font-family: 'Montserrat', sans-serif;
                color: #fff; margin-bottom: 30px; font-size: 14px; 
                letter-spacing: 4px; text-transform: uppercase; opacity: 0.8; 
            }}
            
            input[type="text"] {{
                font-family: 'Poppins', sans-serif;
                width: 100%; padding: 15px; margin-bottom: 25px;
                background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 12px; color: #fff; outline: none; text-align: center;
            }}

            button {{
                font-family: 'Montserrat', sans-serif;
                width: 100%; padding: 15px; background: #00d2ff;
                border: none; border-radius: 12px; color: #000;
                font-weight: bold; cursor: pointer; transition: 0.4s;
                text-transform: uppercase; letter-spacing: 2px;
            }}
            button:hover {{ background: #fff; box-shadow: 0 0 25px rgba(0, 210, 255, 0.6); transform: translateY(-2px); }}
        </style>
    </head>
    <body class="theme-{current_theme}">
        <div class="header-title"><h1 class="jubayer-text">NAYEM OFCL</h1></div>
        <div class="login-box">
            <h2>NM LODGING</h2>
            <form method="post">
                <input type="text" name="username" placeholder="ENTER SYSTEM KEY" required>
                <button type="submit">Access System</button>
            </form>
        </div>

        <div class="theme-switcher">
            <div class="theme-btn" style="background:#0f0c29" onclick="location.href='/set_theme/1'"></div>
            <div class="theme-btn" style="background:#ee7752" onclick="location.href='/set_theme/2'"></div>
            <div class="theme-btn" style="background:#FC466B" onclick="location.href='/set_theme/3'"></div>
            <div class="theme-btn" style="background:#1e3c72" onclick="location.href='/set_theme/4'"></div>
            <div class="theme-btn" style="background:#f093fb" onclick="location.href='/set_theme/5'"></div>
            <div class="theme-btn" style="background:#000000" onclick="location.href='/set_theme/6'"></div>
            <div class="theme-btn" style="background:#00dbde" onclick="location.href='/set_theme/7'"></div>
            <div class="theme-btn" style="background:#85FFBD" onclick="location.href='/set_theme/8'"></div>
            <div class="theme-btn" style="background:#667eea" onclick="location.href='/set_theme/9'"></div>
            <div class="theme-btn" style="background:red" onclick="location.href='/set_theme/10'"></div>
        </div>
    </body>
    </html>
    '''

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/", methods=["GET", "POST"])
def index():
    if 'username' not in session:
        return redirect(url_for("login"))

    user_dir = get_user_upload_path()

    if request.method == "POST":
        file = request.files.get("file")
        if file and file.filename.endswith(".zip"):
            app_name = file.filename.replace(".zip", "")
            app_dir = os.path.join(user_dir, app_name)
            os.makedirs(app_dir, exist_ok=True)
            file.save(os.path.join(app_dir, "app.zip"))

    apps = []
    if os.path.exists(user_dir):
        for name in os.listdir(user_dir):
            app_dir = os.path.join(user_dir, name)
            if not os.path.isdir(app_dir): continue
            
            # মেমোরিতে প্রসেস আছে কি না আর পোলিং ঠিক আছে কি না চেক করা
            p = processes.get((session['username'], name))
            is_running = False
            if p:
                if p.poll() is None:
                    is_running = True
                else:
                    processes.pop((session['username'], name), None)

            apps.append({
                "name": name,
                "running": is_running
            })

    return render_template("index.html", apps=apps)

@app.route("/get_log/<name>")
def get_log(name):
    if 'username' not in session: return "Unauthorized", 401
    user_dir = get_user_upload_path()
    log_file = os.path.join(user_dir, name, "logs.txt")
    
    # প্রসেস স্ট্যাটাস চেক
    p = processes.get((session['username'], name))
    running_status = "RUNNING" if (p and p.poll() is None) else "OFFLINE"

    log_data = "System waiting for execution..."
    if os.path.exists(log_file):
        with open(log_file, "r", errors="ignore") as f:
            log_data = f.read()[-5000:] # লগের সাইজ বাড়িয়ে ৫০০০ করা হলো

    import json
    return json.dumps({"status": running_status, "log": log_data})

@app.route("/run/<name>")
def run(name):
    if 'username' not in session: return redirect(url_for("login"))
    key = (session['username'], name)
    if key not in processes or processes[key].poll() is not None:
        if len(processes) < MAX_RUNNING:
            start_app(name)
    return redirect(url_for("index"))

@app.route("/stop/<name>")
def stop(name):
    if 'username' not in session: return redirect(url_for("login"))
    stop_app(name)
    return redirect(url_for("index"))

@app.route("/restart/<name>")
def restart(name):
    if 'username' not in session: return redirect(url_for("login"))
    stop_app(name)
    start_app(name)
    return redirect(url_for("index"))

@app.route("/delete/<name>")
def delete(name):
    if 'username' not in session: return redirect(url_for("login"))
    stop_app(name)
    user_dir = get_user_upload_path()
    app_dir = os.path.join(user_dir, name)
    if os.path.exists(app_dir):
        shutil.rmtree(app_dir)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8090)
