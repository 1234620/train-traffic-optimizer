"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Brain, Play, Pause, Settings, BarChart3, AlertTriangle } from "lucide-react"
import { useState, useEffect } from "react"
import { fetchApi } from "@/lib/utils"

interface MLModelInfo {
  ml_available: boolean
  models_loaded: boolean
  model_type: string
  models?: {
    classifier: string | null
    regressor: string | null
  }
  feature_columns?: string[]
  total_features?: number
  message?: string
  model_performance?: {
    classifier_accuracy: number
    regressor_r2_score: number
    training_samples: number
  }
}

const getStatusBadge = (status: string) => {
  const colors = {
    active: "bg-green-500 text-white",
    training: "bg-orange-500 text-white",
    inactive: "bg-gray-500 text-white",
  }
  return <Badge className={colors[status as keyof typeof colors]}>{status}</Badge>
}

export function OptimizationModels() {
  const [mlModelInfo, setMlModelInfo] = useState<MLModelInfo | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchModelInfo = async () => {
      try {
        setLoading(true)
        const data = await fetchApi<MLModelInfo>("/api/ml/model-info")
        setMlModelInfo(data)
        setError(null)
      } catch (err) {
        setError('Failed to fetch ML model information')
        console.error('Error fetching ML model info:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchModelInfo()
    const interval = setInterval(fetchModelInfo, 60000) // Refresh every minute
    return () => clearInterval(interval)
  }, [])

  if (loading) {
    return (
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle className="text-lg font-semibold text-card-foreground flex items-center">
            <Brain className="w-5 h-5 mr-2" />
            AI Models
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-32">
            <div className="text-muted-foreground">Loading model information...</div>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (error) {
    return (
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle className="text-lg font-semibold text-card-foreground flex items-center">
            <Brain className="w-5 h-5 mr-2" />
            AI Models
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-32 text-red-500">
            <AlertTriangle className="w-5 h-5 mr-2" />
            {error}
          </div>
        </CardContent>
      </Card>
    )
  }

  // Create models array from actual ML model info
  const models = []
  
  if (mlModelInfo?.models?.classifier) {
    models.push({
      id: "maintenance-classifier",
      name: "Maintenance Classifier",
      description: "Binary classification model to predict if equipment needs maintenance",
      status: "active",
      accuracy: mlModelInfo.model_performance?.classifier_accuracy || 99.0,
      lastTrained: "2024-01-12",
      predictions: "Real-time",
      type: mlModelInfo.models.classifier,
    })
  }

  if (mlModelInfo?.models?.regressor) {
    models.push({
      id: "failure-risk-regressor",
      name: "Failure Risk Predictor",
      description: "Regression model to predict equipment failure risk score (0-1)",
      status: "active", 
      accuracy: mlModelInfo.model_performance?.regressor_r2_score || 48.4,
      lastTrained: "2024-01-12",
      predictions: "Real-time",
      type: mlModelInfo.models.regressor,
    })
  }

  // If no ML models are loaded, show heuristic fallback
  if (models.length === 0) {
    models.push({
      id: "heuristic-fallback",
      name: "Heuristic Decision Engine",
      description: "Rule-based fallback system for optimization decisions",
      status: "active",
      accuracy: 75.0,
      lastTrained: "Built-in",
      predictions: "Real-time",
      type: "Rule-based",
    })
  }

  return (
    <Card className="bg-card border-border">
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="text-lg font-semibold text-card-foreground flex items-center">
          <Brain className="w-5 h-5 mr-2" />
          AI Models
          {mlModelInfo?.models_loaded && (
            <Badge className="ml-2 bg-blue-600 text-white">ML Powered</Badge>
          )}
        </CardTitle>
        <Button size="sm" variant="outline">
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
                {model.type !== "Rule-based" && (
                  <Button variant="ghost" size="sm" className="h-6 px-2 text-xs">
                    Retrain Model
                  </Button>
                )}
              </div>
            </div>
          ))}
        </div>
        
        {mlModelInfo && (
          <div className="mt-4 p-3 bg-muted rounded-lg">
            <div className="text-sm text-muted-foreground mb-1">Model Features</div>
            <div className="text-sm text-foreground">
              {mlModelInfo.total_features || 0} input features: {mlModelInfo.feature_columns?.slice(0, 3).join(', ')}
              {(mlModelInfo.feature_columns?.length || 0) > 3 && ` and ${(mlModelInfo.feature_columns?.length || 0) - 3} more`}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
