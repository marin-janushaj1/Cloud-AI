# Team Yunus — Cloud AI (Machine Learning Project)

**Team Members:**
- **Marin Janushaj** - Dataset 1: UK Housing Price Prediction
- **Yunus Eren Ertaş** - Dataset 2: UK Electricity Consumption Analysis

**Course:** Cloud & AI
**Academic Year:** 2025
**Institution:** Thomas More University - Geel

---

## 📋 Project Overview

This repository contains **two comprehensive machine learning projects** demonstrating end-to-end ML workflows from data acquisition to production deployment.

### 🏡 Dataset 1: UK Housing Price Prediction
**Lead:** Marin Janushaj

An end-to-end machine learning project predicting UK house prices from 22.4M+ transactions (1995-2017)

### 🎯 Project Overview

This project demonstrates the complete machine learning workflow from data acquisition to production deployment:
- **Dataset:** 22.4 million UK housing transactions
- **Goal:** Predict property prices based on type, location, age, tenure, and temporal features
- **Approaches:** Manual training, automated ML (PyCaret), and cloud training (AWS SageMaker)
- **Deployment:** Production-ready Streamlit web application with API backend

### 📊 Key Results

| Metric | Value |
|--------|-------|
| **Best Model** | LightGBM |
| **Test R² Score** | 0.446 |
| **Mean Absolute Error** | £122,353 |
| **RMSE** | £473,417 |
| **MAPE** | 69.83% |
| **Training Data** | 22.4M records (full dataset) |
| **Training Time** | 26 seconds |

**Why LightGBM won?**
- Trained on full dataset (vs. sampled data in AutoML)
- Excellent handling of categorical features
- Fast training and inference
- Superior generalization to test set

### ⚡ Dataset 2: UK Electricity Consumption Analysis
**Lead:** Yunus Eren Ertaş

Analysis and prediction of UK electricity consumption patterns, exploring temporal trends, regional variations, and forecasting future demand.

- **Dataset:** UK electricity consumption data
- **Goal:** Predict electricity demand and analyze consumption patterns
- **Approaches:** Time series analysis, regression models, and forecasting techniques
- **Key Features:** Temporal patterns, regional analysis, demand forecasting

**Status:** [In Progress/Complete]

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- 16GB+ RAM (for full dataset processing)
- Virtual environment recommended

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/cloud-ai-project.git
cd cloud-ai-project

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Run the Web Application

```bash
# Start Dataset 1 (UK Housing) Streamlit app
streamlit run app.py

# Start Dataset 2 (UK Electricity) Streamlit app
streamlit run electricity_app.py

# Apps will open in browser at http://localhost:8501
```

### Notebook Workflow

**Dataset 1 - UK Housing (Marin Janushaj):**
```bash
jupyter notebook dataset1_uk_housing/1_load.ipynb           # Data acquisition
jupyter notebook dataset1_uk_housing/2_clean.ipynb          # Data cleaning
jupyter notebook dataset1_uk_housing/3_eda.ipynb            # Exploratory analysis
jupyter notebook dataset1_uk_housing/4_model.ipynb          # Manual model training
jupyter notebook dataset1_uk_housing/4.5_pycaret_comparison.ipynb  # AutoML
jupyter notebook dataset1_uk_housing/4.7_sagemaker_ready.ipynb     # AWS SageMaker
jupyter notebook dataset1_uk_housing/6_model_comparison.ipynb      # Comparison
jupyter notebook dataset1_uk_housing/5_deploy.ipynb        # Deployment guide
```

**Dataset 2 - UK Electricity (Yunus Eren Ertaş):**
```bash
jupyter notebook dataset2_uk_electricity/1_combine.ipynb    # Data combination
jupyter notebook dataset2_uk_electricity/2_clean.ipynb      # Data cleaning
jupyter notebook dataset2_uk_electricity/3_eda.ipynb        # Exploratory analysis
jupyter notebook dataset2_uk_electricity/4_model.ipynb      # Model training
jupyter notebook dataset2_uk_electricity/5_deploy.ipynb     # Deployment
```

---

## 📚 Project Notebooks

### 1. Data Loading (`1_load.ipynb`)
- Downloads UK housing dataset from Kaggle
- Initial data exploration (22.4M records, 2GB)
- Dataset structure analysis
- Memory optimization strategies

### 2. Data Cleaning (`2_clean.ipynb`)
- Column renaming (lowercase, snake_case)
- Missing value analysis and imputation
- Outlier detection and handling
- Categorical encoding preparation
- Data type optimization
- **Output:** `uk_housing_clean.parquet` (efficient storage)

### 3. Exploratory Data Analysis (`3_eda.ipynb`)
- Price distribution and trends over time
- Geographic analysis (county-level patterns)
- Property type analysis
- Temporal patterns (seasonality, market trends)
- Correlation analysis
- **Key Findings:**
  - London properties 3x more expensive than national average
  - Strong upward price trend 1995-2007, crash in 2008
  - Property type significantly impacts price
  - Freehold vs leasehold price differentials

### 4. Model Training (`4_model.ipynb`)
Models trained and compared:
1. **Linear Regression** (baseline) - R² = 0.244
2. **Random Forest** - R² = 0.400
3. **XGBoost** - R² = 0.441
4. **LightGBM** - R² = 0.446 ⭐ **WINNER**

**Approach:**
- Temporal train-test split (1995-2015 train, 2016-2017 test)
- Log transformation of target variable
- Target encoding for county (high cardinality)
- One-hot encoding for property type, tenure
- 5-fold cross-validation
- **Output:** `best_model.pkl` (LightGBM with preprocessing pipeline)

### 5. PyCaret AutoML (`4.5_pycaret_comparison.ipynb`)
- Automated comparison of 15+ ML algorithms
- Hyperparameter tuning for top 3 models
- Ensemble models (blending + stacking)
- **Best AutoML:** Extra Trees (R² = 0.238)
- **Limitation:** Trained on 500K sample (2.2%) for speed
- **Conclusion:** Full dataset training beats AutoML on sampled data

### 6. AWS SageMaker Training (`4.7_sagemaker_ready.ipynb`)
- Cloud-based model training on AWS SageMaker
- Automated hyperparameter tuning (10 training jobs)
- Bayesian optimization for parameter search
- **Results:** XGBoost R² = 0.440
- **Infrastructure:** ml.m5.xlarge instances
- **Cost:** ~$1-2 (AWS Free Tier eligible)
- **Key Advantage:** Scalable to any dataset size

### 7. Model Comparison (`6_model_comparison.ipynb`)
Comprehensive comparison of all approaches:
- Manual training results
- PyCaret AutoML results
- AWS SageMaker results
- Visualizations and performance metrics
- **Conclusion:** LightGBM (manual) is the best overall model

### 8. Deployment Guide (`5_deploy.ipynb`)
- Production prediction function
- Flask API example
- Docker containerization
- CI/CD pipeline (GitHub Actions)
- Monitoring and maintenance strategies

---

## 🌐 Web Application

### Features
- **Interactive UI:** User-friendly Streamlit interface
- **Real-time Predictions:** Instant price estimates
- **Confidence Intervals:** 95% prediction intervals using MAE
- **Model Metrics:** Transparent performance display
- **Visualizations:** Interactive Plotly charts
- **Input Validation:** Comprehensive error handling

### Usage

1. Select property characteristics:
   - Type (Detached, Semi-Detached, Terraced, Flat, Other)
   - Age (New Build vs Established)
   - Tenure (Freehold vs Leasehold)
   - County/Region
   - Year of transfer
   - Month and quarter

2. Click "Predict House Price"

3. View results:
   - Predicted price
   - Confidence interval
   - Price visualization
   - Technical details (expandable)

### Screenshot
![Streamlit App](https://via.placeholder.com/800x400?text=Streamlit+App+Screenshot)

---

## 🔧 API Documentation

### Flask API Endpoint

Start the API server:
```bash
python dataset1_uk_housing/api_example.py
```

### Endpoints

**Health Check**
```bash
GET /health
```
Response:
```json
{
  "status": "ok",
  "model": "LightGBM"
}
```

**Predict Price**
```bash
POST /predict
Content-Type: application/json

{
  "property_type": "F",
  "is_new": "Y",
  "duration": "L",
  "county": "GREATER LONDON",
  "year": 2016,
  "month": 1,
  "quarter": 1
}
```

Response:
```json
{
  "price": 680122,
  "price_log": 13.4300,
  "confidence_lower": 435416,
  "confidence_upper": 925122,
  "model": "LightGBM"
}
```

### Parameter Reference

| Parameter | Values | Description |
|-----------|--------|-------------|
| `property_type` | D, S, T, F, O | Detached, Semi, Terraced, Flat, Other |
| `is_new` | Y, N | New build or established |
| `duration` | F, L, U | Freehold, Leasehold, Unknown |
| `county` | String | UK county name (uppercase) |
| `year` | 1995-2025 | Year of transfer |
| `month` | 1-12 | Month of transfer |
| `quarter` | 1-4 | Quarter of year |

---

## 🐳 Docker Deployment

### Build Image
```bash
docker build -t uk-housing-predictor .
```

### Run Container
```bash
docker run -p 5000:5000 uk-housing-predictor
```

### Docker Compose
```bash
docker-compose up
```

### Environment Variables
```bash
MODEL_PATH=/app/data/clean/best_model.pkl
PORT=5000
DEBUG=False
```

---

## ☁️ Cloud Deployment

### Streamlit Cloud
1. Push code to GitHub
2. Connect repository at [share.streamlit.io](https://share.streamlit.io)
3. Configure `requirements.txt` and Python version
4. Deploy with one click

**Live Demo:** [Coming Soon]

### AWS SageMaker
- Notebook training: `4.7_sagemaker_ready.ipynb`
- Automated hyperparameter tuning
- Model artifacts stored in S3
- (Endpoint deployment requires additional IAM permissions)

### Heroku
```bash
heroku create uk-housing-predictor
git push heroku main
```

### Oracle Cloud (Free Tier)
- Always Free compute instances
- Detailed guide: `AWS_SETUP_GUIDE.md`

---

## 📊 Model Comparison Summary

| Approach | Best Model | R² | MAE (£) | Training Data | Time |
|----------|-----------|-----|---------|--------------|------|
| **Manual** | LightGBM | 0.446 | 122,353 | 22.4M (100%) | 26s |
| **AutoML** | Extra Trees | 0.238 | 119,250 | 500K (2.2%) | 45s |
| **Cloud** | XGBoost (SageMaker) | 0.440 | 123,000 | Variable | 50min |

**Winner:** LightGBM (Manual Training)

**Key Insight:** More training data trumps algorithm sophistication. LightGBM on full dataset outperformed AutoML ensembles on sampled data.

---

## 📁 Repository Structure

```
cloud-ai-project/
│
├── data/
│   ├── raw/                          # Original Kaggle downloads (gitignored)
│   └── clean/                        # Processed data
│       ├── uk_housing_clean.parquet  # Main dataset (gitignored if >100MB)
│       └── best_model.pkl            # Trained model (gitignored if >100MB)
│
├── dataset1_uk_housing/
│   ├── 1_load.ipynb                  # Data acquisition
│   ├── 2_clean.ipynb                 # Data cleaning
│   ├── 3_eda.ipynb                   # Exploratory analysis
│   ├── 4_model.ipynb                 # Manual model training
│   ├── 4.5_pycaret_comparison.ipynb  # AutoML comparison
│   ├── 4.7_sagemaker_ready.ipynb     # AWS SageMaker training
│   ├── 6_model_comparison.ipynb      # Comprehensive comparison
│   ├── 5_deploy.ipynb                # Deployment guide
│   ├── api_example.py                # Flask API code
│   ├── Dockerfile.example            # Docker configuration
│   ├── docker-compose.example.yml    # Docker Compose config
│   └── .github/workflows/            # CI/CD pipelines
│       └── deploy.example.yml
│
├── dataset2_uk_electricity/          # Project 2 - UK Electricity (Yunus)
│   ├── 1_combine.ipynb               # Data combination
│   ├── 2_clean.ipynb                 # Data cleaning
│   ├── 3_eda.ipynb                   # Exploratory analysis
│   ├── 4_model.ipynb                 # Model training
│   └── 5_deploy.ipynb                # Deployment guide
│
├── app.py                            # Streamlit app (Dataset 1)
├── electricity_app.py                # Streamlit app (Dataset 2)
├── requirements.txt                  # Python dependencies
├── README.md                         # This file
├── NEXT_STEPS.md                     # Development roadmap
├── AWS_SETUP_GUIDE.md               # AWS configuration guide
└── .gitignore                        # Git ignore rules
```

---

## 🛠️ Technologies Used

### Machine Learning
- **scikit-learn** 1.5.2 - Core ML algorithms
- **XGBoost** 2.1.3 - Gradient boosting
- **LightGBM** 4.5.0 - Fast gradient boosting
- **PyCaret** 3.3.2 - Automated ML

### Data Processing
- **pandas** 2.2.3 - Data manipulation
- **numpy** 1.26.4 - Numerical computing
- **pyarrow** 22.0.0 - Efficient file I/O
- **category-encoders** 2.8.1 - Advanced encoding

### Visualization
- **matplotlib** 3.10.7 - Static plots
- **seaborn** 0.13.2 - Statistical visualizations
- **plotly** 6.1.0 - Interactive charts

### Web & Deployment
- **Streamlit** 1.41.1 - Web application
- **Flask** 3.1.2 - REST API
- **boto3** 1.40.69 - AWS SDK
- **sagemaker** 3.0.1 - AWS SageMaker

### Development
- **Jupyter** 7.5.0 - Interactive notebooks
- **Docker** - Containerization
- **GitHub Actions** - CI/CD

---

## 📈 Future Improvements

### Model Enhancements
- [ ] Add property size (square footage) if available
- [ ] Incorporate latitude/longitude for geospatial features
- [ ] Time series modeling for price trends
- [ ] Ensemble LightGBM + XGBoost predictions
- [ ] Neural network experiments

### Feature Engineering
- [ ] Distance to London/major cities
- [ ] Local amenities (schools, transport)
- [ ] Economic indicators (GDP, unemployment)
- [ ] Mortgage rate correlations

### Deployment
- [x] Streamlit web app
- [ ] Streamlit Cloud deployment
- [ ] RESTful API
- [ ] Docker containerization
- [ ] CI/CD pipeline
- [ ] Model monitoring and retraining

### Documentation
- [x] Comprehensive README
- [ ] API documentation (Swagger/OpenAPI)
- [ ] Model cards (performance, limitations)
- [ ] User guide

---

## 🎓 Academic Deliverables

### Completed ✅
- [x] Data cleaning and EDA
- [x] Multiple model training approaches
- [x] PyCaret automated ML
- [x] AWS SageMaker cloud training
- [x] Model comparison and evaluation
- [x] Streamlit web application
- [x] Deployment infrastructure (Docker, API)

### For Presentation (Nov 28, 2025)
- Who's who in Team Yunus
- EDA key findings
- Model comparison results
- Live demo or screenshots
- Q&A preparation

---

## 👥 Team Contributions

### 🏡 Dataset 1: UK Housing Price Prediction
**Lead:** Marin Janushaj
- Complete data pipeline (loading, cleaning, EDA)
- Model training (Manual, AutoML, AWS SageMaker)
- Hyperparameter tuning and optimization
- Model comparison and evaluation
- Streamlit web application development
- Documentation and notebooks

### ⚡ Dataset 2: UK Electricity Consumption Analysis
**Lead:** Yunus Eren Ertaş
- Data combination and preprocessing
- Time series analysis and EDA
- Model training and forecasting
- Pattern recognition and insights
- Electricity consumption Streamlit app
- Dataset 2 documentation

### 🚀 Deployment, Frontend & Backend
**Lead:** Marin Janushaj / Yunus Eren Ertas
- Production deployment infrastructure
- Frontend design and user experience
- Backend API development
- Docker containerization
- CI/CD pipeline setup
- System integration and testing
- Cloud deployment (AWS, Streamlit Cloud)

*Note: This is a collaborative effort - all team members contributed to project planning, presentations, and overall success!*

---

## 📄 License

This project is for academic purposes only.

**Data Source:** [UK Housing Price Paid Data](https://www.kaggle.com/datasets/hm-land-registry/uk-housing-prices-paid) (CC0: Public Domain)

---

## 🔗 Links

- **Dataset:** [Kaggle - UK Housing Prices](https://www.kaggle.com/datasets/hm-land-registry/uk-housing-prices-paid)
- **AWS SageMaker:** [Documentation](https://docs.aws.amazon.com/sagemaker/)
- **Streamlit:** [Documentation](https://docs.streamlit.io/)
- **PyCaret:** [Documentation](https://pycaret.gitbook.io/)

---

## 📞 Contact

**Team Yunus** - Cloud & AI Project 2025

For questions or feedback, please reach out to team members or open an issue on GitHub.

---

**Last Updated:** November 2025
**Status:** ✅ Complete - Ready for Presentation
