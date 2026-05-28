import sys
sys.path.insert(0, '/content')
import os
os.chdir('/content')
from pathlib import Path

# Ensure the folder containing app.py is always on sys.path and is the
# working directory so tictactoe_ai.py and tictactoe.model are found
# regardless of where Streamlit was launched from (e.g. Google Colab).
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
os.chdir(_HERE)

import streamlit as st
import subprocess
import time
from tictactoe_ai import (
    create_board, check_winner, is_draw,
    get_available_moves, get_ai_move,
    load_model, save_model, _train_q, MODEL_PATH,
)

# ── Auto-train model if tictactoe.model is missing ───────────────────────────
if not Path(MODEL_PATH).exists():
    with st.spinner("🧠  First run — training AI model… (takes ~5 s)"):
        q = _train_q(episodes=60_000)
        save_model(q)

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Tic Tac Toe · AI",
    page_icon="🎮",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Mono:wght@400;500&display=swap');

:root {
    --bg:        #0d0d0f;
    --surface:   #16161a;
    --border:    #2a2a32;
    --accent-x:  #ff4d6d;
    --accent-o:  #4cc9f0;
    --text:      #e8e8ef;
    --muted:     #5a5a72;
    --win-glow:  0 0 24px rgba(255,255,120,0.35);
}

html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--bg) !important;
    color: var(--text);
    font-family: 'DM Mono', monospace;
}

[data-testid="stSidebar"] {
    background-color: var(--surface) !important;
    border-right: 1px solid var(--border);
}

h1, h2, h3 { font-family: 'Syne', sans-serif; }

/* Hide default Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }

/* Title */
.game-title {
    font-family: 'Syne', sans-serif;
    font-size: 2.6rem;
    font-weight: 800;
    letter-spacing: -1px;
    background: linear-gradient(135deg, var(--accent-x) 0%, var(--accent-o) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    margin-bottom: 0.1rem;
}
.game-subtitle {
    text-align: center;
    color: var(--muted);
    font-size: 0.78rem;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-bottom: 1.6rem;
}

/* Status banner */
.status-banner {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 0.75rem 1.2rem;
    text-align: center;
    font-family: 'Syne', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    margin-bottom: 1.2rem;
    letter-spacing: 0.5px;
}
.status-x   { color: var(--accent-x); border-color: var(--accent-x); }
.status-o   { color: var(--accent-o); border-color: var(--accent-o); }
.status-win { box-shadow: var(--win-glow); border-color: #ffee88; color: #ffee88; }
.status-draw{ color: var(--muted); }

/* Board grid */
.board-wrap {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
    max-width: 340px;
    margin: 0 auto 1.6rem auto;
}

/* Cell buttons  — Streamlit injects stButton div wrappers */
.board-wrap [data-testid="stButton"] button {
    width: 100% !important;
    height: 100px !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 2.6rem !important;
    font-weight: 800 !important;
    border-radius: 14px !important;
    border: 2px solid var(--border) !important;
    background: var(--surface) !important;
    color: var(--text) !important;
    cursor: pointer;
    transition: all 0.18s ease;
}
.board-wrap [data-testid="stButton"] button:hover {
    border-color: var(--muted) !important;
    transform: scale(1.04);
}

/* Scoreboard */
.score-grid {
    display: flex;
    justify-content: center;
    gap: 1rem;
    margin-bottom: 1.4rem;
}
.score-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 0.7rem 1.4rem;
    text-align: center;
    min-width: 80px;
}
.score-label {
    font-size: 0.68rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--muted);
}
.score-value {
    font-family: 'Syne', sans-serif;
    font-size: 1.9rem;
    font-weight: 800;
    line-height: 1.1;
}
.score-x { color: var(--accent-x); }
.score-o { color: var(--accent-o); }
.score-d { color: var(--muted); }

/* Sidebar labels */
.sidebar-label {
    font-size: 0.72rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 0.25rem;
    display: block;
}

/* Move history */
.move-log {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 0.8rem 1rem;
    font-size: 0.78rem;
    color: var(--muted);
    max-height: 180px;
    overflow-y: auto;
    line-height: 1.8;
}
.move-x { color: var(--accent-x); font-weight: 500; }
.move-o { color: var(--accent-o); font-weight: 500; }
</style>
""", unsafe_allow_html=True)


# ── Session state ─────────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "board":        create_board(),
        "current":      "X",
        "game_over":    False,
        "winner":       None,
        "win_combo":    None,
        "scores":       {"X": 0, "O": 0, "Draw": 0},
        "move_log":     [],
        "ai_thinking":  False,
        "game_count":   0,
        "difficulty":   "hard",
        "mode":         "vs_ai",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()
s = st.session_state

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<span class="sidebar-label">Game Mode</span>', unsafe_allow_html=True)
    mode = st.radio(
        "",
        ["vs_ai", "vs_human"],
        format_func=lambda x: "🤖  You vs AI" if x == "vs_ai" else "👥  Two Players",
        key="mode_radio",
        index=0 if s.mode == "vs_ai" else 1,
    )
    if mode != s.mode:
        s.mode = mode

    if s.mode == "vs_ai":
        st.markdown('<span class="sidebar-label" style="margin-top:1rem;display:block">AI Difficulty</span>', unsafe_allow_html=True)
        diff = st.select_slider("", options=["easy", "medium", "hard"], value=s.difficulty, key="diff_slider")
        if diff != s.difficulty:
            s.difficulty = diff

    st.divider()

    st.markdown('<span class="sidebar-label">Move History</span>', unsafe_allow_html=True)
    if s.move_log:
        log_html = "<div class='move-log'>"
        for entry in s.move_log[-20:]:
            cls = "move-x" if "X" in entry else "move-o"
            log_html += f"<div class='{cls}'>{entry}</div>"
        log_html += "</div>"
        st.markdown(log_html, unsafe_allow_html=True)
    else:
        st.markdown("<div class='move-log' style='text-align:center'>No moves yet</div>", unsafe_allow_html=True)

    st.divider()
    if st.button("🔄  New Game", use_container_width=True):
        s.board     = create_board()
        s.current   = "X"
        s.game_over = False
        s.winner    = None
        s.win_combo = None
        s.move_log  = []
        s.game_count += 1
        st.rerun()

    if st.button("🗑️  Reset Scores", use_container_width=True):
        s.scores    = {"X": 0, "O": 0, "Draw": 0}
        s.board     = create_board()
        s.current   = "X"
        s.game_over = False
        s.winner    = None
        s.win_combo = None
        s.move_log  = []
        s.game_count = 0
        st.rerun()

    st.divider()
    if st.button("🧠  Retrain AI Model", use_container_width=True):
        with st.spinner("Training… (~5 s)"):
            q = _train_q(episodes=60_000)
            save_model(q)
        st.success("Model retrained & saved to tictactoe.model")
        st.rerun()

# ── Main area ─────────────────────────────────────────────────────────────────
st.markdown('<div class="game-title">TIC TAC TOE</div>', unsafe_allow_html=True)
model_status = "✦ Q-Learning model loaded" if Path(MODEL_PATH).exists() else "✦ Minimax fallback"
st.markdown(f'<div class="game-subtitle">{model_status}</div>', unsafe_allow_html=True)

# Scoreboard
sc = s.scores
st.markdown(f"""
<div class="score-grid">
  <div class="score-card">
    <div class="score-label">You (X)</div>
    <div class="score-value score-x">{sc['X']}</div>
  </div>
  <div class="score-card">
    <div class="score-label">Draws</div>
    <div class="score-value score-d">{sc['Draw']}</div>
  </div>
  <div class="score-card">
    <div class="score-label">{"AI" if s.mode == "vs_ai" else "P2"} (O)</div>
    <div class="score-value score-o">{sc['O']}</div>
  </div>
</div>
""", unsafe_allow_html=True)

# Status banner
def status_html():
    if s.winner == "X":
        msg = "🎉 You Win!" if s.mode == "vs_ai" else "🎉 Player X Wins!"
        return f'<div class="status-banner status-win">{msg}</div>'
    if s.winner == "O":
        msg = "🤖 AI Wins!" if s.mode == "vs_ai" else "🎉 Player O Wins!"
        return f'<div class="status-banner status-win">{msg}</div>'
    if s.game_over:
        return '<div class="status-banner status-draw">🤝 It\'s a Draw!</div>'
    if s.current == "X":
        label = "Your Turn" if s.mode == "vs_ai" else "Player X's Turn"
        return f'<div class="status-banner status-x">✕  {label}</div>'
    label = "AI is thinking…" if s.mode == "vs_ai" else "Player O's Turn"
    return f'<div class="status-banner status-o">◯  {label}</div>'

st.markdown(status_html(), unsafe_allow_html=True)

# ── Board ─────────────────────────────────────────────────────────────────────
SYMBOLS = {"X": "✕", "O": "◯", " ": "·"}

st.markdown('<div class="board-wrap">', unsafe_allow_html=True)
cols = st.columns(3)
for i in range(9):
    row, col_idx = divmod(i, 3)
    with cols[col_idx]:
        cell_val = s.board[i]
        label    = SYMBOLS.get(cell_val, cell_val)
        disabled = s.game_over or cell_val != " "
        if st.button(label, key=f"cell_{i}_{s.game_count}", disabled=disabled):
            if not s.game_over and cell_val == " " and s.current == "X":
                # Human move
                s.board[i] = "X"
                row_n, col_n = divmod(i, 3)
                s.move_log.append(f"X → row {row_n+1}, col {col_n+1}")
                combo = check_winner(s.board, "X")
                if combo:
                    s.winner    = "X"
                    s.win_combo = combo
                    s.game_over = True
                    s.scores["X"] += 1
                elif is_draw(s.board):
                    s.game_over = True
                    s.scores["Draw"] += 1
                else:
                    s.current = "O"
                st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# ── AI move (fires on rerun when it's O's turn) ───────────────────────────────
if not s.game_over and s.current == "O" and s.mode == "vs_ai":
    time.sleep(0.35)   # brief "thinking" pause for UX
    move = get_ai_move(s.board, difficulty=s.difficulty)
    if move is not None:
        s.board[move] = "O"
        row_n, col_n = divmod(move, 3)
        s.move_log.append(f"O → row {row_n+1}, col {col_n+1}")
        combo = check_winner(s.board, "O")
        if combo:
            s.winner    = "O"
            s.win_combo = combo
            s.game_over = True
            s.scores["O"] += 1
        elif is_draw(s.board):
            s.game_over = True
            s.scores["Draw"] += 1
        else:
            s.current = "X"
    st.rerun()

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center;color:#2e2e3a;font-size:0.7rem;margin-top:2rem;letter-spacing:2px'>
Q-LEARNING · MINIMAX · ALPHA-BETA · tictactoe.model
</div>
""", unsafe_allow_html=True)