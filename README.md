# 🚂 Train Traffic Throughput Maximization System

**Advanced AI-Powered Railway Optimization Platform for Indian Railways**

## 🎯 Overview

This system provides real-time train traffic optimization using advanced AI algorithms, predictive analytics, and intelligent decision-making to maximize railway throughput while ensuring safety and efficiency. The system features a modern Next.js frontend integrated with a powerful FastAPI backend.

## ✨ Features

### 🎨 Frontend (Next.js)
- **Real-time Dashboard**: Live monitoring of trains, tracks, and system performance
- **Train Management**: Complete train tracking, status updates, and control
- **Track Management**: Infrastructure monitoring, maintenance scheduling, and capacity tracking
- **AI Optimization Center**: Interactive optimization decisions and performance analytics
- **Analytics & Reporting**: Comprehensive performance metrics and trend analysis
- **Responsive Design**: Modern, mobile-friendly interface with dark/light themes

### 🚀 Backend (FastAPI)
- **AI Optimization Engine**: Multiple optimization algorithms for different scenarios
- **Real-time Simulation**: Live railway system simulation with realistic data
- **WebSocket Support**: Real-time updates and notifications
- **RESTful API**: Comprehensive API endpoints for all system functions
- **Predictive Analytics**: Machine learning-based predictions for maintenance and delays
- **Safety Monitoring**: Real-time safety validation and conflict detection

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd SIH2
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install frontend dependencies**
   ```bash
   cd railway-optimization
   npm install
   ```

### Running the System

**Option 1: Integrated Startup (Recommended)**
```bash
python start_full_system.py
```

This will:
- Check all requirements
- Install frontend dependencies if needed
- Build the frontend
- Start the backend server
- Start the frontend development server
- Provide access URLs

**Option 2: Manual Startup**

1. **Start the backend**:
   ```bash
   python app.py
   ```

2. **Start the frontend** (in another terminal):
   ```bash
   cd railway-optimization
   npm run dev
   ```

### Access Points

- **Frontend Dashboard**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/docs
- **WebSocket**: ws://localhost:8000/ws

## 🏗️ Architecture

### Backend (FastAPI)
- **Core Engine**: Railway system simulation and optimization
- **AI Algorithms**: Multiple optimization strategies
- **Real-time Updates**: WebSocket support for live data
- **REST API**: Comprehensive API endpoints
- **Data Models**: Structured data representation with Pydantic

### Frontend (Next.js)
- **Dashboard**: Real-time monitoring interface
- **Analytics**: Performance charts and metrics
- **Train Management**: Live train status and control
- **Track Management**: Infrastructure monitoring
- **AI Center**: Optimization decisions and controls

## 📊 Key Components

### AI Optimization Engine
- **Headway Optimization**: Prevents collisions and improves flow
- **Junction Management**: Resolves conflicts at railway junctions
- **Speed Optimization**: Balances speed with fuel efficiency
- **Predictive Maintenance**: ML-based maintenance scheduling
- **Slot Trading**: Dynamic slot allocation between trains
- **Route Optimization**: Alternative routing for delays

### Real-time Features
- **Live Train Tracking**: Real-time position and status updates
- **Performance Metrics**: Continuous monitoring of system KPIs
- **Alert System**: Automated notifications for critical events
- **WebSocket Updates**: Sub-second latency for real-time data

## 🔧 API Endpoints

### Core Endpoints
- `GET /api/health` - System health check
- `GET /api/trains` - List all trains
- `GET /api/tracks` - List all tracks
- `GET /api/junctions` - List all junctions
- `GET /api/optimizations` - Get AI optimization decisions
- `GET /api/metrics` - System performance metrics

### Detailed Endpoints
- `GET /api/trains/{id}` - Get specific train details
- `GET /api/trains/{id}/status` - Get train real-time status
- `PUT /api/trains/{id}/status` - Update train status
- `GET /api/tracks/{id}` - Get specific track details
- `GET /api/tracks/{id}/trains` - Get trains on specific track
- `GET /api/optimizations/{id}` - Get specific optimization
- `PUT /api/optimizations/{id}` - Update optimization status

### Analytics Endpoints
- `GET /api/analytics/performance` - Performance analytics data
- `GET /api/analytics/reports` - Generate reports
- `GET /api/alerts` - System alerts and notifications
- `GET /api/network/status` - Network connectivity status

### WebSocket
- `ws://localhost:8000/ws` - Real-time updates

## 🎨 Frontend Pages

### Dashboard (`/`)
- Live metrics and KPIs with real-time updates
- Real-time train status map with location tracking
- System overview and alerts
- Network status monitoring
- Recent optimization decisions

### Trains (`/trains`)
- Complete train management interface
- Train filtering and search capabilities
- Real-time status updates
- Performance statistics and analytics
- Individual train detail views

### Tracks (`/tracks`)
- Track condition monitoring
- Maintenance scheduling interface
- Capacity utilization visualization
- Weather and signal status
- Track-specific train listings

### Optimization (`/optimization`)
- AI optimization center
- Decision management interface
- Performance analytics
- Control interfaces for manual overrides
- Real-time optimization metrics

### Analytics (`/analytics`)
- Comprehensive reporting dashboard
- Performance trends and forecasting
- KPI dashboards with interactive charts
- Report generation and export
- Historical data analysis

## 🔬 Technical Details

### Backend Technologies
- **FastAPI**: Modern Python web framework with automatic API docs
- **Uvicorn**: ASGI server for high performance
- **Pydantic**: Data validation and serialization
- **WebSockets**: Real-time communication
- **NumPy/Pandas**: Data processing and analytics
- **Asyncio**: Asynchronous programming for better performance

### Frontend Technologies
- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first styling
- **Radix UI**: Accessible component library
- **Recharts**: Data visualization and charts
- **Lucide React**: Modern icon library
- **React Hooks**: State management and side effects

### AI/ML Features
- **Multi-objective Optimization**: Balances multiple performance criteria
- **Predictive Analytics**: Machine learning for maintenance and delays
- **Real-time Decision Making**: Sub-second optimization decisions
- **Adaptive Algorithms**: Self-improving optimization strategies
- **Confidence Scoring**: AI decision confidence metrics

## 📈 Performance Metrics

- **Throughput Score**: Overall system efficiency (0-100)
- **Average Delay**: Mean delay across all trains
- **Efficiency**: Fuel and energy efficiency metrics
- **Safety Violations**: Real-time safety monitoring
- **Passenger Satisfaction**: Service quality indicators
- **AI Accuracy**: Machine learning model performance
- **Energy Savings**: Fuel consumption optimization

## 🛡️ Safety Features

- **Real-time Conflict Detection**: Prevents collisions
- **Safety Overlay**: ATP/Kavach integration ready
- **Emergency Protocols**: Automated safety responses
- **Audit Logging**: Complete decision tracking
- **Risk Assessment**: Continuous safety evaluation

## 🚀 Deployment

### Development
```bash
python start_full_system.py
```

### Docker Support
```bash
docker-compose up -d
```

### Production Deployment
1. Build the frontend: `cd railway-optimization && npm run build`
2. Start the backend: `uvicorn app:app --host 0.0.0.0 --port 8000`
3. Serve static files through nginx or similar

## 🎯 Key Features Integration

### Real-time Data Flow
- Backend generates realistic railway simulation data
- Frontend consumes data via REST API and WebSocket
- Automatic fallback to mock data if backend unavailable
- Real-time updates every 5-10 seconds

### AI Decision Making
- Backend runs optimization algorithms continuously
- Frontend displays AI decisions with confidence scores
- Interactive decision management interface
- Real-time impact assessment

### Modern UI/UX
- Responsive design for all screen sizes
- Dark/light theme support
- Loading states and error handling
- Smooth animations and transitions
- Accessible components

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the API documentation at `/api/docs`
- Review the code comments for implementation details

---

**Built with ❤️ for Indian Railways**

*This system demonstrates advanced AI-powered railway optimization with a modern, production-ready architecture.*