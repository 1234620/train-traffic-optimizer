"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Brain, Play, Pause, Settings, BarChart3 } from "lucide-react"

const models = [
  {
    id: "traffic-flow",
    name: "Traffic Flow Optimization",
    description: "Real-time traffic routing and congestion management",
    status: "active",
    accuracy: 97.3,
    lastTrained: "2024-01-15",
    predictions: "15.2M",
    type: "Deep Learning",
  },
  {
    id: "predictive-maintenance",
    name: "Predictive Maintenance",
    description: "Equipment failure prediction and maintenance scheduling",
    status: "active",
    accuracy: 94.1,
    lastTrained: "2024-01-12",
    predictions: "8.7M",
    type: "Random Forest",
  },
  {
    id: "demand-forecasting",
    name: "Passenger Demand Forecasting",
    description: "Predict passenger volumes and optimize capacity allocation",
    status: "training",
    accuracy: 91.8,
    lastTrained: "2024-01-10",
    predictions: "12.4M",
    type: "LSTM Neural Network",
  },
  {
    id: "route-optimization",
    name: "Dynamic Route Planning",
    description: "Optimal route selection based on real-time conditions",
    status: "active",
    accuracy: 95.7,
    lastTrained: "2024-01-14",
    predictions: "6.3M",
    type: "Reinforcement Learning",
  },
]

const getStatusBadge = (status: string) => {
  const colors = {
    active: "bg-accent text-accent-foreground",
    training: "bg-chart-4 text-white",
    inactive: "bg-secondary text-secondary-foreground",
  }
  return <Badge className={colors[status as keyof typeof colors]}>{status}</Badge>
}

export function OptimizationModels() {
  return (
    <Card className="bg-card border-border">
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="text-lg font-semibold text-card-foreground flex items-center">
          <Brain className="w-5 h-5 mr-2" />
          AI Models
        </CardTitle>
        <Button size="sm">
          <Settings className="w-4 h-4 mr-2" />
          Manage Models
        </Button>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {models.map((model) => (
            <div key={model.id} className="p-4 rounded-lg bg-muted">
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-1">
                    <h4 className="font-semibold text-foreground">{model.name}</h4>
                    {getStatusBadge(model.status)}
                  </div>
                  <p className="text-sm text-muted-foreground mb-2">{model.description}</p>
                  <div className="flex items-center space-x-4 text-xs text-muted-foreground">
                    <span>Type: {model.type}</span>
                    <span>Accuracy: {model.accuracy}%</span>
                    <span>Predictions: {model.predictions}</span>
                  </div>
                </div>
                <div className="flex space-x-2">
                  <Button variant="outline" size="sm">
                    <BarChart3 className="w-4 h-4" />
                  </Button>
                  <Button variant="outline" size="sm">
                    {model.status === "active" ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                  </Button>
                </div>
              </div>
              <div className="flex items-center justify-between text-xs">
                <span className="text-muted-foreground">Last trained: {model.lastTrained}</span>
                <Button variant="ghost" size="sm" className="h-6 px-2 text-xs">
                  Retrain Model
                </Button>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
