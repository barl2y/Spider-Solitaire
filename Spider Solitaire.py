import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Klondike Solitaire — 蜘蛛百人一首",
    page_icon="🂠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Streamlit 여백 및 헤더 제거
st.markdown("""
    <style>
    [data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; }
    .main .block-container { padding: 0rem !important; max-width: 100% !important; }
    iframe { border: none !important; width: 100vw !important; height: 100vh !important; }
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
    body {
        background-color: #0d0d0d;
        background-image: 
            radial-gradient(circle at 50% 50%, rgba(36, 52, 71, 0.3) 0%, rgba(13, 13, 13, 0.95) 100%),
            url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%23b89b5e' fill-opacity='0.04' fill-rule='evenodd'%3E%3Cpath d='M30 30L15 0H0v15l30 30 30-30V0H45L30 30zM0 45h15l15-15 15 15h15V30L30 60 0 30v15z'/%3E%3C/g%3E%3C/svg%3E");
        font-family: 'Shippori Mincho', serif;
        width: 100vw; height: 100vh; overflow: hidden;
        display: flex; flex-direction: column;
    }

    #top-bar {
        height: 52px; background: rgba(21, 21, 21, 0.9);
        border-bottom: 1px solid rgba(184, 155, 94, 0.3);
        display: flex; justify-content: space-between; align-items: center;
        padding: 0 25px; color: #f3ebdd; font-size: 16px; z-index: 100;
    }
    .jp-title { font-weight: 800; letter-spacing: 0.2em; color: #f3ebdd; }
    .jp-stats { font-family: 'Cinzel', serif; color: #b89b5e; font-size: 15px; }

    #game-board { flex: 1; position: relative; width: 100%; height: calc(100vh - 104px); }

    #bottom-bar {
        height: 52px; background: rgba(15, 15, 15, 0.95);
        border-top: 1px solid rgba(184, 155, 94, 0.2);
        display: flex; justify-content: center; align-items: center; gap: 15px; z-index: 100;
    }
    .btn {
        background: linear-gradient(180deg, #243447 0%, #151515 100%);
        color: #f3ebdd; border: 1px solid #b89b5e; padding: 6px 18px;
        border-radius: 2px; cursor: pointer; font-family: 'Shippori Mincho', serif;
        font-size: 14px; letter-spacing: 0.1em; transition: all 0.2s;
    }
    .btn:hover { background: #b83b32; color: #fff; border-color: #f3ebdd; }

    /* 자동 완성 버튼 UI (중앙 정렬) */
    #auto-btn {
        position: absolute; left: 50%; transform: translateX(-50%);
        top: 2%; display: none; z-index: 500;
        background: linear-gradient(180deg, #b89b5e 0%, #7a612d 100%);
        color: #0d0d0d; font-weight: 800; font-size: 15px;
        padding: 8px 24px; border: 2px solid #f3ebdd; border-radius: 4px;
        box-shadow: 0 0 15px rgba(184, 155, 94, 0.6); cursor: pointer;
        transition: all 0.2s;
    }
    #auto-btn:hover { transform: translateX(-50%) scale(1.05); background: #f3ebdd; }

    /* 카드 스타일 */
    .card {
        position: absolute; border-radius: 6px; background-color: #f3ebdd;
        background-image: radial-gradient(#e5d9c5 1px, transparent 0); background-size: 8px 8px;
        border: 1px solid #c8b9a6; box-shadow: 0 4px 10px rgba(0,0,0,0.6);
        cursor: grab; display: flex; flex-direction: column; justify-content: space-between;
        padding: 6px; font-family: 'Cinzel', serif; font-weight: 700;
        transition: left 0.2s ease-out, top 0.2s ease-out, transform 0.2s ease;
        z-index: 10;
    }
    .card.dragging {
        cursor: grabbing !important; transition: none !important;
        box-shadow: 0 12px 24px rgba(0,0,0,0.8), 0 0 15px rgba(184, 155, 94, 0.9) !important;
        z-index: 9999 !important;
    }
    .card.highlight {
        animation: hintPulse 1s infinite alternate;
        border: 2px solid #b83b32 !important;
    }
    @keyframes hintPulse {
        0% { transform: scale(1); box-shadow: 0 0 5px #b83b32; }
        100% { transform: scale(1.08); box-shadow: 0 0 20px #b83b32; }
    }
    .card.back {
        background: #1a2634; border: 1px solid #b89b5e;
        background-image: url("data:image/svg+xml,%3Csvg width='24' height='41.569' viewBox='0 0 24 41.569' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M12 0L0 6.928v13.856L12 27.713l12-6.929V6.928L12 0zm0 2.309l9.6 5.543v11.085L12 24.48 2.4 18.937V7.852L12 2.31zM12 27.713L0 34.641v6.928h24v-6.928l-12-6.928z' fill='%23b89b5e' fill-opacity='0.25'/%3E%3C/svg%3E");
        cursor: pointer;
    }
    .card.red { color: #b83b32; }
    .card.black { color: #151515; }
    .card .corner { line-height: 1; text-align: center; font-size: 0.9em; }
    .card .suit-center { font-size: 1.8em; text-align: center; margin: auto; }

    .card-slot {
        position: absolute; border-radius: 6px;
        border: 1px dashed rgba(184, 155, 94, 0.3); background: rgba(21, 21, 21, 0.4);
        display: flex; align-items: center; justify-content: center;
        color: rgba(184, 155, 94, 0.3); font-size: 1rem;
    }

    /* 승리 일본풍 애니메이션 (벚꽃 & 종이풍선) */
    #anim-container {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        pointer-events: none; overflow: hidden; z-index: 2000; display: none;
    }
    .sakura {
        position: absolute; background: #ffb7c5; border-radius: 100% 0 100% 0;
        opacity: 0.8; animation: fall 4s linear infinite;
    }
    @keyframes fall {
        0% { transform: translateY(-10vh) rotate(0deg); opacity: 0.9; }
        100% { transform: translateY(105vh) rotate(360deg); opacity: 0.2; }
    }
    .balloon {
        position: absolute; width: 50px; height: 50px; border-radius: 50%;
        background: conic-gradient(#b83b32 0 90deg, #f3ebdd 90deg 180deg, #243447 180deg 270deg, #b89b5e 270deg 360deg);
        box-shadow: inset 0 0 8px rgba(0,0,0,0.3); opacity: 0.9;
        animation: floatUp 6s ease-in infinite;
    }
    @keyframes floatUp {
        0% { transform: translateY(105vh) scale(0.6); }
        100% { transform: translateY(-20vh) scale(1.2); }
    }

    /* 승리 모달 창 */
    #win-modal {
        position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
        background: rgba(13, 13, 13, 0.95); border: 2px solid #b89b5e;
        padding: 30px 50px; text-align: center; color: #f3ebdd;
        box-shadow: 0 0 30px rgba(0,0,0,0.9), 0 0 15px rgba(184, 155, 94, 0.5);
        z-index: 3000; display: none; border-radius: 4px;
    }
    #win-modal h2 { font-weight: 800; color: #b89b5e; letter-spacing: 0.3em; margin-bottom: 15px; font-size: 24px; }
    #win-modal p { font-size: 16px; margin: 8px 0; color: #f3ebdd; }
    #win-modal .modal-btn { margin-top: 20px; }
</style>
</head>
<body>

<div id="top-bar">
    <div class="jp-title">クロンダイク — Klondike Solitaire</div>
    <div class="jp-stats">점수: <span id="score">0</span> &nbsp;|&nbsp; 시간: <span id="timer">00:00</span></div>
</div>

<div id="game-board">
    <button id="auto-btn" onclick="runAutoComplete()">⚡ 자동 완성 실행</button>
</div>

<div id="bottom-bar">
    <button class="btn" onclick="initGame()">새 게임</button>
    <button class="btn" onclick="undoMove()">되돌리기 (Undo)</button>
    <button class="btn" onclick="showHint()">힌트 (Hint)</button>
</div>

<div id="anim-container"></div>

<div id="win-modal">
    <h2>祝・見事クリア！</h2>
    <p>축하합니다! 게임을 완설하셨습니다.</p>
    <hr style="border:0; border-top:1px solid rgba(184,155,94,0.3); margin: 15px 0;">
    <p>최종 점수: <span id="final-score" style="color:#b89b5e; font-weight:bold;">0</span>점</p>
    <p>소요 시간: <span id="final-time" style="color:#b89b5e; font-weight:bold;">00:00</span></p>
    <button class="btn modal-btn" onclick="initGame()">다시 도전하기</button>
</div>

<script>
const SUITS = ['♠', '♥', '♦', '♣'];
const VALUES = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K'];

let stock = [], waste = [], foundations = [[], [], [], []], tableau = [[], [], [], [], [], [], []];
let history = [];
let dragGroup = [], isDragging = false, dragStartX = 0, dragStartY = 0;
let cardW = 0, cardH = 0, gap = 0, startY = 0;
let timeSeconds = 0, timerInterval = null, score = 0, isGameWon = false;

function resizeBoard() {
    const board = document.getElementById('game-board');
    const w = board.clientWidth, h = board.clientHeight;
    gap = w * 0.02; cardW = (w - (gap * 8)) / 7; cardH = cardW * 1.45;
    if (cardH * 4.2 > h) { cardH = h / 4.2; cardW = cardH / 1.45; gap = (w - (cardW * 7)) / 8; }
    startY = cardH + gap * 1.2; render();
}

function initGame() {
    document.getElementById('win-modal').style.display = 'none';
    document.getElementById('anim-container').style.display = 'none';
    document.getElementById('anim-container').innerHTML = '';
    document.getElementById('auto-btn').style.display = 'none';
    isGameWon = false;

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
        if (!isGameWon) {
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
    if (history.length === 0 || isGameWon) return;
    let state = JSON.parse(history.pop());
    stock = state.stock; waste = state.waste;
    foundations = state.foundations; tableau = state.tableau; score = state.score;
    render();
}

function render() {
    const board = document.getElementById('game-board');
    // auto-btn 유지를 위해 카드 요소만 삭제
    const cardsAndSlots = board.querySelectorAll('.card, .card-slot');
    cardsAndSlots.forEach(el => el.remove());

    document.getElementById('score').innerText = score;

    let leftStock = gap;
    createSlot(leftStock, gap, '空', () => handleStockClick());
    if (stock.length > 0) {
        let c = createCardEl(stock[stock.length - 1], leftStock, gap, false);
        c.onclick = handleStockClick;
    }

    let leftWaste = gap * 2 + cardW;
    createSlot(leftWaste, gap, '捨');
    if (waste.length > 0) {
        let card = waste[waste.length - 1];
        let c = createCardEl(card, leftWaste, gap, true);
        bindDragEvents(c, card, 'waste', 0, waste.length - 1);
    }

    for (let i = 0; i < 4; i++) {
        let leftF = gap * (4 + i) + cardW * (3 + i);
        createSlot(leftF, gap, '組');
        if (foundations[i].length > 0) {
            let card = foundations[i][foundations[i].length - 1];
            let c = createCardEl(card, leftF, gap, true);
            bindDragEvents(c, card, 'foundation', i, foundations[i].length - 1);
        }
    }

    for (let i = 0; i < 7; i++) {
        let leftT = gap * (1 + i) + cardW * i;
        createSlot(leftT, startY, '場');
        for (let j = 0; j < tableau[i].length; j++) {
            let card = tableau[i][j];
            let topT = startY + j * (cardH * 0.25);
            let c = createCardEl(card, leftT, topT, card.faceUp);
            if (card.faceUp) {
                bindDragEvents(c, card, 'tableau', i, j);
            }
        }
    }

    checkAutoCompleteCondition();
    checkWinCondition();
}

function createSlot(x, y, label, onClick) {
    const board = document.getElementById('game-board');
    const slot = document.createElement('div');
    slot.className = 'card-slot';
    slot.style.width = cardW + 'px'; slot.style.height = cardH + 'px';
    slot.style.left = x + 'px'; slot.style.top = y + 'px';
    slot.innerText = label;
    if (onClick) slot.onclick = onClick;
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
    if (isGameWon) return;
    saveState();
    if (stock.length === 0) {
        stock = waste.reverse().map(c => ({...c, faceUp: false}));
        waste = [];
    } else {
        let card = stock.pop(); card.faceUp = true; waste.push(card);
    }
    render();
}

function bindDragEvents(el, card, srcType, colIdx, cardIdx) {
    let clickTime = 0;
    el.onmousedown = (e) => {
        if (e.button !== 0 || isGameWon) return;
        
        let now = new Date().getTime();
        if (now - clickTime < 280) {
            autoMove(card, srcType, colIdx, cardIdx);
            clickTime = 0; return;
        }
        clickTime = now;

        e.preventDefault();
        isDragging = true; dragStartX = e.clientX; dragStartY = e.clientY;
        dragGroup = [];

        if (srcType === 'tableau') {
            for (let k = cardIdx; k < tableau[colIdx].length; k++) {
                let targetCard = tableau[colIdx][k];
                let cEl = document.getElementById(targetCard.uid);
                if (cEl) {
                    cEl.classList.add('dragging');
                    dragGroup.push({
                        el: cEl, card: targetCard,
                        origX: parseFloat(cEl.style.left), origY: parseFloat(cEl.style.top)
                    });
                }
            }
        } else {
            el.classList.add('dragging');
            dragGroup.push({ el: el, card: card, origX: parseFloat(el.style.left), origY: parseFloat(el.style.top) });
        }

        document.onmousemove = (e) => {
            if (!isDragging) return;
            let dx = e.clientX - dragStartX, dy = e.clientY - dragStartY;
            dragGroup.forEach(item => {
                item.el.style.left = (item.origX + dx) + 'px';
                item.el.style.top = (item.origY + dy) + 'px';
            });
        };

        document.onmouseup = (e) => {
            if (!isDragging) return;
            isDragging = false;
            document.onmousemove = null; document.onmouseup = null;

            dragGroup.forEach(item => item.el.classList.remove('dragging'));
            let dropped = checkDrop(card, srcType, colIdx, cardIdx, e.clientX, e.clientY);
            if (!dropped) {
                dragGroup.forEach(item => { item.el.style.left = item.origX + 'px'; item.el.style.top = item.origY + 'px'; });
            } else { render(); }
        };
    };
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
            let leftF = gap * (4 + f) + cardW * (3 + f);
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
        let leftT = gap * (1 + t) + cardW * t;
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

/* 힌트 시스템 */
function showHint() {
    document.querySelectorAll('.card').forEach(c => c.classList.remove('highlight'));
    // 1. Foundation 우선 이동
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
            if ((!topCard && tCard.value === 1) || (topCard && topCard.suit === tCard.suit && topCard.value === tCard.value - 1)) {
                document.getElementById(tCard.uid)?.classList.add('highlight'); return;
            }
        }
    }
    // 2. Stock 추천
    if (stock.length > 0) {
        let stockEl = document.getElementById(stock[stock.length - 1].uid);
        if (stockEl) stockEl.classList.add('highlight');
    }
}

/* 자동 완성 조건 체크 및 실행 */
function checkAutoCompleteCondition() {
    if (stock.length > 0 || waste.length > 1) return;
    let allFaceUp = tableau.every(col => col.every(c => c.faceUp));
    if (allFaceUp && !isGameWon) {
        document.getElementById('auto-btn').style.display = 'block';
    } else {
        document.getElementById('auto-btn').style.display = 'none';
    }
}

function runAutoComplete() {
    document.getElementById('auto-btn').style.display = 'none';
    let autoInterval = setInterval(() => {
        let moved = false;
        // waste -> foundation
        if (waste.length > 0) {
            let card = waste[waste.length - 1];
            for (let f = 0; f < 4; f++) {
                let topCard = foundations[f][foundations[f].length - 1];
                if ((!topCard && card.value === 1) || (topCard && topCard.suit === card.suit && topCard.value === card.value - 1)) {
                    foundations[f].push(waste.pop()); score += 10; moved = true; break;
                }
            }
        }
        // tableau -> foundation
        if (!moved) {
            for (let t = 0; t < 7; t++) {
                if (tableau[t].length === 0) continue;
                let card = tableau[t][tableau[t].length - 1];
                for (let f = 0; f < 4; f++) {
                    let topCard = foundations[f][foundations[f].length - 1];
                    if ((!topCard && card.value === 1) || (topCard && topCard.suit === card.suit && topCard.value === card.value - 1)) {
                        foundations[f].push(tableau[t].pop()); score += 10; moved = true; break;
                    }
                }
                if (moved) break;
            }
        }
        render();
        if (!moved || foundations.every(f => f.length === 13)) {
            clearInterval(autoInterval);
        }
    }, 120);
}

/* 클리어 감지 & 승리 애니메이션 */
function checkWinCondition() {
    let win = foundations.every(f => f.length === 13);
    if (win && !isGameWon) {
        isGameWon = true;
        triggerVictory();
    }
}

function triggerVictory() {
    clearInterval(timerInterval);
    const container = document.getElementById('anim-container');
    container.style.display = 'block';
    container.innerHTML = '';

    // 벚꽃 애니메이션 생성
    for (let i = 0; i < 40; i++) {
        let sakura = document.createElement('div');
        sakura.className = 'sakura';
        sakura.style.left = Math.random() * 100 + 'vw';
        sakura.style.width = (Math.random() * 8 + 8) + 'px';
        sakura.style.height = (Math.random() * 12 + 10) + 'px';
        sakura.style.animationDelay = (Math.random() * 3) + 's';
        sakura.style.animationDuration = (Math.random() * 3 + 3) + 's';
        container.appendChild(sakura);
    }

    // 종이풍선 애니메이션 생성
    for (let i = 0; i < 12; i++) {
        let balloon = document.createElement('div');
        balloon.className = 'balloon';
        balloon.style.left = (Math.random() * 85 + 5) + 'vw';
        balloon.style.animationDelay = (Math.random() * 4) + 's';
        balloon.style.animationDuration = (Math.random() * 4 + 4) + 's';
        container.appendChild(balloon);
    }

    // 팝업 결과창 출현
    setTimeout(() => {
        document.getElementById('final-score').innerText = score;
        document.getElementById('final-time').innerText = document.getElementById('timer').innerText;
        document.getElementById('win-modal').style.display = 'block';
    }, 1200);
}

window.onresize = resizeBoard;
window.onload = initGame;
</script>
</body>
</html>
"""

components.html(klondike_full_html, height=800, scrolling=False)
