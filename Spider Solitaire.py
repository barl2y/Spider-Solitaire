import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Klondike Solitaire — 蜘蛛百人一首",
    page_icon="🂠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    [data-testid="stHeader"], [data-testid="stToolbar"], footer { display: none !important; }
    .main .block-container { 
        padding: 0rem !important; 
        margin: 0rem !important;
        max-width: 100% !important; 
        width: 100% !important;
    }
    html, body {
        margin: 0 !important;
        padding: 0 !important;
        overflow: hidden !important;
        width: 100% !important;
        height: 100% !important;
    }
    iframe { 
        border: none !important; 
        width: 100% !important; 
        height: 100vh !important; 
        display: block !important;
    }
    </style>
""", unsafe_allow_html=True)

klondike_full_html = """
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<style>
    @import url('https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@600;800&family=Cinzel:wght@700&display=swap');

    * { box-sizing: border-box; margin: 0; padding: 0; user-select: none; }
    html, body {
        width: 100%; height: 100%; overflow: hidden;
        background-color: #0c0d10;
        background-image: 
            radial-gradient(circle at 50% 35%, rgba(184, 155, 94, 0.22) 0%, rgba(12, 13, 16, 0.98) 75%),
            radial-gradient(circle at 10% 90%, rgba(184, 59, 50, 0.18) 0%, transparent 50%),
            radial-gradient(circle at 90% 10%, rgba(36, 52, 71, 0.3) 0%, transparent 50%),
            url("data:image/svg+xml,%3Csvg width='80' height='80' viewBox='0 0 80 80' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%23d4af37' fill-opacity='0.06' fill-rule='evenodd'%3E%3Cpath d='M0 0h40v40H0V0zm40 40h40v40H40V40zm0-40h40v40H40V0zM0 40h40v40H0V40z'/%3E%3Ccircle cx='40' cy='40' r='18' stroke='%23d4af37' stroke-opacity='0.08' stroke-width='2' fill='none'/%3E%3C/g%3E%3C/svg%3E");
        font-family: 'Shippori Mincho', serif;
        display: flex; flex-direction: column;
        position: relative;
    }

    /* 벚꽃 가지 오나먼트 및 분홍색 광원 애니메이션 */
    .cherry-branch {
        position: absolute; top: 35px; pointer-events: none; z-index: 6;
    }
    .cherry-left { left: -10px; width: 300px; height: 300px; }
    .cherry-right { right: -10px; width: 300px; height: 300px; transform: scaleX(-1); }

    .cherry-glow {
        animation: sakuraGlowPulse 3.5s ease-in-out infinite alternate;
    }
    @keyframes sakuraGlowPulse {
        0% { filter: drop-shadow(0 0 6px rgba(255, 183, 197, 0.3)); }
        50% { filter: drop-shadow(0 0 18px rgba(255, 183, 197, 0.8)); }
        100% { filter: drop-shadow(0 0 28px rgba(255, 105, 180, 0.9)); }
    }

    /* 등불(Lantern) 주황색 따뜻한 광원 애니메이션 */
    .lantern-glow {
        animation: lanternGlowPulse 2.2s ease-in-out infinite alternate;
        transform-origin: center;
    }
    @keyframes lanternGlowPulse {
        0% { filter: drop-shadow(0 0 5px rgba(255, 160, 50, 0.5)) drop-shadow(0 0 12px rgba(255, 100, 0, 0.3)); opacity: 0.8; }
        100% { filter: drop-shadow(0 0 22px rgba(255, 190, 60, 1)) drop-shadow(0 0 35px rgba(255, 120, 0, 0.8)); opacity: 1; }
    }

    /* 하단 전통 실루엣 건물 */
    .bg-building {
        position: absolute; bottom: 50px; pointer-events: none; z-index: 2; opacity: 0.25;
    }
    .building-left { left: 0; width: 220px; }
    .building-right { right: 0; width: 220px; transform: scaleX(-1); }

    #top-bar {
        height: 50px; background: rgba(15, 15, 18, 0.92);
        border-bottom: 1px solid rgba(212, 175, 55, 0.4);
        box-shadow: 0 2px 10px rgba(0,0,0,0.5);
        display: flex; justify-content: space-between; align-items: center;
        padding: 0 25px; color: #f3ebdd; font-size: 16px; z-index: 100; flex-shrink: 0;
    }
    .jp-title { font-weight: 800; letter-spacing: 0.25em; color: #f3ebdd; text-shadow: 0 0 8px rgba(212,175,55,0.3); }
    .jp-stats { font-family: 'Cinzel', serif; color: #d4af37; font-size: 15px; }

    #game-board { flex: 1; position: relative; width: 100%; height: 100%; overflow: hidden; z-index: 10; }

    #bottom-bar {
        height: 50px; background: rgba(12, 12, 15, 0.95);
        border-top: 1px solid rgba(212, 175, 55, 0.3);
        display: flex; justify-content: center; align-items: center; gap: 15px; z-index: 100; flex-shrink: 0;
    }
    .btn {
        background: linear-gradient(180deg, #1c2836 0%, #0d0d10 100%);
        color: #f3ebdd; border: 1px solid #d4af37; padding: 6px 18px;
        border-radius: 3px; cursor: pointer; font-family: 'Shippori Mincho', serif;
        font-size: 14px; letter-spacing: 0.1em; transition: all 0.2s;
        box-shadow: 0 2px 6px rgba(0,0,0,0.4);
    }
    .btn:hover { background: #b83b32; color: #fff; border-color: #f3ebdd; box-shadow: 0 0 10px rgba(184,59,50,0.6); }

    #auto-btn {
        position: absolute; left: 50%; transform: translateX(-50%);
        top: 12px; display: none; z-index: 500;
        background: linear-gradient(180deg, #ffd700 0%, #997a00 100%);
        color: #0d0d0d; font-weight: 800; font-size: 14px;
        padding: 6px 22px; border: 2px solid #fff8dc; border-radius: 4px;
        box-shadow: 0 0 20px rgba(255, 215, 0, 0.8); cursor: pointer; transition: all 0.2s;
    }
    #auto-btn:hover { transform: translateX(-50%) scale(1.05); background: #fff8dc; }

    .card {
        position: absolute; border-radius: 6px; background-color: #f3ebdd;
        background-image: radial-gradient(#e5d9c5 1px, transparent 0); background-size: 6px 6px;
        border: 1px solid #c8b9a6; box-shadow: 0 4px 10px rgba(0,0,0,0.6);
        cursor: grab; display: flex; flex-direction: column; justify-content: space-between;
        padding: 4px; font-family: 'Cinzel', serif; font-weight: 700;
        transition: transform 0.15s ease, box-shadow 0.2s ease, border-color 0.2s ease;
        z-index: 10;
    }

    .card.selected {
        border: 2px solid #ffd700 !important;
        box-shadow: 0 0 22px rgba(255, 215, 0, 1), 0 0 8px rgba(255, 255, 255, 0.9) !important;
        transform: translateY(-8px) scale(1.03) !important;
        z-index: 8000 !important;
    }

    .card.dragging {
        cursor: grabbing !important; transition: none !important;
        box-shadow: 0 12px 24px rgba(0,0,0,0.8), 0 0 18px rgba(212, 175, 55, 0.9) !important;
        z-index: 9999 !important;
    }
    .card.highlight { animation: hintPulse 1s infinite alternate; border: 2px solid #b83b32 !important; }
    @keyframes hintPulse {
        0% { transform: scale(1); box-shadow: 0 0 5px #b83b32; }
        100% { transform: scale(1.05); box-shadow: 0 0 15px #b83b32; }
    }
    .card.back {
        background: #141f2c; border: 1px solid #d4af37;
        background-image: url("data:image/svg+xml,%3Csvg width='24' height='41.569' viewBox='0 0 24 41.569' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M12 0L0 6.928v13.856L12 27.713l12-6.929V6.928L12 0zm0 2.309l9.6 5.543v11.085L12 24.48 2.4 18.937V7.852L12 2.31zM12 27.713L0 34.641v6.928h24v-6.928l-12-6.928z' fill='%23d4af37' fill-opacity='0.3'/%3E%3C/svg%3E");
        cursor: pointer;
    }
    .card.red { color: #b83b32; }
    .card.black { color: #151515; }
    .card .corner { line-height: 1; text-align: center; font-size: 0.8em; }
    .card .suit-center { font-size: 1.35em; text-align: center; margin: auto; }

    .card-slot {
        position: absolute; border-radius: 6px;
        border: 1px dashed rgba(212, 175, 55, 0.4); background: rgba(20, 20, 25, 0.5);
        display: flex; align-items: center; justify-content: center;
        color: rgba(212, 175, 55, 0.4); font-size: 0.85rem;
    }

    #fx-canvas { position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 2000; }

    /* 모달 */
    #win-modal {
        position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
        background: rgba(12, 12, 15, 0.96); border: 2px solid #d4af37;
        padding: 30px 45px; text-align: center; color: #f3ebdd;
        box-shadow: 0 0 40px rgba(0,0,0,0.95), 0 0 20px rgba(212, 175, 55, 0.6);
        z-index: 3000; display: none; border-radius: 4px;
    }

    #fail-modal {
        position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
        background: radial-gradient(circle, rgba(35, 10, 15, 0.98) 0%, rgba(10, 5, 8, 0.98) 100%);
        border: 2px solid #ff0055; padding: 35px 50px; text-align: center; color: #f3ebdd;
        box-shadow: 0 0 50px rgba(255, 0, 85, 0.6), inset 0 0 20px rgba(255, 0, 85, 0.3);
        z-index: 3000; display: none; border-radius: 6px;
    }
    #fail-modal h2 { font-weight: 800; color: #ff0055; letter-spacing: 0.25em; margin-bottom: 12px; font-size: 24px; text-shadow: 0 0 10px #ff0055; }
    #fail-modal p { font-size: 15px; margin: 6px 0; color: #f3ebdd; }
    .btn-fail {
        background: linear-gradient(180deg, #ff0055 0%, #80002a 100%) !important;
        border-color: #ff99b3 !important; margin-top: 18px;
    }
    .btn-fail:hover { box-shadow: 0 0 15px rgba(255,0,85,0.8) !important; }
</style>
</head>
<body>

<!-- 좌/우 상단 벚꽃 가지 + 전통 등불 (빛의 색깔 및 주기적 변동 적용) -->
<svg class="cherry-branch cherry-left" viewBox="0 0 200 200">
    <path d="M 0 0 Q 60 40 120 20 T 180 60" stroke="#3a2312" stroke-width="5" fill="none" />
    <path d="M 60 40 Q 90 70 110 100" stroke="#3a2312" stroke-width="3" fill="none" />
    <!-- 벚꽃 꽃잎 (핑크빛 광원) -->
    <g class="cherry-glow">
        <circle cx="120" cy="20" r="12" fill="#ffc0cb" opacity="0.95" />
        <circle cx="180" cy="60" r="14" fill="#ffb7c5" opacity="0.95" />
        <circle cx="110" cy="100" r="10" fill="#ffb7c5" opacity="0.95" />
    </g>
    <!-- 등불 연결선 및 등불 (주황색/황금빛 광원) -->
    <line x1="180" y1="60" x2="180" y2="95" stroke="#222" stroke-width="2" />
    <g class="lantern-glow">
        <rect x="168" y="95" width="24" height="32" rx="3" fill="#e65100" stroke="#d4af37" stroke-width="2"/>
        <rect x="172" y="99" width="16" height="24" rx="1" fill="#ffb74d"/>
        <line x1="180" y1="99" x2="180" y2="123" stroke="#e65100" stroke-width="1.5"/>
    </g>
</svg>

<svg class="cherry-branch cherry-right" viewBox="0 0 200 200">
    <path d="M 0 0 Q 60 40 120 20 T 180 60" stroke="#3a2312" stroke-width="5" fill="none" />
    <path d="M 60 40 Q 90 70 110 100" stroke="#3a2312" stroke-width="3" fill="none" />
    <g class="cherry-glow">
        <circle cx="120" cy="20" r="12" fill="#ffc0cb" opacity="0.95" />
        <circle cx="180" cy="60" r="14" fill="#ffb7c5" opacity="0.95" />
        <circle cx="110" cy="100" r="10" fill="#ffb7c5" opacity="0.95" />
    </g>
    <line x1="180" y1="60" x2="180" y2="95" stroke="#222" stroke-width="2" />
    <g class="lantern-glow">
        <rect x="168" y="95" width="24" height="32" rx="3" fill="#e65100" stroke="#d4af37" stroke-width="2"/>
        <rect x="172" y="99" width="16" height="24" rx="1" fill="#ffb74d"/>
        <line x1="180" y1="99" x2="180" y2="123" stroke="#e65100" stroke-width="1.5"/>
    </g>
</svg>

<!-- 하단 일본 풍격 전통 기와 건물 Silhouettes -->
<svg class="bg-building building-left" viewBox="0 0 200 150">
    <path d="M 10 150 L 10 90 L 0 90 L 30 60 L 170 60 L 200 90 L 190 90 L 190 150 Z" fill="#d4af37"/>
    <path d="M 20 60 L 100 20 L 180 60 Z" fill="#b83b32"/>
</svg>
<svg class="bg-building building-right" viewBox="0 0 200 150">
    <path d="M 10 150 L 10 90 L 0 90 L 30 60 L 170 60 L 200 90 L 190 90 L 190 150 Z" fill="#d4af37"/>
    <path d="M 20 60 L 100 20 L 180 60 Z" fill="#b83b32"/>
</svg>

<div id="top-bar">
    <div class="jp-title">クロンダイク — Klondike Solitaire</div>
    <div class="jp-stats">점수: <span id="score">0</span> &nbsp;|&nbsp; 시간: <span id="timer">00:00</span></div>
</div>

<div id="game-board">
    <button id="auto-btn" onclick="runAutoComplete()">⚡ 자동 완성 실행</button>
    <canvas id="fx-canvas"></canvas>
</div>

<div id="bottom-bar">
    <button class="btn" onclick="initGame()">새 게임</button>
    <button class="btn" onclick="undoMove()">되돌리기 (Undo)</button>
    <button class="btn" onclick="showHint()">힌트 (Hint)</button>
</div>

<div id="win-modal">
    <h2>祝・見事クリア！</h2>
    <p>축하합니다! 게임을 완성하셨습니다.</p>
    <hr style="border:0; border-top:1px solid rgba(212,175,55,0.3); margin: 12px 0;">
    <p>최종 점수: <span id="final-score" style="color:#d4af37; font-weight:bold;">0</span>점</p>
    <p>소요 시간: <span id="final-time" style="color:#d4af37; font-weight:bold;">00:00</span></p>
    <button class="btn" style="margin-top:15px;" onclick="initGame()">다시 도전하기</button>
</div>

<div id="fail-modal">
    <h2>NO MORE MOVES</h2>
    <p>더 이상 이동 가능한 수가 없습니다!</p>
    <hr style="border:0; border-top:1px solid rgba(255,0,85,0.3); margin: 12px 0;">
    <p>최종 점수: <span id="fail-score" style="color:#ff0055; font-weight:bold;">0</span>점</p>
    <button class="btn btn-fail" onclick="initGame()">다시 시도하기</button>
</div>

<script>
const SUITS = ['♠', '♥', '♦', '♣'];
const VALUES = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K'];

let stock = [], waste = [], foundations = [[], [], [], []], tableau = [[], [], [], [], [], [], []];
let history = [];
let dragGroup = [], isDragging = false, dragStartX = 0, dragStartY = 0;
let cardW = 0, cardH = 0, gap = 0, startY = 0, offsetX = 0;
let timeSeconds = 0, timerInterval = null, score = 0, isGameWon = false, isGameOver = false;
let selectedInfo = null;

function clearSelection() {
    selectedInfo = null;
    document.querySelectorAll('.card').forEach(c => c.classList.remove('selected'));
}

function updateSelectedUI() {
    document.querySelectorAll('.card').forEach(c => c.classList.remove('selected'));
    if (selectedInfo && selectedInfo.card) {
        let selectedEl = document.getElementById(selectedInfo.card.uid);
        if (selectedEl) selectedEl.classList.add('selected');
    }
}

function resizeBoard() {
    const board = document.getElementById('game-board');
    const w = board.clientWidth;
    
    cardW = Math.min((w * 0.88) / 7.8, 82); 
    cardH = cardW * 1.42;
    gap = cardW * 0.18; 

    let totalWidth = (cardW * 7) + (gap * 6);
    offsetX = Math.max((w - totalWidth) / 2, 15);
    startY = cardH + gap * 1.2; 
    render();
}

function initGame() {
    document.getElementById('win-modal').style.display = 'none';
    document.getElementById('fail-modal').style.display = 'none';
    document.getElementById('auto-btn').style.display = 'none';
    isGameWon = false;
    isGameOver = false;
    clearSelection();

    let deck = [], idCounter = 0;
    for (let s = 0; s < 4; s++) {
        for (let v = 1; v <= 13; v++) {
            deck.push({
                suit: SUITS[s], color: (s === 1 || s === 2) ? 'red' : 'black',
                value: v, name: VALUES[v-1], faceUp: false, uid: 'card_' + (idCounter++)
            });
        }
    }
    deck.sort(() => Math.random() - 0.5);

    tableau = [[], [], [], [], [], [], []]; foundations = [[], [], [], []];
    waste = []; history = []; score = 0;

    for (let i = 0; i < 7; i++) {
        for (let j = 0; j <= i; j++) {
            let card = deck.pop();
            if (j === i) card.faceUp = true;
            tableau[i].push(card);
        }
    }
    stock = deck;

    clearInterval(timerInterval);
    timeSeconds = 0;
    timerInterval = setInterval(() => {
        if (!isGameWon && !isGameOver) {
            timeSeconds++;
            let m = String(Math.floor(timeSeconds / 60)).padStart(2, '0');
            let s = String(timeSeconds % 60).padStart(2, '0');
            document.getElementById('timer').innerText = `${m}:${s}`;
        }
    }, 1000);

    resizeBoard();
}

function saveState() {
    history.push(JSON.stringify({ stock, waste, foundations, tableau, score }));
}

function undoMove() {
    if (history.length === 0 || isGameWon || isGameOver) return;
    clearSelection();
    let state = JSON.parse(history.pop());
    stock = state.stock; waste = state.waste;
    foundations = state.foundations; tableau = state.tableau; score = state.score;
    render();
}

function render() {
    const board = document.getElementById('game-board');
    const cardsAndSlots = board.querySelectorAll('.card, .card-slot');
    cardsAndSlots.forEach(el => el.remove());

    document.getElementById('score').innerText = score;

    let leftStock = offsetX;
    createSlot(leftStock, gap, '空', () => handleStockClick());
    if (stock.length > 0) {
        let c = createCardEl(stock[stock.length - 1], leftStock, gap, false);
        c.onclick = (e) => { e.stopPropagation(); handleStockClick(); };
    }

    let leftWaste = offsetX + cardW + gap;
    createSlot(leftWaste, gap, '捨', () => tryMoveSelectedTo('waste', 0));
    if (waste.length > 0) {
        let card = waste[waste.length - 1];
        let c = createCardEl(card, leftWaste, gap, true);
        bindCardEvents(c, card, 'waste', 0, waste.length - 1);
    }

    for (let i = 0; i < 4; i++) {
        let leftF = offsetX + (cardW + gap) * (3 + i);
        createSlot(leftF, gap, '組', () => tryMoveSelectedTo('foundation', i));
        if (foundations[i].length > 0) {
            let card = foundations[i][foundations[i].length - 1];
            let c = createCardEl(card, leftF, gap, true);
            bindCardEvents(c, card, 'foundation', i, foundations[i].length - 1);
        }
    }

    const cardSpacing = Math.min(cardH * 0.22, 22); 
    for (let i = 0; i < 7; i++) {
        let leftT = offsetX + (cardW + gap) * i;
        createSlot(leftT, startY, '場', () => tryMoveSelectedTo('tableau', i));
        
        for (let j = 0; j < tableau[i].length; j++) {
            let card = tableau[i][j];
            let topT = startY + j * cardSpacing;
            let c = createCardEl(card, leftT, topT, card.faceUp);
            if (card.faceUp) bindCardEvents(c, card, 'tableau', i, j);
        }
    }

    updateSelectedUI();
    checkAutoCompleteCondition();
    checkWinCondition();
    checkNoMovesCondition();
}

function createSlot(x, y, label, onClick) {
    const board = document.getElementById('game-board');
    const slot = document.createElement('div');
    slot.className = 'card-slot';
    slot.style.width = cardW + 'px'; slot.style.height = cardH + 'px';
    slot.style.left = x + 'px'; slot.style.top = y + 'px';
    slot.innerText = label;
    slot.onclick = (e) => { e.stopPropagation(); if (onClick) onClick(); };
    board.appendChild(slot);
}

function createCardEl(card, x, y, faceUp) {
    const board = document.getElementById('game-board');
    const el = document.createElement('div');
    el.id = card.uid;
    el.style.width = cardW + 'px'; el.style.height = cardH + 'px';
    el.style.left = x + 'px'; el.style.top = y + 'px';

    if (!faceUp) {
        el.className = 'card back';
    } else {
        el.className = `card ${card.color}`;
        el.innerHTML = `
            <div class="corner">${card.name}<br>${card.suit}</div>
            <div class="suit-center">${card.suit}</div>
            <div class="corner" style="transform: rotate(180deg);">${card.name}<br>${card.suit}</div>
        `;
    }
    board.appendChild(el);
    return el;
}

function handleStockClick() {
    if (isGameWon || isGameOver) return;
    clearSelection();
    saveState();
    if (stock.length === 0) {
        stock = waste.reverse().map(c => ({...c, faceUp: false}));
        waste = [];
    } else {
        let card = stock.pop(); card.faceUp = true; waste.push(card);
    }
    render();
}

function bindCardEvents(el, card, srcType, colIdx, cardIdx) {
    let clickTime = 0, isMoveAction = false;
    el.onmousedown = (e) => {
        if (e.button !== 0 || isGameWon || isGameOver) return;
        e.stopPropagation();

        let now = new Date().getTime();
        if (now - clickTime < 260) {
            clearSelection(); autoMove(card, srcType, colIdx, cardIdx);
            clickTime = 0; return;
        }
        clickTime = now;

        if (selectedInfo && (selectedInfo.card.uid !== card.uid)) {
            let moved = tryMoveSelectedTo(srcType, colIdx);
            if (moved) return;
        }

        isDragging = false; isMoveAction = false;
        dragStartX = e.clientX; dragStartY = e.clientY;
        dragGroup = [];

        if (srcType === 'tableau') {
            for (let k = cardIdx; k < tableau[colIdx].length; k++) {
                let targetCard = tableau[colIdx][k];
                let cEl = document.getElementById(targetCard.uid);
                if (cEl) dragGroup.push({ el: cEl, card: targetCard, origX: parseFloat(cEl.style.left), origY: parseFloat(cEl.style.top) });
            }
        } else {
            dragGroup.push({ el: el, card: card, origX: parseFloat(el.style.left), origY: parseFloat(el.style.top) });
        }

        document.onmousemove = (e) => {
            let dx = e.clientX - dragStartX, dy = e.clientY - dragStartY;
            if (Math.abs(dx) > 5 || Math.abs(dy) > 5) {
                isDragging = true; isMoveAction = true;
                dragGroup.forEach(item => {
                    item.el.classList.add('dragging');
                    item.el.style.left = (item.origX + dx) + 'px';
                    item.el.style.top = (item.origY + dy) + 'px';
                });
            }
        };

        document.onmouseup = (e) => {
            document.onmousemove = null; document.onmouseup = null;
            if (isDragging) {
                dragGroup.forEach(item => item.el.classList.remove('dragging'));
                let dropped = checkDrop(card, srcType, colIdx, cardIdx, e.clientX, e.clientY);
                if (!dropped) dragGroup.forEach(item => { item.el.style.left = item.origX + 'px'; item.el.style.top = item.origY + 'px'; });
                else { clearSelection(); render(); }
                isDragging = false;
            } else if (!isMoveAction) {
                if (selectedInfo && selectedInfo.card.uid === card.uid) {
                    clearSelection();
                } else {
                    selectedInfo = { card, srcType, colIdx, cardIdx };
                }
                updateSelectedUI();
            }
        };
    };
}

function tryMoveSelectedTo(targetType, targetColIdx) {
    if (!selectedInfo) return false;
    let { card, srcType, colIdx: srcCol, cardIdx: srcIdx } = selectedInfo;

    if (targetType === 'foundation') {
        if (selectedInfo.srcType === 'tableau' && srcIdx !== tableau[srcCol].length - 1) return false;
        let target = foundations[targetColIdx];
        let topCard = target[target.length - 1];
        if ((!topCard && card.value === 1) || (topCard && topCard.suit === card.suit && topCard.value === card.value - 1)) {
            saveState(); target.push(removeSourceCard(srcType, srcCol, srcIdx)[0]);
            score += 10; clearSelection(); render(); return true;
        }
    }

    if (targetType === 'tableau') {
        if (srcType === 'tableau' && srcCol === targetColIdx) { clearSelection(); return true; }
        let targetCol = tableau[targetColIdx];
        let topCard = targetCol[targetCol.length - 1];
        if ((!topCard && card.value === 13) || (topCard && topCard.color !== card.color && topCard.value === card.value + 1)) {
            saveState();
            tableau[targetColIdx] = tableau[targetColIdx].concat(removeSourceCard(srcType, srcCol, srcIdx));
            score += 5; clearSelection(); render(); return true;
        }
    }
    clearSelection();
    return false;
}

function autoMove(card, srcType, colIdx, cardIdx) {
    if (srcType === 'tableau' && cardIdx !== tableau[colIdx].length - 1) return;
    for (let f = 0; f < 4; f++) {
        let target = foundations[f]; let topCard = target[target.length - 1];
        if ((!topCard && card.value === 1) || (topCard && topCard.suit === card.suit && topCard.value === card.value - 1)) {
            saveState(); target.push(removeSourceCard(srcType, colIdx, cardIdx)[0]);
            score += 10; render(); return;
        }
    }
    for (let t = 0; t < 7; t++) {
        if (srcType === 'tableau' && t === colIdx) continue;
        let targetCol = tableau[t]; let topCard = targetCol[targetCol.length - 1];
        if ((!topCard && card.value === 13) || (topCard && topCard.color !== card.color && topCard.value === card.value + 1)) {
            saveState();
            tableau[t] = tableau[t].concat(removeSourceCard(srcType, colIdx, cardIdx));
            score += 5; render(); return;
        }
    }
}

function checkDrop(card, srcType, srcCol, srcIdx, mouseX, mouseY) {
    if (dragGroup.length === 1) {
        for (let f = 0; f < 4; f++) {
            let leftF = offsetX + (cardW + gap) * (3 + f);
            if (mouseX >= leftF - 20 && mouseX <= leftF + cardW + 20 && mouseY >= gap - 20 && mouseY <= gap + cardH + 20) {
                let target = foundations[f]; let topCard = target[target.length - 1];
                if ((!topCard && card.value === 1) || (topCard && topCard.suit === card.suit && topCard.value === card.value - 1)) {
                    saveState(); target.push(removeSourceCard(srcType, srcCol, srcIdx)[0]);
                    score += 10; return true;
                }
            }
        }
    }
    for (let t = 0; t < 7; t++) {
        let leftT = offsetX + (cardW + gap) * t;
        let targetCol = tableau[t]; let topCard = targetCol[targetCol.length - 1];
        if (mouseX >= leftT - 15 && mouseX <= leftT + cardW + 15) {
            if ((!topCard && card.value === 13) || (topCard && topCard.color !== card.color && topCard.value === card.value + 1)) {
                saveState();
                tableau[t] = tableau[t].concat(removeSourceCard(srcType, srcCol, srcIdx));
                score += 5; return true;
            }
        }
    }
    return false;
}

function removeSourceCard(type, col, idx) {
    let cards = [];
    if (type === 'waste') cards = waste.pop();
    else if (type === 'foundation') cards = foundations[col].pop();
    else if (type === 'tableau') {
        cards = tableau[col].splice(idx);
        if (tableau[col].length > 0) tableau[col][tableau[col].length - 1].faceUp = true;
    }
    return Array.isArray(cards) ? cards : [cards];
}

/* 스톡/버려진 카드를 전수 조사하여 완전히 유효한 수가 없는지 판단하는 최신화 기준 */
function checkNoMovesCondition() {
    if (isGameWon || isGameOver) return;

    // 1. 현재 버려진 카드(Waste)에서 옮길 수 있는지 체킹
    if (waste.length > 0) {
        let wCard = waste[waste.length - 1];
        for (let f = 0; f < 4; f++) {
            let topCard = foundations[f][foundations[f].length - 1];
            if ((!topCard && wCard.value === 1) || (topCard && topCard.suit === wCard.suit && topCard.value === wCard.value - 1)) return;
        }
        for (let t = 0; t < 7; t++) {
            let topCard = tableau[t][tableau[t].length - 1];
            if ((!topCard && wCard.value === 13) || (topCard && topCard.color !== wCard.color && topCard.value === wCard.value + 1)) return;
        }
    }

    // 2. 필드(Tableau)의 오픈 카드들에서 옮길 수 있는지 체킹
    for (let t = 0; t < 7; t++) {
        if (tableau[t].length === 0) continue;
        for (let j = 0; j < tableau[t].length; j++) {
            let card = tableau[t][j];
            if (!card.faceUp) continue;
            if (j === tableau[t].length - 1) {
                for (let f = 0; f < 4; f++) {
                    let topCard = foundations[f][foundations[f].length - 1];
                    if ((!topCard && card.value === 1) || (topCard && card.suit === topCard.suit && topCard.value === topCard.value - 1)) return;
                }
            }
            for (let t2 = 0; t2 < 7; t2++) {
                if (t === t2) continue;
                let topCard = tableau[t2][tableau[t2].length - 1];
                if ((!topCard && card.value === 13 && j > 0) || (topCard && topCard.color !== card.color && topCard.value === card.value + 1)) return;
            }
        }
    }

    // 3. 스톡(Stock)에 남아있는 모든 카드들을 검수
    // 스톡에 남아있는 카드 중 단 하나라도 필드나 완성덱으로 이동될 가능성이 있다면 종료하지 않음
    if (stock.length > 0) {
        for (let i = 0; i < stock.length; i++) {
            let sCard = stock[i];
            for (let f = 0; f < 4; f++) {
                let topCard = foundations[f][foundations[f].length - 1];
                if ((!topCard && sCard.value === 1) || (topCard && topCard.suit === sCard.suit && topCard.value === sCard.value - 1)) return;
            }
            for (let t = 0; t < 7; t++) {
                let topCard = tableau[t][tableau[t].length - 1];
                if ((!topCard && sCard.value === 13) || (topCard && topCard.color !== sCard.color && topCard.value === sCard.value + 1)) return;
            }
        }
    }

    // 위 3가지 가능성을 모두 통과 못 했다면 Game Over 판정
    triggerFailScreen();
}

function triggerFailScreen() {
    isGameOver = true;
    clearInterval(timerInterval);
    launchCrimsonShatterImpact();
    setTimeout(() => {
        document.getElementById('fail-score').innerText = score;
        document.getElementById('fail-modal').style.display = 'block';
    }, 600);
}

function launchCrimsonShatterImpact() {
    const canvas = document.getElementById('fx-canvas');
    const ctx = canvas.getContext('2d');
    canvas.width = canvas.clientWidth;
    canvas.height = canvas.clientHeight;

    const cx = canvas.width / 2, cy = canvas.height / 2;
    let particles = [], shockwaves = [];

    shockwaves.push({ x: cx, y: cy, r: 10, maxR: Math.max(cx, cy) * 1.2, alpha: 1, color: '#ff0055', lw: 20 });
    for (let i = 0; i < 80; i++) {
        let ang = Math.random() * Math.PI * 2;
        let spd = Math.random() * 15 + 4;
        particles.push({
            x: cx, y: cy, vx: Math.cos(ang) * spd, vy: Math.sin(ang) * spd,
            life: 1, color: Math.random() > 0.3 ? '#ff0055' : '#ffffff', size: Math.random() * 6 + 2
        });
    }

    function anim() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        shockwaves.forEach(sw => {
            sw.r += (sw.maxR - sw.r) * 0.1;
            sw.alpha -= 0.03;
            if (sw.alpha > 0) {
                ctx.save(); ctx.beginPath(); ctx.arc(sw.x, sw.y, sw.r, 0, Math.PI * 2);
                ctx.lineWidth = sw.lw; ctx.strokeStyle = sw.color; ctx.globalAlpha = Math.max(0, sw.alpha);
                ctx.stroke(); ctx.restore();
            }
        });
        particles.forEach(p => {
            p.x += p.vx; p.y += p.vy; p.life -= 0.02;
            if (p.life > 0) {
                ctx.save(); ctx.globalAlpha = p.life; ctx.fillStyle = p.color;
                ctx.beginPath(); ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2); ctx.fill(); ctx.restore();
            }
        });
        if (shockwaves.some(s => s.alpha > 0) || particles.some(p => p.life > 0)) requestAnimationFrame(anim);
    }
    anim();
}

function showHint() {
    document.querySelectorAll('.card').forEach(c => c.classList.remove('highlight'));
    if (waste.length > 0) {
        let wCard = waste[waste.length - 1];
        for (let f = 0; f < 4; f++) {
            let topCard = foundations[f][foundations[f].length - 1];
            if ((!topCard && wCard.value === 1) || (topCard && topCard.suit === wCard.suit && topCard.value === wCard.value - 1)) {
                document.getElementById(wCard.uid)?.classList.add('highlight'); return;
            }
        }
    }
    for (let t = 0; t < 7; t++) {
        if (tableau[t].length === 0) continue;
        let tCard = tableau[t][tableau[t].length - 1];
        for (let f = 0; f < 4; f++) {
            let topCard = foundations[f][foundations[f].length - 1];
            if ((!topCard && tCard.value === 1) || (topCard && tCard.suit === tCard.suit && topCard.value === tCard.value - 1)) {
                document.getElementById(tCard.uid)?.classList.add('highlight'); return;
            }
        }
    }
    if (stock.length > 0) {
        let stockEl = document.getElementById(stock[stock.length - 1].uid);
        if (stockEl) stockEl.classList.add('highlight');
    }
}

function checkAutoCompleteCondition() {
    if (stock.length > 0 || waste.length > 1) return;
    let allFaceUp = tableau.every(col => col.every(c => c.faceUp));
    if (allFaceUp && !isGameWon) document.getElementById('auto-btn').style.display = 'block';
    else document.getElementById('auto-btn').style.display = 'none';
}

function runAutoComplete() {
    document.getElementById('auto-btn').style.display = 'none';
    clearSelection();
    let autoInterval = setInterval(() => {
        let moved = false;
        if (waste.length > 0) {
            let card = waste[waste.length - 1];
            for (let f = 0; f < 4; f++) {
                let topCard = foundations[f][foundations[f].length - 1];
                if ((!topCard && card.value === 1) || (topCard && topCard.suit === card.suit && topCard.value === card.value - 1)) {
                    foundations[f].push(waste.pop()); score += 10; moved = true; break;
                }
            }
        }
        if (!moved) {
            for (let t = 0; t < 7; t++) {
                if (tableau[t].length === 0) continue;
                let card = tableau[t][tableau[t].length - 1];
                for (let f = 0; f < 4; f++) {
                    let topCard = foundations[f][foundations[f].length - 1];
                    if ((!topCard && card.value === 1) || (topCard && card.suit === card.suit && topCard.value === card.value - 1)) {
                        foundations[f].push(tableau[t].pop()); score += 10; moved = true; break;
                    }
                }
                if (moved) break;
            }
        }
        render();
        if (!moved || foundations.every(f => f.length === 13)) clearInterval(autoInterval);
    }, 100);
}

function checkWinCondition() {
    let win = foundations.every(f => f.length === 13);
    if (win && !isGameWon) {
        isGameWon = true;
        clearInterval(timerInterval);
        document.getElementById('final-score').innerText = score;
        document.getElementById('final-time').innerText = document.getElementById('timer').innerText;
        document.getElementById('win-modal').style.display = 'block';
    }
}

window.onresize = resizeBoard;
window.onload = () => { setTimeout(initGame, 100); };
</script>
</body>
</html>
"""

components.html(klondike_full_html, height=850, scrolling=False)
