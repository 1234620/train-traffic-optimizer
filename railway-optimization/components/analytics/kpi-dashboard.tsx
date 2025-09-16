"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import { Target, Award, AlertTriangle, CheckCircle } from "lucide-react"

const kpiData = [
  {
    category: "Operational Excellence",
    kpis: [
      { name: "Network Availability", current: 99.2, target: 99.5, status: "good" },
      { name: "Asset Utilization", current: 87.5, target: 85.0, status: "excellent" },
      { name: "Maintenance Efficiency", current: 94.1, target: 95.0, status: "good" },
    ],
  },
  {
    category: "Customer Experience",
    kpis: [
      { name: "On-Time Performance", current: 94.2, target: 95.0, status: "good" },
      { name: "Customer Satisfaction", current: 4.3, target: 4.5, status: "good", isRating: true },
      { name: "Service Reliability", current: 96.8, target: 97.0, status: "good" },
    ],
  },
  {
    category: "Safety & Security",
    kpis: [
      { name: "Safety Incidents", current: 0.02, target: 0.05, status: "excellent", isIncident: true },
      { name: "Security Compliance", current: 98.7, target: 98.0, status: "excellent" },
      { name: "Emergency Response", current: 92.3, target: 90.0, status: "excellent" },
    ],
  },
  {
    category: "Financial Performance",
    kpis: [
      { name: "Revenue per Km", current: 85.2, target: 80.0, status: "excellent" },
      { name: "Cost Efficiency", current: 78.9, target: 82.0, status: "warning" },
      { name: "ROI on AI Investment", current: 23.5, target: 20.0, status: "excellent" },
    ],
  },
]

const getStatusIcon = (status: string) => {
  switch (status) {
    case "excellent":
      return <Award className="w-4 h-4 text-accent" />
    case "good":
      return <CheckCircle className="w-4 h-4 text-primary" />
    case "warning":
      return <AlertTriangle className="w-4 h-4 text-chart-4" />
    default:
      return <Target className="w-4 h-4 text-muted-foreground" />
  }
}

const getStatusBadge = (status: string) => {
  const colors = {
    excellent: "bg-accent text-accent-foreground",
    good: "bg-primary text-primary-foreground",
    warning: "bg-chart-4 text-white",
    critical: "bg-destructive text-destructive-foreground",
  }
  return <Badge className={colors[status as keyof typeof colors]}>{status}</Badge>
}

export function KPIDashboard() {
  return (
    <Card className="bg-card border-border">
      <CardHeader>
        <CardTitle className="text-lg font-semibold text-card-foreground flex items-center">
          <Target className="w-5 h-5 mr-2" />
          Key Performance Indicators
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {kpiData.map((category) => (
            <div key={category.category} className="space-y-4">
              <h4 className="font-semibold text-foreground">{category.category}</h4>
              <div className="space-y-3">
                {category.kpis.map((kpi) => (
                  <div key={kpi.name} className="p-3 rounded-lg bg-muted">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-card-foreground">{kpi.name}</span>
                      <div className="flex items-center space-x-2">
                        {getStatusIcon(kpi.status)}
                        {getStatusBadge(kpi.status)}
                      </div>
                    </div>
                    <div className="flex items-center justify-between mb-2">
                      <div className="text-lg font-bold text-foreground">
                        {kpi.isRating ? `${kpi.current}/5.0` : kpi.isIncident ? `${kpi.current}%` : `${kpi.current}%`}
                      </div>
                      <div className="text-sm text-muted-foreground">
                        Target: {kpi.isRating ? `${kpi.target}/5.0` : `${kpi.target}%`}
                      </div>
                    </div>
                    <Progress value={kpi.isRating ? (kpi.current / 5) * 100 : kpi.current} className="h-2" />
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
