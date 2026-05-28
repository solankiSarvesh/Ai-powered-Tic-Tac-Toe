import sys
import os
sys.path.insert(0, '/content')
os.chdir('/content')

import streamlit as st
import time
from pathlib import Path
from tictactoe_ai import (
    create_board, check_winner, is_draw,
    get_available_moves, get_ai_move,
    load_model, save_model, _train_q, MODEL_PATH,
)

if not Path(MODEL_PATH).exists():
    with st.spinner("🧠 Training AI model for the first time..."):
        q = _train_q(episodes=60_000)
        save_model(q)

st.set_page_config(
    page_title="TicTacToe AI",
    page_icon="✦",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Outfit:wght@300;400;500;600&display=swap');

:root {
    --bg:         #0a0e1a;
    --bg2:        #0f1528;
    --card:       #131929;
    --card2:      #1a2138;
    --border:     #1e2d4a;
    --border2:    #243557;
    --x-color:    #f97316;
    --x-glow:     #f9731640;
    --o-color:    #38bdf8;
    --o-glow:     #38bdf840;
    --gold:       #fbbf24;
    --gold-glow:  #fbbf2430;
    --text:       #e2e8f0;
    --muted:      #64748b;
    --muted2:     #94a3b8;
    --line:       #2d4a7a;
    --green:      #34d399;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background: var(--bg) !important;
    color: var(--text);
    font-family: 'Outfit', sans-serif;
}

/* Subtle grid background */
[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image:
        linear-gradient(rgba(56,189,248,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(56,189,248,0.03) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none;
    z-index: 0;
}

[data-testid="stSidebar"] {
    background: var(--bg2) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] > div { padding-top: 2rem !important; }

#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }
[data-testid="stMainBlockContainer"] { padding-top: 1.5rem !important; }

/* ── TITLE ── */
.ttl-wrap {
    text-align: center;
    margin-bottom: 1.8rem;
    position: relative;
}
.ttl-eyebrow {
    font-family: 'Outfit', sans-serif;
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 5px;
    text-transform: uppercase;
    color: var(--o-color);
    margin-bottom: 0.3rem;
}
.ttl-main {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 4.5rem;
    letter-spacing: 6px;
    line-height: 1;
    background: linear-gradient(135deg, #f97316 0%, #fbbf24 40%, #38bdf8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    filter: drop-shadow(0 0 30px rgba(249,115,22,0.3));
}
.ttl-sub {
    font-size: 0.72rem;
    font-weight: 400;
    color: var(--muted);
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-top: 0.4rem;
}
.ttl-line {
    width: 60px;
    height: 2px;
    background: linear-gradient(90deg, var(--x-color), var(--o-color));
    margin: 0.9rem auto 0;
    border-radius: 2px;
}

/* ── SCOREBOARD ── */
.scoreboard {
    display: flex;
    gap: 10px;
    margin-bottom: 1.4rem;
    justify-content: center;
}
.score-pill {
    flex: 1;
    max-width: 120px;
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1rem 0.5rem;
    text-align: center;
    position: relative;
    overflow: hidden;
    transition: transform 0.2s;
}
.score-pill::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
}
.score-pill.sp-x::before  { background: var(--x-color); box-shadow: 0 0 10px var(--x-glow); }
.score-pill.sp-d::before  { background: var(--gold); box-shadow: 0 0 10px var(--gold-glow); }
.score-pill.sp-o::before  { background: var(--o-color); box-shadow: 0 0 10px var(--o-glow); }
.score-num {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 2.6rem;
    line-height: 1;
    letter-spacing: 2px;
}
.sp-x .score-num { color: var(--x-color); text-shadow: 0 0 20px var(--x-glow); }
.sp-d .score-num { color: var(--gold);    text-shadow: 0 0 20px var(--gold-glow); }
.sp-o .score-num { color: var(--o-color); text-shadow: 0 0 20px var(--o-glow); }
.score-lbl {
    font-size: 0.6rem;
    font-weight: 600;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: var(--muted);
    margin-top: 0.25rem;
}

/* ── STATUS BANNER ── */
.status-wrap {
    margin-bottom: 1.4rem;
    border-radius: 14px;
    padding: 0.85rem 1.5rem;
    text-align: center;
    font-size: 1rem;
    font-weight: 500;
    letter-spacing: 1px;
    border: 1px solid;
    position: relative;
    overflow: hidden;
}
.status-wrap::before {
    content: '';
    position: absolute;
    inset: 0;
    opacity: 0.06;
    background: currentColor;
}
.st-x    { color: var(--x-color); border-color: #f9731650; }
.st-o    { color: var(--o-color); border-color: #38bdf850; }
.st-win  { color: var(--gold);    border-color: #fbbf2480; animation: pulse-win 1.5s ease-in-out infinite; }
.st-draw { color: var(--muted2);  border-color: var(--border); }

@keyframes pulse-win {
    0%,100% { box-shadow: 0 0 0px transparent; }
    50%      { box-shadow: 0 0 24px var(--gold-glow); }
}

/* ── HASH BOARD ── */
.board-outer {
    display: flex;
    justify-content: center;
    margin-bottom: 1.6rem;
}
.hash-board {
    display: grid;
    grid-template-columns: repeat(3, 100px);
    grid-template-rows: repeat(3, 100px);
    position: relative;
}

/* The 4 hash lines */
.hash-board::before, .hash-board::after,
.hash-v1, .hash-v2 {
    content: '';
    position: absolute;
    background: linear-gradient(180deg, transparent, var(--line) 20%, var(--line) 80%, transparent);
    border-radius: 3px;
}
/* Horizontal lines */
.hash-board::before {
    top: 100px; left: 10px; right: 10px; height: 2px;
    background: linear-gradient(90deg, transparent, var(--line) 10%, var(--line) 90%, transparent);
}
.hash-board::after {
    top: 200px; left: 10px; right: 10px; height: 2px;
    background: linear-gradient(90deg, transparent, var(--line) 10%, var(--line) 90%, transparent);
}
/* Vertical lines injected as siblings */
.hash-v1 {
    left: 100px; top: 10px; bottom: 10px; width: 2px;
    background: linear-gradient(180deg, transparent, var(--line) 10%, var(--line) 90%, transparent) !important;
}
.hash-v2 {
    left: 200px; top: 10px; bottom: 10px; width: 2px;
    background: linear-gradient(180deg, transparent, var(--line) 10%, var(--line) 90%, transparent) !important;
}

.cell-btn {
    width: 100px; height: 100px;
    display: flex; align-items: center; justify-content: center;
    cursor: pointer;
    background: transparent;
    border: none;
    position: relative;
    transition: background 0.2s;
    border-radius: 0;
    z-index: 1;
}
.cell-btn:hover { background: rgba(255,255,255,0.03); }
.cell-btn:disabled { cursor: default; }

/* X drawn with two pseudo lines */
.mark-x {
    width: 54px; height: 54px;
    position: relative;
    animation: pop-in 0.25s cubic-bezier(0.34,1.56,0.64,1);
}
.mark-x::before, .mark-x::after {
    content: '';
    position: absolute;
    width: 100%; height: 4px;
    background: var(--x-color);
    box-shadow: 0 0 12px var(--x-glow), 0 0 24px var(--x-glow);
    border-radius: 3px;
    top: 50%; left: 0;
    transform-origin: center;
}
.mark-x::before { transform: translateY(-50%) rotate(45deg); }
.mark-x::after  { transform: translateY(-50%) rotate(-45deg); }

/* O drawn as a circle */
.mark-o {
    width: 50px; height: 50px;
    border-radius: 50%;
    border: 4px solid var(--o-color);
    box-shadow: 0 0 12px var(--o-glow), 0 0 24px var(--o-glow), inset 0 0 12px var(--o-glow);
    animation: pop-in 0.25s cubic-bezier(0.34,1.56,0.64,1);
}

/* Winning cell highlight */
.cell-win { background: rgba(251,191,36,0.07) !important; border-radius: 8px; }
.cell-win .mark-x::before, .cell-win .mark-x::after {
    background: var(--gold) !important;
    box-shadow: 0 0 16px var(--gold-glow), 0 0 32px var(--gold-glow) !important;
}
.cell-win .mark-o {
    border-color: var(--gold) !important;
    box-shadow: 0 0 16px var(--gold-glow), 0 0 32px var(--gold-glow), inset 0 0 12px var(--gold-glow) !important;
}

/* Empty hover dot */
.cell-empty-hover {
    width: 10px; height: 10px;
    border-radius: 50%;
    background: var(--border2);
    opacity: 0;
    transition: opacity 0.2s;
}
.cell-btn:not(:disabled):hover .cell-empty-hover { opacity: 1; }

@keyframes pop-in {
    0%   { transform: scale(0) rotate(-10deg); opacity: 0; }
    100% { transform: scale(1) rotate(0deg);   opacity: 1; }
}

/* ── SIDEBAR ── */
.sb-section {
    font-size: 0.62rem;
    font-weight: 600;
    letter-spacing: 4px;
    text-transform: uppercase;
    color: var(--o-color);
    margin-bottom: 0.5rem;
    padding-bottom: 0.4rem;
    border-bottom: 1px solid var(--border);
}

/* Streamlit widget overrides */
[data-testid="stSidebar"] [data-testid="stRadio"] label {
    font-size: 0.85rem !important;
    color: var(--muted2) !important;
}
[data-testid="stSidebar"] .stButton button {
    background: var(--card2) !important;
    border: 1px solid var(--border2) !important;
    color: var(--text) !important;
    border-radius: 10px !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    transition: all 0.2s !important;
}
[data-testid="stSidebar"] .stButton button:hover {
    background: var(--border2) !important;
    border-color: var(--o-color) !important;
    color: var(--o-color) !important;
}

/* Move log */
.move-log {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 0.7rem 0.9rem;
    max-height: 160px;
    overflow-y: auto;
    font-size: 0.75rem;
    line-height: 1.9;
}
.move-log::-webkit-scrollbar { width: 3px; }
.move-log::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 3px; }
.log-x { color: var(--x-color); }
.log-o { color: var(--o-color); }
.log-empty { color: var(--muted); font-style: italic; font-size: 0.72rem; }

/* Difficulty indicator dots */
.diff-dots { display: flex; gap: 5px; justify-content: center; margin-top: 0.5rem; }
.diff-dot  { width: 8px; height: 8px; border-radius: 50%; background: var(--border2); }
.diff-dot.active { background: var(--o-color); box-shadow: 0 0 6px var(--o-glow); }

/* Game count badge */
.game-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 0.3rem 0.8rem;
    font-size: 0.68rem;
    color: var(--muted);
    letter-spacing: 1px;
    margin: 0 auto 1.2rem;
    width: fit-content;
}
.game-badge span { color: var(--gold); font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
def init_state():
    for k, v in {
        "board": create_board(), "current": "X", "game_over": False,
        "winner": None, "win_combo": None,
        "scores": {"X": 0, "O": 0, "Draw": 0},
        "move_log": [], "game_count": 1, "difficulty": "hard", "mode": "vs_ai",
    }.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()
s = st.session_state

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sb-section">Game Mode</div>', unsafe_allow_html=True)
    mode = st.radio("", ["vs_ai", "vs_human"],
        format_func=lambda x: "🤖  You vs AI" if x == "vs_ai" else "👥  Two Players",
        key="mode_radio", index=0 if s.mode == "vs_ai" else 1, label_visibility="collapsed")
    if mode != s.mode:
        s.mode = mode

    if s.mode == "vs_ai":
        st.markdown('<br><div class="sb-section">Difficulty</div>', unsafe_allow_html=True)
        diff = st.select_slider("", options=["easy", "medium", "hard"],
            value=s.difficulty, key="diff_slider", label_visibility="collapsed")
        if diff != s.difficulty:
            s.difficulty = diff
        dots = {"easy": 1, "medium": 2, "hard": 3}[s.difficulty]
        dot_html = '<div class="diff-dots">' + \
            ''.join(f'<div class="diff-dot{"  active" if i < dots else ""}"></div>' for i in range(3)) + \
            '</div>'
        st.markdown(dot_html, unsafe_allow_html=True)

    st.markdown('<br><div class="sb-section">Move History</div>', unsafe_allow_html=True)
    if s.move_log:
        log = "".join(
            f'<div class="log-{"x" if "X" in e else "o"}">'
            f'{"✕" if "X" in e else "◯"}  {e}</div>'
            for e in s.move_log[-20:]
        )
        st.markdown(f'<div class="move-log">{log}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="move-log"><span class="log-empty">No moves yet…</span></div>',
            unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("⟳  New Game", use_container_width=True):
        s.board = create_board(); s.current = "X"; s.game_over = False
        s.winner = None; s.win_combo = None; s.move_log = []; s.game_count += 1
        st.rerun()
    if st.button("↺  Reset Scores", use_container_width=True):
        s.scores = {"X": 0, "O": 0, "Draw": 0}; s.board = create_board()
        s.current = "X"; s.game_over = False; s.winner = None
        s.win_combo = None; s.move_log = []; s.game_count = 1
        st.rerun()
    if st.button("⚙  Retrain AI", use_container_width=True):
        with st.spinner("Training…"):
            save_model(_train_q(episodes=60_000))
        st.success("Model saved!")
        st.rerun()

# ── Title ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="ttl-wrap">
  <div class="ttl-eyebrow">Minimax · Q-Learning · Alpha-Beta</div>
  <div class="ttl-main">TIC TAC TOE</div>
  <div class="ttl-sub">Powered by AI</div>
  <div class="ttl-line"></div>
</div>
""", unsafe_allow_html=True)

# Game counter
st.markdown(
    f'<div style="display:flex;justify-content:center">'
    f'<div class="game-badge">GAME  <span>#{s.game_count}</span></div></div>',
    unsafe_allow_html=True)

# ── Scoreboard ─────────────────────────────────────────────────────────────────
sc = s.scores
p1_label = "YOU" if s.mode == "vs_ai" else "P1"
p2_label = "AI"  if s.mode == "vs_ai" else "P2"
st.markdown(f"""
<div class="scoreboard">
  <div class="score-pill sp-x">
    <div class="score-num">{sc['X']}</div>
    <div class="score-lbl">{p1_label} · X</div>
  </div>
  <div class="score-pill sp-d">
    <div class="score-num">{sc['Draw']}</div>
    <div class="score-lbl">Draw</div>
  </div>
  <div class="score-pill sp-o">
    <div class="score-num">{sc['O']}</div>
    <div class="score-lbl">{p2_label} · O</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Status banner ──────────────────────────────────────────────────────────────
if s.winner == "X":
    msg  = "🎉  You Win!" if s.mode == "vs_ai" else "🎉  Player X Wins!"
    cls  = "st-win"
elif s.winner == "O":
    msg  = "🤖  AI Wins!" if s.mode == "vs_ai" else "🎉  Player O Wins!"
    cls  = "st-win"
elif s.game_over:
    msg, cls = "🤝  It's a Draw!", "st-draw"
elif s.current == "X":
    msg  = "Your Turn — Place X" if s.mode == "vs_ai" else "Player X — Your Turn"
    cls  = "st-x"
else:
    msg  = "AI is thinking…" if s.mode == "vs_ai" else "Player O — Your Turn"
    cls  = "st-o"

st.markdown(f'<div class="status-wrap {cls}">{msg}</div>', unsafe_allow_html=True)

# ── Hash Board ─────────────────────────────────────────────────────────────────
win_set = set(s.win_combo) if s.win_combo else set()

def cell_html(idx):
    val      = s.board[idx]
    is_win   = idx in win_set
    win_cls  = " cell-win" if is_win else ""
    if val == "X":
        mark = '<div class="mark-x"></div>'
    elif val == "O":
        mark = '<div class="mark-o"></div>'
    else:
        mark = '<div class="cell-empty-hover"></div>'
    return f'<div class="cell-btn{win_cls}" style="pointer-events:none">{mark}</div>'

# Render hash lines + cell content as pure HTML (visual layer)
cells_html = "".join(cell_html(i) for i in range(9))
st.markdown(f"""
<div class="board-outer">
  <div class="hash-board">
    <div class="hash-v1"></div>
    <div class="hash-v2"></div>
    {cells_html}
  </div>
</div>
""", unsafe_allow_html=True)

# Invisible Streamlit button grid (click layer, positioned on top via CSS)
st.markdown("""
<style>
/* Overlay the 3-col button grid exactly over the hash board */
div[data-testid="stHorizontalBlock"] {
    position: relative;
    width: 300px !important;
    margin: -316px auto 1.6rem auto !important;
    gap: 0 !important;
}
div[data-testid="stHorizontalBlock"] > div {
    padding: 0 !important;
    flex: 0 0 100px !important;
    min-width: 100px !important;
}
div[data-testid="stHorizontalBlock"] .stButton button {
    width: 100px !important;
    height: 100px !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: transparent !important;
    font-size: 1px !important;
    cursor: pointer !important;
    border-radius: 0 !important;
    padding: 0 !important;
}
div[data-testid="stHorizontalBlock"] .stButton button:hover {
    background: rgba(255,255,255,0.04) !important;
}
div[data-testid="stHorizontalBlock"] .stButton button:disabled {
    cursor: default !important;
    background: transparent !important;
}
</style>
""", unsafe_allow_html=True)

cols = st.columns(3)
for i in range(9):
    with cols[i % 3]:
        disabled = s.game_over or s.board[i] != " "
        if st.button("·", key=f"c{i}_{s.game_count}", disabled=disabled, label_visibility="visible"):
            if not s.game_over and s.board[i] == " " and s.current == "X":
                s.board[i] = "X"
                r, c = divmod(i, 3)
                s.move_log.append(f"row {r+1}, col {c+1}")
                combo = check_winner(s.board, "X")
                if combo:
                    s.winner = "X"; s.win_combo = combo; s.game_over = True; s.scores["X"] += 1
                elif is_draw(s.board):
                    s.game_over = True; s.scores["Draw"] += 1
                else:
                    s.current = "O"
                st.rerun()

# ── AI move ────────────────────────────────────────────────────────────────────
if not s.game_over and s.current == "O" and s.mode == "vs_ai":
    time.sleep(0.4)
    move = get_ai_move(s.board, difficulty=s.difficulty)
    if move is not None:
        s.board[move] = "O"
        r, c = divmod(move, 3)
        s.move_log.append(f"row {r+1}, col {c+1}")
        combo = check_winner(s.board, "O")
        if combo:
            s.winner = "O"; s.win_combo = combo; s.game_over = True; s.scores["O"] += 1
        elif is_draw(s.board):
            s.game_over = True; s.scores["Draw"] += 1
        else:
            s.current = "X"
    st.rerun()

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;margin-top:2.5rem;padding-top:1rem;
     border-top:1px solid #1e2d4a;font-size:0.62rem;
     letter-spacing:3px;color:#334155;text-transform:uppercase">
  Tic Tac Toe · AI · Q-Learning · Minimax
</div>
""", unsafe_allow_html=True)
