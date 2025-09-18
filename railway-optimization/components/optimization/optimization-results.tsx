"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { TrendingUp, Clock, Route, Users, Brain, Zap, Wrench } from "lucide-react"
import { useState, useEffect } from "react"
import { fetchApi } from "@/lib/utils"

interface OptimizationDecision {
  id: string
  type: string
  train_id: string | null
  track_id: string | null
  junction_id: string | null
  action: string
  impact: string
  priority: string
  confidence: number
  estimated_benefit: number
  implementation_time: number
  status: string
}

const getImpactBadge = (priority: string) => {
  const colors = {
    critical: "bg-red-500 text-white",
    high: "bg-orange-500 text-white",
    medium: "bg-blue-500 text-white",
    low: "bg-gray-500 text-white",
  }
  return <Badge className={colors[priority as keyof typeof colors] || colors.low}>{priority}</Badge>
}

const getTypeIcon = (type: string) => {
  switch (type) {
    case "route_optimization":
      return Route
    case "headway_optimization":
      return TrendingUp
    case "junction_optimization":
      return Users
    case "speed_optimization":
      return Zap
    case "predictive_maintenance":
      return Wrench
    case "slot_trading":
      return Brain
    default:
      return Clock
  }
}

const getTypeDisplayName = (type: string) => {
  return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

export function OptimizationResults() {
  const [optimizations, setOptimizations] = useState<OptimizationDecision[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const loadOptimizations = async () => {
      try {
        const data = await fetchApi<OptimizationDecision[]>("/api/optimizations")
        setOptimizations(data)
      } catch (error) {
        console.error("Failed to load optimizations:", error)
        // Fallback data
        setOptimizations([
          {
            id: "OPT_001",
            type: "headway_optimization",
            train_id: "T002",
            track_id: "T2",
            junction_id: null,
            action: "Reduce speed of Shatabdi Express by 15.0 km/h",
            impact: "Prevents collision risk and improves safety",
            priority: "critical",
            confidence: 0.95,
            estimated_benefit: 15.5,
            implementation_time: 2,
            status: "pending"
          },
          {
            id: "OPT_002",
            type: "junction_optimization",
            train_id: "T003",
            track_id: null,
            junction_id: "J2",
            action: "Implement dynamic routing for junction J2",
            impact: "Eliminates 1 conflicts and improves flow",
            priority: "high",
            confidence: 0.88,
            estimated_benefit: 22.3,
            implementation_time: 5,
            status: "pending"
          },
          {
            id: "OPT_003",
            type: "speed_optimization",
            train_id: "T001",
            track_id: "T1",
            junction_id: null,
            action: "Increase speed to 140 km/h with fuel optimization",
            impact: "Reduces delay by 10 minutes, saves 1.5% fuel",
            priority: "medium",
            confidence: 0.82,
            estimated_benefit: 18.7,
            implementation_time: 3,
            status: "pending"
          }
        ])
      } finally {
        setLoading(false)
      }
    }

    loadOptimizations()
    const interval = setInterval(loadOptimizations, 10000)
    return () => clearInterval(interval)
  }, [])

  if (loading) {
    return (
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle className="text-lg font-semibold text-card-foreground flex items-center">
            <TrendingUp className="w-5 h-5 mr-2" />
            Recent AI Optimization Decisions
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="p-4 rounded-lg bg-muted">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-start space-x-3">
                    <div className="w-5 h-5 bg-muted rounded mt-0.5"></div>
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-1">
                        <div className="h-4 bg-muted rounded w-32"></div>
                        <div className="h-5 bg-muted rounded w-16"></div>
                      </div>
                      <div className="h-3 bg-muted rounded w-24 mb-1"></div>
                      <div className="h-3 bg-muted rounded w-full"></div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="h-6 bg-muted rounded w-12 mb-1"></div>
                    <div className="h-3 bg-muted rounded w-16"></div>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <div className="h-3 bg-muted rounded w-20"></div>
                  <div className="h-3 bg-muted rounded w-24"></div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="bg-card border-border">
      <CardHeader>
        <CardTitle className="text-lg font-semibold text-card-foreground flex items-center">
          <TrendingUp className="w-5 h-5 mr-2" />
          Recent AI Optimization Decisions
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {optimizations.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <Brain className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p>No optimization decisions available</p>
              <p className="text-sm">AI is analyzing the system...</p>
            </div>
          ) : (
            optimizations.slice(0, 6).map((decision) => {
              const Icon = getTypeIcon(decision.type)
              return (
                <div key={decision.id} className="p-4 rounded-lg bg-muted">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-start space-x-3">
                      <Icon className="w-5 h-5 mt-0.5 text-primary" />
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-1">
                          <h4 className="font-semibold text-foreground">{getTypeDisplayName(decision.type)}</h4>
                          {getImpactBadge(decision.priority)}
                        </div>
                        <p className="text-sm text-primary font-medium mb-1">
                          {decision.train_id ? `Train ${decision.train_id}` : 
                           decision.track_id ? `Track ${decision.track_id}` : 
                           decision.junction_id ? `Junction ${decision.junction_id}` : 'System'}
                        </p>
                        <p className="text-sm text-muted-foreground">{decision.action}</p>
                        <p className="text-xs text-muted-foreground mt-1">{decision.impact}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-lg font-bold text-accent">+{decision.estimated_benefit.toFixed(1)}%</div>
                      <div className="text-xs text-muted-foreground">Benefit</div>
                    </div>
                  </div>
                  <div className="flex items-center justify-between text-xs text-muted-foreground">
                    <span>Confidence: {Math.round(decision.confidence * 100)}%</span>
                    <div className="flex items-center space-x-4">
                      <span>Time: {decision.implementation_time}min</span>
                      <div className="flex items-center">
                        <Clock className="w-3 h-3 mr-1" />
                        <span className={decision.status === 'pending' ? 'text-orange-500' : 'text-green-500'}>
                          {decision.status}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              )
            })
          )}
        </div>
      </CardContent>
    </Card>
  )
}
