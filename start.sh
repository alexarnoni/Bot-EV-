#!/bin/bash

# Caminho do projeto
PROJ_DIR="$HOME/TuringOdds"
VENV_PATH="$PROJ_DIR/venv"

# Inicia sessão do bot_listener.py
tmux new-session -d -s listener bash -c "cd $PROJ_DIR && source $VENV_PATH/bin/activate && python bot_listener.py | tee listener.log"

# Inicia sessão do main.py (que já tem loop interno via schedule)
tmux new-session -d -s main bash -c "cd $PROJ_DIR && source $VENV_PATH/bin/activate && python main.py | tee -a main.log"

echo "✅ Bot rodando nas sessões tmux:"
echo "🎧 tmux attach -t listener"
echo "⚙️  tmux attach -t main"
