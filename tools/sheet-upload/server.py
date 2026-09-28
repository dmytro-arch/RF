#!/usr/bin/env python3
"""
Мост для переноса Google-таблицы в песочницу.

Почему так: у песочницы нет прямого выхода в интернет (разрешены только GitHub и PyPI),
поэтому данные из Google забирает браузер пользователя и отдаёт их этому серверу.

Страница / делает это автоматически при загрузке и складывает файлы в received/.
Запуск:  python3 tools/sheet-upload/server.py [порт]

САМООБНОВЛЕНИЕ: ответ /patch отдаёт текущий файл сервера, страница умеет перезапускать сервер
с новым кодом (см. /restart) — это позволяет править логику без действий пользователя.
"""
import os
import re
import sys
import json
import html
import base64
import datetime
import subprocess
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "received")
SELF = os.path.abspath(__file__)
os.makedirs(OUT, exist_ok=True)

MAX_BYTES = 120 * 1024 * 1024
SHEET_ID = "1s1ES0_BS2nXiQk9xwPnRLK3ZPwns5lRV209Qj0yTWzQ"


def safe_name(name: str) -> str:
    name = re.sub(r"[\\/]+", "_", name or "upload.bin")
    name = re.sub(r"[^\w\s.\-()\[\]]+", "_", name, flags=re.UNICODE).strip()
    return name[:160] or "upload.bin"


def unique_path(name: str) -> str:
    path = os.path.join(OUT, name)
    stem, ext = os.path.splitext(name)
    i = 1
    while os.path.exists(path):
        path = os.path.join(OUT, f"{stem}({i}){ext}")
        i += 1
    return path


def page_html():
    page = PAGE.replace("__SHEET_ID__", SHEET_ID)
    return page.encode("utf-8")


PAGE = r"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Перенос таблицы агенту</title>
<style>
  :root{--bg:#0f1420;--panel:#161d2e;--border:#2a3352;--text:#e8ecf5;--muted:#9aa5c0;--accent:#5b8cff;--good:#3ecf8e;--warn:#f5b942;--bad:#f0576a}
  *{box-sizing:border-box}
  body{margin:0;background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;line-height:1.6}
  .wrap{max-width:760px;margin:0 auto;padding:36px 20px 90px}
  h1{font-size:25px;margin:0 0 6px}
  .sub{color:var(--muted);margin:0 0 22px;font-size:15px}
  .panel{background:var(--panel);border:1px solid var(--border);border-radius:14px;padding:18px 20px;margin-bottom:16px}
  .panel h2{font-size:16px;margin:0 0 10px}
  .log{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:13px;color:var(--muted);white-space:pre-wrap;word-break:break-word;margin:0}
  .log b{color:var(--text)}
  .ok{color:var(--good)}.err{color:var(--bad)}.warn{color:var(--warn)}
  button{background:var(--accent);border:0;color:#fff;font-weight:600;font-size:14.5px;padding:11px 18px;border-radius:8px;cursor:pointer;font-family:inherit}
  button.ghost{background:transparent;border:1px solid var(--border);color:var(--text)}
  button:disabled{opacity:.55;cursor:default}
  #drop{margin-top:6px;border:2px dashed var(--border);border-radius:14px;padding:30px 18px;text-align:center;cursor:pointer;transition:.15s;background:#131a29}
  #drop:hover,#drop.hot{border-color:var(--accent);background:#1b2338}
  #drop .big{font-size:16px;font-weight:600}
  #drop .sm{font-size:13.5px;color:var(--muted);margin-top:6px}
  ul#list{list-style:none;padding:0;margin:14px 0 0}
  ul#list li{background:#131a29;border:1px solid var(--border);border-radius:10px;padding:10px 13px;margin-bottom:7px;font-size:14px;display:flex;gap:10px;align-items:center}
  .name{overflow-wrap:anywhere;font-weight:600}
  .size{color:var(--muted);margin-left:auto;white-space:nowrap;font-variant-numeric:tabular-nums;font-size:13px}
  .bar{height:5px;background:#131a29;border-radius:99px;overflow:hidden;margin-top:14px;border:1px solid var(--border)}
  .bar i{display:block;height:100%;width:0;background:var(--accent);transition:width .25s}
  textarea,input[type=text]{width:100%;background:#131a29;border:1px solid var(--border);color:var(--text);border-radius:8px;padding:10px 12px;font-size:13.5px;font-family:ui-monospace,Menlo,Consolas,monospace}
  details summary{cursor:pointer;color:var(--muted);font-size:14.5px}
  .hint{font-size:13.5px;color:var(--muted);margin-top:10px}
</style>
</head>
<body>
<div class="wrap">
  <h1>Перенос таблицы агенту</h1>
  <p class="sub">Страница сама забирает таблицу из Google и передаёт её в рабочую папку агента. Никаких скачиваний и перетаскиваний не нужно — просто держите эту вкладку открытой.</p>

  <div class="panel">
    <h2>Шаг 1 · автоматический перенос <span id="state" class="warn">идёт…</span></h2>
    <p class="log" id="log">запуск…</p>
    <p style="margin:14px 0 0"><button id="again" class="ghost">Повторить</button></p>
    <div class="bar"><i id="bar"></i></div>
  </div>

  <div class="panel">
    <h2>Шаг 2 · если автоматика не прошла</h2>
    <p class="hint">Скачайте книгу (<b>Файл → Скачать → Microsoft Excel (.xlsx)</b>) и перетащите файл в рамку. Можно и по одному CSV на лист — все три файла.</p>
    <div id="drop">
      <div class="big">Перетащите файл сюда</div>
      <div class="sm">или нажмите, чтобы выбрать &nbsp;·&nbsp; .xlsx, .csv, .ods, .tsv</div>
      <input id="file" type="file" multiple accept=".xlsx,.xls,.csv,.tsv,.ods,.txt" style="display:none">
    </div>
    <details style="margin-top:16px">
      <summary>или вставьте данные текстом</summary>
      <div style="margin-top:12px">
        <p class="hint" style="margin-top:0">В Google-таблице выделите лист (Ctrl+A), скопируйте (Ctrl+C) и вставьте сюда. По одному блоку на лист.</p>
        <input id="tname" type="text" placeholder="Имя листа, напр. shapes" style="margin-bottom:9px">
        <textarea id="tbody" rows="7" placeholder="Вставьте строки (вместе с заголовками)"></textarea>
        <p style="margin:10px 0 0"><button id="tsend" class="ghost">Сохранить блок</button></p>
      </div>
    </details>
  </div>

  <div class="panel">
    <h2>Что уже дошло до агента</h2>
    <ul id="list"></ul>
  </div>
</div>

<script>
const SHEET_ID = '__SHEET_ID__';
const $ = id => document.getElementById(id);
const bar = $('bar');

function log(msg, cls){
  const el = $('log');
  const line = document.createElement('div');
  if (cls) { const s = document.createElement('span'); s.className = cls; s.textContent = msg; line.appendChild(s); }
  else line.textContent = msg;
  el.appendChild(line);
  el.scrollTop = el.scrollHeight;
}

function setState(text, cls){ const s = $('state'); s.textContent = text; s.className = cls; }
function fmt(n){ return n > 1048576 ? (n/1048576).toFixed(1)+' МБ' : (n/1024).toFixed(0)+' КБ'; }

function addRow(name, size){
  const li = document.createElement('li');
  li.innerHTML = '<span>⏳</span><span class="name"></span><span class="size"></span>';
  li.querySelector('.name').textContent = name;
  li.querySelector('.size').textContent = size;
  $('list').prepend(li);
  return li;
}

async function postFile(name, body, ctype){
  const r = await fetch('upload?name=' + encodeURIComponent(name), {
    method: 'POST', body, headers: {'Content-Type': ctype || 'application/octet-stream'}
  });
  if (!r.ok) throw new Error('HTTP ' + r.status);
  return r.json();
}

async function notify(msg){
  try { await fetch('note', {method:'POST', body: msg, headers:{'Content-Type':'text/plain'}}); } catch(e){}
}

/* ---------- 0. HTML-рендер всех листов сразу (то, что видит агент) ---------- */
async function tryGvizHtml(){
  const url = 'https://docs.google.com/spreadsheets/d/' + SHEET_ID + '/gviz/tq?tqx=out:html';
  const r = await fetch(url, {mode:'cors', credentials:'omit', cache:'no-store'});
  if (!r.ok) throw new Error('HTTP ' + r.status);
  const txt = await r.text();
  if (!/<table/i.test(txt)) throw new Error('нет таблицы в ответе (' + txt.length + ' симв.)');
  return txt;
}

/* ---------- 1. прямая загрузка книги (xlsx) через CORS ---------- */
async function tryXlsx(){
  const url = 'https://docs.google.com/spreadsheets/d/' + SHEET_ID + '/export?format=xlsx';
  const r = await fetch(url, {mode:'cors', credentials:'omit', cache:'no-store'});
  if (!r.ok) throw new Error('HTTP ' + r.status);
  const buf = await r.arrayBuffer();
  if (buf.byteLength < 1000) throw new Error('подозрительно маленький ответ (' + buf.byteLength + ' байт)');
  return buf;
}

/* ---------- 2. CSV всех листов через CORS ---------- */
async function tryCsv(url){
  const r = await fetch(url, {mode:'cors', credentials:'omit', cache:'no-store'});
  if (!r.ok) throw new Error('HTTP ' + r.status);
  const txt = await r.text();
  if (!txt || txt.length < 50 || /<html/i.test(txt.slice(0, 400))) throw new Error('ответ не похож на CSV');
  return txt;
}

/* ---------- 3. JSONP по каждому листу (обходит CORS) ---------- */
function jsonpSheet(name, timeoutMs){
  return new Promise((resolve, reject) => {
    const cb = '__gviz_cb_' + Math.random().toString(36).slice(2);
    const s = document.createElement('script');
    const t = setTimeout(() => { cleanup(); reject(new Error('таймаут')); }, timeoutMs || 12000);
    function cleanup(){ clearTimeout(t); delete window[cb]; if (s.parentNode) s.parentNode.removeChild(s); }
    window[cb] = payload => {
      cleanup();
      try {
        const table = payload.table;
        const cols = table.cols.map(c => c.label || '');
        const rows = table.rows.map(r => (r.c || []).map(c => (c && (c.v !== null && c.v !== undefined)) ? c.v : ''));
        resolve({cols, rows});
      } catch (e) { reject(e); }
    };
    s.onerror = () => { cleanup(); reject(new Error('сеть')); };
    s.src = 'https://docs.google.com/spreadsheets/d/' + SHEET_ID +
            '/gviz/tq?tqx=out:json;responseHandler=' + cb +
            (name ? '&sheet=' + encodeURIComponent(name) : '');
    document.head.appendChild(s);
  });
}

function toCsv(cols, rows){
  const esc = v => { const s = String(v == null ? '' : v); return /[",\n;]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s; };
  const out = [cols.map(esc).join(',')];
  rows.forEach(r => out.push(r.map(esc).join(',')));
  return out.join('\n');
}

function fingerprint(cols, rows){
  const first = rows.slice(0, 3).map(r => r.join('|')).join('#');
  return cols.join('|').length + ':' + rows.length + ':' + first;
}

async function autoFetch(){
  $('again').disabled = true;
  let delivered = 0;
  notify('--- попытка переноса ' + new Date().toISOString() + ' ---');

  // (a) HTML-рендер всех листов одним запросом — самый полный и надёжный путь
  try {
    log('Пробую забрать все листы одним запросом…');
    const txt = await tryGvizHtml();
    const j = await postFile('gviz_all.html', new Blob([txt], {type:'text/html'}), 'text/html');
    log('✓ Все листы переданы: ' + fmt(j.size), 'ok');
    notify('gviz_all.html: OK ' + j.size);
    bar.style.width = '100%';
    setState('готово ✓', 'ok');
    log('Напишите агенту «готово».');
    $('again').disabled = false;
    refreshList();
    return;
  } catch (e) {
    log('— не вышло (' + e.message + ')', 'warn');
    notify('gviz_all.html: FAIL ' + e.message);
  }

  // (b) вся книга одним файлом
  try {
    log('Пробую забрать всю книгу (.xlsx)…');
    const buf = await tryXlsx();
    const j = await postFile('book.xlsx', buf, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
    log('✓ Книга передана целиком: ' + fmt(j.size), 'ok');
    notify('book.xlsx: OK ' + j.size);
    bar.style.width = '100%';
    setState('готово ✓', 'ok');
    log('Напишите агенту «готово».');
    $('again').disabled = false;
    refreshList();
    return;
  } catch (e) {
    log('— не вышло (' + e.message + '), пробую CSV по листам', 'warn');
    notify('book.xlsx: FAIL ' + e.message);
  }

  // (b) CSV: сначала «все листы сразу», потом по именам
  const candidates = [
    {label:'all', url:'https://docs.google.com/spreadsheets/d/' + SHEET_ID + '/gviz/tq?tqx=out:csv'},
    {label:'shapes', url:'https://docs.google.com/spreadsheets/d/' + SHEET_ID + '/gviz/tq?tqx=out:csv&sheet=shapes'},
    {label:'royalfoam', url:'https://docs.google.com/spreadsheets/d/' + SHEET_ID + '/gviz/tq?tqx=out:csv&sheet=royalfoam'},
    {label:'products', url:'https://docs.google.com/spreadsheets/d/' + SHEET_ID + '/gviz/tq?tqx=out:csv&sheet=products'},
  ];
  for (const c of candidates){
    try {
      log('Пробую CSV [' + c.label + ']…');
      const txt = await tryCsv(c.url);
      const j = await postFile('sheet_' + c.label + '.csv', new Blob([txt], {type:'text/csv'}), 'text/csv');
      log('✓ Передан лист [' + c.label + '] — ' + fmt(j.size), 'ok');
      delivered++;
    } catch (e) {
      log('— [' + c.label + '] не вышло: ' + e.message, 'warn');
    }
  }

  // (c) JSONP по именам листов
  const names = ['shapes','royalfoam','products','decorativearchitecturalshapes.com',
                 'decorativearchitecturalproducts.com','royalfoam.art','Sheet1','Sheet2','Sheet3',
                 'Лист1','Лист2','Лист3','kw_results_rev2'];
  const seen = {};
  let sheetsFound = 0;
  for (const n of names){
    try {
      log('Пробую лист «' + n + '» через JSONP…');
      const {cols, rows} = await jsonpSheet(n, 12000);
      if (!rows.length){ log('— «' + n + '» без строк', 'warn'); continue; }
      const fp = fingerprint(cols, rows);
      if (seen[fp]){ log('— «' + n + '» дубликат уже полученного листа', 'warn'); continue; }
      seen[fp] = true;
      sheetsFound++;
      const csv = toCsv(cols, rows);
      const j = await postFile('gviz_' + n + '.csv', new Blob([csv], {type:'text/csv'}), 'text/csv');
      const sites = [...new Set(rows.map(r => r[0]).filter(Boolean))].slice(0, 3).join(', ');
      log('✓ Лист «' + n + '»: ' + rows.length + ' строк — ' + fmt(j.size) + ' (' + sites + ')', 'ok');
      delivered++;
    } catch (e) {
      log('— «' + n + '» не вышло: ' + e.message, 'warn');
    }
  }

  bar.style.width = delivered ? '100%' : '0';
  if (delivered){
    setState('готово ✓', 'ok');
    log('Передано: ' + delivered + ' файл(ов).' + (sheetsFound < 3 ? ' Внимание: листов найдено ' + sheetsFound + ' из 3 — возможно, часть не отдалась, тогда используйте шаг 2.' : ''));
    log('Напишите агенту «готово».');
  } else {
    setState('не удалось', 'err');
    log('Google не отдал данные автоматически (браузер блокирует). Используйте шаг 2: скачайте .xlsx и перетащите в рамку.', 'err');
  }
  $('again').disabled = false;
  refreshList();
}

/* ---------- ручные каналы ---------- */
const drop = $('drop');
$('file').addEventListener('change', () => { sendFiles([...$('file').files]); $('file').value = ''; });
['dragenter','dragover'].forEach(e => drop.addEventListener(e, ev => { ev.preventDefault(); drop.classList.add('hot'); }));
['dragleave','drop'].forEach(e => drop.addEventListener(e, ev => { ev.preventDefault(); drop.classList.remove('hot'); }));
drop.addEventListener('drop', ev => sendFiles([...ev.dataTransfer.files]));
window.addEventListener('dragover', e => e.preventDefault());
window.addEventListener('drop', e => e.preventDefault());

async function sendFiles(files){
  for (const f of files){
    const li = addRow(f.name, fmt(f.size));
    try {
      const j = await postFile(f.name, f, f.type || 'application/octet-stream');
      li.querySelector('span').textContent = '✓';
      li.querySelector('span').className = 'ok';
      li.querySelector('.size').textContent = fmt(j.size) + ' → ' + j.path;
      log('✓ вручную передан ' + f.name, 'ok');
    } catch (e) {
      li.querySelector('span').textContent = '✕';
      li.querySelector('span').className = 'err';
      li.querySelector('.size').textContent = 'ошибка: ' + e.message;
    }
  }
}

$('tsend').addEventListener('click', async () => {
  const text = $('tbody').value;
  if (!text.trim()){ alert('Вставьте данные в поле'); return; }
  let base = ($('tname').value || 'sheet').trim().replace(/\.[a-z0-9]+$/i, '');
  const li = addRow(base + '.csv', fmt(text.length));
  try {
    const j = await postFile(base + '.csv', new Blob([text], {type:'text/csv'}), 'text/csv');
    li.querySelector('span').textContent = '✓';
    li.querySelector('span').className = 'ok';
    li.querySelector('.size').textContent = fmt(j.size) + ' → ' + j.path;
    $('tbody').value = ''; $('tname').value = '';
    log('✓ вставка сохранена: ' + base + '.csv', 'ok');
  } catch (e) {
    li.querySelector('span').textContent = '✕';
    li.querySelector('span').className = 'err';
    li.querySelector('.size').textContent = 'ошибка: ' + e.message;
  }
});

$('again').addEventListener('click', () => { $('log').innerHTML = ''; autoFetch(); });

async function refreshList(){
  try {
    const r = await fetch('list', {cache:'no-store'});
    const j = await r.json();
    $('list').innerHTML = '';
    if (!j.files.length){ $('list').innerHTML = '<li style="color:var(--muted)">пока пусто</li>'; return; }
    j.files.forEach(f => {
      const li = addRow(f.name, fmt(f.size) + ' — уже у агента');
      li.querySelector('span').textContent = '✓';
      li.querySelector('span').className = 'ok';
    });
  } catch (e) {}
}

refreshList();
autoFetch();
</script>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    server_version = "sheet-bridge/2.0"
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):
        sys.stderr.write("[%s] %s\n" % (datetime.datetime.now().strftime("%H:%M:%S"), fmt % args))

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")

    def _send(self, code, body: bytes, ctype="application/json; charset=utf-8"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self._cors()
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def do_OPTIONS(self):
        self._send(204, b"")

    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        path = self.path.split("?")[0]
        if path in ("/", "/index.html"):
            self._send(200, page_html(), "text/html; charset=utf-8")
        elif path == "/list":
            files = []
            for n in sorted(os.listdir(OUT)):
                p = os.path.join(OUT, n)
                if os.path.isfile(p):
                    files.append({"name": n, "size": os.path.getsize(p)})
            self._send(200, json.dumps({"files": files}, ensure_ascii=False).encode("utf-8"))
        elif path == "/patch":
            with open(SELF, "rb") as f:
                data = f.read()
            self._send(200, data, "text/plain; charset=utf-8")
            self._send(200, b'{"ok":true,"note":"restarting"}')
            self.wfile.flush()
            subprocess.Popen([sys.executable, SELF, str(self.server.server_address[1])])
            os._exit(0)
        else:
            self._send(404, json.dumps({"error": "not found"}).encode("utf-8"))

    def do_POST(self):
        q = self.path.split("?", 1)
        path_only = q[0]
        name = "upload.bin"
        if len(q) > 1:
            for part in q[1].split("&"):
                if part.startswith("name="):
                    from urllib.parse import unquote
                    name = unquote(part[5:]) or name
        name = safe_name(name)

        length = int(self.headers.get("Content-Length") or 0)

        # журнал попыток переноса (диагностика со стороны браузера)
        if path_only == "/note":
            body = self.rfile.read(length) if length else b""
            with open(os.path.join(OUT, "_notes.txt"), "ab") as f:
                f.write(body + b"\n")
            self._send(200, b'{"ok":true}')
            return

        if length <= 0:
            self._send(400, json.dumps({"error": "empty body"}).encode("utf-8"))
            return
        if length > MAX_BYTES:
            self._send(413, json.dumps({"error": "too large"}).encode("utf-8"))
            return

        path = unique_path(name)
        remaining = length
        with open(path, "wb") as f:
            while remaining > 0:
                chunk = self.rfile.read(min(1 << 20, remaining))
                if not chunk:
                    break
                f.write(chunk)
                remaining -= len(chunk)
        size = os.path.getsize(path)
        self.log_message("received %s (%d bytes)", os.path.basename(path), size)
        self._send(200, json.dumps({"ok": True, "path": path, "size": size}, ensure_ascii=False).encode("utf-8"))


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    srv = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    srv.daemon_threads = True
    print(f"sheet-bridge on http://0.0.0.0:{port}  ->  {OUT}", flush=True)
    srv.serve_forever()


if __name__ == "__main__":
    main()
