# ⚡ UK Electricity Demand - Quick Deployment Guide

**For:** Eren (Dataset 2 - UK Electricity)
**By:** Team Yunus - Cloud AI Project
**Status:** Fast-track deployment (housing infrastructure already exists!)

---

## 🎯 Quick Summary

You're in luck! Since the housing model is already deployed, **90% of the infrastructure is ready**. You just need to:

1. ✅ Generate the missing model and data files (~15 min)
2. ✅ Add electricity prediction to ML service (~10 min)
3. ✅ Test locally (~10 min)
4. ✅ Build Docker container (~10 min)
5. ✅ Deploy to Oracle Cloud (~20 min)

**Total time: ~65 minutes** (vs several hours for housing!)

---

## 📊 Current Status

| Component | Status | What's There | What's Missing |
|-----------|--------|--------------|----------------|
| **Notebooks** | ✅ Complete | 6 notebooks in dataset2_uk_electricity/ | Nothing! |
| **Data Pipeline** | ⚠️ Ran | Notebooks executed | Parquet file not saved |
| **Model Training** | ⚠️ Trained | PyCaret model trained | PKL file not saved |
| **Streamlit App** | ✅ Ready | electricity_app.py (168 lines) | Just needs data/model |
| **Docker Setup** | ✅ Ready | Dockerfile.electricity exists | Service commented out |
| **ML Service** | ⚠️ Partial | Endpoint exists | Prediction logic = TODO |
| **Oracle VM** | ✅ Ready | SSH access working | Need to deploy electricity |

---

## ✅ Prerequisites (Already Done!)

These are complete from housing deployment:

- [x] Docker Desktop installed
- [x] Oracle Cloud VM provisioned
- [x] SSH access configured
- [x] Docker on VM installed
- [x] Project cloned to VM
- [x] Networks and volumes created
- [x] Port 5001 (ML service) and 8080 (API) working

**What you'll add:**
- Port 8502 for electricity Streamlit app
- Electricity model endpoint in ML service

---

## 🚀 Phase 1: Generate Missing Files (15 minutes)

The notebooks ran but didn't save the output files to the right places.

### Step 1.1: Generate Data File

```bash
cd /Users/marinjanushaj/Documents/Cloud-AI

# Open Jupyter
jupyter notebook
```

**In Jupyter:**
1. Open `dataset2_uk_electricity/2_clean.ipynb`
2. Find the last cell (should save parquet file)
3. **If this cell doesn't exist, add it:**

```python
# At the end of notebook 2_clean.ipynb
import os

# Ensure directory exists
os.makedirs('../data/clean', exist_ok=True)

# Save cleaned hourly data
hourly_df.to_parquet('../data/clean/uk_electricity_hourly.parquet', index=False)

print(f"✅ Saved: {len(hourly_df):,} rows to data/clean/uk_electricity_hourly.parquet")
print(f"File size: {os.path.getsize('../data/clean/uk_electricity_hourly.parquet') / 1024 / 1024:.1f} MB")
```

4. Run this cell (or Restart & Run All if unsure)
5. Wait ~2-3 minutes for it to save

**Verify it worked:**
```bash
# Back in terminal
ls -lh data/clean/uk_electricity_hourly.parquet

# Should show something like:
# -rw-r--r--  1 user  staff  45M Nov 24 19:00 data/clean/uk_electricity_hourly.parquet
```

✅ **Checkpoint:** Data file exists and is 30-50 MB

---

### Step 1.2: Generate Model File

**In Jupyter:**
1. Open `dataset2_uk_electricity/4_model.ipynb`
2. Scroll to the bottom - find where model is trained
3. **Add/verify this cell at the end:**

```python
# At the end of notebook 4_model.ipynb
import os
from pycaret.regression import save_model

# Create models directory
os.makedirs('../models', exist_ok=True)

# Save the best model
save_model(best_model, '../models/best_electricity_model_fast')

print("✅ Model saved to: models/best_electricity_model_fast.pkl")

# Also save to data/clean for ML service
os.makedirs('../data/clean', exist_ok=True)
save_model(best_model, '../data/clean/electricity_model')
print("✅ Model also saved to: data/clean/electricity_model.pkl")
```

4. Run this cell (if model is already trained, this should be instant)
5. If model isn't trained, you'll need to run the whole notebook (~10-20 min)

**Verify it worked:**
```bash
# Check both locations
ls -lh models/best_electricity_model_fast.pkl
ls -lh data/clean/electricity_model.pkl

# Both should exist and be ~500KB - 2MB
```

✅ **Checkpoint:** Model files exist in both locations

---

### Step 1.3: Update .gitignore

The electricity model should be committed (it's not too large):

```bash
cd /Users/marinjanushaj/Documents/Cloud-AI

# Check if models are already allowed
grep -E "electricity.*pkl" .gitignore || echo "Need to update .gitignore"
```

**If you see "Need to update .gitignore", open `.gitignore` and add:**

```
# Allow electricity models (they're small enough)
!data/clean/electricity_model.pkl
!models/best_electricity_model_fast.pkl
```

---

## 🔧 Phase 2: Implement ML Service (10 minutes)

The ML service has a TODO stub for electricity. Let's implement it!

### Step 2.1: Understand the Electricity Model

**What features does it need?**

Open `electricity_app.py` and look at lines ~85-95 to see feature engineering:

```python
# Features the model expects:
- hour (0-23)
- day_of_week (0-6)
- month (1-12)
- week (1-53)
- is_weekend (0 or 1)
- lag_1 (demand 1 hour ago)
- lag_24 (demand 24 hours ago)
- lag_168 (demand 1 week ago)
- rolling_mean_24 (24-hour moving average)
- rolling_mean_168 (weekly moving average)
```

**For API predictions**, we'll simplify to just datetime + optional features.

---

### Step 2.2: Update ml_service/predict.py

**Open:** `ml_service/predict.py`

**Find the `predict_electricity` method (around line 142-162)** - it currently says:

```python
def predict_electricity(self, features: Dict[str, Any]) -> Dict[str, Any]:
    if self.electricity_model is None:
        raise ValueError("Electricity model not loaded")

    try:
        # TODO: Implement electricity prediction logic
        raise NotImplementedError("Electricity prediction not yet implemented")
```

**Replace with:**

```python
def predict_electricity(self, year: int, month: int, day: int, hour: int = 12) -> Dict[str, Any]:
    """
    Predict UK electricity demand

    Args:
        year: Year (2025+)
        month: Month (1-12)
        day: Day of month (1-31)
        hour: Hour of day (0-23), default 12

    Returns:
        Dictionary with demand prediction in MW
    """
    if self.electricity_model is None:
        raise ValueError("Electricity model not loaded")

    try:
        from datetime import datetime

        # Create datetime
        dt = datetime(year, month, day, hour)

        # Feature engineering (matching training)
        features_df = pd.DataFrame([{
            'hour': dt.hour,
            'day_of_week': dt.weekday(),
            'month': dt.month,
            'week': dt.isocalendar()[1],
            'is_weekend': 1 if dt.weekday() >= 5 else 0,
            # For lags, use average historical values as baseline
            'lag_1': 35000,      # Typical UK demand
            'lag_24': 35000,
            'lag_168': 35000,
            'rolling_mean_24': 35000,
            'rolling_mean_168': 35000
        }])

        # Make prediction
        prediction = self.electricity_model.predict(features_df)[0]

        return {
            "demand_mw": round(float(prediction), 2),
            "datetime": dt.isoformat(),
            "model": "PyCaret Regression",
            "note": "Lag features use historical averages (no recent data available)"
        }

    except Exception as e:
        logger.error(f"Electricity prediction error: {e}")
        raise
```

**Save the file.**

---

### Step 2.3: Update ml_service/server.py

**Open:** `ml_service/server.py`

**Find the `/predict-electricity` endpoint (around line 126-136)** - currently returns 501.

**Replace the entire function with:**

```python
@app.route('/predict-electricity', methods=['POST'])
def predict_electricity():
    """
    Predict UK electricity demand

    Expected JSON body:
    {
        "year": 2025,
        "month": 1,
        "day": 15,
        "hour": 12  // optional, defaults to 12
    }
    """
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['year', 'month', 'day']
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            return jsonify({
                "error": f"Missing required fields: {', '.join(missing_fields)}",
                "required_fields": required_fields
            }), 400

        # Optional hour field
        hour = data.get('hour', 12)

        # Validate ranges
        if not (2020 <= data['year'] <= 2030):
            return jsonify({"error": "Year must be between 2020 and 2030"}), 400

        if not (1 <= data['month'] <= 12):
            return jsonify({"error": "Month must be between 1 and 12"}), 400

        if not (1 <= data['day'] <= 31):
            return jsonify({"error": "Day must be between 1 and 31"}), 400

        if not (0 <= hour <= 23):
            return jsonify({"error": "Hour must be between 0 and 23"}), 400

        # Make prediction
        result = predictor.predict_electricity(
            year=data['year'],
            month=data['month'],
            day=data['day'],
            hour=hour
        )

        return jsonify(result), 200

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        return jsonify({
            "error": "Prediction failed",
            "details": str(e)
        }), 500
```

**Save the file.**

---

## 🧪 Phase 3: Local Testing (10 minutes)

Test everything works before Docker.

### Step 3.1: Test ML Service Locally

```bash
cd /Users/marinjanushaj/Documents/Cloud-AI/ml_service

# Start the service
PORT=5001 /Users/marinjanushaj/Documents/Cloud-AI/venv311/bin/python server.py
```

**Expected output:**
```
✓ Loaded housing model: LightGBM
✓ Loaded electricity model
 * Running on http://127.0.0.1:5001
```

**In a NEW terminal, test the electricity endpoint:**

```bash
# Test electricity prediction
curl -X POST http://localhost:5001/predict-electricity \
  -H "Content-Type: application/json" \
  -d '{"year":2025,"month":1,"day":15,"hour":14}'

# Should return:
# {"demand_mw":35234.56,"datetime":"2025-01-15T14:00:00","model":"PyCaret Regression",...}
```

✅ **Checkpoint:** Electricity prediction returns a demand value

Press `Ctrl+C` to stop the ML service.

---

### Step 3.2: Test Streamlit App Locally

```bash
cd /Users/marinjanushaj/Documents/Cloud-AI

# Run electricity app
/Users/marinjanushaj/Documents/Cloud-AI/venv311/bin/streamlit run electricity_app.py --server.port=8502
```

**Expected:**
- App opens in browser at http://localhost:8502
- You see "UK Electricity Demand Forecasting" interface
- Can select forecast settings and generate predictions

**Try making a prediction:**
1. Select "24 hours" forecast
2. Click "Generate Forecast"
3. Should see a chart with predicted demand

✅ **Checkpoint:** Electricity app runs and shows forecasts

Press `Ctrl+C` to stop Streamlit.

---

## 🐳 Phase 4: Docker Deployment (10 minutes)

### Step 4.1: Update docker-compose.yml

**Open:** `docker-compose.yml`

**Find the commented electricity service** (around line 74-89) and **uncomment it:**

```yaml
  electricity-app:
    build:
      context: .
      dockerfile: Dockerfile.electricity
    container_name: electricity-app
    ports:
      - "8502:8502"
    volumes:
      - ./data/clean:/app/data/clean:ro
      - ./models:/app/models:ro
    networks:
      - frontend
    depends_on:
      - ml-service
    restart: unless-stopped
```

**Save the file.**

---

### Step 4.2: Build Electricity Container

```bash
cd /Users/marinjanushaj/Documents/Cloud-AI

# Build just the electricity service
docker-compose build electricity-app

# Should take 3-5 minutes (Python + dependencies)
```

**Expected output:**
```
Successfully built electricity-app
```

---

### Step 4.3: Start All Services

```bash
# Start everything (housing + electricity)
docker-compose up -d

# Check all 4 containers are running
docker-compose ps

# Should show:
# ml-service      Up
# api-gateway     Up
# housing-app     Up
# electricity-app Up
```

---

### Step 4.4: Test All Endpoints

```bash
# Test ML service has both models
curl http://localhost:5001/health

# Test housing (should still work)
curl -X POST http://localhost:8080/api/v1/predict/housing \
  -H "Content-Type: application/json" \
  -d '{"property_type":"T","is_new":"N","duration":"F","county":"GREATER LONDON","year":2016,"month":6}'

# Test electricity
curl -X POST http://localhost:5001/predict-electricity \
  -H "Content-Type: application/json" \
  -d '{"year":2025,"month":1,"day":15,"hour":14}'

# Test Streamlit apps in browser:
open http://localhost:8501  # Housing
open http://localhost:8502  # Electricity
```

✅ **Checkpoint:** All 4 services running, both Streamlit apps accessible

---

## ☁️ Phase 5: Oracle Cloud Deployment (20 minutes)

Now deploy to your existing Oracle VM!

### Step 5.1: Commit and Push Changes

```bash
cd /Users/marinjanushaj/Documents/Cloud-AI

# Check what changed
git status

# Add all electricity files
git add .
git commit -m "Add electricity model deployment

- Generated electricity model and data files
- Implemented ML service electricity prediction
- Updated docker-compose to include electricity-app
- Tested locally - all services working

Ready for Oracle Cloud deployment"

git push origin main
```

---

### Step 5.2: SSH to Oracle VM

```bash
# SSH to your VM (use your saved connection)
ssh -i ~/.ssh/your-key ubuntu@158.180.57.220

# Or if you saved it as an alias:
ssh oracle-vm
```

---

### Step 5.3: Pull Latest Changes

```bash
# On the VM
cd ~/Cloud-AI

# Pull latest code
git pull origin main

# You should see:
# - Updated docker-compose.yml
# - New electricity model files
# - Updated ML service code
```

---

### Step 5.4: Build on VM

```bash
# Still on VM
cd ~/Cloud-AI

# Stop current services
docker compose down

# Build electricity service (uses swap space - takes 5-10 min)
docker compose build electricity-app

# If it hangs, you may need to build services one by one (see DEPLOYMENT_GUIDE.md)
```

**Alternative if hanging:**
```bash
# Build services one at a time
docker compose build ml-service
docker compose build api-gateway
docker compose build housing-app
docker compose build electricity-app
```

---

### Step 5.5: Start All Services on VM

```bash
# Start all 4 services
docker compose up -d

# Check status
docker compose ps

# Should show all 4 running:
# ml-service, api-gateway, housing-app, electricity-app
```

---

### Step 5.6: Configure Firewall (If Needed)

If electricity port 8502 isn't open:

```bash
# On VM - open port 8502
sudo ufw allow 8502/tcp
sudo ufw status
```

**In Oracle Cloud Console:**
1. Go to your instance details
2. Click on the subnet
3. Click on the default security list
4. Add Ingress Rule:
   - Source: 0.0.0.0/0
   - Destination Port: 8502
   - Description: Electricity Streamlit App

---

### Step 5.7: Test from Your Computer

```bash
# Test electricity app (from your Mac)
curl http://158.180.57.220:5001/predict-electricity \
  -H "Content-Type: application/json" \
  -d '{"year":2025,"month":1,"day":15,"hour":14}'

# Test in browser:
open http://158.180.57.220:8501  # Housing app
open http://158.180.57.220:8502  # Electricity app
```

✅ **Checkpoint:** Both apps accessible from internet!

---

## 📋 Phase 6: Testing Checklist

Mark each as you test:

### Local Docker Testing
- [ ] ML service loads both models (check /health)
- [ ] Housing prediction still works
- [ ] Electricity prediction returns demand values
- [ ] Housing Streamlit app loads (8501)
- [ ] Electricity Streamlit app loads (8502)
- [ ] Both apps can make predictions

### Oracle VM Testing
- [ ] All 4 containers running (`docker compose ps`)
- [ ] ML service health check works (port 5001)
- [ ] API gateway health check works (port 8080)
- [ ] Housing app accessible from internet
- [ ] Electricity app accessible from internet
- [ ] Predictions work from public URLs
- [ ] No port conflicts or errors in logs

### Integration Testing
- [ ] Housing and electricity don't interfere with each other
- [ ] Can use both apps simultaneously
- [ ] VM performance is acceptable (check with `htop`)
- [ ] Logs show no errors (`docker compose logs`)

---

## ❌ Troubleshooting

### Issue: Model file not found

**Symptom:** ML service logs show "Electricity model not found"

**Fix:**
```bash
# Check if file exists
ls -lh data/clean/electricity_model.pkl

# If missing, re-run notebook 4_model.ipynb and save model
# Then rebuild Docker container
```

---

### Issue: Data file not found

**Symptom:** Electricity app says "File not found: uk_electricity_hourly.parquet"

**Fix:**
```bash
# Check if file exists
ls -lh data/clean/uk_electricity_hourly.parquet

# If missing, re-run notebook 2_clean.ipynb
# Then restart Docker containers
```

---

### Issue: Port 8502 already in use

**Symptom:** "Port 8502 is already allocated"

**Fix:**
```bash
# Find what's using the port
lsof -i :8502

# Kill the process or change electricity port in docker-compose.yml
```

---

### Issue: Prediction returns 501 Not Implemented

**Symptom:** Electricity endpoint still says not implemented

**Fix:**
- Make sure you updated `ml_service/server.py` with new prediction code
- Rebuild ML service container: `docker compose build ml-service`
- Restart: `docker compose up -d`

---

### Issue: VM out of memory during build

**Symptom:** Build hangs or crashes on Oracle VM

**Fix:**
```bash
# Check swap is enabled
free -h

# If no swap, add it:
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Then rebuild
```

---

### Issue: Features don't match model training

**Symptom:** "Feature names don't match" or "Wrong number of features"

**Fix:**
- Check what features the PyCaret model expects
- Update `predict_electricity()` to match exactly
- Make sure feature engineering is identical to training

---

## 🎓 Understanding the Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    YOUR DEPLOYED SYSTEM                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐      ┌──────────────┐      ┌───────────┐ │
│  │  Housing     │      │  Go API      │      │  Python   │ │
│  │  Streamlit   │──────│  Gateway     │──────│  ML       │ │
│  │  (8501)      │      │  (8080)      │      │  Service  │ │
│  └──────────────┘      └──────────────┘      │  (5001)   │ │
│         │                     │               │           │ │
│         │                     │               │ Housing   │ │
│         │                     │               │ Model     │ │
│  ┌──────────────┐            │               │           │ │
│  │  Electricity │            │               │ Electricity│ │
│  │  Streamlit   │────────────┘               │ Model     │ │
│  │  (8502)      │                            └───────────┘ │
│  └──────────────┘                                   │       │
│         │                                           │       │
│    Users access                              Both models    │
│    both apps                                 in one service │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Key points:**
- Both Streamlit apps talk to the **same ML service** (port 5001)
- Housing goes through API gateway for validation
- Electricity talks directly to ML service (simpler)
- All running in Docker containers on Oracle Cloud
- Both models loaded in memory in the ML service

---

## 📊 Comparison: Housing vs Electricity Deployment

| Aspect | Housing (Dataset 1) | Electricity (Dataset 2) |
|--------|---------------------|-------------------------|
| **Complexity** | High (first deployment) | Low (infrastructure exists) |
| **Model Type** | LightGBM (scikit-learn) | PyCaret Regression |
| **Model Size** | 506 KB | ~500 KB - 2 MB |
| **Data Size** | 1 GB parquet | 30-50 MB parquet |
| **API Flow** | Through API Gateway (Go) | Direct to ML service |
| **Features** | 7 categorical + encoded | 10 time-based features |
| **Streamlit Port** | 8501 | 8502 |
| **Prediction Type** | Single prediction | Recursive forecasting |
| **Time to Deploy** | 3-4 hours | ~65 minutes |

---

## 🎯 Success Criteria

You'll know everything is working when:

✅ **Local:**
- `docker-compose ps` shows 4 services running
- Both Streamlit apps load in browser (8501 and 8502)
- Predictions work in both apps
- No errors in `docker-compose logs`

✅ **Cloud:**
- VM is accessible via SSH
- Both apps accessible from your computer
- Other people can access both public URLs
- Services restart automatically if VM reboots

✅ **Presentation Ready:**
- Two live demos (housing + electricity)
- Can explain the architecture
- Monitoring/logs available if asked
- GitHub shows complete project

---

## 🚀 What's Next (Optional)

### Add More Features:
1. **Historical data comparison** - Show actual vs predicted
2. **Batch predictions** - Upload CSV of dates
3. **Model metrics dashboard** - Show R², MAE, etc.
4. **Alert system** - Notify if demand is unusually high/low

### Improve ML Service:
1. **Use actual lags** - Store recent predictions for better lag features
2. **Confidence intervals** - Add prediction uncertainty
3. **Model versioning** - A/B test different models
4. **Caching** - Speed up repeat predictions

### Add to CI/CD:
1. Update GitHub Actions to test electricity endpoints
2. Auto-deploy electricity on successful tests
3. Add electricity to monitoring dashboard

---

## 💡 Pro Tips

**For Presentations:**
- "We deployed TWO ML models (housing + electricity) using microservices"
- "Both use the same ML service but serve different use cases"
- "Housing uses validated API, electricity is direct for speed"
- "All containerized with Docker, running on Oracle Cloud"

**For Debugging:**
```bash
# View logs for specific service
docker compose logs -f electricity-app

# Check resource usage
docker stats

# Restart just one service
docker compose restart electricity-app

# Rebuild after code changes
docker compose build electricity-app && docker compose up -d
```

---

## 📞 Need Help?

**Common Commands:**
```bash
# Status of services
docker compose ps

# View all logs
docker compose logs

# Restart everything
docker compose restart

# Stop everything
docker compose down

# Full rebuild
docker compose down && docker compose build && docker compose up -d
```

**VM Access:**
```bash
ssh -i ~/.ssh/your-key ubuntu@158.180.57.220
```

**Check VM Resources:**
```bash
free -h        # RAM usage
df -h          # Disk space
docker stats   # Container resources
```

---

## ✅ Final Checklist

Before marking this complete:

- [ ] Notebooks 2 and 4 ran successfully
- [ ] Model file exists: `data/clean/electricity_model.pkl`
- [ ] Data file exists: `data/clean/uk_electricity_hourly.parquet`
- [ ] ML service updated with prediction logic
- [ ] Tested locally - ML service works
- [ ] Tested locally - Streamlit app works
- [ ] Docker compose includes electricity service
- [ ] Built electricity Docker container
- [ ] All 4 services running locally
- [ ] Committed changes to Git
- [ ] Pushed to GitHub
- [ ] Pulled on Oracle VM
- [ ] Built on Oracle VM
- [ ] All 4 services running on VM
- [ ] Port 8502 open in firewall
- [ ] Housing app accessible from internet
- [ ] Electricity app accessible from internet
- [ ] Both apps making predictions
- [ ] Tested by team member
- [ ] Ready for presentation

---

**Good luck! The hard work is done - now you're just replicating success! ⚡🎉**

---

*Generated by Claude Code for Team Yunus Cloud AI Project*
