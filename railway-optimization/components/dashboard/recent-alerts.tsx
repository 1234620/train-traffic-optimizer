"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { AlertTriangle, Info, AlertCircle, Clock } from "lucide-react"

const alerts = [
  {
    id: 1,
    type: "warning",
    title: "Track Maintenance Scheduled",
    description: "Section 12A-15B will be under maintenance from 02:00 to 06:00",
    time: "2 hours ago",
    priority: "medium",
  },
  {
    id: 2,
    type: "error",
    title: "Signal Failure - Junction 45",
    description: "Manual override activated. Estimated repair time: 45 minutes",
    time: "15 minutes ago",
    priority: "high",
  },
  {
    id: 3,
    type: "info",
    title: "Weather Advisory",
    description: "Heavy rainfall expected in Northern region. Speed restrictions applied",
    time: "1 hour ago",
    priority: "low",
  },
  {
    id: 4,
    type: "warning",
    title: "Platform Overcrowding",
    description: "Platform 7 at Mumbai Central exceeding capacity limits",
    time: "30 minutes ago",
    priority: "medium",
  },
]

const getAlertIcon = (type: string) => {
  switch (type) {
    case "error":
      return AlertCircle
    case "warning":
      return AlertTriangle
    default:
      return Info
  }
}

const getAlertColor = (priority: string) => {
  switch (priority) {
    case "high":
      return "bg-destructive text-destructive-foreground"
    case "medium":
      return "bg-chart-4 text-white"
    default:
      return "bg-accent text-accent-foreground"
  }
}

export function RecentAlerts() {
  return (
    <Card className="bg-card border-border">
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="text-lg font-semibold text-card-foreground">Recent Alerts</CardTitle>
        <Button variant="outline" size="sm">
          View All
        </Button>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {alerts.map((alert) => {
            const Icon = getAlertIcon(alert.type)
            return (
              <div key={alert.id} className="flex items-start space-x-3 p-3 rounded-lg bg-muted">
                <Icon className="w-5 h-5 mt-0.5 text-muted-foreground" />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2 mb-1">
                    <h4 className="text-sm font-medium text-foreground">{alert.title}</h4>
                    <Badge className={getAlertColor(alert.priority)}>{alert.priority}</Badge>
                  </div>
                  <p className="text-sm text-muted-foreground mb-2">{alert.description}</p>
                  <div className="flex items-center text-xs text-muted-foreground">
                    <Clock className="w-3 h-3 mr-1" />
                    {alert.time}
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </CardContent>
    </Card>
  )
}
