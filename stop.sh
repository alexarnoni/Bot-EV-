#!/bin/bash

tmux kill-session -t listener 2>/dev/null
tmux kill-session -t main 2>/dev/null

echo "🛑 Sessões tmux encerradas: listener e main."
