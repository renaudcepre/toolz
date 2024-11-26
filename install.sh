#!/bin/bash

# Chemin absolu du répertoire du script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Installer uv si nécessaire
if ! command -v uv &> /dev/null; then
    echo "Installing uv package manager..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

# Créer un environnement virtuel s'il n'existe pas déjà
if [ ! -d "$SCRIPT_DIR/.venv" ]; then
    echo "Creating virtual environment..."
    uv venv
fi

# Installer le package en mode éditable
echo "Installing package..."
source .venv/bin/activate
uv pip install -e .

# Ajouter le chemin au .zshrc s'il n'y est pas déjà
VENV_PATH_LINE="export PATH=\"$SCRIPT_DIR/.venv/bin:\$PATH\""
if ! grep -q "$VENV_PATH_LINE" "$HOME/.zshrc"; then
    echo "Adding virtual environment to PATH in .zshrc..."
    echo "" >> "$HOME/.zshrc"
    echo "# Added by my-scripts installer" >> "$HOME/.zshrc"
    echo "$VENV_PATH_LINE" >> "$HOME/.zshrc"
    echo "Virtual environment added to PATH. Please run 'source ~/.zshrc' to apply changes."
else
    echo "PATH already configured in .zshrc"
fi

echo "Installation completed! Please run 'source ~/.zshrc' to use the commands in your current shell."