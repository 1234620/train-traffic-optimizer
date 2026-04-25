<p align="center">
  <h1 align="center">RAILWAY TRAFFIC OPTIMIZATION SYSTEM</h1>
</p>

<p align="center">
  <i>Optimizing Rail Networks, Predicting Failures, Maximizing Throughput</i>
</p>

<p align="center">
  <img src="https://img.shields.io/github/last-commit/1234620/train-traffic-optimizer?style=flat-square&color=orange" alt="Last Commit" />
  <img src="https://img.shields.io/github/languages/top/1234620/train-traffic-optimizer?style=flat-square&color=blue" alt="Top Language" />
  <img src="https://img.shields.io/github/languages/count/1234620/train-traffic-optimizer?style=flat-square&color=green" alt="Languages" />
  <img src="https://img.shields.io/github/license/1234620/train-traffic-optimizer?style=flat-square&color=yellow" alt="License" />
  <img src="https://img.shields.io/github/repo-size/1234620/train-traffic-optimizer?style=flat-square&color=red" alt="Repo Size" />
</p>

<p align="center">
  <i>Built with the tools and technologies:</i>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white" alt="scikit-learn" />
  <img src="https://img.shields.io/badge/NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white" alt="NumPy" />
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker" />
  <br/>
  <img src="https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=next.js&logoColor=white" alt="Next.js" />
  <img src="https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react&logoColor=black" alt="React" />
  <img src="https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white" alt="HTML5" />
  <img src="https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white" alt="CSS3" />
  <img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black" alt="JavaScript" />
</p>

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [API Reference](#api-reference)
- [Machine Learning Models](#machine-learning-models)
- [Frontend](#frontend)
- [Real-time Updates](#real-time-updates)
- [Development](#development)
- [Troubleshooting](#troubleshooting)
- [Performance Metrics](#performance-metrics)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

---

## Overview

A comprehensive AI-powered railway traffic optimization system with machine learning-based predictive maintenance, real-time monitoring, and intelligent decision-making capabilities. The platform integrates advanced ML models with a modern web interface to deliver actionable insights for railway network management.

---

## Features

### AI and Machine Learning
- **Predictive Maintenance** -- ML models with 99% accuracy for equipment failure prediction
- **Real-time Risk Assessment** -- Continuous monitoring of train and track conditions
- **Intelligent Optimization** -- AI-driven traffic flow optimization algorithms
- **Heuristic Fallback** -- Rule-based system when ML models are unavailable

### Real-time Monitoring
- **Live Train Tracking** -- Real-time position, speed, fuel, and delay monitoring
- **Track Utilization** -- Dynamic track usage and efficiency metrics
- **Performance Analytics** -- Comprehensive system performance dashboards
- **WebSocket Updates** -- Real-time data streaming to the frontend

### Optimization Algorithms
| # | Algorithm | Description |
|---|-----------|-------------|
| 1 | Headway Optimization | Minimize train spacing for maximum throughput |
| 2 | Junction Conflict Resolution | Intelligent junction management |
| 3 | Speed Optimization | Dynamic speed adjustments for efficiency |
| 4 | Route Optimization | Optimal path finding and scheduling |
| 5 | Slot Trading | Dynamic slot allocation and trading |
| 6 | Predictive Maintenance | ML-powered maintenance scheduling |

---

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+ and npm
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/1234620/train-traffic-optimizer.git
cd train-traffic-optimizer
```

### 2. Backend Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Train ML models (optional - models are pre-trained)
python train_ml_model.py

# Start the backend server
python app.py
```

The backend will be available at `http://localhost:8000`

### 3. Frontend Setup
```bash
# Navigate to frontend directory
cd railway-optimization

# Install dependencies
npm install

# Build the frontend
npm run build

# Return to root directory
cd ..
```

### 4. Start the Complete System
```bash
# Start the backend (serves both API and frontend)
python app.py
```

Access the application at `http://localhost:8000`

---

## Project Structure

```
train-traffic-optimizer/
├── app.py                             # Main FastAPI backend
├── train_ml_model.py                  # ML model training script
├── requirements.txt                   # Python dependencies
├── Dockerfile                         # Docker configuration
├── docker-compose.yml                 # Docker Compose orchestration
├── nginx.conf                         # Nginx reverse proxy config
├── models/                            # Trained ML models
│   ├── maintenance_classifier.joblib
│   ├── failure_risk_regressor.joblib
│   └── model_metadata.json
├── railway-optimization/              # Next.js frontend
│   ├── app/                           # Next.js app directory
│   ├── components/                    # React components
│   ├── out/                           # Built frontend (generated)
│   └── package.json
├── services/                          # Backend service modules
├── schemas/                           # Data schemas
├── simulation/                        # Simulation utilities
├── scripts/                           # Automation scripts
├── docs/                              # Documentation
└── templates/                         # HTML templates
```

---

## API Reference

### Core System
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/metrics` | System performance metrics |
| `GET` | `/api/trains` | Train information and status |
| `GET` | `/api/tracks` | Track utilization data |
| `GET` | `/api/optimizations` | AI optimization decisions |

### Machine Learning
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/ml/maintenance-predictions` | ML maintenance predictions |
| `GET` | `/api/ml/model-info` | ML model performance metrics |
| `GET` | `/api/ml/risk-summary` | System risk assessment |

### Documentation and Real-time
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/docs` | Interactive API documentation (Swagger UI) |
| `GET` | `/` | Frontend application |
| `WS` | `/ws` | WebSocket for real-time updates |

---

## Machine Learning Models

### Maintenance Classifier
| Property | Value |
|----------|-------|
| Type | RandomForestClassifier |
| Accuracy | 99.0% |
| Purpose | Binary classification for maintenance needs |
| Features | 11 input features (speed, fuel, temperature, etc.) |

### Failure Risk Regressor
| Property | Value |
|----------|-------|
| Type | GradientBoostingRegressor |
| R-squared Score | 48.4% |
| Purpose | Continuous risk score prediction (0-1) |
| Features | 11 input features (same as classifier) |

### Training Data
- **Samples**: 4,000 synthetic railway data points
- **Features**: Speed, fuel level, temperature, brake wear, track conditions, and more
- **Labels**: Maintenance needs and failure risk scores

---

## Frontend

### Dashboard
- Real-time system overview
- Performance metrics and KPIs
- Live train status monitoring

### AI Optimization
- ML-powered maintenance predictions
- AI model performance metrics
- Optimization recommendations
- Train-wise risk assessment

### Train Management
- Individual train details
- Real-time status updates
- Performance tracking

### Analytics
- Historical data visualization
- Performance trends
- System analytics

---

## Real-time Updates

The system provides real-time updates via WebSocket:

| Update Type | Interval |
|-------------|----------|
| System Updates | Every 5 seconds |
| Background Processing | Every 10 seconds |
| ML Predictions | Every 30 seconds |
| Optimization Decisions | Continuous |

---

## Development

### Backend Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run with auto-reload
python app.py
```

### Frontend Development
```bash
cd railway-optimization

# Install dependencies
npm install

# Development server
npm run dev

# Build for production
npm run build
```

### ML Model Retraining
```bash
# Retrain models with new data
python train_ml_model.py
```

---

## Troubleshooting

### Frontend Not Loading
If you see `Directory 'railway-optimization/out/_next' does not exist`:
1. Navigate to the frontend directory: `cd railway-optimization`
2. Install dependencies: `npm install`
3. Build the frontend: `npm run build`
4. Restart the backend: `python app.py`

### ML Models Not Working
If ML predictions show "Heuristic" instead of "ML-Powered":
1. Ensure models are trained: `python train_ml_model.py`
2. Check that the `models/` directory exists with `.joblib` files
3. Restart the backend server

### API Errors
- Check that all dependencies are installed: `pip install -r requirements.txt`
- Ensure Python 3.8+ is being used
- Check the console for specific error messages

---

## Performance Metrics

| Metric | Value |
|--------|-------|
| System Throughput | 95%+ efficiency |
| ML Prediction Accuracy | 99% (classifier) |
| Regressor R-squared | 48.4% |
| Real-time Update Latency | < 100ms |
| API Response Time | < 50ms average |
| WebSocket Latency | < 10ms |

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Commit: `git commit -m "Add feature"`
5. Push: `git push origin feature-name`
6. Create a Pull Request

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) -- Robust backend framework
- [Next.js](https://nextjs.org/) -- Modern frontend framework
- [scikit-learn](https://scikit-learn.org/) -- Machine learning capabilities
- [React](https://react.dev/) -- Component-based UI architecture
- [Docker](https://www.docker.com/) -- Containerized deployment

---

<p align="center">
  <b>Built for efficient railway operations</b>
</p>