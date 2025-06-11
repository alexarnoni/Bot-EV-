#!/bin/bash
cd "$(dirname "$0")"

echo "🔍 Verificando sessões tmux..."

tmux ls 2>/dev/null || {
    echo "❌ Nenhuma sessão tmux ativa."
    exit 1
}

echo ""
echo "🎧 Sessão 'listener':"
if tmux has-session -t listener 2>/dev/null; then
    echo "✅ Ativa"
    echo "📄 Últimas linhas do log (listener.log):"
    tail -n 5 listener.log 2>/dev/null || echo "⚠️ Log não encontrado"
else
    echo "❌ Não está rodando"
fi

echo ""
echo "⚙️ Sessão 'main':"
if tmux has-session -t main 2>/dev/null; then
    echo "✅ Ativa"
    echo "📄 Últimas linhas do log (main.log):"
    tail -n 5 main.log 2>/dev/null || echo "⚠️ Log não encontrado"
else
    echo "❌ Não está rodando"
fi


