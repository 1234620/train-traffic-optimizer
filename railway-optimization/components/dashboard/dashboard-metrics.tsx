"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Train, Clock, TrendingUp, AlertCircle } from "lucide-react"

const metrics = [
  {
    title: "Active Trains",
    value: "1,247",
    change: "+12",
    changeType: "increase" as const,
    icon: Train,
    description: "Currently in operation",
  },
  {
    title: "On-Time Performance",
    value: "94.2%",
    change: "+2.1%",
    changeType: "increase" as const,
    icon: Clock,
    description: "Last 24 hours",
  },
  {
    title: "Network Efficiency",
    value: "87.5%",
    change: "+5.3%",
    changeType: "increase" as const,
    icon: TrendingUp,
    description: "AI optimization impact",
  },
  {
    title: "Active Alerts",
    value: "23",
    change: "-8",
    changeType: "decrease" as const,
    icon: AlertCircle,
    description: "Requiring attention",
  },
]

export function DashboardMetrics() {
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
              <div className="flex items-center space-x-2 mt-1">
                <Badge
                  variant={metric.changeType === "increase" ? "default" : "secondary"}
                  className={
                    metric.changeType === "increase"
                      ? "bg-accent text-accent-foreground"
                      : "bg-secondary text-secondary-foreground"
                  }
                >
                  {metric.change}
                </Badge>
                <p className="text-xs text-muted-foreground">{metric.description}</p>
              </div>
            </CardContent>
          </Card>
        )
      })}
    </div>
  )
}
