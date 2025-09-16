"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { LineChart, Line, ResponsiveContainer, XAxis, YAxis } from "recharts"
import { TrendingUp, Users, Zap, Clock } from "lucide-react"
import { useState, useEffect } from "react"
import { fetchApi } from "@/lib/utils"

interface MetricData {
  time: string
  value: number
}

interface LiveMetric {
  title: string
  value: string
  change: string
  trend: "up" | "down"
  icon: any
  color: string
  data: MetricData[]
}

export function LiveMetrics() {
  const [metrics, setMetrics] = useState<LiveMetric[]>([])

  useEffect(() => {
    let mounted = true
    const seed = () => Array.from({ length: 20 }, (_, i) => ({ time: `${i}`, value: 0 }))

    const load = async () => {
      try {
        const data = await fetchApi<any>("/api/metrics")
        if (!mounted) return
        setMetrics([
          {
            title: "Throughput Score",
            value: String(data.throughput_score),
            change: "+2.1%",
            trend: "up",
            icon: TrendingUp,
            color: "#164e63",
            data: seed(),
          },
          {
            title: "Total Trains",
            value: String(data.total_trains),
            change: "+1",
            trend: "up",
            icon: Users,
            color: "#84cc16",
            data: seed(),
          },
          {
            title: "Avg Efficiency %",
            value: String(data.average_efficiency),
            change: "+1.2%",
            trend: "up",
            icon: Zap,
            color: "#ea580c",
            data: seed(),
          },
          {
            title: "Avg Delay (min)",
            value: String(data.average_delay),
            change: "-0.5",
            trend: "down",
            icon: Clock,
            color: "#f97316",
            data: seed(),
          },
        ])
      } catch (e) {
        console.error("Failed to load metrics:", e)
        // Set fallback data
        setMetrics([
          {
            title: "Throughput Score",
            value: "87.3",
            change: "+2.1%",
            trend: "up",
            icon: TrendingUp,
            color: "#164e63",
            data: seed(),
          },
          {
            title: "Total Trains",
            value: "6",
            change: "+1",
            trend: "up",
            icon: Users,
            color: "#84cc16",
            data: seed(),
          },
          {
            title: "Avg Efficiency %",
            value: "89.2",
            change: "+1.2%",
            trend: "up",
            icon: Zap,
            color: "#ea580c",
            data: seed(),
          },
          {
            title: "Avg Delay (min)",
            value: "4.7",
            change: "-0.5",
            trend: "down",
            icon: Clock,
            color: "#f97316",
            data: seed(),
          },
        ])
      }
    }

    load()
    const interval = setInterval(async () => {
      try {
        const data = await fetchApi<any>("/api/metrics")
        if (!mounted) return
        setMetrics((prev) =>
          prev.map((m) => {
            const nextVal =
              m.title === "Throughput Score" ? data.throughput_score :
              m.title === "Total Trains" ? data.total_trains :
              m.title === "Avg Efficiency %" ? data.average_efficiency :
              data.average_delay
            return {
              ...m,
              value: String(nextVal),
              data: [...m.data.slice(1), { time: Date.now().toString(), value: Number(nextVal) }],
            }
          }),
        )
      } catch (e) {
        console.error("Failed to update metrics:", e)
      }
    }, 5000)

    return () => {
      mounted = false
      clearInterval(interval)
    }
  }, [])

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {metrics.map((metric) => {
        const Icon = metric.icon
        return (
          <Card key={metric.title} className="bg-card border-border">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-card-foreground">{metric.title}</CardTitle>
              <Icon className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-foreground">{metric.value}</div>
              <div className="flex items-center space-x-2 mt-1 mb-3">
                <span className={`text-xs font-medium ${metric.trend === "up" ? "text-accent" : "text-destructive"}`}>
                  {metric.change}
                </span>
                <span className="text-xs text-muted-foreground">from last hour</span>
              </div>
              <div className="h-16">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={metric.data}>
                    <XAxis dataKey="time" hide />
                    <YAxis hide />
                    <Line
                      type="monotone"
                      dataKey="value"
                      stroke={metric.color}
                      strokeWidth={2}
                      dot={false}
                      animationDuration={300}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        )
      })}
    </div>
  )
}
