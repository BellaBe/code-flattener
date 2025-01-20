.PHONY: help run clean

help:
	@echo "Available targets:"
	@echo "  make run     - Clone/scan a remote repository with defaults"
	@echo "  make clean   - Remove the entire output folder"

REPO_URL ?= https://github.com/keizerzilla/telegram-chat-parser.git

# Patterns to exclude. Adjust or extend as needed.
EXCLUDES = \
	".github/*" \
	"tests" \
	".gitignore" \
	"*.lock" \
	"*.toml" \
	"*.pdg" \
	"*.txt" \
	"*.ini" \
	"LICENSE" \
	"coveragerc" \
	".editorconfig" \
	"Makefile" \
	".pre-commit-config.yaml" \
	".vscode/*" \
	".devcontainer/*" \
	"guides/*" \
	"images/*" \
	".git/*" \
	"*.csv" \
	"*.svg" \
	"*.png" \
	"*.jpg" \
	"*/package-lock.json" \
	"package-lock.json" \
	"*/package.json" \
	"*/logs/*" \
	"*/data/*" \
	"*logs/session_*"

# Run the script against a remote repository (by default REPO_URL),
# excluding specified patterns and enabling verbose output.
run:
	python3 src/main.py "$(REPO_URL)" \
	    --exclude $(EXCLUDES) \
	    --verbose \
	    --ignore-hidden

# Clean up all generated output folders/files
clean:
	rm -rf output
