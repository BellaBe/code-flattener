.PHONY: help run_remote run_local clean

help:
	@echo "Available targets:"
	@echo "  make run_remote   - Run against a remote GitHub repository"
	@echo "  make run_local    - Run against a local repository directory"
	@echo "  make clean        - Remove the generated output file"

# Example: run against a remote repository
run_remote:
	python3 src/main.py \
	    --repo "https://github.com/user/repo" \
	    --output "output.txt" \
	    --exclude "*.md" "*.png" \
	    --select "*.py" \
	    --branch "main" \
	    --verbose

# Example: run against a local directory
run_local:
	python3 src/main.py \
	    --repo "/path/to/local/repo" \
	    --output "output.txt" \
	    --exclude "*.md" \
	    --verbose

clean:
	rm -f output.txt

