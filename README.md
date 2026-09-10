# NutriTrack AI - BMI and Age based nutrition deficiency detection

**Student:** AKHIL PREMAN | **Repo:** github.com/akhil-preman/Nutritrack | **[📜 Click Here to View Chronological Commit History for Guide Review](https://github.com/akhil-preman/Nutritrack/commits/main)**

This repository maintains day-wise chronological development for academic evaluation.

---

## Progress Log

### Day 1 - Sep 5, 2026 - Completed ✅
**Commit:** `Initial Commit` 
- Created Flask project structure (app.py, templates/, static/css/)
- Home page running on http://127.0.0.1:5000
- GitHub repository initialized and pushed
- Status: Verified in commit history

### Day 2 - Sep 10, 2026 - Completed ✅
**Commit:** `Day 2: Added User Registration + BMI + Commercial UI`
- **Registration Fix:** Removed all pre-filled values - Now shows empty white boxes with green border (#2E7D32) as per commercial health-app standards
- **Logic Added:** User registration with age, height, weight + BMI calculation (weight / (height/100)^2)
- **UI:** Commercial green-white theme implemented
- **Git Operations:** Resolved merge conflict using `git pull --rebase` and successfully pushed to main
- **Verification:** All files visible in `github.com/akhil-preman/Nutritrack` - History visible in `/commits/main`

### Day 3 - Next (Planned)
- Food logging dashboard
- AI-based deficiency detection logic
- SQLite database integration for user profiles

---

## 🛠️ Tech Stack
- Backend: Python Flask
- Database: SQLite
- Frontend: HTML5, CSS3 (Commercial Green/White Theme)
- Version Control: Git & GitHub

## 🔍 For Guide Evaluation
1. Click **3 Commits** on main page OR open History link at top of this README
2. You will see Day 1 -> Day 2 progress in chronological order
3. Click any commit to see exact code changes made on that day
4. No code was deleted - Day 1 code is preserved in history and merged into Day 2

## 🚀 How to Run
`pip install -r requirements.txt`
`python app.py`
Open http://127.0.0.1:5000
