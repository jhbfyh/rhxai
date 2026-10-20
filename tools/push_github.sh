#!/usr/bin/env bash
# 把当前目录的内容推送到 GitHub 仓库。
# 用法：bash tools/push_github.sh [分支名]
# 认证：使用 Git Credential Manager，首次 push 会弹窗登录 GitHub。
set -euo pipefail

REPO="${REPO:-https://github.com/jhbfyh/rhxai.git}"
BRANCH="${1:-main}"

cd "$(dirname "$0")/.."

if [ ! -d .git ]; then
  git init -b "$BRANCH"
fi

git remote remove origin 2>/dev/null || true
git remote add origin "$REPO"

git add -A
if git diff --cached --quiet; then
  echo "无新增改动，跳过提交"
else
  git commit -m "更新站点内容"
fi

# 与远程历史对齐，避免非快进；首次会拉下远程已有的提交
git fetch origin "$BRANCH"
if git rev-parse --verify "origin/$BRANCH" >/dev/null 2>&1; then
  git merge --allow-unrelated-histories --no-edit "origin/$BRANCH" || true
fi

git push -u origin "$BRANCH"
