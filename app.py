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
<title>Atlas-Diagnostics PRO — Diagnóstico Sistémico</title>
<meta property="og:title" content="Atlas-Diagnostics — Sistema de Diagnóstico e Sessões">
<meta property="og:description" content="Gestão avançada de pacientes, 12 pilares sistémicos, relatórios e evolução clínica.">
<meta property="og:image" content="https://atlas-diagnostics.onrender.com/static/capa.png">
<meta property="og:url" content="https://atlas-diagnostics.onrender.com">
<meta property="og:type" content="website">
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
.container { width: 100%; max-width: 1000px; display: flex; flex-direction: column; gap: 20px; }

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
h1 { font-family: 'Cinzel', serif; color: var(--gold); font-size: 1.6rem; margin-top: 8px; }

.panel {
    background: var(--card-bg);
    border: 1px solid var(--gold);
    border-radius: 14px;
    padding: 20px;
    display: flex;
    flex-direction: column;
    gap: 15px;
}
.pro-btn {
    background: rgba(212, 175, 55, 0.12);
    border: 1px solid var(--gold);
    color: var(--gold);
    padding: 10px 16px;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    font-size: 0.85rem;
    display: inline-flex;
    align-items: center;
    gap: 6px;
}
.pro-btn:hover { background: var(--gold); color: #000; }
.btn-save { background: rgba(16, 185, 129, 0.15); border-color: var(--green); color: var(--green); }
.btn-save:hover { background: var(--green); color: #000; }
.btn-danger { background: rgba(239, 68, 68, 0.15); border-color: var(--red); color: var(--red); }
.btn-danger:hover { background: var(--red); color: #fff; }

.grid-pilares { display: grid; grid-template-columns: repeat(auto-fit, minmax(310px, 1fr)); gap: 16px; }
.pilar-card { background: var(--card-bg); border: 1px solid var(--border); border-radius: 12px; padding: 18px; display: flex; flex-direction: column; gap: 10px; }
.pilar-title { font-family: 'Cinzel', serif; font-size: 0.95rem; color: var(--gold); }
.options-row { display: grid; grid-template-columns: repeat(5, 1fr); gap: 4px; }
.opt-btn { background: rgba(0,0,0,0.4); border: 1px solid var(--border); border-radius: 6px; color: var(--muted); font-size: 0.68rem; padding: 7px 2px; text-align: center; cursor: pointer; }
.opt-btn.active-am { background: rgba(212, 175, 55, 0.25); border-color: var(--gold); color: var(--gold); font-weight: bold; }
.opt-btn.active-dd { background: rgba(239, 68, 68, 0.25); border-color: var(--red); color: #fca5a5; font-weight: bold; }

.report-box { background: rgba(0,0,0,0.5); border: 1px solid var(--border); border-radius: 10px; padding: 15px; font-size: 0.88rem; line-height: 1.5; color: var(--muted); }
.report-box h3 { color: var(--gold); font-family: 'Cinzel', serif; margin-bottom: 8px; }
</style>
</head>
<body>

<div class="container">
    <!-- ECRÃ DE AUTENTICAÇÃO -->
    <div id="authScreen">
        <h2 style="font-family:'Cinzel',serif; color:var(--gold); text-align:center;">Atlas-Diagnostics</h2>
        <div class="tab-row">
            <button type="button" class="tab-btn active" onclick="switchTab('login')">Entrar (Login)</button>
            <button type="button" class="tab-btn" onclick="switchTab('signup')">Criar Conta</button>
        </div>
        <div id="authMsg" style="font-size:0.8rem; color:var(--red); text-align:center; min-height:16px;"></div>
        <input type="text" id="authUsername" class="auth-input" placeholder="Nome de Utilizador" autocomplete="off">
        <input type="password" id="authPassword" class="auth-input" placeholder="Password" autocomplete="new-password">
        <button type="button" class="btn-auth" id="authBtnAction" onclick="fazerLogin()">Entrar na Conta</button>
    </div>

    <!-- ECRÃ PRINCIPAL -->
    <div id="appScreen">
        <header>
            <span style="font-size:0.75rem; letter-spacing:2px; color:var(--gold); text-transform:uppercase;">Plataforma Clínica & Sistémica</span>
            <h1>Atlas-Diagnostics PRO</h1>
            <p style="font-size:0.8rem; color:var(--muted); margin-top:5px;">Terapeuta/Médico: <strong id="lblUserLogged" style="color:var(--gold);"></strong> | <a href="#" onclick="fazerLogout()" style="color:var(--blue);">Terminar Sessão</a> | <a href="#" onclick="apagarContaUtilizador()" style="color:var(--red);">Apagar Conta</a></p>
        </header>

        <!-- GESTÃO DE CLIENTES & SESSÕES -->
        <div class="panel">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
                <div style="display:flex; gap:10px; align-items:center; flex-wrap:wrap; flex:1;">
                    <label style="font-size:0.85rem; color:var(--gold); font-weight:600;">Cliente:</label>
                    <select id="selectCliente" class="auth-input" style="max-width:260px; padding:8px;" onchange="selecionarCliente(this.value)">
                        <option value="">Selecione um cliente...</option>
                    </select>
                    <button type="button" class="pro-btn" onclick="criarNovoClientePrompt()">➕ Novo Cliente</button>
                    <button type="button" class="pro-btn btn-danger" onclick="apagarClienteAtual()" style="padding:10px 12px;">🗑️ Apagar Cliente</button>
                </div>
                <div style="display:flex; gap:10px; align-items:center; flex-wrap:wrap;">
                    <label style="font-size:0.85rem; color:var(--gold); font-weight:600;">Sessão:</label>
                    <select id="selectSessao" class="auth-input" style="max-width:200px; padding:8px;" onchange="carregarSessaoSelecionada(this.value)">
                        <option value="">Selecione sessão...</option>
                    </select>
                    <button type="button" class="pro-btn" onclick="criarNovaSessao()">➕ Nova Sessão</button>
                </div>
            </div>

            <!-- FICHA DO CLIENTE -->
            <div id="fichaClienteContainer" style="display:none; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap:12px; margin-top:5px; border-top:1px solid var(--border); padding-top:15px;">
                <div>
                    <label style="font-size:0.75rem; color:var(--muted);">Nome do Paciente / Cliente:</label>
                    <input type="text" id="inputNomeCliente" class="auth-input" onchange="atualizarFichaCliente()">
                </div>
                <div>
                    <label style="font-size:0.75rem; color:var(--muted);">Idade:</label>
                    <input type="number" id="inputIdadeCliente" class="auth-input" onchange="atualizarFichaCliente()">
                </div>
                <div style="grid-column: 1 / -1;">
                    <label style="font-size:0.75rem; color:var(--muted);">Objetivo Principal (Sonho ou obstáculo a superar):</label>
                    <input type="text" id="inputObjetivoCliente" class="auth-input" onchange="atualizarFichaCliente()" placeholder="Ex: Conseguir lançar o negócio e ter paz mental">
                </div>
            </div>
        </div>

        <!-- GRINHA DOS 12 PILARES -->
        <div id="workspaceArea" style="display:none; flex-direction:column; gap:20px;">
            <div class="grid-pilares" id="pilaresGrid"></div>

            <!-- AVALIAÇÃO DE IMPACTO GERAL NO DIA -->
            <div class="panel">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-family:'Cinzel',serif; color:var(--gold); font-size:0.95rem;">Impacto Sistémico Global no Dia a Dia</span>
                    <span id="lblImpactoVal" style="color:var(--blue); font-weight:bold;">50%</span>
                </div>
                <p style="font-size:0.8rem; color:var(--muted);">Até que ponto uma disfunção numa área compromete o rendimento e o estado mental do dia inteiro?</p>
                <input type="range" id="rangeImpacto" min="0" max="100" value="50" style="accent-color: var(--gold);" oninput="document.getElementById('lblImpactoVal').innerText = this.value + '%'">
            </div>

            <!-- BOTÕES DE AÇÃO E CÁLCULO -->
            <div style="display:flex; justify-content:space-between; flex-wrap:wrap; gap:12px;">
                <div style="display:flex; gap:10px; flex-wrap:wrap;">
                    <button type="button" class="pro-btn btn-save" onclick="guardarSessaoAtual()">💾 Gravar Sessão</button>
                    <button type="button" class="pro-btn" onclick="calcularResultadoRaioX()">⚡ Calcular Raio-X & Conselho</button>
                </div>
                <div style="display:flex; gap:10px; flex-wrap:wrap;">
                    <button type="button" class="pro-btn btn-danger" onclick="apagarSessaoAtual()">🗑️ Apagar Sessão</button>
                    <button type="button" class="pro-btn" onclick="exportarPDFSessao()">📄 Exportar PDF da Sessão</button>
                    <button type="button" class="pro-btn" onclick="exportarPDFMacro()">📊 Exportar PDF Macro (Evolução)</button>
                </div>
            </div>

            <!-- RELATÓRIO, RAIO-X E CONSELHO -->
            <div class="panel" id="relatorioPanel" style="display:none;">
                <div class="report-box">
                    <h3>🔍 Relatório de Raio-X Sistémico</h3>
                    <div id="txtRaioX" style="margin-bottom: 12px; color: #fff;"></div>
                    <h3>💡 Conselho Terapêutico & Direção Causal</h3>
                    <div id="txtConselho" style="color: var(--gold);"></div>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
let currentUser = null;
let clientesData = [];
let clienteAtualId = null;
let sessaoAtualId = null;
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
    if(!u || !p) { document.getElementById('authMsg').innerText = "Preencha todos os campos."; return; }
    let res = await fetch('/api/login', { method: 'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({username: u, password: p}) });
    let data = await res.json();
    if(data.success) {
        currentUser = u;
        document.getElementById('lblUserLogged').innerText = u;
        document.getElementById('authScreen').style.display = 'none';
        document.getElementById('appScreen').style.display = 'flex';
        initGrid();
        carregarDadosUtilizador();
    } else {
        document.getElementById('authMsg').innerText = data.error;
    }
}

async function fazerSignup() {
    let u = document.getElementById('authUsername').value;
    let p = document.getElementById('authPassword').value;
    if(!u || !p) { document.getElementById('authMsg').innerText = "Preencha todos os campos."; return; }
    let res = await fetch('/api/signup', { method: 'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({username: u, password: p}) });
    let data = await res.json();
    if(data.success) { alert("Conta criada com sucesso!"); switchTab('login'); }
    else { document.getElementById('authMsg').innerText = data.error; }
}

function fazerLogout() {
    currentUser = null; clienteAtualId = null; sessaoAtualId = null;
    document.getElementById('appScreen').style.display = 'none';
    document.getElementById('authScreen').style.display = 'flex';
}

async function apagarContaUtilizador() {
    if(!confirm("⚠️ Deseja apagar permanentemente a sua conta e todos os dados?")) return;
    let res = await fetch('/api/utilizador/apagar', { method: 'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({username: currentUser}) });
    let data = await res.json();
    if(data.success) { alert("Conta apagada."); fazerLogout(); }
}

function initGrid() {
    const grid = document.getElementById('pilaresGrid');
    let html = '';
    pilaresDef.forEach(p => {
        html += `
        <div class="pilar-card">
            <div class="pilar-title">${p.nome}</div>
            <div style="font-size:0.75rem; color:var(--muted);">Energia Atual (AM):</div>
            <div class="options-row" id="row_am_${p.id}">
                <button type="button" data-nvl="mau" class="opt-btn" onclick="selecionarNivel(${p.id}, 'am', 'mau', this)">Esgotada</button>
                <button type="button" data-nvl="razoavel" class="opt-btn" onclick="selecionarNivel(${p.id}, 'am', 'razoavel', this)">Fraca</button>
                <button type="button" data-nvl="normal" class="opt-btn" onclick="selecionarNivel(${p.id}, 'am', 'normal', this)">Normal</button>
                <button type="button" data-nvl="bom" class="opt-btn" onclick="selecionarNivel(${p.id}, 'am', 'bom', this)">Boa</button>
                <button type="button" data-nvl="excelente" class="opt-btn" onclick="selecionarNivel(${p.id}, 'am', 'excelente', this)">Máxima</button>
            </div>
            <div style="font-size:0.75rem; color:var(--muted); margin-top:4px;">Peso / Problema (DD):</div>
            <div class="options-row" id="row_dd_${p.id}">
                <button type="button" data-nvl="mau" class="opt-btn" onclick="selecionarNivel(${p.id}, 'dd', 'mau', this)">Nenhum</button>
                <button type="button" data-nvl="razoavel" class="opt-btn" onclick="selecionarNivel(${p.id}, 'dd', 'razoavel', this)">Pouco</button>
                <button type="button" data-nvl="normal" class="opt-btn" onclick="selecionarNivel(${p.id}, 'dd', 'normal', this)">Médio</button>
                <button type="button" data-nvl="bom" class="opt-btn" onclick="selecionarNivel(${p.id}, 'dd', 'bom', this)">Pesado</button>
                <button type="button" data-nvl="excelente" class="opt-btn" onclick="selecionarNivel(${p.id}, 'dd', 'excelente', this)">Insuportável</button>
            </div>
            <input type="hidden" id="val_am_${p.id}" value="50">
            <input type="hidden" id="val_dd_${p.id}" value="50">
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

async function carregarDadosUtilizador() {
    let res = await fetch(`/api/dados?username=${currentUser}`);
    let data = await res.json();
    clientesData = data.clientes || [];
    atualizarSelectClientes();
}

function atualizarSelectClientes() {
    let sel = document.getElementById('selectCliente');
    let html = '<option value="">Selecione um cliente...</option>';
    clientesData.forEach(c => {
        html += `<option value="${c.id}">${c.nome} (${c.idade || '?'} anos)</option>`;
    });
    sel.innerHTML = html;
    document.getElementById('selectSessao.innerHTML') = '<option value="">Selecione sessão...</option>';
    document.getElementById('fichaClienteContainer').style.display = 'none';
    document.getElementById('workspaceArea').style.display = 'none';
}

async function criarNovoClientePrompt() {
    let nome = prompt("Nome completo do Cliente / Paciente:");
    if(!nome) return;
    let idade = prompt("Idade do cliente:", "35");
    let objetivo = prompt("Objetivo principal (Sonho / Obstáculo):", "Alcançar equilíbrio e autonomia");

    let res = await fetch('/api/cliente/criar', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({username: currentUser, nome: nome, idade: idade, objetivo: objetivo})
    });
    let data = await res.json();
    if(data.success) {
        await carregarDadosUtilizador();
        document.getElementById('selectCliente').value = data.cliente.id;
        selecionarCliente(data.cliente.id);
    }
}

function selecionarCliente(clienteId) {
    clienteAtualId = clienteId;
    if(!clienteId) {
        document.getElementById('fichaClienteContainer').style.display = 'none';
        document.getElementById('workspaceArea').style.display = 'none';
        return;
    }
    let cliente = clientesData.find(c => c.id === clienteId);
    if(!cliente) return;

    document.getElementById('inputNomeCliente').value = cliente.nome;
    document.getElementById('inputIdadeCliente').value = cliente.idade || '';
    document.getElementById('inputObjetivoCliente').value = cliente.objetivo || '';
    document.getElementById('fichaClienteContainer').style.display = 'grid';

    let selSessao = document.getElementById('selectSessao');
    let html = '<option value="">Selecione sessão...</option>';
    cliente.sessoes.forEach(s => {
        html += `<option value="${s.id}">${s.titulo} (${s.data || 'recente'})</option>`;
    });
    selSessao.innerHTML = html;
    document.getElementById('workspaceArea').style.display = 'none';
}

async function atualizarFichaCliente() {
    if(!clienteAtualId) return;
    let payload = {
        username: currentUser,
        cliente_id: clienteAtualId,
        nome: document.getElementById('inputNomeCliente').value,
        idade: document.getElementById('inputIdadeCliente').value,
        objetivo: document.getElementById('inputObjetivoCliente').value
    };
    await fetch('/api/cliente/atualizar', { method: 'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload) });
    await carregarDadosUtilizador();
    document.getElementById('selectCliente').value = clienteAtualId;
}

async function apagarClienteAtual() {
    if(!clienteAtualId || !confirm("⚠️ Deseja apagar este cliente e todo o seu histórico de sessões?")) return;
    let res = await fetch('/api/cliente/apagar', { method: 'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({username: currentUser, cliente_id: clienteAtualId}) });
    let data = await res.json();
    if(data.success) { await carregarDadosUtilizador(); alert("Cliente apagado."); }
}

async function criarNovaSessao() {
    if(!clienteAtualId) { alert("Selecione um cliente primeiro."); return; }
    let res = await fetch('/api/sessao/criar', { method: 'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({username: currentUser, cliente_id: clienteAtualId}) });
    let data = await res.json();
    if(data.success) {
        await carregarDadosUtilizador();
        document.getElementById('selectCliente').value = clienteAtualId;
        selecionarCliente(clienteAtualId);
        document.getElementById('selectSessao').value = data.sessao.id;
        carregarSessaoSelecionada(data.sessao.id);
    }
}

function carregarSessaoSelecionada(sessaoId) {
    if(!sessaoId) {
        sessaoAtualId = null;
        document.getElementById('workspaceArea').style.display = 'none';
        return;
    }
    sessaoAtualId = sessaoId;
    let cliente = clientesData.find(c => c.id === clienteAtualId);
    let sessao = cliente.sessoes.find(s => s.id === sessaoId);
    if(!sessao) return;

    document.getElementById('rangeImpacto').value = sessao.impacto || 50;
    document.getElementById('lblImpactoVal').innerText = (sessao.impacto || 50) + '%';

    pilaresDef.forEach(p => {
        let sp = sessao.pilares.find(x => x.id === p.id) || {am: 50, dd: 50};
        document.getElementById(`val_am_${p.id}`).value = sp.am;
        document.getElementById(`val_dd_${p.id}`).value = sp.dd;
        atualizarBotaoVisual(p.id, 'am', sp.am);
        atualizarBotaoVisual(p.id, 'dd', sp.dd);
    });

    document.getElementById('workspaceArea').style.display = 'flex';
    document.getElementById('relatorioPanel').style.display = 'none';
}

function atualizarBotaoVisual(pilarId, tipo, valor) {
    let nivelNome = 'normal';
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
    if(!sessaoAtualId) return;
    let pilares = pilaresDef.map(p => ({
        id: p.id,
        am: document.getElementById(`val_am_${p.id}`).value,
        dd: document.getElementById(`val_dd_${p.id}`).value
    }));

    let payload = {
        username: currentUser,
        cliente_id: clienteAtualId,
        sessao_id: sessaoAtualId,
        impacto: document.getElementById('rangeImpacto').value,
        pilares: pilares
    };

    let res = await fetch('/api/sessao/salvar', { method: 'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload) });
    let data = await res.json();
    if(data.success) { alert("✅ Sessão gravada com sucesso!"); await carregarDadosUtilizador(); document.getElementById('selectCliente').value = clienteAtualId; selecionarCliente(clienteAtualId); document.getElementById('selectSessao').value = sessaoAtualId; }
}

async function apagarSessaoAtual() {
    if(!sessaoAtualId || !confirm("⚠️ Deseja apagar esta sessão?")) return;
    let res = await fetch('/api/sessao/apagar', { method: 'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({username: currentUser, cliente_id: clienteAtualId, sessao_id: sessaoAtualId}) });
    let data = await res.json();
    if(data.success) { alert("Sessão apagada."); await carregarDadosUtilizador(); selecionarCliente(clienteAtualId); }
}

function calcularResultadoRaioX() {
    let totalAm = 0, totalDd = 0;
    pilaresDef.forEach(p => {
        totalAm += parseInt(document.getElementById(`val_am_${p.id}`).value);
        totalDd += parseInt(document.getElementById(`val_dd_${p.id}`).value);
    });
    let mediaAm = Math.round(totalAm / 12);
    let mediaDd = Math.round(totalDd / 12);
    let impacto = document.getElementById('rangeImpacto').value;

    let raioHtml = `<strong>Balanço Energético Médio (AM):</strong> ${mediaAm}/95<br>
                    <strong>Índice Global de Peso / Problemas (DD):</strong> ${mediaDd}/95<br>
                    <strong>Fator de Impacto Diário:</strong> ${impacto}%<br>`;
    
    let conselhoHtml = "";
    if(mediaAm < 40 && mediaDd > 60) {
        conselhoHtml = "⚠️ O cliente encontra-se numa zona de alto esgotamento com forte pressão sistémica. Priorize a estabilização urgente do Sono (Pilar 1) e alívio de Finanças (Pilar 2) antes de avançar com projetos complexos.";
    } else if(mediaAm >= 70) {
        conselhoHtml = "🌟 Excelente vitalidade sistémica. O cliente tem margem de manobra para direcionar energia para os Planos de Futuro (Pilar 10) e consolidação profissional.";
    } else {
        conselhoHtml = "⚖️ Estado de equilíbrio instável. Há áreas moderadas a necessitar de reorganização de tempo (Pilar 9) para evitar bloqueios em cascata.";
    }

    document.getElementById('txtRaioX').innerHTML = raioHtml;
    document.getElementById('txtConselho').innerHTML = conselhoHtml;
    document.getElementById('relatorioPanel').style.display = 'block';
}

function exportarPDFSessao() {
    let cliente = clientesData.find(c => c.id === clienteAtualId);
    let jan = window.open('', '_blank');
    jan.document.write(`<html><head><title>Relatório de Sessão</title><style>body{font-family:sans-serif;padding:30px;color:#000;}</style></head><body>`);
    jan.document.write(`<h1>Atlas-Diagnostics — Relatório de Sessão</h1>`);
    jan.document.write(`<p><strong>Cliente:</strong> ${cliente.nome} | <strong>Idade:</strong> ${cliente.idade || 'N/A'}</p>`);
    jan.document.write(`<p><strong>Objetivo:</strong> ${cliente.objetivo || 'N/A'}</p><hr>`);
    jan.document.write(`<h3>Avaliação dos 12 Pilares:</h3><ul>`);
    pilaresDef.forEach(p => {
        let am = document.getElementById(`val_am_${p.id}`).value;
        let dd = document.getElementById(`val_dd_${p.id}`).value;
        jan.document.write(`<li><strong>${p.nome}</strong> — Energia (AM): ${am} | Peso (DD): ${dd}</li>`);
    });
    jan.document.write(`</ul><br><button onclick="window.print()">Imprimir / Guardar PDF</button></body></html>`);
    jan.document.close();
}

function exportarPDFMacro() {
    let cliente = clientesData.find(c => c.id === clienteAtualId);
    let jan = window.open('', '_blank');
    jan.document.write(`<html><head><title>Relatório Macro de Evolução</title><style>body{font-family:sans-serif;padding:30px;color:#000;}</style></head><body>`);
    jan.document.write(`<h1>Atlas-Diagnostics — Relatório Macro de Progressão</h1>`);
    jan.document.write(`<p><strong>Cliente:</strong> ${cliente.nome} | <strong>Total de Sessões Registadas:</strong> ${cliente.sessoes.length}</p><hr>`);
    cliente.sessoes.forEach((s, idx) => {
        jan.document.write(`<h3>Sessão #${idx + 1} — ${s.titulo} (${s.data || 'N/A'})</h3>`);
        jan.document.write(`<p>Impacto Diário: ${s.impacto || 50}%</p>`);
    });
    jan.document.write(`<br><button onclick="window.print()">Imprimir / Guardar PDF Macro</button></body></html>`);
    jan.document.close();
}
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
    if not u or not p: return jsonify({'success': False, 'error': 'Preencha todos os campos.'})
    user_file = os.path.join(DATA_DIR, f"{u}.json")
    if os.path.exists(user_file): return jsonify({'success': False, 'error': 'Utilizador já existe.'})
    with open(user_file, 'w', encoding='utf-8') as f:
        json.dump({'password': hash_password(p), 'clientes': []}, f, ensure_ascii=False, indent=4)
    return jsonify({'success': True})

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    u, p = data.get('username'), data.get('password')
    user_file = os.path.join(DATA_DIR, f"{u}.json")
    if not os.path.exists(user_file): return jsonify({'success': False, 'error': 'Utilizador não encontrado.'})
    with open(user_file, 'r', encoding='utf-8') as f: user_data = json.load(f)
    if user_data['password'] != hash_password(p): return jsonify({'success': False, 'error': 'Password incorreta.'})
    return jsonify({'success': True})

@app.route('/api/utilizador/apagar', methods=['POST'])
def api_apagar_utilizador():
    data = request.json
    u = data.get('username')
    user_file = os.path.join(DATA_DIR, f"{u}.json")
    if os.path.exists(user_file): os.remove(user_file)
    return jsonify({'success': True})

@app.route('/api/dados', methods=['GET'])
def api_obter_dados():
    u = request.args.get('username')
    user_file = os.path.join(DATA_DIR, f"{u}.json")
    if not os.path.exists(user_file): return jsonify({'clientes': []})
    with open(user_file, 'r', encoding='utf-8') as f: user_data = json.load(f)
    return jsonify({'clientes': user_data.get('clientes', [])})

@app.route('/api/cliente/criar', methods=['POST'])
def api_criar_cliente():
    data = request.json
    u = data.get('username')
    user_file = os.path.join(DATA_DIR, f"{u}.json")
    with open(user_file, 'r', encoding='utf-8') as f: user_data = json.load(f)
    
    novo_cliente = {
        'id': f"cli_{int(os.urandom(3).hex(), 16)}",
        'nome': data.get('nome'),
        'idade': data.get('idade'),
        'objetivo': data.get('objetivo'),
        'sessoes': []
    }
    user_data['clientes'].append(novo_cliente)
    with open(user_file, 'w', encoding='utf-8') as f: json.dump(user_data, f, ensure_ascii=False, indent=4)
    return jsonify({'success': True, 'cliente': novo_cliente})

@app.route('/api/cliente/atualizar', methods=['POST'])
def api_atualizar_cliente():
    data = request.json
    u, cli_id = data.get('username'), data.get('cliente_id')
    user_file = os.path.join(DATA_DIR, f"{u}.json")
    with open(user_file, 'r', encoding='utf-8') as f: user_data = json.load(f)
    for c in user_data['clientes']:
        if c['id'] == cli_id:
            c['nome'] = data.get('nome')
            c['idade'] = data.get('idade')
            c['objetivo'] = data.get('objetivo')
            break
    with open(user_file, 'w', encoding='utf-8') as f: json.dump(user_data, f, ensure_ascii=False, indent=4)
    return jsonify({'success': True})

@app.route('/api/cliente/apagar', methods=['POST'])
def api_apagar_cliente():
    data = request.json
    u, cli_id = data.get('username'), data.get('cliente_id')
    user_file = os.path.join(DATA_DIR, f"{u}.json")
    with open(user_file, 'r', encoding='utf-8') as f: user_data = json.load(f)
    user_data['clientes'] = [c for c in user_data['clientes'] if c['id'] != cli_id]
    with open(user_file, 'w', encoding='utf-8') as f: json.dump(user_data, f, ensure_ascii=False, indent=4)
    return jsonify({'success': True})

@app.route('/api/sessao/criar', methods=['POST'])
def api_criar_sessao():
    data = request.json
    u, cli_id = data.get('username'), data.get('cliente_id')
    user_file = os.path.join(DATA_DIR, f"{u}.json")
    with open(user_file, 'r', encoding='utf-8') as f: user_data = json.load(f)
    
    sessao_id = f"ses_{int(os.urandom(3).hex(), 16)}"
    for c in user_data['clientes']:
        if c['id'] == cli_id:
            nova_sessao = {
                'id': sessao_id,
                'titulo': f"Sessão #{len(c['sessoes']) + 1}",
                'data': "2026-11-17",
                'impacto': 50,
                'pilares': []
            }
            c['sessoes'].append(nova_sessao)
            break
    with open(user_file, 'w', encoding='utf-8') as f: json.dump(user_data, f, ensure_ascii=False, indent=4)
    return jsonify({'success': True, 'sessao': {'id': sessao_id}})

@app.route('/api/sessao/salvar', methods=['POST'])
def api_salvar_sessao():
    data = request.json
    u, cli_id, ses_id = data.get('username'), data.get('cliente_id'), data.get('sessao_id')
    user_file = os.path.join(DATA_DIR, f"{u}.json")
    with open(user_file, 'r', encoding='utf-8') as f: user_data = json.load(f)
    for c in user_data['clientes']:
        if c['id'] == cli_id:
            for s in c['sessoes']:
                if s['id'] == ses_id:
                    s['impacto'] = data.get('impacto')
                    s['pilares'] = data.get('pilares')
                    break
    with open(user_file, 'w', encoding='utf-8') as f: json.dump(user_data, f, ensure_ascii=False, indent=4)
    return jsonify({'success': True})

@app.route('/api/sessao/apagar', methods=['POST'])
def api_apagar_sessao():
    data = request.json
    u, cli_id, ses_id = data.get('username'), data.get('cliente_id'), data.get('sessao_id')
    user_file = os.path.join(DATA_DIR, f"{u}.json")
    with open(user_file, 'r', encoding='utf-8') as f: user_data = json.load(f)
    for c in user_data['clientes']:
        if c['id'] == cli_id:
            c['sessoes'] = [s for s in c['sessoes'] if s['id'] != ses_id]
            break
    with open(user_file, 'w', encoding='utf-8') as f: json.dump(user_data, f, ensure_ascii=False, indent=4)
    return jsonify({'success': True})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
