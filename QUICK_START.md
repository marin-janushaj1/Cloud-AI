# ⚡ Quick Start - Do This First!

**Total time:** 5 minutes
**Goal:** Test if your ML service works

---

## 🎯 Do This Right Now (5 Minutes)

### Step 1: Open Terminal

Press `Cmd + Space`, type "Terminal", press Enter

### Step 2: Copy and Paste These Commands

```bash
# Go to ml_service folder
cd /Users/marinjanushaj/Documents/Cloud-AI/ml_service

# Start the ML service
PORT=5001 /Users/marinjanushaj/Documents/Cloud-AI/venv311/bin/python server.py
```

### Step 3: What You Should See

```
================================================================================
ML PREDICTION SERVICE STARTING
================================================================================

Listening on http://0.0.0.0:5001

INFO:predict:✓ Loaded housing model: LightGBM
 * Running on http://127.0.0.1:5001
```

**✅ If you see this - IT WORKS!**

### Step 4: Test It (Open a NEW Terminal)

```bash
# Test health check
curl http://localhost:5001/health
```

**Expected:** Should see `"status":"ok"`

```bash
# Test prediction
curl -X POST http://localhost:5001/predict-housing \
  -H "Content-Type: application/json" \
  -d '{"property_type":"T","is_new":"N","duration":"F","county":"GREATER LONDON","year":2016,"month":6}'
```

**Expected:** Should see `"price":511741.71` (or similar number)

### Step 5: Stop It

Go back to first terminal, press `Ctrl + C`

---

## 🎉 Success!

If you got a price prediction, your ML service works!

**Next:** Read `DEPLOYMENT_GUIDE.md` for full instructions

---

## ❌ Got an Error?

### "ModuleNotFoundError: No module named 'flask'"

```bash
# Install dependencies
/Users/marinjanushaj/Documents/Cloud-AI/venv311/bin/pip install -r requirements.txt
```

### "Model file not found"

```bash
# Check if model exists
ls -lh /Users/marinjanushaj/Documents/Cloud-AI/data/clean/best_model.pkl
```

If file doesn't exist:
1. Open Jupyter notebook
2. Run `dataset1_uk_housing/4_model.ipynb`
3. Wait for training to complete

### "Port 5000 is already in use"

This is normal on Mac. We're already using port 5001 (see the PORT=5001 in the command).

---

## 📖 Where to Learn More

- **DEPLOYMENT_GUIDE.md** - Full beginner's guide (read this next!)
- **TESTING.md** - Technical testing details
- **ml_service/README.md** - ML service documentation
- **api/README.md** - API gateway documentation

---

**You're doing great! 🚀**
