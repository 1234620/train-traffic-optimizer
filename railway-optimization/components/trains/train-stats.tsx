"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Train, Clock, AlertTriangle, CheckCircle } from "lucide-react"
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

export function TrainStats() {
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
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[1, 2, 3, 4].map((i) => (
          <Card key={i} className="bg-card border-border">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <div className="h-4 bg-muted rounded w-20"></div>
              <div className="h-5 w-5 bg-muted rounded"></div>
            </CardHeader>
            <CardContent>
              <div className="h-8 bg-muted rounded w-16 mb-2"></div>
              <div className="h-3 bg-muted rounded w-24"></div>
            </CardContent>
          </Card>
        ))}
      </div>
    )
  }

  if (!metrics) return null

  const onTimePercentage = Math.max(0, 100 - (metrics.average_delay * 2))
  const onTimeTrains = Math.round((metrics.total_trains * onTimePercentage) / 100)
  const delayedTrains = metrics.total_trains - onTimeTrains

  const stats = [
    {
      title: "Total Trains",
      value: metrics.total_trains.toString(),
      subtitle: "Active in network",
      icon: Train,
      color: "text-primary",
    },
    {
      title: "On Schedule",
      value: onTimeTrains.toString(),
      subtitle: `${onTimePercentage.toFixed(1)}% on-time`,
      icon: CheckCircle,
      color: "text-accent",
    },
    {
      title: "Delayed",
      value: delayedTrains.toString(),
      subtitle: `Avg delay: ${metrics.average_delay.toFixed(1)} min`,
      icon: Clock,
      color: "text-chart-4",
    },
    {
      title: "Critical Issues",
      value: metrics.safety_violations.toString(),
      subtitle: "Require attention",
      icon: AlertTriangle,
      color: "text-destructive",
    },
  ]

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {stats.map((stat) => {
        const Icon = stat.icon
        return (
          <Card key={stat.title} className="bg-card border-border">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-card-foreground">{stat.title}</CardTitle>
              <Icon className={`h-5 w-5 ${stat.color}`} />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-foreground">{stat.value}</div>
              <p className="text-xs text-muted-foreground mt-1">{stat.subtitle}</p>
            </CardContent>
          </Card>
        )
      })}
    </div>
  )
}
