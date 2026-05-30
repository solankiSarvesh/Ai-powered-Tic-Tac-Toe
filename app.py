import sys, os

import streamlit as st
import time
from pathlib import Path
from tictactoe_ai import (
    create_board, check_winner, is_draw,
    get_available_moves, get_ai_move,
    load_model, save_model, _train_q, MODEL_PATH,
)

if not Path(MODEL_PATH).exists():
    with st.spinner("Training AI model for the first time..."):
        save_model(_train_q(episodes=60_000))

st.set_page_config(page_title="TicTacToe AI", page_icon="✦",
                   layout="centered", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Outfit:wght@300;400;500;600&display=swap');
:root {
    --bg:#0a0e1a; --bg2:#0f1528; --card:#131929; --card2:#1a2138;
    --border:#1e2d4a; --border2:#243557;
    --x:#f97316; --xg:#f9731640;
    --o:#38bdf8; --og:#38bdf840;
    --gold:#fbbf24; --goldg:#fbbf2430;
    --text:#e2e8f0; --muted:#64748b; --muted2:#94a3b8;
}
*,*::before,*::after { box-sizing:border-box; }
html,body,[data-testid="stAppViewContainer"],[data-testid="stMain"] {
    background:var(--bg)!important; color:var(--text); font-family:'Outfit',sans-serif;
}
[data-testid="stAppViewContainer"]::before {
    content:''; position:fixed; inset:0;
    background-image:
        linear-gradient(rgba(56,189,248,.03) 1px,transparent 1px),
        linear-gradient(90deg,rgba(56,189,248,.03) 1px,transparent 1px);
    background-size:40px 40px; pointer-events:none; z-index:0;
}
[data-testid="stSidebar"] { background:var(--bg2)!important; border-right:1px solid var(--border)!important; }
[data-testid="stSidebar"]>div { padding-top:2rem!important; }
#MainMenu,footer,header { visibility:hidden; }
[data-testid="stDecoration"] { display:none; }
[data-testid="stMainBlockContainer"] { padding-top:1.2rem!important; max-width:520px!important; }

.ttl { text-align:center; margin-bottom:1.3rem; }
.ttl-eye { font-size:.6rem; font-weight:600; letter-spacing:5px; text-transform:uppercase; color:var(--o); margin-bottom:.2rem; }
.ttl-main { font-family:'Bebas Neue',sans-serif; font-size:4rem; letter-spacing:6px; line-height:1;
    background:linear-gradient(135deg,#f97316 0%,#fbbf24 45%,#38bdf8 100%);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    filter:drop-shadow(0 0 28px rgba(249,115,22,.3)); }
.ttl-sub { font-size:.65rem; color:var(--muted); letter-spacing:3px; text-transform:uppercase; margin-top:.2rem; }
.ttl-line { width:56px; height:2px; background:linear-gradient(90deg,var(--x),var(--o)); margin:.7rem auto 0; border-radius:2px; }

.scoreboard { display:flex; gap:10px; margin-bottom:1rem; justify-content:center; }
.score-pill { flex:1; max-width:110px; background:var(--card); border:1px solid var(--border);
    border-radius:14px; padding:.85rem .5rem; text-align:center; position:relative; overflow:hidden; }
.score-pill::before { content:''; position:absolute; top:0; left:0; right:0; height:2px; }
.sp-x::before { background:var(--x); box-shadow:0 0 8px var(--xg); }
.sp-d::before { background:var(--gold); box-shadow:0 0 8px var(--goldg); }
.sp-o::before { background:var(--o); box-shadow:0 0 8px var(--og); }
.score-num { font-family:'Bebas Neue',sans-serif; font-size:2.2rem; line-height:1; letter-spacing:2px; }
.sp-x .score-num { color:var(--x); text-shadow:0 0 16px var(--xg); }
.sp-d .score-num { color:var(--gold); text-shadow:0 0 16px var(--goldg); }
.sp-o .score-num { color:var(--o); text-shadow:0 0 16px var(--og); }
.score-lbl { font-size:.58rem; font-weight:600; letter-spacing:3px; text-transform:uppercase; color:var(--muted); margin-top:.2rem; }

.status-wrap { margin-bottom:1rem; border-radius:12px; padding:.75rem 1.2rem;
    text-align:center; font-size:.92rem; font-weight:500; letter-spacing:.5px;
    border:1px solid; position:relative; overflow:hidden; }
.status-wrap::before { content:''; position:absolute; inset:0; opacity:.06; background:currentColor; }
.st-x    { color:var(--x);    border-color:#f9731650; }
.st-o    { color:var(--o);    border-color:#38bdf850; }
.st-win  { color:var(--gold); border-color:#fbbf2480; animation:pulse-win 1.4s ease-in-out infinite; }
.st-draw { color:var(--muted2);border-color:var(--border); }
@keyframes pulse-win { 0%,100%{box-shadow:none;} 50%{box-shadow:0 0 22px var(--goldg);} }

.sb-sec { font-size:.6rem; font-weight:600; letter-spacing:4px; text-transform:uppercase;
    color:var(--o); margin-bottom:.45rem; padding-bottom:.3rem; border-bottom:1px solid var(--border); }
.diff-dots { display:flex; gap:5px; justify-content:center; margin-top:.4rem; }
.diff-dot  { width:8px; height:8px; border-radius:50%; background:var(--border2); }
.diff-dot.on { background:var(--o); box-shadow:0 0 6px var(--og); }
[data-testid="stSidebar"] .stButton>button {
    background:var(--card2)!important; border:1px solid var(--border2)!important;
    color:var(--text)!important; border-radius:10px!important;
    font-family:'Outfit',sans-serif!important; font-size:.82rem!important;
    font-weight:500!important; transition:all .2s!important;
    width:100%!important; height:auto!important; padding:.45rem 1rem!important;
}
[data-testid="stSidebar"] .stButton>button:hover {
    background:var(--border2)!important; border-color:var(--o)!important; color:var(--o)!important;
}
.move-log { background:var(--card); border:1px solid var(--border); border-radius:10px;
    padding:.65rem .85rem; max-height:150px; overflow-y:auto; font-size:.73rem; line-height:1.9; }
.move-log::-webkit-scrollbar { width:3px; }
.move-log::-webkit-scrollbar-thumb { background:var(--border2); border-radius:3px; }
.log-x{color:var(--x);} .log-o{color:var(--o);}
.game-badge { display:inline-flex; align-items:center; gap:6px; background:var(--card);
    border:1px solid var(--border); border-radius:20px; padding:.28rem .85rem;
    font-size:.63rem; color:var(--muted); letter-spacing:1px; }
.game-badge b { color:var(--gold); }
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
def init_state():
    for k, v in {
        "board": create_board(), "current": "X", "game_over": False,
        "winner": None, "win_combo": None,
        "scores": {"X": 0, "O": 0, "Draw": 0},
        "move_log": [], "game_count": 1,
        "difficulty": "hard", "mode": "vs_ai",
        "restart_at": None,
    }.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()
s = st.session_state

# ── Handle click from board iframe via query param ─────────────────────────────
params = st.query_params
if "move" in params:
    idx = int(params["move"])
    st.query_params.clear()
    human_can_move = (s.mode == "vs_human") or (s.current == "X")
    if not s.game_over and s.board[idx] == " " and human_can_move:
        player = s.current
        s.board[idx] = player
        r2, c2 = divmod(idx, 3)
        s.move_log.append(f"{player} · r{r2+1} c{c2+1}")
        combo = check_winner(s.board, player)
        if combo:
            s.winner = player; s.win_combo = combo
            s.game_over = True; s.scores[player] += 1
        elif is_draw(s.board):
            s.game_over = True; s.scores["Draw"] += 1
        else:
            s.current = "O" if player == "X" else "X"
    st.rerun()

# ── Auto-restart ───────────────────────────────────────────────────────────────
if s.game_over and s.restart_at is None:
    s.restart_at = time.time() + 2.5

if s.restart_at is not None and time.time() >= s.restart_at:
    s.board = create_board(); s.current = "X"; s.game_over = False
    s.winner = None; s.win_combo = None; s.move_log = []
    s.game_count += 1; s.restart_at = None
    st.rerun()

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sb-sec">Game Mode</div>', unsafe_allow_html=True)
    mode = st.radio("", ["vs_ai", "vs_human"],
        format_func=lambda x: "🤖  You vs AI" if x == "vs_ai" else "👥  Two Players",
        key="mode_radio", index=0 if s.mode == "vs_ai" else 1,
        label_visibility="collapsed")
    if mode != s.mode:
        s.mode = mode

    if s.mode == "vs_ai":
        st.markdown('<br><div class="sb-sec">Difficulty</div>', unsafe_allow_html=True)
        diff = st.select_slider("", options=["easy", "medium", "hard"],
            value=s.difficulty, key="diff_slider", label_visibility="collapsed")
        if diff != s.difficulty:
            s.difficulty = diff
        n = {"easy": 1, "medium": 2, "hard": 3}[s.difficulty]
        st.markdown(
            '<div class="diff-dots">' +
            ''.join(f'<div class="diff-dot{"  on" if i < n else ""}"></div>' for i in range(3)) +
            '</div>', unsafe_allow_html=True)

    st.markdown('<br><div class="sb-sec">Move History</div>', unsafe_allow_html=True)
    if s.move_log:
        rows = "".join(
            f'<div class="log-{"x" if "X" in e else "o"}">{"✕" if "X" in e else "◯"}  {e}</div>'
            for e in s.move_log[-20:])
        st.markdown(f'<div class="move-log">{rows}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="move-log" style="color:#64748b;font-style:italic;font-size:.72rem">No moves yet…</div>',
            unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("⟳  New Game", use_container_width=True):
        s.board = create_board(); s.current = "X"; s.game_over = False
        s.winner = None; s.win_combo = None; s.move_log = []
        s.game_count += 1; s.restart_at = None
        st.rerun()
    if st.button("↺  Reset Scores", use_container_width=True):
        s.scores = {"X": 0, "O": 0, "Draw": 0}; s.board = create_board()
        s.current = "X"; s.game_over = False; s.winner = None
        s.win_combo = None; s.move_log = []; s.game_count = 1; s.restart_at = None
        st.rerun()
    if st.button("⚙  Retrain AI", use_container_width=True):
        with st.spinner("Training…"):
            save_model(_train_q(episodes=60_000))
        st.success("Model saved!")
        st.rerun()

# ── Title ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="ttl">
  <div class="ttl-eye">Minimax · Q-Learning · Alpha-Beta</div>
  <div class="ttl-main">TIC TAC TOE</div>
  <div class="ttl-sub">Powered by AI</div>
  <div class="ttl-line"></div>
</div>""", unsafe_allow_html=True)

st.markdown(
    f'<div style="display:flex;justify-content:center;margin-bottom:.8rem">'
    f'<div class="game-badge">GAME &nbsp;<b>#{s.game_count}</b></div></div>',
    unsafe_allow_html=True)

# ── Scoreboard ─────────────────────────────────────────────────────────────────
sc = s.scores
p1 = "YOU" if s.mode == "vs_ai" else "P1"
p2 = "AI"  if s.mode == "vs_ai" else "P2"
st.markdown(f"""
<div class="scoreboard">
  <div class="score-pill sp-x"><div class="score-num">{sc['X']}</div><div class="score-lbl">{p1} · X</div></div>
  <div class="score-pill sp-d"><div class="score-num">{sc['Draw']}</div><div class="score-lbl">Draw</div></div>
  <div class="score-pill sp-o"><div class="score-num">{sc['O']}</div><div class="score-lbl">{p2} · O</div></div>
</div>""", unsafe_allow_html=True)

# ── Status ─────────────────────────────────────────────────────────────────────
if s.winner == "X":
    msg, cls = ("🎉  You Win!" if s.mode == "vs_ai" else "🎉  Player X Wins!"), "st-win"
elif s.winner == "O":
    msg, cls = ("🤖  AI Wins!" if s.mode == "vs_ai" else "🎉  Player O Wins!"), "st-win"
elif s.game_over:
    msg, cls = "🤝  It's a Draw!", "st-draw"
elif s.current == "X":
    msg = "Your Turn — Place X" if s.mode == "vs_ai" else "Player X — Your Turn"
    cls = "st-x"
else:
    msg = "AI is thinking…" if s.mode == "vs_ai" else "Player O — Your Turn"
    cls = "st-o"

if s.restart_at:
    secs = max(1, round(s.restart_at - time.time()))
    msg += f"  ·  New game in {secs}s"

st.markdown(f'<div class="status-wrap {cls}">{msg}</div>', unsafe_allow_html=True)

# ── Board rendered as self-contained HTML component ────────────────────────────
win_set = set(s.win_combo) if s.win_combo else set()
human_can_move = (not s.game_over) and ((s.mode == "vs_human") or (s.current == "X"))

def cell_content(idx):
    val = s.board[idx]
    if val == "X":
        win = "win" if idx in win_set else ""
        return f'<div class="mark mark-x {win}"></div>'
    if val == "O":
        win = "win" if idx in win_set else ""
        return f'<div class="mark mark-o {win}"></div>'
    return ""

cells_html = ""
for i in range(9):
    clickable = human_can_move and s.board[i] == " "
    cursor    = "pointer" if clickable else "default"
    onclick   = f"move({i})" if clickable else ""
    hover_cls = "hoverable" if clickable else ""
    cells_html += f'<div class="cell {hover_cls}" style="cursor:{cursor}" onclick="{onclick}">{cell_content(i)}</div>'

board_html = f"""
<!DOCTYPE html>
<html>
<head>
<style>
  * {{ box-sizing:border-box; margin:0; padding:0; }}
  body {{ background:transparent; display:flex; justify-content:center; padding:4px; }}

  .board {{
    display: grid;
    grid-template-columns: repeat(3, 108px);
    grid-template-rows:    repeat(3, 108px);
    position: relative;
  }}

  /* Hash lines using box-shadow on a single overlay element */
  .board::before {{
    content: '';
    position: absolute;
    inset: 12px;
    background:
      /* vertical lines */
      linear-gradient(#2d4a7a,#2d4a7a) 36% 0 / 2px 100%,
      linear-gradient(#2d4a7a,#2d4a7a) 63% 0 / 2px 100%,
      /* horizontal lines */
      linear-gradient(#2d4a7a,#2d4a7a) 0 36% / 100% 2px,
      linear-gradient(#2d4a7a,#2d4a7a) 0 63% / 100% 2px;
    background-repeat: no-repeat;
    pointer-events: none;
    z-index: 1;
  }}

  .cell {{
    width: 108px; height: 108px;
    display: flex; align-items: center; justify-content: center;
    position: relative; z-index: 2;
    transition: background .15s;
    border-radius: 8px;
  }}
  .cell.hoverable:hover {{ background: rgba(255,255,255,.05); }}

  /* X mark */
  .mark {{ position:absolute; pointer-events:none;
    animation: pop .22s cubic-bezier(.34,1.56,.64,1) both; }}
  .mark-x {{ width:52px; height:52px; }}
  .mark-x::before, .mark-x::after {{
    content:''; position:absolute; width:100%; height:4px;
    background:#f97316; border-radius:3px; top:50%; left:0;
    box-shadow: 0 0 10px #f9731660, 0 0 22px #f9731640;
  }}
  .mark-x::before {{ transform:translateY(-50%) rotate(45deg); }}
  .mark-x::after  {{ transform:translateY(-50%) rotate(-45deg); }}
  .mark-x.win::before, .mark-x.win::after {{
    background:#fbbf24;
    box-shadow: 0 0 14px #fbbf2460, 0 0 28px #fbbf2440;
  }}

  /* O mark */
  .mark-o {{
    width:50px; height:50px; border-radius:50%;
    border:4px solid #38bdf8;
    box-shadow: 0 0 10px #38bdf860, 0 0 22px #38bdf840, inset 0 0 10px #38bdf840;
  }}
  .mark-o.win {{
    border-color:#fbbf24;
    box-shadow: 0 0 14px #fbbf2460, 0 0 28px #fbbf2440, inset 0 0 10px #fbbf2440;
  }}

  @keyframes pop {{
    0%   {{ transform:scale(0) rotate(-15deg); opacity:0; }}
    100% {{ transform:scale(1) rotate(0);      opacity:1; }}
  }}
</style>
</head>
<body>
  <div class="board">{cells_html}</div>
  <script>
    function move(idx) {{
      // Navigate the parent Streamlit page with ?move=idx to trigger rerun
      const url = new URL(window.parent.location.href);
      url.searchParams.set('move', idx);
      window.parent.location.href = url.toString();
    }}
  </script>
</body>
</html>
"""

import streamlit.components.v1 as components
components.html(board_html, height=340, scrolling=False)

# ── AI move ────────────────────────────────────────────────────────────────────
if not s.game_over and s.current == "O" and s.mode == "vs_ai":
    time.sleep(0.35)
    move = get_ai_move(s.board, difficulty=s.difficulty)
    if move is not None:
        s.board[move] = "O"
        r2, c2 = divmod(move, 3)
        s.move_log.append(f"O · r{r2+1} c{c2+1}")
        combo = check_winner(s.board, "O")
        if combo:
            s.winner = "O"; s.win_combo = combo
            s.game_over = True; s.scores["O"] += 1
        elif is_draw(s.board):
            s.game_over = True; s.scores["Draw"] += 1
        else:
            s.current = "X"
    st.rerun()

# ── Keep reruns going while waiting to auto-restart ───────────────────────────
if s.restart_at is not None:
    time.sleep(1)
    st.rerun()

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;margin-top:1.5rem;padding-top:1rem;
     border-top:1px solid #1e2d4a;font-size:.6rem;
     letter-spacing:3px;color:#334155;text-transform:uppercase">
  Tic Tac Toe · AI · Q-Learning · Minimax · Alpha-Beta
</div>""", unsafe_allow_html=True)
