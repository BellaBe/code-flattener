.PHONY: help run clean

help:
	@echo "Available targets:"
	@echo "  make run     - Clone/scan a remote repository with defaults"
	@echo "  make clean   - Remove the entire output folder"

REPO_URL ?= https://github.com/virattt/ai-hedge-fund

# Patterns to exclude. Adjust or extend as needed.
EXCLUDES = \
	".github/workflows" \
	"tests" \
	".gitignore" \
	"*.md" \
	"*.lock" \
	"*.toml" \
	"*.pdg" \
	"*.txt" \
	"*.ini" \
	"LICENSE" \

# Run the script against a remote repository (by default REPO_URL),
# excluding specified patterns and enabling verbose output.
run:
	python3 src/main.py "$(REPO_URL)" \
	    --exclude $(EXCLUDES) \
	    --verbose

# Clean up all generated output folders/files
clean:
	rm -rf output
