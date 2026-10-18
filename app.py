from flask import Flask, render_template_string, request, redirect, url_for, jsonify, session
import os, subprocess, zipfile, psutil, time, shutil

app = Flask(__name__)
app.secret_key = "HiroCloud_Super_Secret_Key"

BOTS_DIR = "bots"
os.makedirs(BOTS_DIR, exist_ok=True)

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HiroCloud - Premium Bot Manager</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;700&display=swap');
        
        :root { 
            --bg: #06080f; 
            --panel: rgba(17, 24, 39, 0.7); 
            --border: rgba(55, 65, 81, 0.5); 
            --text: #f8fafc; 
            --text2: #94a3b8; 
            --primary: #6366f1; 
            --primary-hover: #4f46e5;
            --green: #10b981; 
            --red: #ef4444; 
            --purple: #8b5cf6; 
            --glass: blur(12px) saturate(180%);
        }
        
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', sans-serif; }
        
        body { 
            background-color: var(--bg); 
            background-image: 
                radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.15) 0px, transparent 50%),
                radial-gradient(at 100% 100%, rgba(139, 92, 246, 0.15) 0px, transparent 50%);
            color: var(--text); 
            display: flex; 
            flex-direction: row; 
            height: 100vh; 
            overflow: hidden; 
        }
        
        /* SIDEBAR */
        .sidebar { 
            width: 260px; 
            background: var(--panel); 
            backdrop-filter: var(--glass);
            -webkit-backdrop-filter: var(--glass);
            border-right: 1px solid var(--border); 
            display: flex; 
            flex-direction: column; 
            padding: 24px 0; 
            transition: 0.3s; 
            z-index: 10;
        }
        
        .logo { 
            font-size: 26px; 
            font-weight: 800; 
            background: linear-gradient(135deg, #818cf8, #38bdf8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            padding: 0 24px 30px; 
            display: flex; 
            align-items: center; 
            gap: 12px; 
        }
        
        .menu { list-style: none; display: flex; flex-direction: column; gap: 5px; padding: 0 12px;}
        
        .menu li { 
            padding: 14px 20px; 
            color: var(--text2); 
            cursor: pointer; 
            display: flex; 
            align-items: center; 
            gap: 14px; 
            font-weight: 600; 
            font-size: 15px; 
            border-radius: 10px;
            transition: 0.2s; 
        }
        
        .menu li:hover, .menu li.active { 
            background: rgba(99, 102, 241, 0.15); 
            color: var(--text); 
            transform: translateX(5px);
        }

        .menu li.active {
            border-left: 4px solid var(--primary);
        }
        
        /* MAIN CONTENT */
        .main { flex: 1; padding: 40px; overflow-y: auto; width: 100%; position: relative; }
        
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 40px; }
        .header h1 { font-size: 32px; font-weight: 800; letter-spacing: -0.5px; }
        .os-info { font-family: 'JetBrains Mono', monospace; font-size: 12px; color: var(--text2); background: var(--panel); backdrop-filter: var(--glass); padding: 10px 18px; border-radius: 10px; border: 1px solid var(--border); display: flex; gap: 15px; flex-wrap: wrap; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);}
        
        /* STATS GRID */
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 24px; margin-bottom: 40px; }
        .card { 
            background: var(--panel); 
            backdrop-filter: var(--glass);
            padding: 24px; 
            border-radius: 16px; 
            border: 1px solid var(--border); 
            transition: transform 0.3s, box-shadow 0.3s;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        }
        .card:hover { transform: translateY(-5px); box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2); border-color: rgba(99, 102, 241, 0.4);}
        .card-title { font-size: 13px; color: var(--text2); text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 12px; font-weight: 700; }
        .card-val { font-size: 36px; font-weight: 800; font-family: 'JetBrains Mono', monospace; color: #fff;}
        .bar-bg { width: 100%; height: 8px; background: rgba(0,0,0,0.3); border-radius: 4px; margin-top: 16px; overflow: hidden; }
        .bar-fill { height: 100%; background: linear-gradient(90deg, #8b5cf6, #6366f1); border-radius: 4px; transition: width 0.5s; box-shadow: 0 0 10px rgba(139, 92, 246, 0.5);}
        
        /* TABLE & BUTTONS */
        .section-title { font-size: 20px; font-weight: 800; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; }
        .btn { 
            padding: 10px 20px; 
            border-radius: 8px; 
            border: none; 
            font-weight: 600; 
            cursor: pointer; 
            transition: all 0.2s; 
            font-size: 14px; 
            text-decoration: none; 
            display: inline-flex; 
            align-items: center;
            gap: 8px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        .btn:active { transform: scale(0.98); }
        .btn-green { background: var(--green); color: #fff; }
        .btn-green:hover { background: #059669; box-shadow: 0 0 15px rgba(16, 185, 129, 0.4); }
        .btn-primary { background: var(--primary); color: #fff; }
        .btn-primary:hover { background: var(--primary-hover); box-shadow: 0 0 15px rgba(99, 102, 241, 0.4); }
        .btn-red { background: var(--red); color: #fff; }
        .btn-red:hover { background: #dc2626; box-shadow: 0 0 15px rgba(239, 68, 68, 0.4); }
        
        .table-wrap { width: 100%; overflow-x: auto; border-radius: 16px; border: 1px solid var(--border); background: var(--panel); backdrop-filter: var(--glass);}
        table { width: 100%; border-collapse: collapse; min-width: 500px; }
        th, td { padding: 18px 24px; text-align: left; border-bottom: 1px solid var(--border); font-size: 14px; }
        th { background: rgba(0,0,0,0.2); color: var(--text2); font-weight: 600; font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px;}
        tr:last-child td { border-bottom: none; }
        tr:hover td { background: rgba(255,255,255,0.02); }
        
        .badge { padding: 6px 12px; border-radius: 20px; font-size: 12px; font-weight: 700; font-family: 'JetBrains Mono', monospace; display: inline-block;}
        .badge-run { background: rgba(16, 185, 129, 0.15); color: var(--green); border: 1px solid var(--green); box-shadow: 0 0 10px rgba(16,185,129,0.2); }
        .badge-stop { background: rgba(239, 68, 68, 0.15); color: var(--red); border: 1px solid var(--red); box-shadow: 0 0 10px rgba(239,68,68,0.2); }
        
        /* DEPLOY FORM */
        .deploy-box { background: var(--panel); backdrop-filter: var(--glass); padding: 30px; border-radius: 16px; border: 1px solid var(--border); margin-bottom: 40px; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);}
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; margin-bottom: 10px; font-size: 14px; color: var(--text2); font-weight: 600; }
        input[type="text"], input[type="file"], input[type="password"] { width: 100%; padding: 14px; background: rgba(0,0,0,0.2); border: 1px solid var(--border); color: var(--text); border-radius: 10px; font-family: 'JetBrains Mono', monospace; font-size: 14px; transition: border 0.3s, box-shadow 0.3s;}
        input[type="text"]:focus, input[type="file"]:focus, input[type="password"]:focus { outline: none; border-color: var(--primary); box-shadow: 0 0 0 3px rgba(99,102,241,0.2);}
        input[type="file"]::file-selector-button { background: var(--border); color: var(--text); border: none; padding: 10px 16px; border-radius: 6px; cursor: pointer; margin-right: 15px; font-weight: bold; transition: 0.2s;}
        input[type="file"]::file-selector-button:hover { background: var(--text2); color: var(--bg);}
        
        .page { display: none; animation: fadeIn 0.4s ease-out; }
        .page.active { display: block; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        
        /* FILE MANAGER */
        .fm-layout { display: flex; gap: 24px; height: calc(100vh - 160px); flex-direction: row; }
        .fm-sidebar { width: 260px; background: var(--panel); backdrop-filter: var(--glass); border: 1px solid var(--border); border-radius: 16px; padding: 20px; overflow-y: auto; }
        .fm-bot-item { padding: 14px; border-radius: 10px; cursor: pointer; font-weight: 600; margin-bottom: 8px; transition: 0.2s; display: flex; align-items: center; gap: 10px; color: var(--text2);}
        .fm-bot-item:hover, .fm-bot-item.active { background: rgba(99, 102, 241, 0.15); color: var(--text); border-left: 3px solid var(--primary);}
        .fm-main { flex: 1; background: var(--panel); backdrop-filter: var(--glass); border: 1px solid var(--border); border-radius: 16px; display: flex; flex-direction: column; overflow: hidden; }
        .fm-toolbar { padding: 16px 20px; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap:15px; background: rgba(0,0,0,0.1);}
        .fm-path { font-family: 'JetBrains Mono', monospace; color: var(--text); font-size: 14px; background: rgba(0,0,0,0.2); padding: 6px 12px; border-radius: 6px; border: 1px solid var(--border);}
        .fm-files { flex: 1; padding: 20px; overflow-y: auto; }
        .fm-item { padding: 16px; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; cursor: pointer; transition: 0.2s; border-radius: 8px;}
        .fm-item:hover { background: rgba(255,255,255,0.03); transform: translateX(5px); }
        .fm-item-name { display: flex; align-items: center; gap: 12px; font-weight: 500; font-size: 15px; }
        
        /* MODALS */
        .editor-modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.7); backdrop-filter: blur(4px); z-index: 1000; justify-content: center; align-items: center; }
        .editor-box { background: var(--bg); width: 90%; height: 90%; border-radius: 16px; border: 1px solid var(--border); display: flex; flex-direction: column; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);}
        .editor-header { padding: 20px 24px; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; background: rgba(255,255,255,0.02); border-radius: 16px 16px 0 0;}
        .editor-textarea { flex: 1; width: 100%; background: rgba(0,0,0,0.3); color: #a78bfa; border: none; padding: 24px; font-family: 'JetBrains Mono', monospace; font-size: 15px; resize: none; outline: none; line-height: 1.6; }
        .editor-footer { padding: 20px 24px; border-top: 1px solid var(--border); display: flex; justify-content: flex-end; gap: 12px; background: rgba(255,255,255,0.02); border-radius: 0 0 16px 16px;}
        
        .login-box { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); background: var(--panel); backdrop-filter: var(--glass); padding: 48px; border-radius: 20px; border: 1px solid var(--border); width: 90%; max-width: 400px; text-align: center; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5); }
        .login-box h2 { margin-bottom: 30px; font-size: 32px; font-weight: 800; background: linear-gradient(135deg, #818cf8, #38bdf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; display: flex; justify-content: center; align-items: center; gap: 12px;}

        /* RESPONSIVE */
        @media (max-width: 768px) {
            body { flex-direction: column; }
            .sidebar { width: 100%; height: auto; padding: 15px 0; border-right: none; border-bottom: 1px solid var(--border); flex-direction: row; align-items: center; overflow-x: auto;}
            .logo { padding: 0 20px; font-size: 22px; white-space: nowrap;}
            .menu { flex-direction: row; padding: 0 20px; gap: 10px;}
            .menu li { padding: 10px 15px; font-size: 14px; border-radius: 8px; white-space: nowrap;}
            .menu li:hover, .menu li.active { transform: none; border-left: none; background: rgba(99, 102, 241, 0.2);}
            .main { padding: 20px; }
            .fm-layout { flex-direction: column; height: auto; }
            .fm-sidebar { width: 100%; max-height: 200px; }
            .header h1 { font-size: 24px; }
            .card-val { font-size: 28px;}
        }
    </style>
</head>
<body>
    {% if not session.get('logged_in') %}
    <div class="login-box">
        <h2>⚡ HiroCloud</h2>
        <form method="POST" action="/login">
            <div class="form-group"><input type="text" name="username" placeholder="Username" required></div>
            <div class="form-group"><input type="password" name="password" placeholder="Password" required></div>
            <button type="submit" class="btn btn-primary" style="width:100%; padding:14px; font-size:16px; justify-content:center;">Login System</button>
        </form>
        {% if error %}<p style="color:var(--red); margin-top:15px; font-weight:600;">{{ error }}</p>{% endif %}
    </div>
    {% else %}
    <div class="sidebar">
        <div class="logo">⚡ <span>HiroCloud</span></div>
        <ul class="menu">
            <li id="nav-monitor" class="active" onclick="showPage('monitor', this)">📊 Monitor</li>
            <li id="nav-bots" onclick="showPage('bots', this)">🤖 Bots</li>
            <li id="nav-deploy" onclick="showPage('deploy', this)">📦 Deploy</li>
            <li id="nav-files" onclick="showPage('files', this); loadBotsToFm();">📁 Files</li>
            <li onclick="location.href='/logout'" style="color:var(--red); margin-top:auto;">🚪 Logout</li>
        </ul>
    </div>
    <div class="main">
        <!-- MONITOR -->
        <div id="page-monitor" class="page active">
            <div class="header">
                <h1>Dashboard Overview</h1>
                <div class="os-info">Host: vps-cloud <span>OS: Ubuntu 22.04 LTS</span></div>
            </div>
            <div class="stats">
                <div class="card"><div class="card-title">CPU Usage</div><div class="card-val">{{ cpu }}%</div><div class="bar-bg"><div class="bar-fill" style="width: {{ cpu }}%"></div></div></div>
                <div class="card"><div class="card-title">Memory</div><div class="card-val">{{ ram }}%</div><div class="bar-bg"><div class="bar-fill" style="width: {{ ram }}%"></div></div></div>
                <div class="card"><div class="card-title">Disk Space</div><div class="card-val">{{ disk }}%</div><div class="bar-bg"><div class="bar-fill" style="width: {{ disk }}%"></div></div></div>
                <div class="card"><div class="card-title">Network</div><div class="card-val" style="font-size: 24px; margin-top:10px;">↓0.2 ↑0.6 KB/s</div></div>
            </div>
            <div class="section-title">Active Bots <button onclick="showPage('deploy', document.getElementById('nav-deploy'))" class="btn btn-green">+ New Deploy</button></div>
            <div class="table-wrap">
                <table>
                    <tr><th>Status</th><th>Bot Name</th><th>Command</th><th>PID</th></tr>
                    {% for bot in bots %}
                    <tr>
                        <td><span class="badge {{ 'badge-run' if bot.running else 'badge-stop' }}">{{ "RUNNING" if bot.running else "STOPPED" }}</span></td>
                        <td style="font-weight:700; font-size:15px;">{{ bot.name }}</td>
                        <td style="font-family: 'JetBrains Mono', monospace; color: var(--text2);">python3 main.py</td>
                        <td style="font-family: 'JetBrains Mono', monospace; color: var(--text2);">{{ bot.pid }}</td>
                    </tr>
                    {% else %}<tr><td colspan="4" style="text-align:center; color:var(--text2); padding:30px;">No bots deployed yet.</td></tr>{% endfor %}
                </table>
            </div>
        </div>

        <!-- BOTS -->
        <div id="page-bots" class="page">
            <div class="header"><h1>Bots Manager</h1></div>
            <div style="margin-bottom: 24px; display:flex; gap:12px;">
                <button class="btn btn-primary" onclick="location.reload()">↻ Refresh List</button>
                <button onclick="showPage('deploy', document.getElementById('nav-deploy'))" class="btn btn-green">+ Deploy New Bot</button>
            </div>
            <div class="table-wrap">
                <table>
                    <tr><th>Status</th><th>Bot Name</th><th>Actions</th></tr>
                    {% for bot in bots %}
                    <tr>
                        <td><span class="badge {{ 'badge-run' if bot.running else 'badge-stop' }}">{{ "RUNNING" if bot.running else "STOPPED" }}</span></td>
                        <td style="font-weight:700; font-size:15px;">{{ bot.name }}</td>
                        <td style="display:flex; gap:10px;">
                            <form action="/run/{{ bot.name }}" method="post" style="display:inline;">
                                <button type="submit" class="btn btn-primary" style="padding: 8px 16px; font-size:13px;">▶ Start</button>
                            </form>
                            <form action="/stop/{{ bot.name }}" method="post" style="display:inline;">
                                <button type="submit" class="btn btn-red" style="padding: 8px 16px; font-size:13px;">■ Stop</button>
                            </form>
                        </td>
                    </tr>
                    {% endfor %}
                </table>
            </div>
        </div>

        <!-- DEPLOY -->
        <div id="page-deploy" class="page">
            <div class="header"><h1>Deploy New Bot</h1></div>
            <p style="color:var(--text2); margin-bottom: 24px; font-size:15px;">Upload ZIP bot kamu — requirements.txt will be installed automatically.</p>
            <div class="deploy-box">
                <form action="/upload" method="post" enctype="multipart/form-data">
                    <div class="form-group"><label>BOT NAME *</label><input type="text" name="name" placeholder="my-awesome-bot" required></div>
                    <div class="form-group"><label>EXECUTION COMMAND *</label><input type="text" name="command" value="python3 main.py" required></div>
                    <div class="form-group"><label>ZIP FILE *</label><input type="file" name="zipfile" accept=".zip" required></div>
                    <button type="submit" class="btn" style="width: 100%; padding: 16px; font-size: 16px; background: linear-gradient(90deg, #0ea5e9, #6366f1); color: white; margin-top:10px; justify-content:center;">🚀 Deploy Bot Now</button>
                </form>
            </div>
        </div>

        <!-- FILES -->
        <div id="page-files" class="page">
            <div class="header"><h1>File Manager</h1></div>
            <div class="fm-layout">
                <div class="fm-sidebar" id="fm-bot-list"><div style="color:var(--text2); font-size:12px; font-weight:800; letter-spacing:1px; margin-bottom:15px;">SELECT BOT</div></div>
                <div class="fm-main">
                    <div class="fm-toolbar">
                        <div class="fm-path" id="fm-current-path">/ Select a bot</div>
                        <div style="display:flex; gap:10px;">
                            <button class="btn btn-primary" onclick="fmGoUp()" id="btn-up" style="display:none; padding:8px 14px;">↑ Up</button>
                            <button class="btn btn-green" onclick="openEditor('', '')" id="btn-new-file" style="display:none; padding:8px 14px;">+ New File</button>
                        </div>
                    </div>
                    <div class="fm-files" id="fm-file-list"><div style="text-align:center; color:var(--text2); margin-top:80px; font-size:15px;">Select a bot to browse files</div></div>
                </div>
            </div>
        </div>
    </div>

    <!-- EDITOR MODAL -->
    <div class="editor-modal" id="editor-modal">
        <div class="editor-box">
            <div class="editor-header"><h3 id="editor-title" style="font-family: 'JetBrains Mono', monospace;">Edit File</h3><button class="btn btn-red" onclick="closeEditor()" style="padding:8px 16px;">✕ Close</button></div>
            <textarea class="editor-textarea" id="editor-code" spellcheck="false"></textarea>
            <div class="editor-footer"><button class="btn btn-green" onclick="saveFile()" style="padding:10px 24px; font-size:15px;">💾 Save File</button></div>
        </div>
    </div>

    <script>
        function showPage(pageId, el) {
            document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
            document.getElementById('page-' + pageId).classList.add('active');
            document.querySelectorAll('.menu li').forEach(li => li.classList.remove('active'));
            el.classList.add('active');
        }

        document.addEventListener('submit', function(e) {
            if (e.target.action.includes('/run/') || e.target.action.includes('/stop/')) {
                setTimeout(() => { location.reload(); }, 1500); 
            }
        });

        let currentBot = "", currentFile = "", currentPath = "";
        
        function loadBotsToFm() {
            const botList = document.getElementById('fm-bot-list');
            const tableRows = document.querySelectorAll('#page-monitor table tbody tr');
            let html = '<div style="color:var(--text2); font-size:12px; font-weight:800; letter-spacing:1px; margin-bottom:15px;">SELECT BOT</div>';
            tableRows.forEach(row => {
                const nameTd = row.querySelector('td:nth-child(2)');
                if (nameTd && nameTd.innerText !== 'Nama' && !nameTd.innerText.includes('Belum') && !nameTd.innerText.includes('No bots')) {
                    html += `<div class="fm-bot-item" onclick="loadFiles('${nameTd.innerText}', '', this)">🤖 ${nameTd.innerText}</div>`;
                }
            });
            botList.innerHTML = html;
        }

        async function loadFiles(botName, path, el) {
            if(el) { 
                document.querySelectorAll('.fm-bot-item').forEach(i => i.classList.remove('active')); 
                el.classList.add('active'); 
            }
            currentBot = botName;
            currentPath = path;
            
            document.getElementById('fm-current-path').innerText = `/ ${botName} ${path ? '/ ' + path : ''}`;
            document.getElementById('btn-new-file').style.display = 'inline-flex';
            document.getElementById('btn-up').style.display = path ? 'inline-flex' : 'none';
            
            const res = await fetch(`/api/files/${botName}?path=${path}`);
            const files = await res.json();
            
            let html = '';
            files.forEach(f => { 
                if (f.type === 'dir') {
                    html += `<div class="fm-item" onclick="loadFiles('${botName}', '${f.path}', null)">
                        <div class="fm-item-name">📁 ${f.name}</div>
                        <button class="btn btn-primary" style="padding:6px 12px; font-size:12px;">Open</button>
                    </div>`;
                } else {
                    html += `<div class="fm-item" onclick="openEditor('${f.path}', '${botName}')">
                        <div class="fm-item-name">📄 ${f.name}</div>
                        <button class="btn btn-primary" style="padding:6px 12px; font-size:12px;">Edit</button>
                    </div>`; 
                }
            });
            document.getElementById('fm-file-list').innerHTML = html || '<div style="color:var(--text2); text-align:center; padding:40px;">Folder is empty.</div>';
        }

        function fmGoUp() {
            let parts = currentPath.split('/').filter(p => p);
            parts.pop();
            loadFiles(currentBot, parts.join('/'), null);
        }

        async function openEditor(filepath, botName) {
            if (filepath) {
                currentFile = filepath;
                document.getElementById('editor-title').innerText = `Edit: ${filepath}`;
                const res = await fetch(`/api/read/${botName}/${filepath}`);
                document.getElementById('editor-code').value = await res.text();
            } else {
                currentFile = prompt("File name (e.g: config.py):");
                if (!currentFile) return;
                document.getElementById('editor-title').innerText = `New: ${currentFile}`;
                document.getElementById('editor-code').value = "";
            }
            document.getElementById('editor-modal').style.display = 'flex';
        }

        async function saveFile() {
            const code = document.getElementById('editor-code').value;
            await fetch(`/api/save/${currentBot}/${currentFile}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ code: code }) });
            alert('File saved successfully!');
            closeEditor(); 
            loadFiles(currentBot, currentPath, null);
        }
        function closeEditor() { document.getElementById('editor-modal').style.display = 'none'; }
    </script>
    {% endif %}
</body>
</html>
"""

@app.route('/login', methods=['POST'])
def login():
    if request.form['username'] == 'admin' and request.form['password'] == 'admin123':
        session['logged_in'] = True
        return redirect(url_for('index'))
    return render_template_string(HTML, error="Username/Password Salah", bots=[], cpu=0, ram=0, disk=0)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

@app.route('/')
def index():
    if not session.get('logged_in'): return render_template_string(HTML, bots=[], cpu=0, ram=0, disk=0)
    
    bots = []
    for name in os.listdir(BOTS_DIR):
        path = os.path.join(BOTS_DIR, name)
        if os.path.isdir(path):
            pid = "-"
            is_running = False
            for p in psutil.process_iter(['pid', 'cmdline']):
                try:
                    cmdline = " ".join(p.info['cmdline'] or [])
                    if name in cmdline and "main.py" in cmdline:
                        is_running = True
                        pid = p.info['pid']
                        break
                except: pass
            bots.append({"name": name, "running": is_running, "pid": pid})
    
    disk = psutil.disk_usage('/').percent
    return render_template_string(HTML, cpu=psutil.cpu_percent(), ram=psutil.virtual_memory().percent, disk=disk, bots=bots)

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['zipfile']
    name = request.form['name']
    bot_path = os.path.join(BOTS_DIR, name)
    os.makedirs(bot_path, exist_ok=True)
    
    zip_path = os.path.join(bot_path, "bot.zip")
    file.save(zip_path)
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(bot_path)
    os.remove(zip_path)
    
    req_file = os.path.join(bot_path, "requirements.txt")
    if os.path.exists(req_file): subprocess.run(["pip", "install", "-r", req_file])
    return redirect(url_for('index'))

@app.route('/run/<bot_name>', methods=['POST'])
def run_bot(bot_name):
    bot_path = os.path.join(BOTS_DIR, bot_name)
    subprocess.Popen(["python3", "main.py"], cwd=bot_path, start_new_session=True)
    return redirect(url_for('index'))

@app.route('/stop/<bot_name>', methods=['POST'])
def stop_bot(bot_name):
    for p in psutil.process_iter(['pid', 'cmdline']):
        try:
            cmdline = " ".join(p.info['cmdline'] or [])
            if bot_name in cmdline and "main.py" in cmdline: p.kill()
        except: pass
    return redirect(url_for('index'))

@app.route('/api/files/<bot_name>')
def api_files(bot_name):
    rel_path = request.args.get('path', '')
    bot_path = os.path.join(BOTS_DIR, bot_name, rel_path)
    
    if os.path.exists(bot_path):
        items = []
        for f in os.listdir(bot_path):
            full_path = os.path.join(bot_path, f)
            item_rel_path = os.path.join(rel_path, f).replace("\\\\", "/")
            if os.path.isdir(full_path):
                items.append({"name": f, "type": "dir", "path": item_rel_path})
            else:
                items.append({"name": f, "type": "file", "path": item_rel_path})
        return jsonify(items)
    return jsonify([])

@app.route('/api/read/<bot_name>/<path:filename>')
def api_read(bot_name, filename):
    file_path = os.path.join(BOTS_DIR, bot_name, filename)
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f: return f.read()
        except:
            return "File tidak bisa dibaca (format biner/gambar).", 400
    return "File not found", 404

@app.route('/api/save/<bot_name>/<path:filename>', methods=['POST'])
def api_save(bot_name, filename):
    data = request.get_json()
    file_path = os.path.join(BOTS_DIR, bot_name, filename)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f: f.write(data['code'])
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=2121)