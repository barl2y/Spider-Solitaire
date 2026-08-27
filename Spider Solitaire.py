import streamlit as st

# Set page config at absolute top
st.set_page_config(
    page_title="Spider Solitaire — 蜘蛛百人一首",
    page_icon="🂠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

from game.state import init_session_state, reset_game, get_elapsed_seconds
from ui.styles import get_custom_css
from ui.components import render_header, render_status_bar, render_card_html, render_empty_slot_html
from effects.animations import trigger_completion_effect, trigger_victory_effect

# Initialize Session State
init_session_state()

# Inject Custom Aesthetic CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)

# Render Header
render_header()

game = st.session_state.game

# Control & Settings Panel
ctrl_col1, ctrl_col2, ctrl_col3, ctrl_col4 = st.columns([2, 1, 1, 1])

with ctrl_col1:
    diff_labels = {1: "1 Suit (初級)", 2: "2 Suits (中級)", 4: "4 Suits (上級)"}
    selected_diff = st.selectbox(
        "難易度",
        options=[1, 2, 4],
        format_func=lambda x: diff_labels[x],
        index=[1, 2, 4].index(st.session_state.difficulty),
        label_visibility="collapsed"
    )
    if selected_diff != st.session_state.difficulty:
        reset_game(selected_diff)
        st.rerun()

with ctrl_col2:
    if st.button("待避 (UNDO)"):
        if game.undo():
            st.rerun()

with ctrl_col3:
    if st.button("盤面初期化"):
        reset_game()
        st.rerun()

with ctrl_col4:
    if st.button("新勝負"):
        reset_game()
        st.rerun()

# Time formatting
elapsed_sec = get_elapsed_seconds()
time_str = f"{elapsed_sec // 60:02d}:{elapsed_sec % 60:02d}"

# Render Status Bar
render_status_bar(
    time_str=time_str,
    moves=game.moves,
    undo_cnt=game.undo_count,
    sets=game.completed_sets,
    stock_left=len(game.stock)
)

# Trigger Completion animation if set completed on last turn
if game.last_completed:
    trigger_completion_effect()
    game.last_completed = False

# Trigger Victory screen if won
if game.is_won:
    trigger_victory_effect(time_str, game.moves, game.undo_count)

# Game Board (10 Tableau Columns + Stock Deal Slot)
tableau_cols = st.columns(10)

for col_idx in range(10):
    with tableau_cols[col_idx]:
        cards = game.tableau[col_idx]

        # Top Button: Click to move selected cards here or deal stock if empty click
        col_btn_label = "▼" if cards else "空"
        if st.button(col_btn_label, key=f"col_head_{col_idx}"):
            if game.selected_pos is not None:
                src_col, src_card_idx = game.selected_pos
                if game.move_cards(src_col, src_card_idx, col_idx):
                    st.rerun()
                else:
                    game.selected_pos = None
                    st.rerun()

        if not cards:
            st.markdown(render_empty_slot_html(), unsafe_allow_html=True)
        else:
            for card_idx, card in enumerate(cards):
                is_selected = (game.selected_pos == (col_idx, card_idx))

                # Card HTML rendering
                st.markdown(
                    render_card_html(card, is_selected=is_selected),
                    unsafe_allow_html=True
                )

                # Action button underneath each face-up card
                if card.face_up:
                    if st.button("선택", key=f"btn_{col_idx}_{card_idx}"):
                        if game.selected_pos == (col_idx, card_idx):
                            game.selected_pos = None  # Deselect
                        elif game.selected_pos is not None:
                            # Move attempt
                            src_col, src_card_idx = game.selected_pos
                            if not game.move_cards(src_col, src_card_idx, col_idx):
                                # If move fails, switch selection if valid
                                if game.can_select_stack(col_idx, card_idx):
                                    game.selected_pos = (col_idx, card_idx)
                                else:
                                    game.selected_pos = None
                        else:
                            # New Selection
                            if game.can_select_stack(col_idx, card_idx):
                                game.selected_pos = (col_idx, card_idx)
                        st.rerun()

# Stock Deal Slot Bar
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
        st.markdown("<div style='text-align:center; color:#b89b5e;'>山札 (Deck Empty)</div>", unsafe_allow_html=True)
