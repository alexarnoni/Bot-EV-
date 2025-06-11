#!/bin/bash

# Caminho do projeto
PROJ_DIR="$HOME/TuringOdds"
VENV_PATH="$PROJ_DIR/venv"

# Finaliza sessões antigas
tmux kill-session -t listener 2>/dev/null
tmux kill-session -t main 2>/dev/null

# Cria sessões tmux vazias
tmux new-session -d -s listener
tmux new-session -d -s main

# Envia comandos para a sessão listener
tmux send-keys -t listener "cd $PROJ_DIR" C-m
tmux send-keys -t listener "source $VENV_PATH/bin/activate" C-m
tmux send-keys -t listener "python3 bot_listener.py | tee listener.log" C-m

# Envia comandos para a sessão main
tmux send-keys -t main "cd $PROJ_DIR" C-m
tmux send-keys -t main "source $VENV_PATH/bin/activate" C-m
tmux send-keys -t main "python3 main.py | tee -a main.log" C-m

echo "✅ Bot rodando nas sessões tmux:"
echo "🎧 tmux attach -t listener"
echo "⚙️  tmux attach -t main"
