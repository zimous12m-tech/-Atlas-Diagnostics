from flask import Flask, render_template_string, request, jsonify
import os
import json
import hashlib

app = Flask(__name__)

DATA_DIR = os.path.join(os.path.dirname(__file__), "dados_utilizadores")
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-PT">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Oráculo Causal v11 PRO — Diagnóstico Sistémico</title>
<!-- Metatags para pré-visualização bonita (Open Graph / Imagem de Capa) -->
<meta property="meta:title" content="Oráculo Causal v11 PRO — Sistema de Diagnóstico">
<meta property="meta:description" content="Engenharia de vida, balanço de energia e gestão causal de pacientes.">
<meta property="og:image" content="/static/capa.png">
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700;900&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
:root {
    --bg: #080a0f;
    --card-bg: #11141d;
    --border: #1e2536;
    --gold: #d4af37;
    --gold-glow: rgba(212, 175, 55, 0.15);
    --text: #f1f5f9;
    --muted: #a3b0c2;
    --red: #ef4444;
    --green: #10b981;
    --blue: #38bdf8;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body { background-color: var(--bg); color: var(--text); font-family: 'Inter', sans-serif; padding: 20px; display: flex; justify-content: center; }
.container { width: 100%; max-width: 980px; display: flex; flex-direction: column; gap: 20px; }

#authScreen {
    max-width: 420px;
    margin: 60px auto;
    background: var(--card-bg);
    border: 1px solid var(--gold);
    border-radius: 16px;
    padding: 30px;
    display: flex;
    flex-direction: column;
    gap: 15px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.6);
}
#appScreen { display: none; flex-direction: column; gap: 20px; }

.auth-input {
    background: rgba(0,0,0,0.4);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 12px 14px;
    color: #fff;
    font-size: 0.95rem;
    width: 100%;
}
.auth-input:focus { border-color: var(--gold); outline: none; }
.btn-auth {
    background: linear-gradient(135deg, var(--gold), #b58a10);
    color: #000;
    border: none;
    border-radius: 8px;
    padding: 12px;
    font-weight: 700;
    cursor: pointer;
    font-size: 1rem;
}
.tab-row { display: flex; gap: 10px; margin-bottom: 10px; }
.tab-btn { flex: 1; background: transparent; border: 1px solid var(--border); color: var(--muted); padding: 8px; border-radius: 6px; cursor: pointer; font-weight: 600; }
.tab-btn.active { border-color: var(--gold); color: var(--gold); background: var(--gold-glow); }

header { text-align: center; padding: 20px; background: var(--card-bg); border: 1px solid var(--gold); border-radius: 16px; }
h1 { font-family: 'Cinzel', serif; color: var(--gold); font-size: 1.5rem; margin-top: 8px; }

.session-bar {
    background: var(--card-bg);
    border: 1px solid var(--gold);
    border-radius: 12px;
    padding: 15px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px;
}
.pro-btn {
    background: rgba(212, 175, 55, 0.12);
    border: 1px solid var(--gold);
    color: var(--gold);
    padding: 8px 14px;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    font-size: 0.82rem;
}
.pro-btn:hover { background: var(--gold); color: #000; }
.btn-save-override {
    background: rgba(16, 185, 129, 0.15);
    border: 1px solid var(--green);
    color: var(--green);
}
.btn-save-override:hover { background: var(--green); color: #000; }
.btn-delete-session {
    background: rgba(239, 68, 68, 0.15);
    border: 1px solid var(--red);
    color: var(--red);
}
.btn-delete-session:hover { background: var(--red); color: #fff; }

.grid-pilares { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 16px; }
.pilar-card { background: var(--card-bg); border: 1px solid var(--border); border-radius: 12px; padding: 18px; display: flex; flex-direction: column; gap: 12px; }
.pilar-title { font-family: 'Cinzel', serif; font-size: 0.95rem; color: var(--gold); display: flex; justify-content: space-between; align-items: center; }
.options-row { display: grid; grid-template-columns: repeat(5, 1fr); gap: 4px; }
.opt-btn { background: rgba(0,0,0,0.4); border: 1px solid var(--border); border-radius: 6px; color: var(--muted); font-size: 0.68rem; padding: 7px 2px; text-align: center; cursor: pointer; }
.opt-btn.active-am { background: rgba(212, 175, 55, 0.25); border-color: var(--gold); color: var(--gold); font-weight: bold; }
.opt-btn.active-dd { background: rgba(239, 68, 68, 0.25); border-color: var(--red); color: #fca5a5; font-weight: bold; }
</style>
</head>
<body>

<div class="container">
    <!-- ECRÃ DE AUTENTICAÇÃO (Blindado contra autofill do Chrome) -->
    <div id="authScreen">
        <h2 style="font-family:'Cinzel',serif; color:var(--gold); text-align:center;">Oráculo Causal PRO</h2>
        <div class="tab-row">
            <button type="button" class="tab-btn active" onclick="switchTab('login')">Entrar (Login)</button>
            <button type="button" class="tab-btn" onclick="switchTab('signup')">Criar Conta</button>
        </div>
        <div id="authMsg" style="font-size:0.8rem; color:var(--red); text-align:center; min-height:16px;"></div>
        
        <input type="text" id="authUsername" class="auth-input" placeholder="Nome de Utilizador" autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false">
        <input type="password" id="authPassword" class="auth-input" placeholder="Password" autocomplete="new-password">
        
        <button type="button" class="btn-auth" id="authBtnAction" onclick="fazerLogin()">Entrar na Conta</button>
    </div>

    <!-- ECRÃ PRINCIPAL DA APLICAÇÃO -->
    <div id="appScreen">
        <header>
            <span style="font-size:0.75rem; letter-spacing:2px; color:var(--gold); text-transform:uppercase;">Sistema Multi-Sessão & JSON</span>
            <h1>O Relógio dos 12 Pilares</h1>
            <p style="font-size:0.8rem; color:var(--muted); margin-top:5px;">Utilizador: <strong id="lblUserLogged" style="color:var(--gold);"></strong> | <a href="#" onclick="fazerLogout()" style="color:var(--blue);">Terminar Sessão</a> | <a href="#" onclick="apagarContaUtilizador()" style="color:var(--red);">Apagar a Minha Conta</a></p>
        </header>

        <!-- BARRA DE GESTÃO DE SESSÕES -->
        <div class="session-bar">
            <div style="display:flex; gap:10px; align-items:center; flex-wrap:wrap;">
                <label style="font-size:0.82rem; color:var(--gold); font-weight:600;">Sessão Ativa do Paciente:</label>
                <select id="selectSessao" style="background:#080a0f; color:#fff; border:1px solid var(--gold); border-radius:6px; padding:6px 10px; font-size:0.8rem;" onchange="carregarSessaoSelecionada(this.value)">
                    <option value="">Selecione uma sessão...</option>
                </select>
                <button type="button" class="pro-btn" onclick="criarNovaSessaoPrompt()">➕ Criar Nova Sessão</button>
            </div>
            <div style="display:flex; gap:8px; flex-wrap:wrap;">
                <button type="button" class="pro-btn btn-save-override" onclick="guardarSessaoAtual()">💾 Gravar (Save)</button>
                <button type="button" class="pro-btn btn-delete-session" onclick="apagarSessaoAtual()">🗑️ Apagar Sessão</button>
            </div>
        </div>

        <div style="background:var(--card-bg); border:1px solid var(--border); border-radius:14px; padding:20px; display:flex; flex-direction:column; gap:12px;">
            <label style="font-size:0.82rem; color:var(--gold); font-weight:600;">Nome do Paciente / Cliente e Objetivo:</label>
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:15px;">
                <input type="text" id="inputNomeCliente" class="auth-input" value="Paciente Exemplo">
                <input type="text" id="inputProjeto" class="auth-input" value="Equilíbrio e Bem-estar">
            </div>
        </div>

        <div class="grid-pilares" id="pilaresGrid"></div>
    </div>
</div>

<script>
let currentUser = null;
let sessaoAtivaId = null;
const nvlMapa = { mau: 10, razoavel: 30, normal: 50, bom: 75, excelente: 95 };

const pilaresDef = [
    { id: 1, nome: "1. Sono e Descanso", amDef: "razoavel", ddDef: "bom" },
    { id: 2, nome: "2. Dinheiro e Contas", amDef: "mau", ddDef: "excelente" },
    { id: 3, nome: "3. Trabalho e Projetos", amDef: "bom", ddDef: "bom" },
    { id: 4, nome: "4. Família e Casa", amDef: "mau", ddDef: "bom" },
    { id: 5, nome: "5. Cabeça e Concentração", amDef: "excelente", ddDef: "excelente" },
    { id: 6, nome: "6. Ideias e Aprendizagem", amDef: "razoavel", ddDef: "normal" },
    { id: 7, nome: "7. Casa e Espaço à Volta", amDef: "razoavel", ddDef: "bom" },
    { id: 8, nome: "8. Amigos e Apoio", amDef: "bom", ddDef: "bom" },
    { id: 9, nome: "9. Organização do Tempo", amDef: "mau", ddDef: "bom" },
    { id: 10, nome: "10. Planos para o Futuro", amDef: "excelente", ddDef: "bom" },
    { id: 11, nome: "11. Saúde e Corpo", amDef: "razoavel", ddDef: "bom" },
    { id: 12, nome: "12. Paz Interior e Valores", amDef: "bom", ddDef: "normal" }
];

function switchTab(modo) {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    event.target.classList.add('active');
    const btn = document.getElementById('authBtnAction');
    
    document.getElementById('authUsername').value = '';
    document.getElementById('authPassword').value = '';
    document.getElementById('authMsg').innerText = '';

    if(modo === 'login') {
        btn.innerText = "Entrar na Conta";
        btn.setAttribute('onclick', 'fazerLogin()');
    } else {
        btn.innerText = "Registar Conta";
        btn.setAttribute('onclick', 'fazerSignup()');
    }
}

async function fazerLogin() {
    let u = document.getElementById('authUsername').value;
    let p = document.getElementById('authPassword').value;
    if(!u || !p) {
        document.getElementById('authMsg').innerText = "Preencha todos os campos.";
        return;
    }
    let res = await fetch('/api/login', { method: 'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({username: u, password: p}) });
    let data = await res.json();
    if(data.success) {
        currentUser = u;
        document.getElementById('lblUserLogged').innerText = u;
        document.getElementById('authScreen').style.display = 'none';
        document.getElementById('appScreen').style.display = 'flex';
        initGrid();
        carregarListaSessoes();
    } else {
        document.getElementById('authMsg').innerText = data.error;
    }
}

async function fazerSignup() {
    let u = document.getElementById('authUsername').value;
    let p = document.getElementById('authPassword').value;
    if(!u || !p) {
        document.getElementById('authMsg').innerText = "Preencha todos os campos.";
        return;
    }
    let res = await fetch('/api/signup', { method: 'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({username: u, password: p}) });
    let data = await res.json();
    if(data.success) {
        alert("Conta criada com sucesso! Podes fazer login.");
        switchTab('login');
    } else {
        document.getElementById('authMsg').innerText = data.error;
    }
}

function fazerLogout() {
    currentUser = null;
    sessaoAtivaId = null;
    document.getElementById('authUsername').value = '';
    document.getElementById('authPassword').value = '';
    document.getElementById('authMsg').innerText = '';
    
    document.getElementById('appScreen').style.display = 'none';
    document.getElementById('authScreen').style.display = 'flex';
}

async function apagarContaUtilizador() {
    if(!confirm("⚠️ Tem a certeza que deseja apagar permanentemente a sua conta e todos os dados associados?")) return;
    let res = await fetch('/api/utilizador/apagar', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({username: currentUser})
    });
    let data = await res.json();
    if(data.success) {
        alert("Conta apagada com sucesso.");
        fazerLogout();
    }
}

function initGrid() {
    const grid = document.getElementById('pilaresGrid');
    let html = '';
    pilaresDef.forEach(p => {
        html += `
        <div class="pilar-card" id="card_pilar_${p.id}">
            <div class="pilar-title"><span>${p.nome}</span></div>
            <div style="font-size:0.8rem; color:var(--muted);">Energia Atual (AM):</div>
            <div class="options-row" id="row_am_${p.id}">
                <button type="button" data-nvl="mau" class="opt-btn ${p.amDef==='mau'?'active-am':''}" onclick="selecionarNivel(${p.id}, 'am', 'mau', this)">Esgotada</button>
                <button type="button" data-nvl="razoavel" class="opt-btn ${p.amDef==='razoavel'?'active-am':''}" onclick="selecionarNivel(${p.id}, 'am', 'razoavel', this)">Fraca</button>
                <button type="button" data-nvl="normal" class="opt-btn ${p.amDef==='normal'?'active-am':''}" onclick="selecionarNivel(${p.id}, 'am', 'normal', this)">Normal</button>
                <button type="button" data-nvl="bom" class="opt-btn ${p.amDef==='bom'?'active-am':''}" onclick="selecionarNivel(${p.id}, 'am', 'bom', this)">Boa</button>
                <button type="button" data-nvl="excelente" class="opt-btn ${p.amDef==='excelente'?'active-am':''}" onclick="selecionarNivel(${p.id}, 'am', 'excelente', this)">Máxima</button>
            </div>
            <div style="font-size:0.8rem; color:var(--muted); margin-top:5px;">Peso / Problema (DD):</div>
            <div class="options-row" id="row_dd_${p.id}">
                <button type="button" data-nvl="mau" class="opt-btn ${p.ddDef==='mau'?'active-dd':''}" onclick="selecionarNivel(${p.id}, 'dd', 'mau', this)">Nenhum</button>
                <button type="button" data-nvl="razoavel" class="opt-btn ${p.ddDef==='razoavel'?'active-dd':''}" onclick="selecionarNivel(${p.id}, 'dd', 'razoavel', this)">Pouco</button>
                <button type="button" data-nvl="normal" class="opt-btn ${p.ddDef==='normal'?'active-dd':''}" onclick="selecionarNivel(${p.id}, 'dd', 'normal', this)">Médio</button>
                <button type="button" data-nvl="bom" class="opt-btn ${p.ddDef==='bom'?'active-dd':''}" onclick="selecionarNivel(${p.id}, 'dd', 'bom', this)">Pesado</button>
                <button type="button" data-nvl="excelente" class="opt-btn ${p.ddDef==='excelente'?'active-dd':''}" onclick="selecionarNivel(${p.id}, 'dd', 'excelente', this)">Insuportável</button>
            </div>
            <input type="hidden" id="val_am_${p.id}" value="${nvlMapa[p.amDef]}">
            <input type="hidden" id="val_dd_${p.id}" value="${nvlMapa[p.ddDef]}">
        </div>`;
    });
    grid.innerHTML = html;
}

function selecionarNivel(id, tipo, nivel, btn) {
    document.getElementById(`val_${tipo}_${id}`).value = nvlMapa[nivel];
    const row = btn.parentElement;
    Array.from(row.children).forEach(b => b.classList.remove(tipo === 'am' ? 'active-am' : 'active-dd'));
    btn.classList.add(tipo === 'am' ? 'active-am' : 'active-dd');
}

async function carregarListaSessoes() {
    let res = await fetch(`/api/sessoes?username=${currentUser}`);
    let data = await res.json();
    let select = document.getElementById('selectSessao');
    let html = '<option value="">Selecione uma sessão...</option>';
    data.sessoes.forEach(s => {
        html += `<option value="${s.id}">${s.titulo} — Paciente: ${s.cliente}</option>`;
    });
    select.innerHTML = html;
}

async function criarNovaSessaoPrompt() {
    let nomeCliente = prompt("Nome do Paciente / Cliente (ex: João Barradas):");
    if(!nomeCliente) return;

    let res = await fetch('/api/sessoes/criar', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({username: currentUser, cliente: nomeCliente})
    });
    let data = await res.json();
    if(data.success) {
        await carregarListaSessoes();
        document.getElementById('selectSessao').value = data.sessao.id;
        carregarSessaoSelecionada(data.sessao.id);
    }
}

async function carregarSessaoSelecionada(sessaoId) {
    if(!sessaoId) {
        sessaoAtivaId = null;
        return;
    }
    sessaoAtivaId = sessaoId;
    let res = await fetch(`/api/sessoes/obter?username=${currentUser}&sessao_id=${sessaoId}`);
    let data = await res.json();
    if(data.success) {
        let s = data.sessao;
        document.getElementById('inputNomeCliente').value = s.cliente;
        document.getElementById('inputProjeto').value = s.projeto;
        
        s.pilares.forEach(sp => {
            document.getElementById(`val_am_${sp.id}`).value = sp.am;
            document.getElementById(`val_dd_${sp.id}`).value = sp.dd;
            atualizarBotaoVisual(sp.id, 'am', sp.am);
            atualizarBotaoVisual(sp.id, 'dd', sp.dd);
        });
    }
}

function atualizarBotaoVisual(pilarId, tipo, valor) {
    let nivelNome = 'mau';
    for(let k in nvlMapa) { if(nvlMapa[k] == valor) nivelNome = k; }
    let row = document.getElementById(`row_${tipo}_${pilarId}`);
    Array.from(row.children).forEach(b => {
        b.classList.remove(tipo === 'am' ? 'active-am' : 'active-dd');
        if(b.getAttribute('data-nvl') === nivelNome) {
            b.classList.add(tipo === 'am' ? 'active-am' : 'active-dd');
        }
    });
}

async function guardarSessaoAtual() {
    if(!sessaoAtivaId) {
        alert("Por favor, selecione ou crie uma sessão primeiro!");
        return;
    }

    let dadosPilares = pilaresDef.map(p => ({
        id: p.id,
        am: document.getElementById(`val_am_${p.id}`).value,
        dd: document.getElementById(`val_dd_${p.id}`).value
    }));

    let payload = {
        username: currentUser,
        sessao_id: sessaoAtivaId,
        cliente: document.getElementById('inputNomeCliente').value,
        projeto: document.getElementById('inputProjeto').value,
        pilares: dadosPilares
    };

    let res = await fetch('/api/sessoes/salvar', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify(payload)
    });
    let data = await res.json();
    if(data.success) {
        alert("✅ Alterações gravadas com sucesso na sessão ativa!");
        carregarListaSessoes();
    }
}

async function apagarSessaoAtual() {
    if(!sessaoAtivaId) {
        alert("Nenhuma sessão selecionada para apagar.");
        return;
    }
    if(!confirm("⚠️ Deseja realmente apagar esta sessão/paciente selecionado?")) return;

    let res = await fetch('/api/sessoes/apagar', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({username: currentUser, sessao_id: sessaoAtivaId})
    });
    let data = await res.json();
    if(data.success) {
        alert("Sessão apagada com sucesso.");
        sessaoAtivaId = null;
        document.getElementById('selectSessao').value = "";
        carregarListaSessoes();
    }
}

window.addEventListener('DOMContentLoaded', () => {
    document.getElementById('authUsername').value = '';
    document.getElementById('authPassword').value = '';
});
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/signup', methods=['POST'])
def api_signup():
    data = request.json
    u, p = data.get('username'), data.get('password')
    if not u or not p:
        return jsonify({'success': False, 'error': 'Preencha todos os campos.'})
    user_file = os.path.join(DATA_DIR, f"{u}.json")
    if os.path.exists(user_file):
        return jsonify({'success': False, 'error': 'Utilizador já existe.'})
    with open(user_file, 'w', encoding='utf-8') as f:
        json.dump({'password': hash_password(p), 'sessoes': []}, f, ensure_ascii=False, indent=4)
    return jsonify({'success': True})

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    u, p = data.get('username'), data.get('password')
    user_file = os.path.join(DATA_DIR, f"{u}.json")
    if not os.path.exists(user_file):
        return jsonify({'success': False, 'error': 'Utilizador não encontrado.'})
    with open(user_file, 'r', encoding='utf-8') as f:
        user_data = json.load(f)
    if user_data['password'] != hash_password(p):
        return jsonify({'success': False, 'error': 'Password incorreta.'})
    return jsonify({'success': True})

@app.route('/api/utilizador/apagar', methods=['POST'])
def api_apagar_utilizador():
    data = request.json
    u = data.get('username')
    user_file = os.path.join(DATA_DIR, f"{u}.json")
    if os.path.exists(user_file):
        os.remove(user_file)
    return jsonify({'success': True})

@app.route('/api/sessoes', methods=['GET'])
def api_listar_sessoes():
    u = request.args.get('username')
    user_file = os.path.join(DATA_DIR, f"{u}.json")
    if not os.path.exists(user_file):
        return jsonify({'sessoes': []})
    with open(user_file, 'r', encoding='utf-8') as f:
        user_data = json.load(f)
    lista = [{'id': s['id'], 'titulo': s['titulo'], 'cliente': s['cliente']} for s in user_data.get('sessoes', [])]
    return jsonify({'sessoes': lista})

@app.route('/api/sessoes/criar', methods=['POST'])
def api_criar_sessao():
    data = request.json
    u, cliente_nome = data.get('username'), data.get('cliente')
    user_file = os.path.join(DATA_DIR, f"{u}.json")
    with open(user_file, 'r', encoding='utf-8') as f:
        user_data = json.load(f)
    
    nova_id = f"sessao_{int(os.urandom(2).hex(), 16)}"
    nova_sessao = {
        'id': nova_id,
        'titulo': f"Registo #{len(user_data['sessoes']) + 1}",
        'cliente': cliente_nome,
        'projeto': 'Objetivo / Plano',
        'pilares': []
    }
    user_data['sessoes'].append(nova_sessao)
    with open(user_file, 'w', encoding='utf-8') as f:
        json.dump(user_data, f, ensure_ascii=False, indent=4)
    return jsonify({'success': True, 'sessao': nova_sessao})

@app.route('/api/sessoes/obter', methods=['GET'])
def api_obter_sessao():
    u, s_id = request.args.get('username'), request.args.get('sessao_id')
    user_file = os.path.join(DATA_DIR, f"{u}.json")
    with open(user_file, 'r', encoding='utf-8') as f:
        user_data = json.load(f)
    sessao = next((s for s in user_data['sessoes'] if s['id'] == s_id), None)
    if not sessao:
        return jsonify({'success': False, 'error': 'Sessão não encontrada'})
    return jsonify({'success': True, 'sessao': sessao})

@app.route('/api/sessoes/salvar', methods=['POST'])
def api_salvar_sessao():
    data = request.json
    u, s_id = data.get('username'), data.get('sessao_id')
    user_file = os.path.join(DATA_DIR, f"{u}.json")
    with open(user_file, 'r', encoding='utf-8') as f:
        user_data = json.load(f)
    for s in user_data['sessoes']:
        if s['id'] == s_id:
            s['cliente'] = data.get('cliente')
            s['projeto'] = data.get('projeto')
            s['pilares'] = data.get('pilares')
            break
    with open(user_file, 'w', encoding='utf-8`') as f:
        json.dump(user_data, f, ensure_ascii=False, indent=4)
    return jsonify({'success': True})

@app.route('/api/sessoes/apagar', methods=['POST'])
def api_apagar_sessao():
    data = request.json
    u, s_id = data.get('username'), data.get('sessao_id')
    user_file = os.path.join(DATA_DIR, f"{u}.json")
    with open(user_file, 'r', encoding='utf-8') as f:
        user_data = json.load(f)
    
    user_data['sessoes'] = [s for s in user_data['sessoes'] if s['id'] != s_id]
    
    with open(user_file, 'w', encoding='utf-8') as f:
        json.dump(user_data, f, ensure_ascii=False, indent=4)
    return jsonify({'success': True})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
