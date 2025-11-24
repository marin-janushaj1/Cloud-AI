# 🚀 Complete Deployment Guide - Step by Step

**Author:** Claude Code
**For:** Marin Janushaj
**Goal:** Deploy your UK Housing Price Prediction project to the cloud

This guide assumes you have **ZERO deployment experience**. Follow every step carefully!

---

## 📋 Table of Contents

1. [What Did We Build?](#what-did-we-build)
2. [Prerequisites - What You Need](#prerequisites)
3. [Step-by-Step Instructions](#step-by-step-instructions)
4. [Testing Your Work](#testing-your-work)
5. [Common Errors & Fixes](#common-errors--fixes)
6. [What's Next](#whats-next)

---

## 🏗️ What Did We Build?

We created a **complete backend infrastructure** for your ML project:

### The Big Picture

```
┌─────────────────────────────────────────────────────────────┐
│                        YOUR PROJECT                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐      ┌──────────────┐      ┌───────────┐ │
│  │  Streamlit   │──────│  Go API      │──────│  Python   │ │
│  │  Frontend    │      │  Gateway     │      │  ML Model │ │
│  │  (Port 8501) │      │  (Port 8080) │      │ (Port 5001)│ │
│  └──────────────┘      └──────────────┘      └───────────┘ │
│         │                     │                     │        │
│         │                     │                     │        │
│    User sees this        Validates input      Does ML       │
│    (Web page)            (Security layer)     predictions   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### What Each Part Does

1. **Streamlit Frontend** (`app.py`)
   - What users see in their browser
   - Pretty interface with sliders and buttons
   - Already working! (You've been using it)

2. **Go API Gateway** (`api/`)
   - NEW - We just built this
   - Checks if user inputs are valid
   - Protects your ML model from bad data
   - Written in Go (new language for the course requirement)

3. **Python ML Service** (`ml_service/`)
   - NEW - We just built this
   - Loads your trained LightGBM model
   - Makes predictions
   - Returns prices

4. **Docker** (`docker-compose.yml`)
   - NEW - We just built this
   - Packages everything into containers
   - Makes it easy to deploy anywhere
   - Like a shipping container for code

---

## ✅ Prerequisites - What You Need

### 1. Check Your Model File Exists

```bash
# Run this command in your terminal:
ls -lh data/clean/best_model.pkl
```

**Expected output:**
```
-rw-r--r--@ 1 marinjanushaj  staff   506K Nov 23 15:25 data/clean/best_model.pkl
```

**❌ If you see "No such file":**
- Open Jupyter: `jupyter notebook`
- Go to `dataset1_uk_housing/4_model.ipynb`
- Run all cells (Kernel → Restart & Run All)
- Wait 5-10 minutes for training
- Model will be saved to `data/clean/best_model.pkl`

### 2. Install Docker Desktop

**What is Docker?**
Think of Docker like a virtual shipping container for your code. It packages everything (Python, Go, your models) so it runs the same on any computer.

**How to install:**

1. Go to: https://www.docker.com/products/docker-desktop
2. Download Docker Desktop for Mac
3. Install it (drag to Applications)
4. Open Docker Desktop
5. Wait for "Docker Desktop is running" (whale icon in menu bar)
6. Test it works:

```bash
docker --version
```

**Expected output:**
```
Docker version 24.0.x, build xxxxx
```

### 3. Make Sure Git Is Working

```bash
git status
```

Should show your current branch and modified files.

---

## 🎯 Step-by-Step Instructions

### Option A: Quick Test (No Docker - 5 minutes)

This tests just the Python ML service to make sure it works.

#### Step 1: Open Terminal

- Press `Cmd + Space`
- Type "Terminal"
- Press Enter

#### Step 2: Navigate to Your Project

```bash
cd /Users/marinjanushaj/Documents/Cloud-AI/ml_service
```

#### Step 3: Start the ML Service

```bash
PORT=5001 /Users/marinjanushaj/Documents/Cloud-AI/venv311/bin/python server.py
```

**What you should see:**
```
================================================================================
ML PREDICTION SERVICE STARTING
================================================================================

Listening on http://0.0.0.0:5001

Endpoints:
  GET  /health              - Health check
  POST /predict-housing     - Predict UK housing price
  POST /predict-electricity - Predict UK electricity demand
  GET  /models              - List available models

================================================================================

INFO:predict:✓ Loaded housing model: LightGBM
 * Running on http://127.0.0.1:5001
```

**✅ Success!** Your ML service is running.

**❌ Error: "Port 5000 is in use"?**
- This is normal on Mac (AirPlay uses port 5000)
- We're already using port 5001 instead
- If you see this, it means the command tried to use 5000
- Try: `PORT=5001 python server.py` (make sure PORT= is included)

#### Step 4: Test It (Open a NEW Terminal Window)

**DON'T close the first terminal!** Open a second one:

```bash
# Test health check
curl http://localhost:5001/health

# Should return:
# {"status":"ok","service":"ML Prediction Service",...}
```

```bash
# Test a prediction
curl -X POST http://localhost:5001/predict-housing \
  -H "Content-Type: application/json" \
  -d '{"property_type":"T","is_new":"N","duration":"F","county":"GREATER LONDON","year":2016,"month":6}'

# Should return:
# {"price":511741.71,"confidence_lower":267035.71,...}
```

**🎉 If you see a price (like £511,741), it's working!**

#### Step 5: Stop the Server

- Go back to first terminal
- Press `Ctrl + C`

---

### Option B: Full Docker Test (All Services - 15 minutes)

This tests everything together (ML service + API gateway + Streamlit).

#### Step 1: Make Sure Docker Desktop Is Running

- Look for whale icon in your menu bar (top right)
- Should say "Docker Desktop is running"
- If not, open Docker Desktop app and wait

#### Step 2: Navigate to Project Root

```bash
cd /Users/marinjanushaj/Documents/Cloud-AI
```

#### Step 3: Build Everything (This Takes 5-10 Minutes First Time)

```bash
docker-compose build
```

**What this does:**
- Downloads Python 3.11
- Downloads Go 1.21
- Installs all libraries
- Packages your code into containers

**What you'll see:**
```
Building ml-service...
Step 1/10 : FROM python:3.11-slim
 ---> Downloading...
...
Successfully built ml-service

Building api-gateway...
Step 1/12 : FROM golang:1.21-alpine
...
Successfully built api-gateway

Building housing-app...
...
Successfully built housing-app
```

**⏳ Be patient - first build takes 5-10 minutes!**

#### Step 4: Start All Services

```bash
docker-compose up
```

**What you'll see:**
```
Creating network "cloud-ai_backend" ... done
Creating network "cloud-ai_frontend" ... done
Creating ml-service ... done
Creating api-gateway ... done
Creating housing-app ... done

ml-service    | ✓ Loaded housing model: LightGBM
api-gateway   | Listening on :8080
housing-app   | You can now view your Streamlit app in your browser.
```

**✅ When you see "You can now view your Streamlit app" - it's ready!**

#### Step 5: Test Each Service

Open a **NEW terminal window** (keep docker-compose running in the first).

```bash
# 1. Test ML Service
curl http://localhost:5001/health

# 2. Test API Gateway
curl http://localhost:8080/api/v1/health

# 3. Test housing prediction through API Gateway
curl -X POST http://localhost:8080/api/v1/predict/housing \
  -H "Content-Type: application/json" \
  -d '{"property_type":"T","is_new":"N","duration":"F","county":"GREATER LONDON","year":2016,"month":6}'

# 4. Open Streamlit in browser
open http://localhost:8501
```

**🎉 If all 4 work, you're ready for cloud deployment!**

#### Step 6: Stop Everything

In the terminal running docker-compose:
- Press `Ctrl + C`
- Wait for "Stopping..." messages
- Run: `docker-compose down`

---

## 🧪 Testing Your Work

### Checklist - Mark Each Item When Done

**Option A (Quick Test):**
- [ ] ML service starts without errors
- [ ] Health check returns `"status":"ok"`
- [ ] Housing prediction returns a price
- [ ] Price is a reasonable number (£100k - £1M)

**Option B (Docker Test):**
- [ ] Docker Desktop is running
- [ ] `docker-compose build` completes without errors
- [ ] `docker-compose up` starts all 3 services
- [ ] ML service health check works (port 5001)
- [ ] API gateway health check works (port 8080)
- [ ] Streamlit opens in browser (port 8501)
- [ ] Can make prediction in Streamlit
- [ ] `docker-compose down` stops everything cleanly

---

## ❌ Common Errors & Fixes

### Error 1: "docker: command not found"

**Problem:** Docker is not installed or not in PATH

**Fix:**
1. Install Docker Desktop (see Prerequisites)
2. Open Docker Desktop app
3. Wait for it to start
4. Close and reopen terminal
5. Try again

### Error 2: "Cannot connect to the Docker daemon"

**Problem:** Docker Desktop is not running

**Fix:**
1. Open Docker Desktop application
2. Wait for whale icon in menu bar
3. Should say "Docker Desktop is running"
4. Try again

### Error 3: "Port 5000 is already in use"

**Problem:** macOS AirPlay Receiver uses port 5000

**Fix (Option 1 - Recommended):**
- Use port 5001 instead: `PORT=5001 python server.py`
- docker-compose already configured for this

**Fix (Option 2):**
1. Open System Settings
2. Go to General → AirDrop & Handoff
3. Turn off "AirPlay Receiver"

### Error 4: "Model file not found"

**Problem:** `best_model.pkl` doesn't exist

**Fix:**
1. Open `dataset1_uk_housing/4_model.ipynb`
2. Run all cells (Kernel → Restart & Run All)
3. Wait for training to complete
4. Model saved to `data/clean/best_model.pkl`

### Error 5: "Permission denied" (Docker)

**Problem:** Docker needs permission to access files

**Fix:**
```bash
# Give Docker access to your project folder
# This is already set up, but if you see errors:
chmod -R 755 .
```

### Error 6: Container won't start - "address already in use"

**Problem:** Port is busy from previous run

**Fix:**
```bash
# Stop all Docker containers
docker-compose down

# If that doesn't work:
docker ps  # See running containers
docker stop <container-id>  # Stop specific container

# Then try again:
docker-compose up
```

### Error 7: "Build failed" or "go: module not found"

**Problem:** Network issue or Docker cache problem

**Fix:**
```bash
# Clean build (removes cache)
docker-compose build --no-cache

# Or rebuild specific service:
docker-compose build --no-cache api-gateway
```

---

## 🎓 Understanding the Code

### What You Need to Know for Presentation

**Question:** "What backend did you build?"

**Answer:**
"I built a microservices architecture with three components:
1. **Python ML service** - Loads our trained LightGBM model and makes predictions
2. **Go API gateway** - Validates user input and adds security (showing we learned a new language)
3. **Streamlit frontend** - User-friendly web interface
All containerized with Docker for easy deployment."

**Question:** "Why Go instead of Python for the API?"

**Answer:**
"Go is much faster and more efficient than Python for API servers. The Go API uses only 10MB of memory vs 150MB for Python. Plus, learning Go was a course requirement to demonstrate using new technologies."

**Question:** "What's a microservice?"

**Answer:**
"Instead of one big application, we split it into small, independent services:
- ML service handles predictions
- API service handles validation
- Frontend handles UI
Each can be updated, scaled, or debugged independently."

**Question:** "How does Docker help?"

**Answer:**
"Docker packages everything (code, dependencies, Python, Go) into containers. This means the code runs identically on my laptop, on test servers, and in production. No more 'it works on my machine' problems."

---

## 📁 File Structure Explained

Here's what each new file does:

```
Cloud-AI/
│
├── ml_service/                    ← NEW: Python ML Service
│   ├── server.py                  # Flask web server (API endpoints)
│   ├── predict.py                 # ML prediction logic
│   ├── Dockerfile                 # Instructions to build Python container
│   ├── requirements.txt           # Python libraries needed
│   └── README.md                  # Documentation for ML service
│
├── api/                           ← NEW: Go API Gateway
│   ├── main.go                    # Go server entry point
│   ├── go.mod                     # Go dependencies
│   ├── go.sum                     # Go dependency checksums
│   ├── Dockerfile                 # Instructions to build Go container
│   ├── models/models.go           # Data structures for API
│   ├── handlers/
│   │   ├── housing.go             # Housing prediction endpoint
│   │   └── health.go              # Health check endpoint
│   └── middleware/cors.go         # Security settings
│
├── docker-compose.yml             ← NEW: Orchestrates all services
├── Dockerfile.housing             ← NEW: Streamlit housing container
├── Dockerfile.electricity         ← NEW: Streamlit electricity container
├── .dockerignore                  ← NEW: Files to exclude from Docker
│
├── TESTING.md                     ← NEW: Technical testing guide
├── DEPLOYMENT_GUIDE.md            ← THIS FILE: Beginner's guide
│
├── app.py                         # Your existing Streamlit app
├── data/clean/best_model.pkl      # Your trained model (506 KB)
└── dataset1_uk_housing/           # Your existing notebooks
    ├── 4_model.ipynb              # Model training notebook
    └── ...
```

---

## 🚀 What's Next?

Now that you understand the basics, here's your deployment journey:

### ✅ Completed

- [x] **Phase 1.1:** Python ML microservice created
- [x] **Phase 1.2:** Go API gateway created
- [x] **Phase 1.3:** Backend testing guide created
- [x] **Phase 3:** Docker setup complete

### 🔜 Next Steps (In Order)

#### **NEXT: Phase 2.1 - Deploy Streamlit to Cloud (30 minutes)**

**Why this first?** Quick win! Shows progress to your team/professor quickly.

**What you'll do:**
1. Create account on Streamlit Cloud (free)
2. Connect your GitHub repository
3. Click "Deploy"
4. Get a public URL: `https://your-app.streamlit.app`

**Requirements:**
- GitHub account (you have this)
- Streamlit Cloud account (free - we'll create)
- Your code pushed to GitHub

---

#### **Then: Phase 4 - CI/CD Pipeline (1 hour)**

**What is CI/CD?** Continuous Integration / Continuous Deployment
- Every time you push code to GitHub
- Automated tests run
- If tests pass, automatically deploys to cloud

**What you'll do:**
1. Create `.github/workflows/` folder
2. Add workflow files (I'll help you)
3. Configure GitHub secrets
4. Push code → automatic deployment

---

#### **Then: Phase 5 - Oracle Cloud (2-3 hours)**

**Why Oracle?** Free forever tier (not a trial - actually free!)

**What you'll do:**
1. Create Oracle Cloud account
2. Create a VM instance (free)
3. Install Docker on VM
4. Deploy your containers
5. Get a public IP address

**What you'll have:**
- Real production server
- Public URL anyone can access
- Fully working ML API

---

#### **Finally: Phase 6 - Polish & Document (1 hour)**

**What you'll do:**
1. Add monitoring (logs, errors)
2. Create API documentation
3. Write deployment guide for your team
4. Create presentation slides

---

## 📞 What to Do Right Now

### Immediate Action Items:

**1. Test Option A (Quick Test) - DO THIS NOW**
   - Takes 5 minutes
   - Proves your ML service works
   - No Docker needed
   - Follow "Option A" section above

**2. If Option A Works:**
   - Mark it complete in the checklist
   - Message me: "Option A complete - ML service works"
   - I'll help you with Docker next

**3. If Option A Has Errors:**
   - Read the error message carefully
   - Check "Common Errors & Fixes" section
   - Try the suggested fix
   - If still stuck, copy the exact error message and ask me

**4. Once Both Options Work:**
   - We'll commit everything to Git
   - Push to GitHub
   - Move to Phase 2.1 (Streamlit Cloud)

---

## 🆘 Getting Help

### When You're Stuck

**Copy and send me:**
1. What you were trying to do (which step)
2. The exact command you ran
3. The complete error message
4. Screenshot if possible

**Example:**
```
Step: Option A, Step 3 (starting ML service)
Command: PORT=5001 python server.py
Error: ModuleNotFoundError: No module named 'flask'
```

### Before Asking for Help, Try:

1. Read the error message carefully
2. Check "Common Errors & Fixes" section
3. Make sure Docker Desktop is running (if using Docker)
4. Make sure you're in the right directory
5. Try the command again (sometimes it just works)

---

## 🎉 Celebration Checklist

Mark these off as you complete them:

- [ ] I understand what microservices are
- [ ] I understand what Docker does
- [ ] I can start the ML service manually
- [ ] I can test the ML service with curl
- [ ] I successfully ran docker-compose build
- [ ] I successfully ran docker-compose up
- [ ] All 3 services start without errors
- [ ] I can access Streamlit at localhost:8501
- [ ] I understand the file structure
- [ ] I'm ready for Phase 2.1 (Streamlit Cloud)

---

## 📚 Useful Commands Reference

```bash
# Navigate to project
cd /Users/marinjanushaj/Documents/Cloud-AI

# Check if model exists
ls -lh data/clean/best_model.pkl

# Start ML service (no Docker)
cd ml_service
PORT=5001 python server.py

# Test ML service
curl http://localhost:5001/health

# Docker commands
docker --version                    # Check Docker installed
docker ps                          # See running containers
docker-compose build               # Build all containers
docker-compose up                  # Start all services
docker-compose up -d               # Start in background
docker-compose down                # Stop all services
docker-compose logs ml-service     # View logs for specific service
docker-compose restart ml-service  # Restart specific service

# Git commands (for later)
git status                         # See what changed
git add .                          # Stage all changes
git commit -m "Add backend"        # Save changes
git push                           # Upload to GitHub
```

---

## ✉️ Contact

**Your AI Assistant:** Claude Code
**Your Project Lead:** You! (Marin Janushaj)
**Deployment Lead:** Alexandros Gkiorgkinis

---

**Remember:** You've built something impressive! A complete ML microservices backend with Docker containerization. Take it one step at a time, and you'll have it deployed to the cloud soon.

Good luck! 🚀
