import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Klondike Solitaire",
    page_icon="♠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Streamlit 패딩 제거 및 전체 화면 최적화
st.markdown("""
    <style>
    [data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; }
    .main .block-container { padding: 0rem !important; max-width: 100% !important; }
    iframe { border: none !important; width: 100vw !important; height: 100vh !important; }
    </style>
""", unsafe_allow_html=True)

# 클론다이크 카드 게임 (HTML5 + Drag & Drop JS)
klondike_html = """
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<style>
    * { box-sizing: border-box; margin: 0; padding: 0; user-select: none; }
    body {
        background-color: #0f5e36;
        background-image: radial-gradient(#157a46 15%, transparent 16%), radial-gradient(#157a46 15%, transparent 16%);
        background-size: 60px 60px;
        background-position: 0 0, 30px 30px;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        width: 100vw; height: 100vh; overflow: hidden;
        display: flex; flex-direction: column;
    }
    #top-bar {
        height: 48px; background: rgba(0, 0, 0, 0.4);
        display: flex; justify-content: space-between; align-items: center;
        padding: 0 20px; color: #ffffff; font-weight: bold; font-size: 16px;
    }
    #game-board {
        flex: 1; position: relative; width: 100%; height: calc(100vh - 96px);
    }
    #bottom-bar {
        height: 48px; background: rgba(0, 0, 0, 0.5);
        display: flex; justify-content: center; align-items: center; gap: 20px;
    }
    .btn {
        background: transparent; border: 1px solid rgba(255,255,255,0.3);
        color: white; padding: 6px 16px; border-radius: 4px; cursor: pointer;
        font-size: 14px; font-weight: bold; transition: all 0.2s;
    }
    .btn:hover { background: rgba(255,255,255,0.2); border-color: white; }

    /* Card Styling */
    .card {
        position: absolute; border-radius: 8px; background: white;
        box-shadow: 2px 2px 6px rgba(0,0,0,0.4); cursor: pointer;
        display: flex; flex-direction: column; justify-content: space-between;
        padding: 6px; font-weight: bold; font-family: 'Arial', sans-serif;
        transition: transform 0.1s; z-index: 10;
    }
    .card.back {
        background: linear-gradient(135deg, #1e5799 0%,#207cca 51%,#7db9e8 100%);
        border: 2px solid #ffffff;
    }
    .card.back::after {
        content: ''; display: block; width: 100%; height: 100%;
        border: 1px dashed rgba(255,255,255,0.5); border-radius: 4px;
    }
    .card.red { color: #d32f2f; }
    .card.black { color: #212121; }
    .card .corner { line-height: 1; text-align: center; }
    .card .suit-center { font-size: 28px; text-align: center; margin-top: auto; margin-bottom: auto; }
    .card-slot {
        position: absolute; border-radius: 8px;
        border: 2px solid rgba(255,255,255,0.2); background: rgba(0,0,0,0.1);
    }
</style>
</head>
<body>

<div id="top-bar">
    <div>Klondike 솔리테어</div>
    <div>점수: <span id="score">0</span> &nbsp;&nbsp;|&nbsp;&nbsp; 시간: <span id="timer">00:00</span></div>
</div>

<div id="game-board"></div>

<div id="bottom-bar">
    <button class="btn" onclick="initGame()">새 게임</button>
    <button class="btn" onclick="undoMove()">실행 취소</button>
</div>

<script>
const SUITS = ['♠', '♥', '♦', '♣'];
const VALUES = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K'];

let stock = [], waste = [], foundations = [[], [], [], []], tableau = [[], [], [], [], [], [], []];
let history = [];
let dragGroup = [], dragOffset = {x: 0, y: 0}, originalPos = [];
let cardW = 0, cardH = 0, gap = 0, startY = 0;
let timeSeconds = 0, timerInterval = null, score = 0;

function resizeBoard() {
    const board = document.getElementById('game-board');
    const w = board.clientWidth;
    const h = board.clientHeight;
    
    gap = w * 0.02;
    cardW = (w - (gap * 8)) / 7;
    cardH = cardW * 1.4;
    
    if (cardH * 4.5 > h) {
        cardH = h / 4.5;
        cardW = cardH / 1.4;
        gap = (w - (cardW * 7)) / 8;
    }
    startY = cardH + gap * 1.5;
    render();
}

function initGame() {
    let deck = [];
    for (let s = 0; s < 4; s++) {
        for (let v = 1; v <= 13; v++) {
            deck.push({
                suit: SUITS[s],
                color: (s === 1 || s === 2) ? 'red' : 'black',
                value: v,
                name: VALUES[v-1],
                faceUp: false,
                id: s + '_' + v
            });
        }
    }
    deck.sort(() => Math.random() - 0.5);

    tableau = [[], [], [], [], [], [], []];
    foundations = [[], [], [], []];
    waste = [];
    history = [];
    score = 0;

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
        timeSeconds++;
        let m = String(Math.floor(timeSeconds / 60)).padStart(2, '0');
        let s = String(timeSeconds % 60).padStart(2, '0');
        document.getElementById('timer').innerText = `${m}:${s}`;
    }, 1000);

    resizeBoard();
}

function saveState() {
    history.push(JSON.stringify({ stock, waste, foundations, tableau, score }));
}

function undoMove() {
    if (history.length === 0) return;
    let state = JSON.parse(history.pop());
    stock = state.stock; waste = state.waste;
    foundations = state.foundations; tableau = state.tableau;
    score = state.score;
    render();
}

function render() {
    const board = document.getElementById('game-board');
    board.innerHTML = '';
    document.getElementById('score').innerText = score;

    // Draw Slots
    let leftStock = gap;
    createSlot(leftStock, gap, 'stock', () => handleStockClick());
    if (stock.length > 0) {
        let c = createCardEl(stock[stock.length - 1], leftStock, gap, false);
        c.onclick = handleStockClick;
    }

    let leftWaste = gap * 2 + cardW;
    createSlot(leftWaste, gap, 'waste');
    if (waste.length > 0) {
        let card = waste[waste.length - 1];
        let c = createCardEl(card, leftWaste, gap, true);
        makeDraggable(c, card, 'waste', 0, waste.length - 1);
    }

    for (let i = 0; i < 4; i++) {
        let leftF = gap * (4 + i) + cardW * (3 + i);
        createSlot(leftF, gap, 'foundation');
        if (foundations[i].length > 0) {
            let card = foundations[i][foundations[i].length - 1];
            let c = createCardEl(card, leftF, gap, true);
            makeDraggable(c, card, 'foundation', i, foundations[i].length - 1);
        }
    }

    for (let i = 0; i < 7; i++) {
        let leftT = gap * (1 + i) + cardW * i;
        createSlot(leftT, startY, 'tableau');
        for (let j = 0; j < tableau[i].length; j++) {
            let card = tableau[i][j];
            let topT = startY + j * (cardH * 0.25);
            let c = createCardEl(card, leftT, topT, card.faceUp);
            if (card.faceUp) {
                makeDraggable(c, card, 'tableau', i, j);
                c.ondblclick = () => autoMove(card, i, j);
            }
        }
    }
}

function createSlot(x, y, type, onClick) {
    const board = document.getElementById('game-board');
    const slot = document.createElement('div');
    slot.className = 'card-slot';
    slot.style.width = cardW + 'px'; slot.style.height = cardH + 'px';
    slot.style.left = x + 'px'; slot.style.top = y + 'px';
    if (onClick) slot.onclick = onClick;
    board.appendChild(slot);
}

function createCardEl(card, x, y, faceUp) {
    const board = document.getElementById('game-board');
    const el = document.createElement('div');
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
    saveState();
    if (stock.length === 0) {
        stock = waste.reverse().map(c => ({...c, faceUp: false}));
        waste = [];
    } else {
        let card = stock.pop();
        card.faceUp = true;
        waste.push(card);
    }
    render();
}

function makeDraggable(el, card, srcType, colIdx, cardIdx) {
    el.onmousedown = (e) => {
        e.preventDefault();
        saveState();

        dragGroup = [];
        if (srcType === 'tableau') {
            for (let k = cardIdx; k < tableau[colIdx].length; k++) {
                let cEl = getCardElement(tableau[colIdx][k].id);
                dragGroup.push({ el: cEl, card: tableau[colIdx][k], origX: parseFloat(cEl.style.left), origY: parseFloat(cEl.style.top) });
            }
        } else {
            dragGroup.push({ el, card, origX: parseFloat(el.style.left), origY: parseFloat(el.style.top) });
        }

        dragOffset.x = e.clientX;
        dragOffset.y = e.clientY;

        document.onmousemove = (e) => {
            let dx = e.clientX - dragOffset.x;
            let dy = e.clientY - dragOffset.y;
            dragGroup.forEach(item => {
                item.el.style.left = (item.origX + dx) + 'px';
                item.el.style.top = (item.origY + dy) + 'px';
                item.el.style.zIndex = 1000;
            });
        };

        document.onmouseup = (e) => {
            document.onmousemove = null;
            document.onmouseup = null;

            let dropped = checkDrop(card, srcType, colIdx, cardIdx, e.clientX, e.clientY);
            if (!dropped) {
                history.pop();
                dragGroup.forEach(item => {
                    item.el.style.left = item.origX + 'px';
                    item.el.style.top = item.origY + 'px';
                    item.el.style.zIndex = 10;
                });
            } else {
                render();
            }
        };
    };
}

function autoMove(card, colIdx, cardIdx) {
    if (cardIdx !== tableau[colIdx].length - 1) return;
    saveState();
    for (let f = 0; f < 4; f++) {
        let target = foundations[f];
        let topCard = target[target.length - 1];
        if ((!topCard && card.value === 1) || (topCard && topCard.suit === card.suit && topCard.value === card.value - 1)) {
            target.push(tableau[colIdx].pop());
            if (tableau[colIdx].length > 0) tableau[colIdx][tableau[colIdx].length - 1].faceUp = true;
            score += 10;
            render();
            return;
        }
    }
    history.pop();
}

function checkDrop(card, srcType, srcCol, srcIdx, mouseX, mouseY) {
    // Check Foundations (Single Card Only)
    if (dragGroup.length === 1) {
        for (let f = 0; f < 4; f++) {
            let leftF = gap * (4 + f) + cardW * (3 + f);
            if (mouseX >= leftF && mouseX <= leftF + cardW && mouseY >= gap && mouseY <= gap + cardH) {
                let target = foundations[f];
                let topCard = target[target.length - 1];
                if ((!topCard && card.value === 1) || (topCard && topCard.suit === card.suit && topCard.value === card.value - 1)) {
                    target.push(removeSourceCard(srcType, srcCol, srcIdx)[0]);
                    score += 10;
                    return true;
                }
            }
        }
    }

    // Check Tableau
    for (let t = 0; t < 7; t++) {
        let leftT = gap * (1 + t) + cardW * t;
        let targetCol = tableau[t];
        let topCard = targetCol[targetCol.length - 1];
        let topY = targetCol.length === 0 ? startY : startY + (targetCol.length - 1) * (cardH * 0.25);

        if (mouseX >= leftT && mouseX <= leftT + cardW && mouseY >= topY && mouseY <= topY + cardH * 1.5) {
            if ((!topCard && card.value === 13) || (topCard && topCard.color !== card.color && topCard.value === card.value + 1)) {
                let movedCards = removeSourceCard(srcType, srcCol, srcIdx);
                tableau[t] = tableau[t].concat(movedCards);
                score += 5;
                return true;
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

function getCardElement(id) {
    // Find Element by Card Logic
    let cards = document.getElementsByClassName('card');
    for (let el of cards) {
        if (el.innerHTML.includes(id.split('_')[0]) && el.innerHTML.includes(VALUES[parseInt(id.split('_')[1])-1])) {
            return el;
        }
    }
    return null;
}

window.onresize = resizeBoard;
window.onload = initGame;
</script>
</body>
</html>
"""

components.html(klondike_html, height=800, scrolling=False)
