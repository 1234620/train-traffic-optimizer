"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"

const systemStats = [
  { name: "Network Capacity", usage: 78, status: "optimal" },
  { name: "Signal Systems", usage: 92, status: "high" },
  { name: "Track Utilization", usage: 65, status: "optimal" },
  { name: "Station Load", usage: 84, status: "high" },
]

export function SystemOverview() {
  return (
    <Card className="bg-card border-border">
      <CardHeader>
        <CardTitle className="text-lg font-semibold text-card-foreground">System Overview</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {systemStats.map((stat) => (
          <div key={stat.name} className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-card-foreground">{stat.name}</span>
              <div className="flex items-center space-x-2">
                <span className="text-sm text-muted-foreground">{stat.usage}%</span>
                <Badge
                  variant={stat.status === "optimal" ? "default" : "secondary"}
                  className={
                    stat.status === "optimal"
                      ? "bg-accent text-accent-foreground"
                      : "bg-destructive text-destructive-foreground"
                  }
                >
                  {stat.status}
                </Badge>
              </div>
            </div>
            <Progress value={stat.usage} className="h-2" />
          </div>
        ))}
      </CardContent>
    </Card>
  )
}
