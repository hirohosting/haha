from flask import Flask, render_template_string, request, redirect, url_for, jsonify, session
import os, subprocess, zipfile, psutil, time, shutil, sys, shlex
from functools import wraps
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "HiroCloud_Super_Secret_Key"
BOTS_DIR = "bots"
os.makedirs(BOTS_DIR, exist_ok=True)

HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HiroCloud</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;500;600;700;800&display=swap');
        :root { --bg: #0b0f19; --panel: #111827; --border: #1f2937; --text: #e2e8f0; --text2: #9ca3af; --primary: #38bdf8; --green: #10b981; --red: #ef4444; --purple: #8b5cf6; }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', sans-serif; }
        body { background-color: var(--bg); color: var(--text); display: flex; height: 100vh; overflow: hidden; }
        
        .sidebar { width: 240px; background: var(--panel); border-right: 1px solid var(--border); display: flex; flex-direction: column; padding: 20px 0; z-index: 10;}
        .logo { font-size: 24px; font-weight: 800; color: var(--primary); padding: 0 24px 30px; display: flex; align-items: center; gap: 10px; }
        .logo span { color: var(--text); }
        .menu { list-style: none; }
        .menu li { padding: 15px 24px; color: var(--text2); cursor: pointer; display: flex; align-items: center; gap: 12px; font-weight: 600; font-size: 15px; transition: 0.2s; position: relative;}
        .menu li:hover, .menu li.active { background: rgba(56, 189, 248, 0.1); color: var(--primary); border-right: 3px solid var(--primary); }
        
        .main { flex: 1; padding: 30px; overflow-y: auto; width: 100%; position: relative; z-index: 1; }
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }
        .header h1 { font-size: 28px; font-weight: 800; }
        .os-info { font-family: 'JetBrains Mono', monospace; font-size: 12px; color: var(--text2); background: var(--panel); padding: 8px 16px; border-radius: 8px; border: 1px solid var(--border); display: flex; gap: 15px; flex-wrap: wrap;}
        
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .card { background: var(--panel); padding: 20px; border-radius: 12px; border: 1px solid var(--border); }
        .card-title { font-size: 12px; color: var(--text2); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px; font-weight: 700; }
        .card-val { font-size: 32px; font-weight: 800; font-family: 'JetBrains Mono', monospace; }
        .bar-bg { width: 100%; height: 6px; background: var(--border); border-radius: 3px; margin-top: 15px; overflow: hidden; }
        .bar-fill { height: 100%; background: var(--purple); border-radius: 3px; transition: width 0.5s; }
        
        .section-title { font-size: 18px; font-weight: 800; margin-bottom: 15px; display: flex; justify-content: space-between; align-items: center; }
        .btn { padding: 8px 16px; border-radius: 6px; border: none; font-weight: 700; cursor: pointer; transition: 0.2s; font-size: 13px; text-decoration: none; display: inline-flex; align-items:center; justify-content:center; gap:5px; z-index: 5; position: relative;}
        .btn-green { background: var(--green); color: #fff; }
        .btn-primary { background: var(--primary); color: #000; }
        .btn-stop { color: #f43f5e; border: 1px solid #4c0519; background: rgba(244, 63, 94, 0.1); padding: 8px 12px; border-radius: 6px; font-weight: 600; font-size: 13px; cursor: pointer; text-decoration: none; display: inline-flex; align-items: center; gap: 6px; }
        .btn-restart { color: #eab308; border: 1px solid #422006; background: rgba(234, 179, 8, 0.1); padding: 8px 10px; border-radius: 6px; font-weight: 600; font-size: 13px; cursor: pointer; text-decoration: none; display: inline-flex; align-items: center; gap: 6px;}
        .btn-log { color: #38bdf8; border: 1px solid #082f49; background: rgba(56, 189, 248, 0.1); padding: 8px 12px; border-radius: 6px; font-weight: 600; font-size: 13px; cursor: pointer; text-decoration: none; display: inline-flex; align-items: center; gap: 6px;}
        .btn-files { color: #e2e8f0; border: 1px solid #334155; background: rgba(255, 255, 255, 0.05); padding: 8px 12px; border-radius: 6px; font-weight: 600; font-size: 13px; cursor: pointer; text-decoration: none; display: inline-flex; align-items: center; gap: 6px;}
        .btn-delete { color: #f43f5e; border: 1px solid #4c0519; background: transparent; padding: 8px 10px; border-radius: 6px; font-weight: 600; font-size: 13px; cursor: pointer; text-decoration: none; display: inline-flex; align-items: center; gap: 6px;}
        
        .table-wrap { width: 100%; overflow-x: auto; -webkit-overflow-scrolling: touch; }
        table { width: 100%; border-collapse: collapse; background: var(--panel); border-radius: 12px; overflow: hidden; border: 1px solid var(--border); min-width: 700px; }
        th, td { padding: 16px; text-align: left; border-bottom: 1px solid var(--border); font-size: 14px; }
        th { background: rgba(255,255,255,0.02); color: var(--text2); font-weight: 600; }
        .badge { padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 700; font-family: 'JetBrains Mono', monospace; }
        .badge-run { background: rgba(16, 185, 129, 0.15); color: var(--green); border: 1px solid var(--green); }
        .badge-stop { background: rgba(239, 68, 68, 0.15); color: var(--red); border: 1px solid var(--red); }
        
        /* --- CSS DEPLOY BOX BARU --- */
        .deploy-box { background: var(--panel); padding: 30px; border-radius: 12px; border: 1px solid var(--border); margin-bottom: 30px; max-width: 700px; }
        .form-group { margin-bottom: 25px; }
        .form-group label { display: block; margin-bottom: 8px; font-size: 13px; color: var(--text2); font-weight: 700; letter-spacing: 1px; text-transform: uppercase; }
        .form-group label span { color: var(--red); }
        .form-group input[type="text"] { width: 100%; padding: 14px; background: rgba(0,0,0,0.2); border: 1px solid var(--border); color: var(--text); border-radius: 8px; font-family: 'JetBrains Mono', monospace; font-size: 14px; }
        .form-group input[type="text"]:focus { outline: none; border-color: var(--primary); }
        .form-group small { display: block; margin-top: 6px; font-size: 12px; color: var(--text2); }
        
        .drop-zone { border: 2px dashed var(--border); border-radius: 12px; padding: 40px 20px; text-align: center; cursor: pointer; transition: 0.2s; background: rgba(255,255,255,0.01); position: relative; }
        .drop-zone:hover, .drop-zone.dragover { border-color: var(--primary); background: rgba(56, 189, 248, 0.05); }
        .drop-zone svg { width: 48px; height: 48px; fill: var(--text2); margin-bottom: 15px; }
        .drop-zone h3 { font-size: 16px; margin-bottom: 5px; color: var(--text); }
        .drop-zone p { font-size: 13px; color: var(--text2); }
        .drop-zone input[type="file"] { position: absolute; top: 0; left: 0; width: 100%; height: 100%; opacity: 0; cursor: pointer; }
        .file-name-display { margin-top: 10px; font-size: 13px; color: var(--primary); font-weight: bold; font-family: 'JetBrains Mono', monospace; }

        .page { display: none; }
        .page.active { display: block; }
        
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
        
        /* MODAL EDITOR - DIPERBAIKI: UKURAN MENYESUAIKAN KODE */
        .editor-modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); z-index: 10000; justify-content: center; align-items: center; }
        .editor-box { background: var(--panel); width: 90%; max-width: 1000px; max-height: 80vh; border-radius: 12px; border: 1px solid var(--border); display: flex; flex-direction: column; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.8); }
        .editor-header { padding: 15px 20px; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; flex-shrink: 0; }
        .editor-textarea { flex: 1; width: 100%; min-height: 200px; background: var(--bg); color: #a78bfa; border: none; padding: 20px; font-family: 'JetBrains Mono', monospace; font-size: 14px; resize: none; outline: none; line-height: 1.5; overflow-y: auto; }
        .editor-footer { padding: 15px 20px; border-top: 1px solid var(--border); display: flex; justify-content: flex-end; gap: 10px; flex-shrink: 0; }
        
        .log-modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); z-index: 10000; justify-content: center; align-items: center; }
        .log-box { background: #000; width: 90%; height: 80%; border-radius: 12px; border: 1px solid var(--border); display: flex; flex-direction: column; }
        .log-content { flex: 1; color: #10b981; padding: 20px; font-family: 'JetBrains Mono', monospace; font-size: 13px; overflow-y: auto; white-space: pre-wrap; }

        .login-box { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); background: var(--panel); padding: 40px; border-radius: 12px; border: 1px solid var(--border); width: 90%; max-width: 350px; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
        .login-box h2 { margin-bottom: 20px; color: var(--primary); font-size: 28px; display: flex; justify-content: center; align-items: center; gap:10px;}

        .bottom-nav { display: none; position: fixed; bottom: 0; left: 0; width: 100%; background-color: #0d1321; border-top: 1px solid var(--border); justify-content: space-around; align-items: center; padding: 10px 0; z-index: 99999; }
        .bottom-nav-item { display: flex; flex-direction: column; align-items: center; color: #7b8b9e; font-size: 12px; font-weight: 600; cursor: pointer; text-decoration: none; gap: 4px; padding: 8px 15px; border-radius: 8px; transition: 0.2s; position: relative;}
        .bottom-nav-item.active { color: var(--primary); background-color: rgba(56, 189, 248, 0.1); }
        .bottom-nav-item svg { width: 24px; height: 24px; fill: currentColor; }

        @media (max-width: 768px) {
            body { flex-direction: column; }
            .sidebar { display: none; }
            .main { padding: 15px; padding-bottom: 90px; }
            .fm-layout { flex-direction: column; height: auto; }
            .fm-sidebar { width: 100%; max-height: 200px; }
            .bottom-nav { display: flex; }
            
            th:nth-child(3), td:nth-child(3),
            th:nth-child(4), td:nth-child(4) { display: none; }
            
            table { min-width: 100%; }
            th, td { padding: 12px 8px; font-size: 13px; }
            
            .btn-action { padding: 10px 14px; font-size: 12px; margin-bottom: 4px; }
            td[style*="display:flex"] { display: flex !important; flex-wrap: wrap !important; gap: 8px !important; justify-content: flex-start !important; }
            
            .editor-textarea { min-height: 150px; }
        }

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
                        <td style="font-family: monospace; color: var(--text2);">{{ bot.command }}</td>
                        <td style="font-family: monospace; color: var(--text2);">{{ bot.pid }}</td>
                        <td style="display:flex; gap:8px; flex-wrap:wrap;">
                            <form action="/stop/{{ bot.name }}" method="post" style="display:inline;">
                                <button type="submit" class="btn-stop" title="Stop">■ Stop</button>
                            </form>
                            <form action="/restart/{{ bot.name }}" method="post" style="display:inline;">
                                <button type="submit" class="btn-restart" title="Restart">↻</button>
                            </form>
                            <button type="button" onclick="viewLogs('{{ bot.name }}')" class="btn-log">Log</button>
                            <button type="button" onclick="openFilesTab('{{ bot.name }}')" class="btn-files">Files</button>
                            <form action="/delete/{{ bot.name }}" method="post" style="display:inline;" onsubmit="return confirm('Yakin ingin menghapus bot ini?');">
                                <button type="submit" class="btn-delete" title="Hapus">🗑️</button>
                            </form>
                        </td>
                    </tr>
                    {% else %}<tr><td colspan="5" style="text-align:center; color:var(--text2);">Belum ada bot.</td></tr>{% endfor %}
                </table>
            </div>
        </div>

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
                        <td style="font-family: monospace; color: var(--text2);">{{ bot.command }}</td>
                        <td style="font-family: monospace; color: var(--text2);">{{ bot.pid }}</td>
                        <td style="display:flex; gap:8px; flex-wrap:wrap;">
                            <form action="/stop/{{ bot.name }}" method="post" style="display:inline;">
                                <button type="submit" class="btn-stop" title="Stop">■ Stop</button>
                            </form>
                            <form action="/restart/{{ bot.name }}" method="post" style="display:inline;">
                                <button type="submit" class="btn-restart" title="Restart">↻</button>
                            </form>
                            <button type="button" onclick="viewLogs('{{ bot.name }}')" class="btn-log">Log</button>
                            <button type="button" onclick="openFilesTab('{{ bot.name }}')" class="btn-files">Files</button>
                            <form action="/delete/{{ bot.name }}" method="post" style="display:inline;" onsubmit="return confirm('Yakin ingin menghapus bot ini?');">
                                <button type="submit" class="btn-delete" title="Hapus">🗑️</button>
                            </form>
                        </td>
                    </tr>
                    {% endfor %}
                </table>
            </div>
        </div>

        <div id="page-deploy" class="page">
            <div class="header"><h1>Deploy Bot</h1></div>
            
            {% if deploy_error %}
            <div class="alert-error" style="display: block;">❌ Gagal menjalankan bot!<br>Error Log:<br>{{ deploy_error }}</div>
            {% endif %}

            {% if deploy_success %}
            <div class="alert-error" style="display: block; background-color: rgba(16, 185, 129, 0.1); color: #10b981; border: 1px solid #10b981;">✅ Bot berhasil di-deploy dan sedang berjalan!</div>
            {% endif %}

            <p style="color:var(--text2); margin-bottom: 20px;">Upload ZIP bot kamu — requirements.txt akan diinstall otomatis.</p>
            <div class="deploy-box">
                <form action="/upload" method="post" enctype="multipart/form-data" id="deployForm">
                    <div class="form-group">
                        <label>NAMA BOT <span>*</span></label>
                        <input type="text" name="name" placeholder="my-awesome-bot" required>
                        <small>Huruf kecil, angka, dan tanda hubung. Contoh: trading-bot</small>
                    </div>
                    <div class="form-group">
                        <label>COMMAND <span>*</span></label>
                        <input type="text" name="command" value="python3 main.py" required>
                        <small>Perintah untuk menjalankan bot setelah deploy.</small>
                    </div>
                    <div class="form-group">
                        <label>FILE ZIP <span>*</span></label>
                        <div class="drop-zone" id="dropZone">
                            <input type="file" name="zipfile" id="zipInput" accept=".zip" required>
                            <svg viewBox="0 0 24 24"><path d="M19,9H15V3H9V9H5L12,16L19,9M5,18V20H19V18H5Z" /></svg>
                            <h3 id="dropText">Drop file ZIP di sini</h3>
                            <p>atau klik untuk browse</p>
                            <div class="file-name-display" id="fileName"></div>
                        </div>
                        <small>ZIP harus mengandung main.py di root folder.</small>
                    </div>
                    <button type="submit" class="btn btn-primary" style="width: 100%; padding: 14px; font-size: 16px; margin-top:10px;">🚀 Deploy Bot</button>
                </form>
            </div>
        </div>

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

    <div class="log-modal" id="log-modal">
        <div class="log-box">
            <div class="editor-header"><h3 id="log-title" style="color:white;">Logs</h3><button class="btn-stop" onclick="closeLogs()">✕ Close</button></div>
            <div class="log-content" id="log-content"></div>
        </div>
    </div>

    <div class="editor-modal" id="editor-modal">
        <div class="editor-box">
            <div class="editor-header"><h3 id="editor-title">Edit File</h3><button class="btn-stop" onclick="closeEditor()">✕ Close</button></div>
            <textarea class="editor-textarea" id="editor-code" spellcheck="false"></textarea>
            <div class="editor-footer"><button class="btn-green" onclick="saveFile()">💾 Save File</button></div>
        </div>
    </div>

    <script>
        window.onerror = function(message, source, lineno, colno, error) {
            alert("⚠️ TERJADI ERROR JAVASCRIPT!\n\nPesan: " + message + "\nBaris: " + lineno + "\n\nSilakan screenshot pesan ini dan kirim ke pembuat script.");
            return false;
        };

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

        // --- JS DRAG & DROP ZIP ---
        const dropZone = document.getElementById('dropZone');
        const zipInput = document.getElementById('zipInput');
        const dropText = document.getElementById('dropText');
        const fileName = document.getElementById('fileName');

        if(zipInput) {
            zipInput.addEventListener('change', function() {
                if(this.files && this.files.length > 0) {
                    fileName.innerText = "📦 " + this.files[0].name;
                    dropText.innerText = "File terpilih";
                }
            });
        }

        if(dropZone) {
            ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
                dropZone.addEventListener(eventName, preventDefaults, false);
            });
            function preventDefaults (e) { e.preventDefault(); e.stopPropagation(); }
            ['dragenter', 'dragover'].forEach(eventName => {
                dropZone.addEventListener(eventName, () => dropZone.classList.add('dragover'), false);
            });
            ['dragleave', 'drop'].forEach(eventName => {
                dropZone.addEventListener(eventName, () => dropZone.classList.remove('dragover'), false);
            });
            dropZone.addEventListener('drop', handleDrop, false);
            function handleDrop(e) {
                let dt = e.dataTransfer;
                let files = dt.files;
                zipInput.files = files;
                if(files.length > 0) {
                    fileName.innerText = "📦 " + files[0].name;
                    dropText.innerText = "File terpilih";
                }
            }
        }

        // --- FILE MANAGER & LOGS JS ---
        let currentBot = "", currentFile = "", currentPath = "";
        
        function loadBotsToFm() {
            const botList = document.getElementById('fm-bot-list');
            const tableRows = document.querySelectorAll('#page-monitor table tbody tr');
            let html = '<div style="color:var(--text2); font-size:12px; font-weight:bold; margin-bottom:10px;">BOTS</div>';
            tableRows.forEach(row => {
                const nameTd = row.querySelector('td:nth-child(2)');
                if (nameTd && nameTd.innerText !== 'Nama' && !nameTd.innerText.includes('Belum')) {
                    html += "<div class='fm-bot-item' onclick=\"loadFiles('" + nameTd.innerText + "', '', this)\">🤖 " + nameTd.innerText + "</div>";
                }
            });
            botList.innerHTML = html;
        }

        async function loadFiles(botName, path, el) {
            if(el) { document.querySelectorAll('.fm-bot-item').forEach(i => i.classList.remove('active')); el.classList.add('active'); }
            currentBot = botName; currentPath = path;
            document.getElementById('fm-current-path').innerText = '/ ' + botName + ' ' + (path ? '/ ' + path : '');
            document.getElementById('btn-new-file').style.display = 'inline-block';
            document.getElementById('btn-up').style.display = path ? 'inline-block' : 'none';
            
            const res = await fetch('/api/files/' + botName + '?path=' + path);
            const files = await res.json();
            
            let html = '';
            files.forEach(f => { 
                if (f.type === 'dir') {
                    html += "<div class='fm-item'><div class='fm-item-name' onclick=\"loadFiles('" + botName + "', '" + f.path + "', null)\">📁 " + f.name + "</div><div style='display:flex;gap:5px;'><button class='btn btn-primary' onclick=\"loadFiles('" + botName + "', '" + f.path + "', null)\" style='padding:4px 8px; font-size:11px;'>Buka</button><button class='btn btn-stop' onclick=\"deleteFile('" + botName + "', '" + f.path + "')\" style='padding:4px 8px; font-size:11px;'>Hapus</button></div></div>";
                } else {
                    html += "<div class='fm-item'><div class='fm-item-name' onclick=\"openEditor('" + f.path + "', '" + botName + "')\">📄 " + f.name + "</div><div style='display:flex;gap:5px;'><button class='btn btn-primary' onclick=\"openEditor('" + f.path + "', '" + botName + "')\" style='padding:4px 8px; font-size:11px;'>Edit</button><button class='btn btn-stop' onclick=\"deleteFile('" + botName + "', '" + f.path + "')\" style='padding:4px 8px; font-size:11px;'>Hapus</button></div></div>"; 
                }
            });
            document.getElementById('fm-file-list').innerHTML = html || '<div style="color:var(--text2);">Folder kosong.</div>';
        }

        function fmGoUp() { let parts = currentPath.split('/').filter(p => p); parts.pop(); loadFiles(currentBot, parts.join('/'), null); }
        
        async function openEditor(filepath, botName) {
            if (filepath) { 
                currentFile = filepath; 
                document.getElementById('editor-title').innerText = 'Edit: ' + filepath; 
                const res = await fetch('/api/read/' + botName + '/' + filepath); 
                const text = await res.text();
                const textarea = document.getElementById('editor-code');
                textarea.value = text;
                
                // LOGIKA AUTO-HEIGHT: Menyesuaikan tinggi textarea dengan jumlah baris
                let lines = text.split('\n').length;
                let lineHeight = 21; // Estimasi tinggi per baris dalam px
                let newHeight = (lines * lineHeight) + 40;
                // Batasi maksimal tinggi agar tidak keluar layar
                if(newHeight > window.innerHeight * 0.6) newHeight = window.innerHeight * 0.6;
                if(newHeight < 200) newHeight = 200; // Minimal tinggi
                
                textarea.style.height = newHeight + 'px';
            } else { 
                currentFile = prompt("Nama file baru:"); 
                if (!currentFile) return; 
                document.getElementById('editor-title').innerText = 'Baru: ' + currentFile; 
                document.getElementById('editor-code').value = ""; 
                document.getElementById('editor-code').style.height = '200px';
            }
            document.getElementById('editor-modal').style.display = 'flex';
        }
        
        async function saveFile() {
            const code = document.getElementById('editor-code').value;
            await fetch('/api/save/' + currentBot + '/' + currentFile, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ code: code }) });
            alert('Berhasil disimpan!'); closeEditor(); loadFiles(currentBot, currentPath, null);
        }
        function closeEditor() { document.getElementById('editor-modal').style.display = 'none'; }

        async function deleteFile(botName, filepath) {
            if(confirm('Yakin ingin menghapus file/folder ' + filepath + ' ini?')) {
                await fetch('/api/delete/' + botName + '/' + filepath, { method: 'DELETE' });
                loadFiles(botName, currentPath, null);
            }
        }

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
            document.getElementById('log-title').innerText = 'Logs: ' + botName;
            document.getElementById('log-modal').style.display = 'flex';
            document.getElementById('log-content').innerText = "Memuat log...\n";
            clearInterval(logInterval);
            logInterval = setInterval(async () => {
                const res = await fetch('/api/logs/' + botName);
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

def login_required(f):
    @wraps(f)
    def wrap(*a, **k):
        if not session.get('logged_in'):
            return redirect(url_for('index'))
        return f(*a, **k)
    return wrap

def bot_dir(name):
    return os.path.abspath(os.path.join(BOTS_DIR, secure_filename(name)))

def safe_path(bot, rel=""):
    base = bot_dir(bot)
    full = os.path.abspath(os.path.join(base, rel))
    if full != base and not full.startswith(base + os.sep):
        raise ValueError("path ilegal")
    return full

def bot_procs(name):
    path = bot_dir(name)
    res = []
    for p in psutil.process_iter(['pid', 'cwd']):
        try:
            if p.info['cwd'] == path:
                res.append(p)
        except Exception:
            pass
    return res

def kill_bot(name):
    for p in bot_procs(name):
        try: p.kill()
        except Exception: pass

def start_bot(name):
    path = bot_dir(name)
    cmd_file = os.path.join(path, ".command")
    cmd = "python3 main.py"
    if os.path.exists(cmd_file):
        cmd = open(cmd_file).read().strip() or cmd
    log = open(os.path.join(path, "bot.log"), "a")
    return subprocess.Popen(shlex.split(cmd), cwd=path, stdout=log,
                            stderr=subprocess.STDOUT, start_new_session=True)

def get_bots():
    bots = []
    for name in sorted(os.listdir(BOTS_DIR)):
        if os.path.isdir(os.path.join(BOTS_DIR, name)):
            procs = bot_procs(name)
            cmd_path = os.path.join(BOTS_DIR, name, ".command")
            cmd_text = "python3 main.py"
            if os.path.exists(cmd_path):
                try:
                    cmd_text = open(cmd_path).read().strip() or cmd_text
                except Exception:
                    pass
            
            bots.append({
                "name": name, 
                "running": bool(procs),
                "pid": procs[0].pid if procs else "-",
                "command": cmd_text
            })
    return bots

def page(**kw):
    return render_template_string(
        HTML, cpu=psutil.cpu_percent(), ram=psutil.virtual_memory().percent,
        disk=psutil.disk_usage('/').percent, bots=get_bots(), **kw)

@app.route('/login', methods=['POST'])
def login():
    if request.form['username'] == 'admin' and request.form['password'] == 'admin123':
        session['logged_in'] = True
        return redirect(url_for('index'))
    return render_template_string(HTML, error="Username/Password Salah",
                                  bots=[], cpu=0, ram=0, disk=0)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

@app.route('/')
def index():
    if not session.get('logged_in'):
        return render_template_string(HTML, bots=[], cpu=0, ram=0, disk=0)
    return page()

@app.route('/upload', methods=['POST'])
@login_required
def upload():
    name = secure_filename(request.form['name'])
    command = request.form.get('command', 'python3 main.py').strip()
    if not name:
        return page(deploy_error="Nama bot tidak valid")
    bot_path = bot_dir(name)
    kill_bot(name)
    os.makedirs(bot_path, exist_ok=True)

    zip_path = os.path.join(bot_path, "bot.zip")
    request.files['zipfile'].save(zip_path)
    try:
        with zipfile.ZipFile(zip_path) as z:
            for m in z.namelist():  # cegah zip-slip
                t = os.path.abspath(os.path.join(bot_path, m))
                if not t.startswith(bot_path + os.sep):
                    return page(deploy_error="ZIP berisi path berbahaya")
            z.extractall(bot_path)
    except zipfile.BadZipFile:
        return page(deploy_error="File ZIP rusak")
    finally:
        if os.path.exists(zip_path):
            os.remove(zip_path)

    if not os.path.exists(os.path.join(bot_path, "main.py")):
        subs = [d for d in os.listdir(bot_path)
                if os.path.isdir(os.path.join(bot_path, d))]
        if len(subs) == 1:
            inner = os.path.join(bot_path, subs[0])
            for f in os.listdir(inner):
                shutil.move(os.path.join(inner, f), bot_path)
            os.rmdir(inner)

    open(os.path.join(bot_path, ".command"), "w").write(command)

    req = os.path.join(bot_path, "requirements.txt")
    if os.path.exists(req):
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", req, "--break-system-packages"])

    open(os.path.join(bot_path, "bot.log"), "w").close()
    proc = start_bot(name)
    time.sleep(3)
    if proc.poll() is not None:
        log = open(os.path.join(bot_path, "bot.log"), errors="ignore").read()
        return page(deploy_error=log.strip()[-800:] or "Script langsung berhenti")
    
    return page(deploy_success=True)

@app.route('/run/<bot_name>', methods=['POST'])
@login_required
def run_bot(bot_name):
    if not bot_procs(bot_name):
        start_bot(bot_name)
    return redirect(url_for('index'))

@app.route('/stop/<bot_name>', methods=['POST'])
@login_required
def stop_bot(bot_name):
    kill_bot(bot_name)
    return redirect(url_for('index'))

@app.route('/restart/<bot_name>', methods=['POST'])
@login_required
def restart_bot(bot_name):
    kill_bot(bot_name)
    time.sleep(0.5)
    start_bot(bot_name)
    return redirect(url_for('index'))

@app.route('/delete/<bot_name>', methods=['POST'])
@login_required
def delete_bot(bot_name):
    kill_bot(bot_name)
    p = bot_dir(bot_name)
    if os.path.isdir(p):
        shutil.rmtree(p)
    return redirect(url_for('index'))

@app.route('/api/files/<bot_name>')
@login_required
def api_files(bot_name):
    rel = request.args.get('path', '')
    try:
        p = safe_path(bot_name, rel)
    except ValueError:
        return jsonify([])
    if not os.path.isdir(p):
        return jsonify([])
    items = []
    for f in sorted(os.listdir(p)):
        items.append({"name": f,
                      "type": "dir" if os.path.isdir(os.path.join(p, f)) else "file",
                      "path": os.path.join(rel, f)})
    return jsonify(items)

@app.route('/api/read/<bot_name>/<path:filename>')
@login_required
def api_read(bot_name, filename):
    try:
        p = safe_path(bot_name, filename)
    except ValueError:
        return "Path ilegal", 400
    if not os.path.isfile(p):
        return "File not found", 404
    try:
        return open(p, encoding='utf-8').read()
    except Exception:
        return "File tidak bisa dibaca (format biner/gambar).", 400

@app.route('/api/save/<bot_name>/<path:filename>', methods=['POST'])
@login_required
def api_save(bot_name, filename):
    try:
        p = safe_path(bot_name, filename)
    except ValueError:
        return jsonify({"status": "error"}), 400
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(request.get_json()['code'])
    return jsonify({"status": "success"})

# FITUR BARU: ENDPOINT UNTUK HAPUS FILE/FOLDER DARI FILE MANAGER
@app.route('/api/delete/<bot_name>/<path:filename>', methods=['DELETE'])
@login_required
def api_delete_file(bot_name, filename):
    try:
        p = safe_path(bot_name, filename)
        if os.path.isdir(p):
            shutil.rmtree(p)
        elif os.path.isfile(p):
            os.remove(p)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)}), 400

@app.route('/api/logs/<bot_name>')
@login_required
def api_logs(bot_name):
    p = os.path.join(bot_dir(bot_name), "bot.log")
    if not os.path.exists(p):
        return ""
    return open(p, errors="ignore").read()[-5000:]

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=2121, threaded=True)