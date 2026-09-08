#!/bin/bash
# generate-changelog.sh - Generate changelog from commits
# Usage: ./scripts/generate-changelog.sh

set -e

echo "# Changelog"
echo ""
echo "## $(date +%Y-%m-%d)"
echo ""

# Get commits since last tag or since beginning
if git describe --tags --exact-match 2>/dev/null; then
    echo "Nothing new since last release"
    exit 0
fi

# Get commits from last tag or show recent
if git describe --tags --abbrev=0 2>/dev/null; then
    LAST_TAG=$(git describe --tags --abbrev=0)
    echo "Changes since $LAST_TAG:"
    git log --oneline --pretty=format:"- %s (%h)" $LAST_TAG..HEAD
else
    echo "Recent commits:"
    git log --oneline --pretty=format:"- %s (%h)" -10
fi

echo ""
echo "---"
echo "*Generated: $(date -Iseconds)*"