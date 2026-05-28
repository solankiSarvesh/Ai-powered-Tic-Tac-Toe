"""
tictactoe_ai.py
---------------
Trains a Q-learning AI for Tic Tac Toe and saves the policy to
'tictactoe.model' (a pickle file).  app.py loads that model and calls
get_ai_move() to query it.

Run this file directly to (re)train and save the model:
    python tictactoe_ai.py

The saved model is a plain dict  {board_state_str: {move_int: q_value, ...}}
so it is human-readable and requires no external ML library at inference time.
"""

import math
import pickle
import random
from pathlib import Path

MODEL_PATH = Path("tictactoe.model")

# ── Board helpers ──────────────────────────────────────────────────────────────

def create_board():
    return [" "] * 9


def board_key(board):
    return "".join(board)


def check_winner(board, player):
    wins = [
        [0,1,2],[3,4,5],[6,7,8],
        [0,3,6],[1,4,7],[2,5,8],
        [0,4,8],[2,4,6],
    ]
    for combo in wins:
        if all(board[i] == player for i in combo):
            return combo
    return None


def is_draw(board):
    return " " not in board and not check_winner(board,"X") and not check_winner(board,"O")


def get_available_moves(board):
    return [i for i,v in enumerate(board) if v == " "]


# ── Minimax (used as teacher / fallback for hard mode) ────────────────────────

def _minimax(board, depth, is_maximizing, alpha, beta):
    if check_winner(board, "O"): return 10 - depth
    if check_winner(board, "X"): return depth - 10
    if is_draw(board):           return 0

    moves = get_available_moves(board)
    if is_maximizing:
        best = -math.inf
        for m in moves:
            board[m] = "O"
            best = max(best, _minimax(board, depth+1, False, alpha, beta))
            board[m] = " "
            alpha = max(alpha, best)
            if beta <= alpha: break
        return best
    else:
        best = math.inf
        for m in moves:
            board[m] = "X"
            best = min(best, _minimax(board, depth+1, True, alpha, beta))
            board[m] = " "
            beta = min(beta, best)
            if beta <= alpha: break
        return best


def _minimax_best(board):
    best_score, best_move = -math.inf, get_available_moves(board)[0]
    for m in get_available_moves(board):
        board[m] = "O"
        s = _minimax(board, 0, False, -math.inf, math.inf)
        board[m] = " "
        if s > best_score:
            best_score, best_move = s, m
    return best_move


# ── Q-learning trainer ────────────────────────────────────────────────────────

def _train_q(episodes=40_000, alpha=0.5, gamma=0.9, epsilon_start=1.0, epsilon_end=0.05):
    """
    Self-play Q-learning.
    O is the Q-learner (maximiser); X plays randomly (opponent).
    Returns q_table: {state_str: {move: q_value}}
    """
    q: dict[str, dict[int, float]] = {}

    def q_val(state, move):
        return q.setdefault(state, {}).get(move, 0.0)

    def best_q_move(board):
        state  = board_key(board)
        moves  = get_available_moves(board)
        return max(moves, key=lambda m: q_val(state, m))

    epsilon = epsilon_start

    for ep in range(episodes):
        board   = create_board()
        epsilon = max(epsilon_end, epsilon_start - (epsilon_start - epsilon_end) * ep / episodes)

        # randomly decide who goes first
        turn = random.choice(["X", "O"])

        prev_state  = None
        prev_move   = None

        while True:
            moves = get_available_moves(board)
            if not moves:
                # draw — give small negative reward to last O move
                if prev_state is not None and prev_move is not None:
                    old = q_val(prev_state, prev_move)
                    q.setdefault(prev_state, {})[prev_move] = old + alpha * (0 - old)
                break

            if turn == "X":
                move = random.choice(moves)        # random opponent
                board[move] = "X"
                if check_winner(board, "X"):
                    # O lost — penalise the last O action
                    if prev_state is not None and prev_move is not None:
                        old = q_val(prev_state, prev_move)
                        q.setdefault(prev_state, {})[prev_move] = old + alpha * (-10 - old)
                    break
                turn = "O"
            else:
                state = board_key(board)
                # ε-greedy
                if random.random() < epsilon:
                    move = random.choice(moves)
                else:
                    move = best_q_move(board)

                board[move] = "O"

                if check_winner(board, "O"):
                    reward = 10
                    old    = q_val(state, move)
                    q.setdefault(state, {})[move] = old + alpha * (reward - old)
                    break

                if is_draw(board):
                    reward = 0.5
                    old    = q_val(state, move)
                    q.setdefault(state, {})[move] = old + alpha * (reward - old)
                    break

                # non-terminal: TD update
                next_moves = get_available_moves(board)
                next_state = board_key(board)
                max_next   = max((q_val(next_state, nm) for nm in next_moves), default=0)
                old        = q_val(state, move)
                q.setdefault(state, {})[move] = old + alpha * (gamma * max_next - old)

                prev_state, prev_move = state, move
                turn = "X"

    return q


# ── Public API ────────────────────────────────────────────────────────────────

def get_ai_move(board, difficulty="hard"):
    """
    Returns the best move index for player O given the current board.

    difficulty:
        "easy"   – 70 % random, 30 % model
        "medium" – 40 % random, 60 % model
        "hard"   – full minimax (unbeatable)
    """
    available = get_available_moves(board)
    if not available:
        return None

    # random short-circuit
    rand_thresh = {"easy": 0.70, "medium": 0.40}.get(difficulty, 0.0)
    if random.random() < rand_thresh:
        return random.choice(available)

    # hard mode: exact minimax
    if difficulty == "hard":
        return _minimax_best(board)

    # easy / medium fallback: use Q-table
    q = load_model()
    if q is None:
        return _minimax_best(board)

    state = board_key(board)
    if state in q:
        return max(available, key=lambda m: q[state].get(m, 0.0))
    return random.choice(available)


# ── Model persistence ─────────────────────────────────────────────────────────

def save_model(q_table, path=MODEL_PATH):
    with open(path, "wb") as f:
        pickle.dump(q_table, f, protocol=pickle.HIGHEST_PROTOCOL)
    print(f"[tictactoe_ai] Model saved → {path}  ({len(q_table):,} states)")


def load_model(path=MODEL_PATH):
    if not Path(path).exists():
        return None
    with open(path, "rb") as f:
        q = pickle.load(f)
    print(f"[tictactoe_ai] Model loaded ← {path}  ({len(q):,} states)")
    return q


# ── Train & save when run directly ───────────────────────────────────────────

if __name__ == "__main__":
    print("[tictactoe_ai] Training Q-learning model …")
    q_table = _train_q(episodes=60_000)
    save_model(q_table)
    print("[tictactoe_ai] Done.  Run  streamlit run app.py  to play.")
