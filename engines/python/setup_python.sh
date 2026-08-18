#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY_ROOT="$BASE_DIR/pyenv"
UV_BIN="$PY_ROOT/bin/uv"
VENV_DIR="$PY_ROOT/venv"
REQUIREMENTS="$BASE_DIR/requirements.txt"
PYTHON_VERSION="3.12"

# === Изолируем всё, что использует uv, внутри PY_ROOT ===
export UV_CACHE_DIR="$PY_ROOT/cache"
export UV_PYTHON_INSTALL_DIR="$PY_ROOT/python"
export UV_TOOL_DIR="$PY_ROOT/tools"
export UV_TOOL_BIN_DIR="$PY_ROOT/toolbin"
export UV_PYTHON_PREFERENCE="only-managed"
export UV_NO_MODIFY_PATH=1
export UV_UNMANAGED_INSTALL="$PY_ROOT/bin"  # куда ставить сам бинарник uv

mkdir -p "$PY_ROOT"

# === 1. Скачиваем uv, если его ещё нет ===
if [ ! -x "$UV_BIN" ]; then
    echo "Скачивание uv..."
    curl -LsSf https://astral.sh/uv/install.sh | \
        env UV_UNMANAGED_INSTALL="$PY_ROOT/bin" UV_NO_MODIFY_PATH=1 sh

    if [ ! -x "$UV_BIN" ]; then
        echo "Ошибка: не удалось скачать uv."
        exit 1
    fi
fi

# === 2. Ставим нужную версию Python внутрь PY_ROOT ===
"$UV_BIN" python install "$PYTHON_VERSION"

# === 3. Создаём venv внутри той же папки, если его ещё нет ===
if [ ! -x "$VENV_DIR/bin/python" ]; then
    echo "Создание виртуального окружения..."
    "$UV_BIN" venv "$VENV_DIR" --python "$PYTHON_VERSION"
fi

if [ -f "$REQUIREMENTS" ]; then
    echo "Установка зависимостей..."
    "$UV_BIN" pip install --python "$VENV_DIR/bin/python" -r "$REQUIREMENTS"
fi

# === 4. Запуск пользовательского скрипта внутри venv ===
exec "$VENV_DIR/bin/python" "$@"