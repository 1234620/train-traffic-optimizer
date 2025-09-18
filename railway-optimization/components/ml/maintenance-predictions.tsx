"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Brain, AlertTriangle, Wrench, TrendingUp, Info } from "lucide-react"
import { useState, useEffect } from "react"
import { fetchApi } from "@/lib/utils"

interface MaintenancePrediction {
  train_id: string
  failure_risk: number
  needs_maintenance: boolean
  risk_level: string
  confidence: number
  model_type: string
  predictions: {
    maintenance_probability: number
    risk_score: number
    estimated_days_to_failure?: number
  }
  features_used?: Record<string, number>
}

interface PredictionsResponse {
  predictions: MaintenancePrediction[]
  model_info: {
    ml_available: boolean
    model_loaded: boolean
    model_type: string
    total_trains_analyzed: number
  }
}

interface RiskSummary {
  summary: {
    total_trains: number
    needs_maintenance: number
    average_risk_score: number
    risk_distribution: Record<string, number>
  }
  alerts: {
    critical_trains: number
    high_risk_trains: number
    immediate_attention_needed: number
  }
  model_type: string
}

const getRiskBadge = (riskLevel: string) => {
  const colors = {
    Critical: "bg-red-600 text-white",
    High: "bg-orange-500 text-white",
    Medium: "bg-yellow-500 text-black",
    Low: "bg-green-500 text-white",
  }
  return <Badge className={colors[riskLevel as keyof typeof colors]}>{riskLevel}</Badge>
}

const getRiskColor = (riskLevel: string) => {
  const colors = {
    Critical: "text-red-600",
    High: "text-orange-500",
    Medium: "text-yellow-600",
    Low: "text-green-600",
  }
  return colors[riskLevel as keyof typeof colors] || "text-gray-600"
}

export function MaintenancePredictions() {
  const [predictions, setPredictions] = useState<MaintenancePrediction[]>([])
  const [riskSummary, setRiskSummary] = useState<RiskSummary | null>(null)
  const [modelInfo, setModelInfo] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchPredictions = async () => {
    try {
      setLoading(true)
      const [predictionsRes, summaryRes, modelRes] = await Promise.all([
        fetchApi('/api/ml/maintenance-predictions'),
        fetchApi('/api/ml/risk-summary'),
        fetchApi('/api/ml/model-info')
      ])
      
      setPredictions((predictionsRes as PredictionsResponse).predictions)
      setModelInfo((predictionsRes as PredictionsResponse).model_info)
      setRiskSummary(summaryRes as RiskSummary)
      setError(null)
    } catch (err) {
      setError('Failed to fetch ML predictions')
      console.error('Error fetching ML predictions:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchPredictions()
    const interval = setInterval(fetchPredictions, 30000) // Refresh every 30 seconds
    return () => clearInterval(interval)
  }, [])

  if (loading) {
    return (
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle className="text-lg font-semibold text-card-foreground flex items-center">
            <Brain className="w-5 h-5 mr-2" />
            ML Maintenance Predictions
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-32">
            <div className="text-muted-foreground">Loading ML predictions...</div>
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
            ML Maintenance Predictions
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

  return (
    <div>
      {/* Train-wise Predictions - Matching provided design */}
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle className="text-lg font-semibold text-card-foreground flex items-center">
            <Brain className="w-5 h-5 mr-2" />
            Train-wise Predictions
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {predictions.map((prediction) => (
              <div key={prediction.train_id} className="p-4 rounded-lg bg-muted border border-border">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center space-x-2">
                    <span className="font-semibold text-foreground text-base">
                      {prediction.train_id}
                    </span>
                    {getRiskBadge(prediction.risk_level)}
                  </div>
                  <div className="text-sm text-muted-foreground flex items-center">
                    <TrendingUp className="w-4 h-4 mr-1" />
                    Confidence: {Math.round(prediction.confidence * 100)}%
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-6 mb-3">
                  <div>
                    <div className="text-sm text-muted-foreground mb-2">Failure Risk</div>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-2xl font-bold text-foreground">
                        {Math.round(prediction.failure_risk * 100)}%
                      </span>
                    </div>
                    <Progress 
                      value={prediction.failure_risk * 100} 
                      className="h-2"
                    />
                  </div>
                  <div>
                    <div className="text-sm text-muted-foreground mb-2">Maintenance Probability</div>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-2xl font-bold text-foreground">
                        {Math.round(prediction.predictions.maintenance_probability * 100)}%
                      </span>
                    </div>
                    <Progress 
                      value={prediction.predictions.maintenance_probability * 100} 
                      className="h-2"
                    />
                  </div>
                </div>

                {prediction.predictions.estimated_days_to_failure && (
                  <div className="text-sm text-muted-foreground">
                    Est. Days to Failure: <span className="text-red-600 font-medium">{prediction.predictions.estimated_days_to_failure} days</span>
                  </div>
                )}

                {prediction.features_used && (
                  <details className="mt-3">
                    <summary className="text-sm text-blue-600 cursor-pointer hover:text-blue-700 flex items-center">
                      <Info className="w-4 h-4 mr-1" />
                      View Analysis Features
                    </summary>
                    <div className="mt-2 grid grid-cols-2 gap-2 text-xs">
                      {Object.entries(prediction.features_used).slice(0, 6).map(([key, value]) => (
                        <div key={key} className="bg-background p-2 rounded border">
                          <div className="text-muted-foreground">{key.replace('_', ' ')}</div>
                          <div className="font-medium">
                            {typeof value === 'number' ? value.toFixed(1) : value}
                          </div>
                        </div>
                      ))}
                    </div>
                  </details>
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
