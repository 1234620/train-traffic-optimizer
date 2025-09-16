"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { AlertTriangle, Clock, Wrench, Route } from "lucide-react"

const alerts = [
  {
    id: 1,
    type: "critical",
    title: "Track Damage Detected",
    section: "SEC-004 (Km 245-247)",
    description: "Severe rail wear detected. Immediate inspection required.",
    time: "15 minutes ago",
    priority: "high",
  },
  {
    id: 2,
    type: "maintenance",
    title: "Scheduled Maintenance",
    section: "SEC-002 (Km 120-135)",
    description: "Track renewal work in progress. Expected completion: 6 hours.",
    time: "2 hours ago",
    priority: "medium",
  },
  {
    id: 3,
    type: "warning",
    title: "High Utilization Alert",
    section: "SEC-003 (Km 180-200)",
    description: "Track utilization exceeding 90%. Consider traffic redistribution.",
    time: "45 minutes ago",
    priority: "medium",
  },
  {
    id: 4,
    type: "info",
    title: "Inspection Completed",
    section: "SEC-001 (Km 85-95)",
    description: "Routine inspection completed. All systems normal.",
    time: "3 hours ago",
    priority: "low",
  },
]

const getAlertIcon = (type: string) => {
  switch (type) {
    case "critical":
      return AlertTriangle
    case "maintenance":
      return Wrench
    case "warning":
      return Clock
    default:
      return Route
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

export function TrackAlerts() {
  return (
    <Card className="bg-card border-border">
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="text-lg font-semibold text-card-foreground">Track Alerts</CardTitle>
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
                  <p className="text-xs font-medium text-primary mb-1">{alert.section}</p>
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
