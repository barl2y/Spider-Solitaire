import random
import copy
import time
import streamlit as st
import streamlit.components.v1 as components

# ==========================================
# 1. Streamlit 페이지 기본 설정
# ==========================================
st.set_page_config(
    page_title="蜘蛛百人一首 — Spider Solitaire",
    page_icon="🂠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 2. 카드 & 도메인 모델
# ==========================================
SUITS = {
    'Spade': {'symbol': '♠', 'color': 'black'},
    'Heart': {'symbol': '♥', 'color': 'red'},
    'Diamond': {'symbol': '♦', 'color': 'red'},
    'Club': {'symbol': '♣', 'color': 'black'},
}

VALUES = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
VALUE_NAMES = {1: 'A', 11: 'J', 12: 'Q', 13: 'K'}


class Card:
    def __init__(self, suit: str, value: int, face_up: bool = False):
        self.suit: str = suit
        self.value: int = value
        self.face_up: bool = face_up
        self.id: str = f"{suit}_{value}_{random.randint(10000, 99999)}"

    @property
    def display_value(self) -> str:
        return VALUE_NAMES.get(self.value, str(self.value))

    @property
    def symbol(self) -> str:
        return SUITS[self.suit]['symbol']

    @property
    def color(self) -> str:
        return SUITS[self.suit]['color']

    def to_dict(self) -> dict:
        return {
            'suit': self.suit,
            'value': self.value,
            'face_up': self.face_up,
            'id': self.id
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Card':
        card = cls(data['suit'], data['value'], data['face_up'])
        card.id = data['id']
        return card


class Deck:
    def __init__(self, difficulty: int = 1):
        self.cards = []
        self._build_deck(difficulty)
        self.shuffle()

    def _build_deck(self, difficulty: int):
        self.cards = []
        if difficulty == 1:
            suits = ['Spade'] * 8
        elif difficulty == 2:
            suits = ['Spade', 'Heart'] * 4
        else:
            suits = ['Spade', 'Heart', 'Diamond', 'Club'] * 2

        for suit in suits:
            for val in VALUES:
                self.cards.append(Card(suit, val, face_up=False))

    def shuffle(self):
        random.shuffle(self.cards)


# ==========================================
# 3. 핵심 게임 로직 Engine
# ==========================================
class SpiderGame:
    def __init__(self, difficulty: int = 1):
        self.difficulty: int = difficulty
        self.tableau = [[] for _ in range(10)]
        self.stock = []
        self.completed_sets: int = 0
        self.moves: int = 0
        self.undo_count: int = 0
        self.history = []
        self.selected_pos = None  # (col_idx, card_idx)
        self.last_completed: bool = False
        self.is_won: bool = False
        self.init_game()

    def init_game(self):
        deck = Deck(self.difficulty)
        all_cards = deck.cards

        self.tableau = [[] for _ in range(10)]
        for i in range(54):
            col = i % 10
            card = all_cards.pop()
            if (col < 4 and len(self.tableau[col]) == 5) or (col >= 4 and len(self.tableau[col]) == 4):
                card.face_up = True
            self.tableau[col].append(card)

        self.stock = all_cards
        self.completed_sets = 0
        self.moves = 0
        self.undo_count = 0
        self.history = []
        self.selected_pos = None
        self.last_completed = False
        self.is_won = False

    def save_state(self):
        state = {
            'tableau': [[c.to_dict() for c in col] for col in self.tableau],
            'stock': [c.to_dict() for c in self.stock],
            'completed_sets': self.completed_sets,
            'moves': self.moves,
            'selected_pos': self.selected_pos,
            'is_won': self.is_won
        }
        self.history.append(state)

    def undo(self) -> bool:
        if not self.history:
            return False
        state = self.history.pop()
        self.tableau = [[Card.from_dict(c) for c in col] for col in state['tableau']]
        self.stock = [Card.from_dict(c) for c in state['stock']]
        self.completed_sets = state['completed_sets']
        self.moves = state['moves']
        self.selected_pos = state['selected_pos']
        self.is_won = state['is_won']
        self.undo_count += 1
        self.last_completed = False
        return True

    def can_select_stack(self, col_idx: int, card_idx: int) -> bool:
        col = self.tableau[col_idx]
        if card_idx < 0 or card_idx >= len(col):
            return False
        if not col[card_idx].face_up:
            return False

        for i in range(card_idx, len(col) - 1):
            curr = col[i]
            nxt = col[i + 1]
            if curr.suit != nxt.suit or curr.value != nxt.value + 1:
                return False
        return True

    def can_move_stack(self, src_col: int, src_card_idx: int, dest_col: int) -> bool:
        if src_col == dest_col:
            return False
        if not self.can_select_stack(src_col, src_card_idx):
            return False

        src_card = self.tableau[src_col][src_card_idx]
        dest_stack = self.tableau[dest_col]

        if not dest_stack:
            return src_card.value == 13

        dest_top = dest_stack[-1]
        return dest_top.value == src_card.value + 1

    def move_cards(self, src_col: int, src_card_idx: int, dest_col: int) -> bool:
        if not self.can_move_stack(src_col, src_card_idx, dest_col):
            return False

        self.save_state()

        moving_cards = self.tableau[src_col][src_card_idx:]
        self.tableau[src_col] = self.tableau[src_col][:src_card_idx]
        self.tableau[dest_col].extend(moving_cards)

        if self.tableau[src_col] and not self.tableau[src_col][-1].face_up:
            self.tableau[src_col][-1].face_up = True

        self.moves += 1
        self.selected_pos = None

        self.last_completed = self.check_completed_sets(dest_col)
        self.check_win()
        return True

    def deal_stock(self) -> bool:
        if any(len(col) == 0 for col in self.tableau):
            return False
        if len(self.stock) < 10:
            return False

        self.save_state()

        completed_any = False
        for col_idx in range(10):
            card = self.stock.pop()
            card.face_up = True
            self.tableau[col_idx].append(card)
            if self.check_completed_sets(col_idx):
                completed_any = True

        self.moves += 1
        self.last_completed = completed_any
        self.check_win()
        return True

    def check_completed_sets(self, col_idx: int) -> bool:
        col = self.tableau[col_idx]
        if len(col) < 13:
            return False

        tail = col[-13:]
        if tail[0].value != 13:
            return False

        suit = tail[0].suit
        for i in range(13):
            if not tail[i].face_up or tail[i].suit != suit or tail[i].value != (13 - i):
                return False

        self.tableau[col_idx] = col[:-13]
        if self.tableau[col_idx] and not self.tableau[col_idx][-1].face_up:
            self.tableau[col_idx][-1].face_up = True

        self.completed_sets += 1
        return True

    def check_win(self):
        if self.completed_sets == 8:
            self.is_won = True


# ==========================================
# 4. 세션 상태 관리
# ==========================================
def init_session_state():
    if 'difficulty' not in st.session_state:
        st.session_state.difficulty = 1

    if 'game' not in st.session_state:
        st.session_state.game = SpiderGame(st.session_state.difficulty)

    if 'start_time' not in st.session_state:
        st.session_state.start_time = time.time()

    if 'elapsed_time' not in st.session_state:
        st.session_state.elapsed_time = 0


def reset_game(difficulty: int = None):
    if difficulty is None:
        difficulty = st.session_state.difficulty
    else:
        st.session_state.difficulty = difficulty

    st.session_state.game = SpiderGame(difficulty)
    st.session_state.start_time = time.time()
    st.session_state.elapsed_time = 0


def get_elapsed_seconds() -> int:
    if st.session_state.game.is_won:
        return st.session_state.elapsed_time
    return int(time.time() - st.session_state.start_time)


# ==========================================
# 5. 전통 일본풍 UI Custom CSS
# ==========================================
def get_custom_css() -> str:
    return """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@500;700;800&family=Cinzel:wght@500;700&display=swap');

    html, body, [data-testid="stAppViewContainer"] {
        background-color: #0d0d0d !important;
        background-image: 
            radial-gradient(circle at 50% 50%, rgba(36, 52, 71, 0.25) 0%, rgba(13, 13, 13, 0.95) 100%),
            url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%23b89b5e' fill-opacity='0.03' fill-rule='evenodd'%3E%3Cpath d='M30 30L15 0H0v15l30 30 30-30V0H45L30 30zM0 45h15l15-15 15 15h15V30L30 60 0 30v15z'/%3E%3C/g%3E%3C/svg%3E") !important;
        color: #f3ebdd !important;
        font-family: 'Shippori Mincho', serif !important;
    }

    [data-testid="stHeader"], [data-testid="stToolbar"] {
        display: none !important;
    }

    .main .block-container {
        padding: 1.5rem 1rem !important;
        max-width: 1400px !important;
    }

    .jp-title {
        text-align: center;
        font-family: 'Shippori Mincho', serif;
        font-weight: 800;
        font-size: 2.2rem;
        letter-spacing: 0.3em;
        color: #f3ebdd;
        text-shadow: 0 0 15px rgba(184, 155, 94, 0.3);
        margin-bottom: 0.2rem;
    }

    .jp-subtitle {
        text-align: center;
        font-family: 'Cinzel', serif;
        font-size: 0.8rem;
        letter-spacing: 0.4em;
        color: #b89b5e;
        text-transform: uppercase;
        margin-bottom: 1.5rem;
    }

    .status-bar {
        display: flex;
        justify-content: space-around;
        align-items: center;
        background: rgba(21, 21, 21, 0.85);
        border: 1px solid rgba(184, 155, 94, 0.3);
        box-shadow: inset 0 0 10px rgba(0,0,0,0.8);
        padding: 0.8rem;
        border-radius: 4px;
        margin-bottom: 1.5rem;
    }

    .status-item { text-align: center; }
    .status-label { font-size: 0.7rem; color: #b89b5e; letter-spacing: 0.15em; margin-bottom: 0.2rem; }
    .status-value { font-family: 'Cinzel', serif; font-size: 1.1rem; font-weight: 700; color: #f3ebdd; }

    div.stButton > button {
        background: linear-gradient(180deg, #243447 0%, #151515 100%) !important;
        color: #f3ebdd !important;
        border: 1px solid #b89b5e !important;
        border-radius: 2px !important;
        font-family: 'Shippori Mincho', serif !important;
        font-size: 0.85rem !important;
        letter-spacing: 0.1em !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.5) !important;
        padding: 0.4rem 0.8rem !important;
        width: 100% !important;
    }

    div.stButton > button:hover {
        background: #b83b32 !important;
        border-color: #f3ebdd !important;
        color: #ffffff !important;
        box-shadow: 0 0 12px rgba(184, 59, 50, 0.6) !important;
        transform: translateY(-1px) !important;
    }

    .card-base {
        width: 100%;
        aspect-ratio: 1 / 1.45;
        border-radius: 5px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.6);
        position: relative;
        user-select: none;
        transition: transform 0.2s cubic-bezier(0.25, 1, 0.5, 1), box-shadow 0.2s ease;
        margin-bottom: -110%;
    }

    .card-face {
        background-color: #f3ebdd;
        background-image: radial-gradient(#e5d9c5 1px, transparent 0);
        background-size: 8px 8px;
        border: 1px solid #c8b9a6;
        color: #151515;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        padding: 0.3rem 0.4rem;
        font-family: 'Cinzel', serif;
        font-weight: 700;
    }

    .card-face.red { color: #b83b32; }

    .card-back {
        background: #1a2634;
        border: 1px solid #b89b5e;
        background-image: url("data:image/svg+xml,%3Csvg width='24' height='41.569' viewBox='0 0 24 41.569' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M12 0L0 6.928v13.856L12 27.713l12-6.929V6.928L12 0zm0 2.309l9.6 5.543v11.085L12 24.48 2.4 18.937V7.852L12 2.31zM12 27.713L0 34.641v6.928h24v-6.928l-12-6.928z' fill='%23b89b5e' fill-opacity='0.25'/%3E%3C/svg%3E");
    }

    .card-selected {
        border: 2px solid #b89b5e !important;
        box-shadow: 0 0 15px rgba(184, 155, 94, 0.9) !important;
        transform: translateY(-8px) scale(1.02);
        z-index: 99 !important;
    }

    .card-empty {
        width: 100%;
        aspect-ratio: 1 / 1.45;
        border: 1px dashed rgba(184, 155, 94, 0.3);
        border-radius: 5px;
        background: rgba(21, 21, 21, 0.4);
        display: flex;
        align-items: center;
        justify-content: center;
        color: rgba(184, 155, 94, 0.4);
        font-size: 0.8rem;
    }
    </style>
    """


# ==========================================
# 6. 연출 애니메이션 (HTML/JS)
# ==========================================
def trigger_completion_effect():
    """벚꽃 세트 완성 효과"""
    html_code = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@800&display=swap');
    
    .overlay {
        position: fixed;
        top: 0; left: 0; width: 100vw; height: 100vh;
        background: rgba(13, 13, 13, 0.75);
        display: flex; justify-content: center; align-items: center;
        z-index: 99999;
        overflow: hidden;
        animation: fadeIn 0.4s ease-out forwards;
    }

    .kanji-title {
        font-family: 'Shippori Mincho', serif;
        font-size: 5rem;
        font-weight: 800;
        color: #f3ebdd;
        text-shadow: 0 0 20px rgba(184, 155, 94, 0.8), 0 0 40px rgba(184, 59, 50, 0.6);
        letter-spacing: 0.3em;
        animation: pulseText 1.8s ease-in-out forwards;
    }

    .petal {
        position: absolute;
        background: radial-gradient(circle, #fce4ec 0%, #f48fb1 70%, #d81b60 100%);
        border-radius: 150% 0 150% 0;
        opacity: 0.85;
        pointer-events: none;
        animation: fall linear infinite;
    }

    @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
    @keyframes pulseText {
        0% { transform: scale(0.6); opacity: 0; }
        50% { transform: scale(1.1); opacity: 1; }
        100% { transform: scale(1.0); opacity: 0; }
    }
    @keyframes fall {
        0% { transform: translateY(-10vh) rotate(0deg); }
        100% { transform: translateY(110vh) rotate(360deg); }
    }
    </style>
    
    <div class="overlay" id="kanji-overlay">
        <div class="kanji-title">完成</div>
    </div>

    <script>
    const overlay = document.getElementById('kanji-overlay');
    for (let i = 0; i < 35; i++) {
        let petal = document.createElement('div');
        petal.className = 'petal';
        let size = Math.random() * 12 + 8;
        petal.style.width = size + 'px';
        petal.style.height = (size * 1.4) + 'px';
        petal.style.left = Math.random() * 100 + 'vw';
        petal.style.animationDuration = (Math.random() * 3 + 2.5) + 's';
        petal.style.animationDelay = (Math.random() * 1.5) + 's';
        overlay.appendChild(petal);
    }
    setTimeout(() => { overlay.style.display = 'none'; }, 2200);
    </script>
    """
    components.html(html_code, height=0, width=0)


def trigger_victory_effect(time_str: str, moves: int, undo_cnt: int):
    """최종 대승리 연출"""
    html_code = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@800&family=Cinzel:wght@700&display=swap');

    .vic-overlay {{
        position: fixed;
        top: 0; left: 0; width: 100vw; height: 100vh;
        background: radial-gradient(circle, rgba(36,52,71,0.95) 0%, rgba(13,13,13,0.98) 100%);
        display: flex; flex-direction: column; justify-content: center; align-items: center;
        z-index: 999999;
        animation: vicFade 0.8s ease-out forwards;
        font-family: 'Shippori Mincho', serif;
        color: #f3ebdd;
    }}

    .vic-kanji {{
        font-size: 4.5rem;
        letter-spacing: 0.4em;
        color: #b89b5e;
        text-shadow: 0 0 25px rgba(184, 155, 94, 0.6);
        margin-bottom: 0.5rem;
    }}

    .vic-sub {{
        font-family: 'Cinzel', serif;
        font-size: 1.2rem;
        letter-spacing: 0.5em;
        color: #b83b32;
        margin-bottom: 2rem;
    }}

    .vic-stats {{
        background: rgba(21, 21, 21, 0.8);
        border: 1px solid #b89b5e;
        padding: 1.5rem 3rem;
        border-radius: 4px;
        text-align: center;
        box-shadow: 0 0 30px rgba(0,0,0,0.8);
    }}

    .vic-stat-row {{
        font-size: 1.1rem;
        margin: 0.6rem 0;
        letter-spacing: 0.15em;
    }}

    .lantern {{
        position: absolute;
        width: 18px; height: 28px;
        background: rgba(184, 59, 50, 0.6);
        border: 1px solid #b89b5e;
        border-radius: 4px;
        box-shadow: 0 0 12px rgba(184, 155, 94, 0.5);
        animation: floatUp linear infinite;
        bottom: -40px;
    }}

    @keyframes vicFade {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
    @keyframes floatUp {{
        0% {{ transform: translateY(0) rotate(0deg); opacity: 0; }}
        20% {{ opacity: 0.8; }}
        100% {{ transform: translateY(-115vh) rotate(20deg); opacity: 0; }}
    }}
    </style>

    <div class="vic-overlay" id="vic-box">
        <div class="vic-kanji">大勝利</div>
        <div class="vic-sub">SPIDER SOLITAIRE</div>
        <div class="vic-stats">
            <div class="vic-stat-row">소요 시간 : {time_str}</div>
            <div class="vic-stat-row">이동 횟수 : {moves}</div>
            <div class="vic-stat-row">Undo 횟수 : {undo_cnt}</div>
        </div>
    </div>

    <script>
    const box = document.getElementById('vic-box');
    for (let i = 0; i < 25; i++) {{
        let lantern = document.createElement('div');
        lantern.className = 'lantern';
        lantern.style.left = Math.random() * 95 + 'vw';
        lantern.style.animationDuration = (Math.random() * 4 + 4) + 's';
        lantern.style.animationDelay = (Math.random() * 2) + 's';
        box.appendChild(lantern);
    }}
    </script>
    """
    components.html(html_code, height=500, width=800)


# ==========================================
# 7. UI 컴포넌트
# ==========================================
def render_card_html(card: Card, is_selected: bool = False) -> str:
    if not card.face_up:
        return '<div class="card-base card-back"></div>'

    color_cls = "red" if card.color == "red" else "black"
    select_cls = "card-selected" if is_selected else ""

    return f"""
    <div class="card-base card-face {color_cls} {select_cls}">
        <div style="font-size:0.9rem; line-height:1;">{card.display_value}<br/><span style="font-size:0.75rem;">{card.symbol}</span></div>
        <div style="text-align:center; font-size:1.3rem;">{card.symbol}</div>
        <div style="font-size:0.9rem; line-height:1; text-align:right;">{card.display_value}</div>
    </div>
    """


# ==========================================
# 8. 메인 실행 애플리케이션
# ==========================================
init_session_state()
st.markdown(get_custom_css(), unsafe_allow_html=True)

st.markdown("""
    <div class="jp-title">蜘蛛百人一首</div>
    <div class="jp-subtitle">Spider Solitaire — Traditional Aesthetic</div>
""", unsafe_allow_html=True)

game = st.session_state.game

ctrl_col1, ctrl_col2, ctrl_col3, ctrl_col4 = st.columns([2, 1, 1, 1])

with ctrl_col1:
    diff_labels = {1: "1 Suit (초급)", 2: "2 Suits (중급)", 4: "4 Suits (상급)"}
    selected_diff = st.selectbox(
        "난이도",
        options=[1, 2, 4],
        format_func=lambda x: diff_labels[x],
        index=[1, 2, 4].index(st.session_state.difficulty),
        label_visibility="collapsed"
    )
    if selected_diff != st.session_state.difficulty:
        reset_game(selected_diff)
        st.rerun()

with ctrl_col2:
    if st.button("Undo (되돌리기)"):
        if game.undo():
            st.rerun()

with ctrl_col3:
    if st.button("게임 리셋"):
        reset_game()
        st.rerun()

with ctrl_col4:
    if st.button("새 게임"):
        reset_game()
        st.rerun()

elapsed_sec = get_elapsed_seconds()
time_str = f"{elapsed_sec // 60:02d}:{elapsed_sec % 60:02d}"

st.markdown(f"""
    <div class="status-bar">
        <div class="status-item"><div class="status-label">시간</div><div class="status-value">{time_str}</div></div>
        <div class="status-item"><div class="status-label">이동</div><div class="status-value">{game.moves}</div></div>
        <div class="status-item"><div class="status-label">UNDO</div><div class="status-value">{game.undo_count}</div></div>
        <div class="status-item"><div class="status-label">완성 세트</div><div class="status-value">{game.completed_sets} / 8</div></div>
        <div class="status-item"><div class="status-label">남은 덱</div><div class="status-value">{len(game.stock)}</div></div>
    </div>
""", unsafe_allow_html=True)

if game.last_completed:
    trigger_completion_effect()
    game.last_completed = False

if game.is_won:
    trigger_victory_effect(time_str, game.moves, game.undo_count)

tableau_cols = st.columns(10)

for col_idx in range(10):
    with tableau_cols[col_idx]:
        cards = game.tableau[col_idx]

        col_btn_label = "▼" if cards else "빈 열"
        if st.button(col_btn_label, key=f"col_head_{col_idx}"):
            if game.selected_pos is not None:
                src_col, src_card_idx = game.selected_pos
                if game.move_cards(src_col, src_card_idx, col_idx):
                    st.rerun()
                else:
                    game.selected_pos = None
                    st.rerun()

        if not cards:
            st.markdown('<div class="card-empty">空</div>', unsafe_allow_html=True)
        else:
            for card_idx, card in enumerate(cards):
                is_selected = (game.selected_pos == (col_idx, card_idx))
                st.markdown(render_card_html(card, is_selected=is_selected), unsafe_allow_html=True)

                if card.face_up:
                    if st.button("선택", key=f"btn_{col_idx}_{card_idx}"):
                        if game.selected_pos == (col_idx, card_idx):
                            game.selected_pos = None
                        elif game.selected_pos is not None:
                            src_col, src_card_idx = game.selected_pos
                            if not game.move_cards(src_col, src_card_idx, col_idx):
                                if game.can_select_stack(col_idx, card_idx):
                                    game.selected_pos = (col_idx, card_idx)
                                else:
                                    game.selected_pos = None
                        else:
                            if game.can_select_stack(col_idx, card_idx):
                                game.selected_pos = (col_idx, card_idx)
                        st.rerun()

st.markdown("<br/>", unsafe_allow_html=True)
deal_col1, deal_col2, deal_col3 = st.columns([4, 2, 4])

with deal_col2:
    if len(game.stock) > 0:
        if st.button(f"카드 배분 (남은 덱: {len(game.stock)}장)"):
            if any(len(c) == 0 for c in game.tableau):
                st.warning("빈 열이 없어야 카드를 배분할 수 있습니다.")
            else:
                if game.deal_stock():
                    st.rerun()
    else:
        st.markdown("<div style='text-align:center; color:#b89b5e;'>덱 카드가 모두 소진되었습니다</div>", unsafe_allow_html=True)
