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
    <title>HiroCloud</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;500;600;700;800&display=swap');
        
        :root { 
            --bg: #0b0f19; 
            --panel: #111827; 
            --border: #1f2937; 
            --text: #e2e8f0; 
            --text2: #9ca3af; 
            --primary: #38bdf8; 
            --green: #10b981; 
            --red: #ef4444; 
            --purple: #8b5cf6; 
        }
        
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', sans-serif; }
        body { background-color: var(--bg); color: var(--text); display: flex; height: 100vh; overflow: hidden; }
        
        /* SIDEBAR */
        .sidebar { width: 240px; background: var(--panel); border-right: 1px solid var(--border); display: flex; flex-direction: column; padding: 20px 0; }
        .logo { font-size: 24px; font-weight: 800; color: var(--primary); padding: 0 24px 30px; display: flex; align-items: center; gap: 10px; }
        .logo span { color: var(--text); }
        .menu { list-style: none; }
        .menu li { padding: 15px 24px; color: var(--text2); cursor: pointer; display: flex; align-items: center; gap: 12px; font-weight: 600; font-size: 15px; transition: 0.2s; }
        .menu li:hover, .menu li.active { background: rgba(56, 189, 248, 0.1); color: var(--primary); border-right: 3px solid var(--primary); }
        
        /* MAIN CONTENT */
        .main { flex: 1; padding: 30px; overflow-y: auto; width: 100%; }
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }
        .header h1 { font-size: 28px; font-weight: 800; }
        .os-info { font-family: 'JetBrains Mono', monospace; font-size: 12px; color: var(--text2); background: var(--panel); padding: 8px 16px; border-radius: 8px; border: 1px solid var(--border); display: flex; gap: 15px; flex-wrap: wrap;}
        
        /* STATS GRID */
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .card { background: var(--panel); padding: 20px; border-radius: 12px; border: 1px solid var(--border); }
        .card-title { font-size: 12px; color: var(--text2); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px; font-weight: 700; }
        .card-val { font-size: 32px; font-weight: 800; font-family: 'JetBrains Mono', monospace; }
        .bar-bg { width: 100%; height: 6px; background: var(--border); border-radius: 3px; margin-top: 15px; overflow: hidden; }
        .bar-fill { height: 100%; background: var(--purple); border-radius: 3px; transition: width 0.5s; }
        
        /* TABLE & BUTTONS */
        .section-title { font-size: 18px; font-weight: 800; margin-bottom: 15px; display: flex; justify-content: space-between; align-items: center; }
        .btn { padding: 8px 16px; border-radius: 6px; border: none; font-weight: 700; cursor: pointer; transition: 0.2s; font-size: 13px; text-decoration: none; display: inline-flex; align-items:center; justify-content:center; gap:5px;}
        .btn-green { background: var(--green); color: #fff; }
        .btn-green:hover { background: #059669; }
        .btn-primary { background: var(--primary); color: #000; }
        .btn-primary:hover { background: #0ea5e9; }
        
        /* TOMBOL AKSI */
        .btn-action { padding: 6px 12px; border-radius: 6px; font-weight: 600; font-size: 13px; cursor: pointer; border: 1px solid; text-decoration: none; display: inline-flex; align-items: center; gap: 6px; transition: 0.2s; background: transparent; z-index: 10; position: relative;}
        .btn-stop { color: #f43f5e; border-color: #4c0519; background: rgba(244, 63, 94, 0.1); }
        .btn-stop:hover { background: rgba(244, 63, 94, 0.2); }
        
        .btn-restart { color: #eab308; border-color: #422006; background: rgba(234, 179, 8, 0.1); padding: 6px 10px;}
        .btn-restart:hover { background: rgba(234, 179, 8, 0.2); }
        
        .btn-log { color: #38bdf8; border-color: #082f49; background: rgba(56, 189, 248, 0.1); }
        .btn-log:hover { background: rgba(56, 189, 248, 0.2); }
        
        .btn-files { color: #e2e8f0; border-color: #334155; background: rgba(255, 255, 255, 0.05); }
        .btn-files:hover { background: rgba(255, 255, 255, 0.1); }
        
        .btn-delete { color: #f43f5e; border-color: #4c0519; padding: 6px 10px; background: transparent;}
        .btn-delete:hover { background: rgba(244, 63, 94, 0.2); }
        
        .table-wrap { width: 100%; overflow-x: auto; -webkit-overflow-scrolling: touch; }
        table { width: 100%; border-collapse: collapse; background: var(--panel); border-radius: 12px; overflow: hidden; border: 1px solid var(--border); min-width: 700px; }
        th, td { padding: 16px; text-align: left; border-bottom: 1px solid var(--border); font-size: 14px; }
        th { background: rgba(255,255,255,0.02); color: var(--text2); font-weight: 600; }
        .badge { padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 700; font-family: 'JetBrains Mono', monospace; }
        .badge-run { background: rgba(16, 185, 129, 0.15); color: var(--green); border: 1px solid var(--green); }
        .badge-stop { background: rgba(239, 68, 68, 0.15); color: var(--red); border: 1px solid var(--red); }
        
        /* DEPLOY FORM */
        .deploy-box { background: var(--panel); padding: 24px; border-radius: 12px; border: 1px solid var(--border); margin-bottom: 30px; }
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; margin-bottom: 8px; font-size: 13px; color: var(--text2); font-weight: 600; }
        input[type="text"], input[type="file"], input[type="password"] { width: 100%; padding: 12px; background: var(--bg); border: 1px solid var(--border); color: var(--text); border-radius: 8px; font-family: 'JetBrains Mono', monospace; font-size: 13px; }
        input[type="file"]::file-selector-button { background: var(--border); color: var(--text); border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; margin-right: 15px; font-weight: bold;}
        
        .page { display: none; }
        .page.active { display: block; }
        
        /* FILE MANAGER */
        .fm-layout { display: flex; gap: 20px; height: calc(100vh - 150px); flex-direction: row; }
        .fm-sidebar { width: 250px; background: var(--panel); border: 1px solid var(--border); border-radius: 12px; padding: 15px; overflow-y: auto; }
        .fm-bot-item { padding: 12px; border-radius: 8px; cursor: pointer; font-weight: bold; margin-bottom: 5px; transition: 0.2s; }
        .fm-bot-item:hover, .fm-bot-item.active { background: rgba(56, 189, 248, 0.1); color: var(--primary); }
        .fm-main { flex: 1; background: var(--panel); border: 1px solid var(--border); border-radius: 12px; display: flex; flex-direction: column; overflow: hidden; }
        .fm-toolbar { padding: 15px; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap:10px;}
        .fm-path { font-family: 'JetBrains Mono', monospace; color: var(--text2); font-size: 14px; }
        .fm-files { flex: 1; padding: 15px; overflow-y: auto; }
        .fm-item { padding: 12px 15px; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; cursor: pointer; }
        .fm-item:hover { background: rgba(255,255,255,0.02); }
        .fm-item-name { display: flex; align-items: center; gap: 10px; font-weight: 600; }
        
        /* MODALS */
        .editor-modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); z-index: 1000; justify-content: center; align-items: center; }
        .editor-box { background: var(--panel); width: 90%; height: 90%; border-radius: 12px; border: 1px solid var(--border); display: flex; flex-direction: column; }
        .editor-header { padding: 15px 20px; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; }
        .editor-textarea { flex: 1; width: 100%; background: var(--bg); color: #a78bfa; border: none; padding: 20px; font-family: 'JetBrains Mono', monospace; font-size: 14px; resize: none; outline: none; line-height: 1.5; }
        .editor-footer { padding: 15px 20px; border-top: 1px solid var(--border); display: flex; justify-content: flex-end; gap: 10px; }
        
        /* LOG MODAL */
        .log-modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); z-index: 1000; justify-content: center; align-items: center; }
        .log-box { background: #000; width: 90%; height: 80%; border-radius: 12px; border: 1px solid var(--border); display: flex; flex-direction: column; }
        .log-content { flex: 1; color: #10b981; padding: 20px; font-family: 'JetBrains Mono', monospace; font-size: 13px; overflow-y: auto; white-space: pre-wrap; }

        /* LOGIN */
        .login-box { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); background: var(--panel); padding: 40px; border-radius: 12px; border: 1px solid var(--border); width: 90%; max-width: 350px; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
        .login-box h2 { margin-bottom: 20px; color: var(--primary); font-size: 28px; display: flex; justify-content: center; align-items: center; gap:10px;}

        /* BOTTOM NAVIGATION */
        .bottom-nav { display: none; position: fixed; bottom: 0; left: 0; width: 100%; background-color: #0d1321; border-top: 1px solid var(--border); justify-content: space-around; align-items: center; padding: 10px 0; z-index: 100; }
        .bottom-nav-item { display: flex; flex-direction: column; align-items: center; color: #7b8b9e; font-size: 12px; font-weight: 600; cursor: pointer; text-decoration: none; gap: 4px; padding: 8px 15px; border-radius: 8px; transition: 0.2s; }
        .bottom-nav-item.active { color: var(--primary); background-color: rgba(56, 189, 248, 0.1); }
        .bottom-nav-item svg { width: 24px; height: 24px; fill: currentColor; }

        /* RESPONSIVE (Tampilan HP) */
        @media (max-width: 768px) {
            body { flex-direction: column; }
            .sidebar { display: none; }
            .main { padding: 15px; padding-bottom: 80px; }
            .fm-layout { flex-direction: column; height: auto; }
            .fm-sidebar { width: 100%; max-height: 200px; }
            .bottom-nav { display: flex; }
            
            /* SEMBUNYIKAN KOLOM COMMAND & PID DI HP */
            th:nth-child(3), td:nth-child(3),
            th:nth-child(4), td:nth-child(4) {
                display: none;
            }
            table { min-width: 100%; }
            th, td { padding: 12px 8px; font-size: 13px; }
            
            /* RAPIKAN TOMBOL AKSI DI HP */
            .btn-action { padding: 6px 8px; font-size: 12px; }
        }

        /* NOTIFIKASI ERROR DEPLOY */
        .alert-error { background-color: rgba(239, 68, 68, 0.1); color: #ef4444; border: 1px solid #ef4444; padding: 15px; border-radius: 8px; margin-bottom: 20px; font-weight: bold; font-family: 'JetBrains Mono', monospace; font-size: 13px; display: none; white-space: pre-wrap;}
    </style>
</head>
<body>
    {% if not session.get('logged_in') %}
    <div class="login-box">
        <h2>⚡ HiroCloud</h2>
        <form method="POST" action="/login">
            <div class="form-group"><input type="text" name="username" placeholder="Username" required></div>
            <div class="form-group"><input type="password" name="password" placeholder="Password" required></div>
            <button type="submit" class="btn btn-primary" style="width:100%; padding:12px;">Login</button>
        </form>
        {% if error %}<p style="color:var(--red); margin-top:10px;">{{ error }}</p>{% endif %}
    </div>
    {% else %}
    
    <!-- SIDEBAR -->
    <div class="sidebar">
        <div class="logo">⚡ <span>HiroCloud</span></div>
        <ul class="menu">
            <li id="nav-monitor-desktop" class="active" onclick="showPage('monitor', this, 'nav-monitor-mobile')">📊 Monitor</li>
            <li id="nav-bots-desktop" onclick="showPage('bots', this, 'nav-bots-mobile')">🤖 Bots</li>
            <li id="nav-deploy-desktop" onclick="showPage('deploy', this, 'nav-deploy-mobile')">📦 Deploy</li>
            <li id="nav-files-desktop" onclick="showPage('files', this, 'nav-files-mobile'); loadBotsToFm();">📁 Files</li>
            <li onclick="location.href='/logout'" style="color:var(--red); margin-top:auto;">🚪 Logout</li>
        </ul>
    </div>

    <div class="main">
        <!-- MONITOR -->
        <div id="page-monitor" class="page active">
            <div class="header">
                <h1>Monitor</h1>
                <div class="os-info">Hostname: vps-cloud <span>OS: Ubuntu 22.04 LTS</span></div>
            </div>
            <div class="stats">
                <div class="card"><div class="card-title">CPU Usage</div><div class="card-val">{{ cpu }}%</div><div class="bar-bg"><div class="bar-fill" style="width: {{ cpu }}%"></div></div></div>
                <div class="card"><div class="card-title">Memory</div><div class="card-val">{{ ram }}%</div><div class="bar-bg"><div class="bar-fill" style="width: {{ ram }}%"></div></div></div>
                <div class="card"><div class="card-title">Disk</div><div class="card-val">{{ disk }}%</div><div class="bar-bg"><div class="bar-fill" style="width: {{ disk }}%"></div></div></div>
                <div class="card"><div class="card-title">Network</div><div class="card-val" style="font-size: 24px;">↓0.2 ↑0.6 KB/s</div></div>
            </div>
            <div class="section-title">BOTS <button onclick="showPage('deploy', document.getElementById('nav-deploy-desktop'), 'nav-deploy-mobile')" class="btn btn-green">+ Deploy</button></div>
            <div class="table-wrap">
                <table>
                    <tr><th>Status</th><th>Nama</th><th>Command</th><th>PID</th><th>Aksi</th></tr>
                    {% for bot in bots %}
                    <tr>
                        <td><span class="badge {{ 'badge-run' if bot.running else 'badge-stop' }}">{{ "running" if bot.running else "stopped" }}</span></td>
                        <td style="font-weight:bold;">{{ bot.name }}</td>
                        <td style="font-family: monospace; color: var(--text2);">python3 main.py</td>
                        <td style="font-family: monospace; color: var(--text2);">{{ bot.pid }}</td>
                        <td style="display:flex; gap:8px; flex-wrap:wrap;">
                            <!-- TOMBOL STOP -->
                            <form action="/stop/{{ bot.name }}" method="post" style="display:inline;">
                                <button type="submit" class="btn-action btn-stop" title="Stop">■ Stop</button>
                            </form>
                            
                            <!-- TOMBOL RESTART -->
                            <form action="/restart/{{ bot.name }}" method="post" style="display:inline;">
                                <button type="submit" class="btn-action btn-restart" title="Restart">↻</button>
                            </form>

                            <!-- TOMBOL LOG & FILES -->
                            <button onclick="viewLogs('{{ bot.name }}')" class="btn-action btn-log">Log</button>
                            <button onclick="openFilesTab('{{ bot.name }}')" class="btn-action btn-files">Files</button>
                            
                            <!-- TOMBOL DELETE -->
                            <form action="/delete/{{ bot.name }}" method="post" style="display:inline;" onsubmit="return confirm('Yakin ingin menghapus bot ini?');">
                                <button type="submit" class="btn-action btn-delete" title="Hapus">🗑️</button>
                            </form>
                        </td>
                    </tr>
                    {% else %}<tr><td colspan="5" style="text-align:center; color:var(--text2);">Belum ada bot.</td></tr>{% endfor %}
                </table>
            </div>
        </div>

        <!-- BOTS -->
        <div id="page-bots" class="page">
            <div class="header"><h1>Bots Manager</h1></div>
            <div style="margin-bottom: 20px;">
                <button class="btn btn-primary" onclick="location.reload()">↻ Refresh</button>
                <button onclick="showPage('deploy', document.getElementById('nav-deploy-desktop'), 'nav-deploy-mobile')" class="btn btn-green">+ Deploy Bot</button>
            </div>
            <div class="table-wrap">
                <table>
                    <tr><th>Status</th><th>Nama</th><th>Command</th><th>PID</th><th>Aksi</th></tr>
                    {% for bot in bots %}
                    <tr>
                        <td><span class="badge {{ 'badge-run' if bot.running else 'badge-stop' }}">{{ "running" if bot.running else "stopped" }}</span></td>
                        <td style="font-weight:bold;">{{ bot.name }}</td>
                        <td style="font-family: monospace; color: var(--text2);">python3 main.py</td>
                        <td style="font-family: monospace; color: var(--text2);">{{ bot.pid }}</td>
                        <td style="display:flex; gap:8px; flex-wrap:wrap;">
                            <form action="/stop/{{ bot.name }}" method="post" style="display:inline;">
                                <button type="submit" class="btn-action btn-stop" title="Stop">■ Stop</button>
                            </form>
                            
                            <form action="/restart/{{ bot.name }}" method="post" style="display:inline;">
                                <button type="submit" class="btn-action btn-restart" title="Restart">↻</button>
                            </form>

                            <button onclick="viewLogs('{{ bot.name }}')" class="btn-action btn-log">Log</button>
                            <button onclick="openFilesTab('{{ bot.name }}')" class="btn-action btn-files">Files</button>
                            
                            <form action="/delete/{{ bot.name }}" method="post" style="display:inline;" onsubmit="return confirm('Yakin ingin menghapus bot ini?');">
                                <button type="submit" class="btn-action btn-delete" title="Hapus">🗑️</button>
                            </form>
                        </td>
                    </tr>
                    {% endfor %}
                </table>
            </div>
        </div>

        <!-- DEPLOY -->
        <div id="page-deploy" class="page">
            <div class="header"><h1>Deploy Bot</h1></div>
            
            {% if deploy_error %}
            <div class="alert-error" style="display: block;">❌ Gagal menjalankan bot!<br>Error Log:<br>{{ deploy_error }}</div>
            {% endif %}

            {% if deploy_success %}
            <div class="alert-error" style="display: block; background-color: rgba(16, 185, 129, 0.1); color: #10b981; border: 1px solid #10b981;">✅ Bot berhasil di-deploy dan sedang berjalan!</div>
            {% endif %}

            <p style="color:var(--text2); margin-bottom: 20px;">Upload ZIP bot kamu — requirements.txt akan diinstall otomatis dan bot akan langsung berjalan.</p>
            <div class="deploy-box">
                <form action="/upload" method="post" enctype="multipart/form-data">
                    <div class="form-group"><label>NAMA BOT *</label><input type="text" name="name" placeholder="my-awesome-bot" required></div>
                    <div class="form-group"><label>COMMAND *</label><input type="text" name="command" value="python3 main.py" required></div>
                    <div class="form-group"><label>FILE ZIP *</label><input type="file" name="zipfile" accept=".zip" required></div>
                    <button type="submit" class="btn btn-primary" style="width: 100%; padding: 14px; font-size: 16px;">🚀 Deploy & Run Bot</button>
                </form>
            </div>
        </div>

        <!-- FILES -->
        <div id="page-files" class="page">
            <div class="header"><h1>File Manager</h1></div>
            <div class="fm-layout">
                <div class="fm-sidebar" id="fm-bot-list"><div style="color:var(--text2); font-size:12px; font-weight:bold; margin-bottom:10px;">BOTS</div></div>
                <div class="fm-main">
                    <div class="fm-toolbar">
                        <div class="fm-path" id="fm-current-path">/ Select a bot</div>
                        <div style="display:flex; gap:10px;">
                            <button class="btn btn-primary" onclick="fmGoUp()" id="btn-up" style="display:none;">↑ Up</button>
                            <button class="btn btn-green" onclick="openEditor('', '')" id="btn-new-file" style="display:none;">+ New File</button>
                        </div>
                    </div>
                    <div class="fm-files" id="fm-file-list"><div style="text-align:center; color:var(--text2); margin-top:50px;">Select a bot to browse files</div></div>
                </div>
            </div>
        </div>
    </div>

    <!-- BOTTOM NAV -->
    <div class="bottom-nav">
        <div class="bottom-nav-item active" id="nav-monitor-mobile" onclick="showPage('monitor', document.getElementById('nav-monitor-desktop'), 'nav-monitor-mobile')">
            <svg viewBox="0 0 24 24"><path d="M21,16H3V4H21M21,2H3C1.89,2 1,2.89 1,4V16A2,2 0 0,0 3,18H10V20H8V22H16V20H14V18H21A2,2 0 0,0 23,16V4C23,2.89 22.1,2 21,2Z" /></svg>
            Monitor
        </div>
        <div class="bottom-nav-item" id="nav-bots-mobile" onclick="showPage('bots', document.getElementById('nav-bots-desktop'), 'nav-bots-mobile')">
            <svg viewBox="0 0 24 24"><path d="M12,2A2,2 0 0,1 14,4C14,4.74 13.6,5.39 13,5.73V7H14A7,7 0 0,1 21,14H22A1,1 0 0,1 23,15V18A1,1 0 0,1 22,19H21V20A2,2 0 0,1 19,22H5A2,2 0 0,1 3,20V19H2A1,1 0 0,1 1,18V15A1,1 0 0,1 2,14H3A7,7 0 0,1 10,7H11V5.73C10.4,5.39 10,4.74 10,4A2,2 0 0,1 12,2M7.5,13A2.5,2.5 0 0,0 5,15.5A2.5,2.5 0 0,0 7.5,18A2.5,2.5 0 0,0 10,15.5A2.5,2.5 0 0,0 7.5,13M16.5,13A2.5,2.5 0 0,0 14,15.5A2.5,2.5 0 0,0 16.5,18A2.5,2.5 0 0,0 19,15.5A2.5,2.5 0 0,0 16.5,13Z" /></svg>
            Bots
        </div>
        <div class="bottom-nav-item" id="nav-deploy-mobile" onclick="showPage('deploy', document.getElementById('nav-deploy-desktop'), 'nav-deploy-mobile')">
            <svg viewBox="0 0 24 24"><path d="M19,9H15V3H9V9H5L12,16L19,9M5,18V20H19V18H5Z" /></svg>
            Deploy
        </div>
        <div class="bottom-nav-item" id="nav-files-mobile" onclick="showPage('files', document.getElementById('nav-files-desktop'), 'nav-files-mobile'); loadBotsToFm();">
            <svg viewBox="0 0 24 24"><path d="M10,4H4C2.89,4 2,4.89 2,6V18A2,2 0 0,0 4,20H20A2,2 0 0,0 22,18V8C22,6.89 21.1,6 20,6H12L10,4Z" /></svg>
            Files
        </div>
    </div>

    <!-- LOG MODAL -->
    <div class="log-modal" id="log-modal">
        <div class="log-box">
            <div class="editor-header"><h3 id="log-title" style="color:white;">Logs</h3><button class="btn btn-red" onclick="closeLogs()">✕ Close</button></div>
            <div class="log-content" id="log-content"></div>
        </div>
    </div>

    <!-- EDITOR MODAL -->
    <div class="editor-modal" id="editor-modal">
        <div class="editor-box">
            <div class="editor-header"><h3 id="editor-title">Edit File</h3><button class="btn btn-red" onclick="closeEditor()">✕ Close</button></div>
            <textarea class="editor-textarea" id="editor-code" spellcheck="false"></textarea>
            <div class="editor-footer"><button class="btn btn-green" onclick="saveFile()">💾 Save File</button></div>
        </div>
    </div>

    <script>
        function showPage(pageId, elDesktop, elMobile) {
            document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
            document.getElementById('page-' + pageId).classList.add('active');
            if(elDesktop) { document.querySelectorAll('.menu li').forEach(li => li.classList.remove('active')); elDesktop.classList.add('active'); }
            if(elMobile) { document.querySelectorAll('.bottom-nav-item').forEach(li => li.classList.remove('active')); document.getElementById(elMobile).classList.add('active'); }
        }

        document.addEventListener('submit', function(e) {
            if (e.target.action.includes('/run/') || e.target.action.includes('/stop/') || e.target.action.includes('/restart/')) {
                setTimeout(() => { location.reload(); }, 1500); 
            }
        });

        let currentBot = "", currentFile = "", currentPath = "";
        function loadBotsToFm() {
            const botList = document.getElementById('fm-bot-list');
            const tableRows = document.querySelectorAll('#page-monitor table tbody tr');
            let html = '<div style="color:var(--text2); font-size:12px; font-weight:bold; margin-bottom:10px;">BOTS</div>';
            tableRows.forEach(row => {
                const nameTd = row.querySelector('td:nth-child(2)');
                if (nameTd && nameTd.innerText !== 'Nama' && !nameTd.innerText.includes('Belum')) {
                    html += `<div class="fm-bot-item" onclick="loadFiles('${nameTd.innerText}', '', this)">🤖 ${nameTd.innerText}</div>`;
                }
            });
            botList.innerHTML = html;
        }

        async function loadFiles(botName, path, el) {
            if(el) { document.querySelectorAll('.fm-bot-item').forEach(i => i.classList.remove('active')); el.classList.add('active'); }
            currentBot = botName; currentPath = path;
            document.getElementById('fm-current-path').innerText = `/ ${botName} ${path ? '/ ' + path : ''}`;
            document.getElementById('btn-new-file').style.display = 'inline-block';
            document.getElementById('btn-up').style.display = path ? 'inline-block' : 'none';
            
            const res = await fetch(`/api/files/${botName}?path=${path}`);
            const files = await res.json();
            
            let html = '';
            files.forEach(f => { 
                if (f.type === 'dir') {
                    html += `<div class="fm-item" onclick="loadFiles('${botName}', '${f.path}', null)"><div class="fm-item-name">📁 ${f.name}</div><button class="btn btn-primary" style="padding:4px 8px; font-size:11px;">Buka</button></div>`;
                } else {
                    html += `<div class="fm-item" onclick="openEditor('${f.path}', '${botName}')"><div class="fm-item-name">📄 ${f.name}</div><button class="btn btn-primary" style="padding:4px 8px; font-size:11px;">Edit</button></div>`; 
                }
            });
            document.getElementById('fm-file-list').innerHTML = html || '<div style="color:var(--text2);">Folder kosong.</div>';
        }

        function fmGoUp() { let parts = currentPath.split('/').filter(p => p); parts.pop(); loadFiles(currentBot, parts.join('/'), null); }
        async function openEditor(filepath, botName) {
            if (filepath) { currentFile = filepath; document.getElementById('editor-title').innerText = `Edit: ${filepath}`; const res = await fetch(`/api/read/${botName}/${filepath}`); document.getElementById('editor-code').value = await res.text(); } 
            else { currentFile = prompt("Nama file baru:"); if (!currentFile) return; document.getElementById('editor-title').innerText = `Baru: ${currentFile}`; document.getElementById('editor-code').value = ""; }
            document.getElementById('editor-modal').style.display = 'flex';
        }
        async function saveFile() {
            const code = document.getElementById('editor-code').value;
            await fetch(`/api/save/${currentBot}/${currentFile}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ code: code }) });
            alert('Berhasil disimpan!'); closeEditor(); loadFiles(currentBot, currentPath, null);
        }
        function closeEditor() { document.getElementById('editor-modal').style.display = 'none'; }

        function openFilesTab(botName) {
            showPage('files', document.getElementById('nav-files-desktop'), 'nav-files-mobile');
            loadBotsToFm();
            setTimeout(() => { 
                const items = document.querySelectorAll('.fm-bot-item');
                items.forEach(item => { if(item.innerText.includes(botName)) { item.click(); } });
            }, 100);
        }

        let logInterval;
        async function viewLogs(botName) {
            document.getElementById('log-title').innerText = `Logs: ${botName}`;
            document.getElementById('log-modal').style.display = 'flex';
            document.getElementById('log-content').innerText = "Memuat log...\n";
            clearInterval(logInterval);
            logInterval = setInterval(async () => {
                const res = await fetch(`/api/logs/${botName}`);
                const text = await res.text();
                const logBox = document.getElementById('log-content');
                logBox.innerText = text || "Belum ada log...";
                logBox.scrollTop = logBox.scrollHeight;
            }, 2000);
        }
        function closeLogs() { document.getElementById('log-modal').style.display = 'none'; clearInterval(logInterval); }
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

    try:
        process = subprocess.Popen(["python3", "main.py"], cwd=bot_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(3) 
        poll = process.poll()
        if poll is not None: 
            _, stderr = process.communicate()
            error_msg = stderr.decode('utf-8')
            error_msg = error_msg.strip().split('\n')[-1] if error_msg else "Unknown Error (Script langsung berhenti)"
            disk = psutil.disk_usage('/').percent
            return render_template_string(HTML, bots=[], cpu=psutil.cpu_percent(), ram=psutil.virtual_memory().percent, disk=disk, deploy_error=error_msg)
        else:
            return render_template_string(HTML, bots=[], cpu=psutil.cpu_percent(), ram=psutil.virtual_memory().percent, disk=psutil.disk_usage('/').percent, deploy_success=True)
    except Exception as e:
        disk = psutil.disk_usage('/').percent
        return render_template_string(HTML, bots=[], cpu=psutil.cpu_percent(), ram=psutil.virtual_memory().percent, disk=disk, deploy_error=str(e))

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

@app.route('/restart/<bot_name>', methods=['POST'])
def restart_bot(bot_name):
    for p in psutil.process_iter(['pid', 'cmdline']):
        try:
            cmdline = " ".join(p.info['cmdline'] or [])
            if bot_name in cmdline and "main.py" in cmdline: p.kill()
        except: pass
    bot_path = os.path.join(BOTS_DIR, bot_name)
    subprocess.Popen(["python3", "main.py"], cwd=bot_path, start_new_session=True)
    return redirect(url_for('index'))

@app.route('/delete/<bot_name>', methods=['POST'])
def delete_bot(bot_name):
    bot_path = os.path.join(BOTS_DIR, bot_name)
    if os.path.exists(bot_path):
        for p in psutil.process_iter(['pid', 'cmdline']):
            try:
                cmdline = " ".join(p.info['cmdline'] or [])
                if bot_name in cmdline and "main.py" in cmdline: p.kill()
            except: pass
        shutil.rmtree(bot_path)
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
            if os.path.isdir(full_path): items.append({"name": f, "type": "dir", "path": item_rel_path})
            else: items.append({"name": f, "type": "file", "path": item_rel_path})
        return jsonify(items)
    return jsonify([])

@app.route('/api/read/<bot_name>/<path:filename>')
def api_read(bot_name, filename):
    file_path = os.path.join(BOTS_DIR, bot_name, filename)
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f: return f.read()
        except: return "File tidak bisa dibaca (format biner/gambar).", 400
    return "File not found", 404

@app.route('/api/save/<bot_name>/<path:filename>', methods=['POST'])
def api_save(bot_name, filename):
    data = request.get_json()
    file_path = os.path.join(BOTS_DIR, bot_name, filename)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f: f.write(data['code'])
    return jsonify({"status": "success"})

@app.route('/api/logs/<bot_name>')
def api_logs(bot_name):
    return f"Log untuk {bot_name} sedang dimuat..."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=2121)