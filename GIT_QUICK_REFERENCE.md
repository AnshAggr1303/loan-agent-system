# 🚀 Git Quick Reference - Copy & Paste Commands

## ⚡ **Quick Push to GitHub (First Time)**

```bash
# Navigate to project
cd /Users/anshagrawal/learnbackend/loan-agent-system

# Initialize git
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: Multi-agent loan application system"

# Connect to GitHub
git remote add origin https://github.com/AnshAggr1303/loan-agent-system.git

# Push
git branch -M main
git push -u origin main
```

---

## 🔄 **Regular Updates (After First Push)**

```bash
# Check what changed
git status

# Add changes
git add .

# Commit
git commit -m "feat: Add new feature"

# Push
git push
```

---

## 📦 **Useful Commands**

```bash
# Check git status
git status

# View commit history
git log --oneline

# View remote URL
git remote -v

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Discard all local changes
git reset --hard HEAD

# Pull latest changes
git pull

# Clone repository
git clone https://github.com/AnshAggr1303/loan-agent-system.git
```

---

## 🌿 **Branching**

```bash
# Create new branch
git checkout -b feature/new-feature

# Switch to main
git checkout main

# Merge branch
git merge feature/new-feature

# Delete branch
git branch -d feature/new-feature

# Push branch to GitHub
git push -u origin feature/new-feature
```

---

## 🔧 **Fix Common Issues**

### Remove file from tracking
```bash
git rm --cached .env.local
git commit -m "chore: Remove .env.local"
git push
```

### Change remote URL
```bash
git remote set-url origin https://github.com/AnshAggr1303/loan-agent-system.git
```

### Force push (use carefully!)
```bash
git push --force
```

### Sync with remote
```bash
git fetch origin
git reset --hard origin/main
```

---

## 📝 **Commit Message Templates**

```bash
# Feature
git commit -m "feat: Add user authentication"

# Bug fix
git commit -m "fix: Resolve KYC timeout issue"

# Documentation
git commit -m "docs: Update README with setup instructions"

# Refactoring
git commit -m "refactor: Simplify orchestrator logic"

# Styling
git commit -m "style: Format code with prettier"

# Testing
git commit -m "test: Add unit tests for underwriting agent"

# Maintenance
git commit -m "chore: Update dependencies"
```

---

## ✅ **Pre-Push Checklist**

Before every `git push`:

```bash
# 1. Check status
git status

# 2. Verify no secrets
cat .gitignore  # Ensure .env.local is listed

# 3. Test locally
npm run build

# 4. Review changes
git diff

# 5. Then push
git push
```

---

## 🎯 **Your Repository**

**URL:** https://github.com/AnshAggr1303/loan-agent-system

**Clone command:**
```bash
git clone https://github.com/AnshAggr1303/loan-agent-system.git
```

---

## 📞 **Need Help?**

Read the full guide: [GITHUB_SETUP.md](./GITHUB_SETUP.md)