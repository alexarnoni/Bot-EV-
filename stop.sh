#!/bin/bash

echo "🛑 Encerrando sessões tmux..."

if tmux has-session -t listener 2>/dev/null; then
    tmux kill-session -t listener
    echo "🎧 Sessão 'listener' encerrada."
else
    echo "⚠️ Sessão 'listener' não estava ativa."
fi

if tmux has-session -t main 2>/dev/null; then
    tmux kill-session -t main
    echo "⚙️ Sessão 'main' encerrada."
else
    echo "⚠️ Sessão 'main' não estava ativa."
fi

echo "✅ Finalizado."
