"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { TrendingUp, TrendingDown, BarChart3, Users, Clock, Route } from "lucide-react"
import { useState, useEffect } from "react"
import { fetchApi } from "@/lib/utils"

interface Metrics {
  throughput_score: number
  total_trains: number
  total_passengers: number
  average_delay: number
  average_efficiency: number
  average_fuel_level: number
  safety_violations: number
  active_decisions: number
  system_status: string
}

export function AnalyticsOverview() {
  const [metrics, setMetrics] = useState<Metrics | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const loadMetrics = async () => {
      try {
        const data = await fetchApi<Metrics>("/api/metrics")
        setMetrics(data)
      } catch (error) {
        console.error("Failed to load metrics:", error)
        // Fallback data
        setMetrics({
          throughput_score: 87.3,
          total_trains: 6,
          total_passengers: 8900,
          average_delay: 4.7,
          average_efficiency: 89.2,
          average_fuel_level: 81.5,
          safety_violations: 0,
          active_decisions: 3,
          system_status: "operational"
        })
      } finally {
        setLoading(false)
      }
    }

    loadMetrics()
    const interval = setInterval(loadMetrics, 10000)
    return () => clearInterval(interval)
  }, [])

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <Card key={i} className="bg-card border-border">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <div className="h-4 bg-muted rounded w-24"></div>
                <div className="h-5 w-5 bg-muted rounded"></div>
              </CardHeader>
              <CardContent>
                <div className="h-8 bg-muted rounded w-16 mb-2"></div>
                <div className="h-3 bg-muted rounded w-20"></div>
              </CardContent>
            </Card>
          ))}
        </div>
        <Card className="bg-card border-border">
          <CardHeader>
            <CardTitle className="text-lg font-semibold text-card-foreground">Performance Summary</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="p-4 rounded-lg bg-muted">
                  <div className="h-4 bg-muted rounded w-20 mb-3"></div>
                  <div className="space-y-2">
                    <div className="h-3 bg-muted rounded w-16"></div>
                    <div className="h-3 bg-muted rounded w-12"></div>
                    <div className="h-3 bg-muted rounded w-14"></div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (!metrics) return null

  // Calculate derived metrics
  const onTimePercentage = Math.max(0, 100 - (metrics.average_delay * 2))
  const routeUtilization = (metrics.total_trains / 10) * 100 // Assuming max 10 trains capacity

  const analyticsMetrics = [
    {
      title: "Network Efficiency",
      value: `${metrics.throughput_score.toFixed(1)}%`,
      change: "+5.3%",
      trend: "up",
      icon: BarChart3,
      color: "text-accent",
      description: "Overall network performance",
    },
    {
      title: "Passenger Volume",
      value: `${(metrics.total_passengers / 1000).toFixed(1)}K`,
      change: "+12.8%",
      trend: "up",
      icon: Users,
      color: "text-primary",
      description: "Total passengers",
    },
    {
      title: "On-Time Performance",
      value: `${onTimePercentage.toFixed(1)}%`,
      change: "+2.1%",
      trend: "up",
      icon: Clock,
      color: "text-chart-3",
      description: "Punctuality rate",
    },
    {
      title: "Route Utilization",
      value: `${routeUtilization.toFixed(1)}%`,
      change: "-1.2%",
      trend: "down",
      icon: Route,
      color: "text-chart-4",
      description: "Track capacity usage",
    },
  ]

  const regionalPerformance = [
    { region: "Northern", efficiency: Math.round(metrics.throughput_score + 2), passengers: `${Math.round(metrics.total_passengers * 0.3 / 1000)}K`, onTime: onTimePercentage + 1, trend: "up" },
    { region: "Western", efficiency: Math.round(metrics.throughput_score - 1), passengers: `${Math.round(metrics.total_passengers * 0.25 / 1000)}K`, onTime: onTimePercentage - 0.5, trend: "up" },
    { region: "Eastern", efficiency: Math.round(metrics.throughput_score - 3), passengers: `${Math.round(metrics.total_passengers * 0.2 / 1000)}K`, onTime: onTimePercentage - 1, trend: "down" },
    { region: "Southern", efficiency: Math.round(metrics.throughput_score + 4), passengers: `${Math.round(metrics.total_passengers * 0.25 / 1000)}K`, onTime: onTimePercentage + 2, trend: "up" },
  ]

  return (
    <div className="space-y-6">
      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {analyticsMetrics.map((metric) => {
          const Icon = metric.icon
          const TrendIcon = metric.trend === "up" ? TrendingUp : TrendingDown
          return (
            <Card key={metric.title} className="bg-card border-border">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-card-foreground">{metric.title}</CardTitle>
                <Icon className={`h-5 w-5 ${metric.color}`} />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-foreground">{metric.value}</div>
                <div className="flex items-center space-x-2 mt-1">
                  <div className="flex items-center space-x-1">
                    <TrendIcon className={`w-3 h-3 ${metric.trend === "up" ? "text-accent" : "text-destructive"}`} />
                    <span
                      className={`text-xs font-medium ${metric.trend === "up" ? "text-accent" : "text-destructive"}`}
                    >
                      {metric.change}
                    </span>
                  </div>
                  <span className="text-xs text-muted-foreground">{metric.description}</span>
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* System Performance */}
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle className="text-lg font-semibold text-card-foreground">System Performance Summary</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {regionalPerformance.map((region) => (
              <div key={region.region} className="p-4 rounded-lg bg-muted">
                <div className="flex items-center justify-between mb-3">
                  <h4 className="font-semibold text-foreground">{region.region} Region</h4>
                  <Badge
                    className={
                      region.trend === "up"
                        ? "bg-accent text-accent-foreground"
                        : "bg-destructive text-destructive-foreground"
                    }
                  >
                    {region.trend === "up" ? "↗" : "↘"}
                  </Badge>
                </div>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Efficiency:</span>
                    <span className="font-medium text-foreground">{region.efficiency}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Passengers:</span>
                    <span className="font-medium text-foreground">{region.passengers}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">On-Time:</span>
                    <span className="font-medium text-foreground">{region.onTime.toFixed(1)}%</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Additional Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="bg-card border-border">
          <CardHeader>
            <CardTitle className="text-sm font-medium text-card-foreground">Safety Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">{metrics.safety_violations}</div>
            <p className="text-xs text-muted-foreground">Safety violations</p>
          </CardContent>
        </Card>
        <Card className="bg-card border-border">
          <CardHeader>
            <CardTitle className="text-sm font-medium text-card-foreground">Active AI Decisions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">{metrics.active_decisions}</div>
            <p className="text-xs text-muted-foreground">Optimization decisions</p>
          </CardContent>
        </Card>
        <Card className="bg-card border-border">
          <CardHeader>
            <CardTitle className="text-sm font-medium text-card-foreground">System Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground capitalize">{metrics.system_status}</div>
            <p className="text-xs text-muted-foreground">Current status</p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
