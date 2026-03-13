# Security & Privacy Guidelines

## Sensitive Files Protection

### Files in `.gitignore` (Never Committed)
These files contain credentials and are protected:
- `config.yaml` - Local development credentials
- `.streamlit/secrets.toml` - Local Streamlit secrets
- `*.db` - Database files with user data
- `__pycache__/` - Python cache

### How to Verify
```bash
# Ensure files are not in git history
git log --all --full-history -- config.yaml

# Check current status
git status
```

---

## Credentials Management

### For Local Development
1. Copy `config.yaml.example` → `config.yaml`
2. Edit with YOUR credentials (never commit)
3. File is protected by `.gitignore`

OR

1. Copy `.streamlit/secrets.toml.example` → `.streamlit/secrets.toml`
2. Edit with YOUR credentials (never commit)
3. File is protected by `.gitignore`

### For Streamlit Cloud
1. Use **Streamlit Cloud Dashboard** → **Settings** → **Secrets**
2. Add credentials in TOML format
3. **NEVER** commit secrets to GitHub
4. Reference: `STREAMLIT_CLOUD_SETUP.md`

---

## Documentation Security

### Safe to Commit ✅
- `config.yaml.example` - Generic placeholders only
- `.streamlit/secrets.toml.example` - Generic placeholders only
- `STREAMLIT_CLOUD_SETUP.md` - References examples file
- `PROMPTS_V03_COMPLETOS.md` - Uses generic credentials

### Never Commit ❌
- `config.yaml` with real credentials
- `.streamlit/secrets.toml` with real credentials
- Any file with actual passwords or API keys
- Personal information (emails, phone numbers)

---

## Database Security

### User Data
- Stored locally in `mtc_history.db` (in .gitignore)
- Each user's validation history is private
- Database is never uploaded to GitHub

### Passwords
- Stored in `config.yaml` (local) or Streamlit Secrets (cloud)
- NOT stored in database
- Never logged or exposed

---

## Code Review Checklist

Before committing, verify:
- [ ] No passwords in code
- [ ] No API keys hardcoded
- [ ] No personal email addresses in examples
- [ ] No database files committed
- [ ] No local secrets in commit
- [ ] Documentation uses generic placeholders
- [ ] Error messages don't expose credentials

```bash
# Quick security scan
git diff --cached | grep -i "password\|secret\|key\|token"
```

---

## If Credentials Were Exposed

If credentials were accidentally committed:

1. **Rotate immediately** - Change all passwords
2. **Remove from history:**
   ```bash
   git filter-branch --tree-filter 'rm -f config.yaml' HEAD
   git push origin main --force
   ```
3. **Check Streamlit Cloud** - Ensure no exposed secrets there
4. **Update documentation** - Add new example values

---

## Environment Variables

Some services use environment variables instead of config files:
- These are set in Streamlit Cloud secrets
- Never hardcoded in `.env` files
- Never printed to logs

---

## Security Best Practices

1. **Rotate Secrets Regularly**
   - Change passwords every 3-6 months
   - Update API keys when projects end

2. **Use Unique Credentials**
   - Different password for each environment (local, cloud, prod)
   - Don't reuse credentials across projects

3. **Monitor Access**
   - Check Streamlit Cloud logs for unauthorized attempts
   - Monitor database for suspicious queries

4. **Document Changes**
   - When rotating credentials, update this document
   - Keep track of what changed and why

---

## Contact

For security concerns, contact the maintainer privately.
Do NOT open GitHub issues about security vulnerabilities.

---

**Last Updated:** 2024-03-13
**Status:** ✅ All security checks passed
