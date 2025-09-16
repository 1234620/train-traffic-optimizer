"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Activity, Wifi, Database, Cpu } from "lucide-react"
import { useState, useEffect } from "react"

interface SystemStatus {
  name: string
  status: "operational" | "degraded" | "down"
  uptime: number
  responseTime: number
  icon: any
}

export function NetworkStatus() {
  const [systems, setSystems] = useState<SystemStatus[]>([
    { name: "Core Network", status: "operational", uptime: 99.8, responseTime: 45, icon: Wifi },
    { name: "Database Cluster", status: "operational", uptime: 99.9, responseTime: 23, icon: Database },
    { name: "AI Processing", status: "degraded", uptime: 97.2, responseTime: 156, icon: Cpu },
    { name: "Monitoring System", status: "operational", uptime: 99.7, responseTime: 67, icon: Activity },
  ])

  useEffect(() => {
    const interval = setInterval(() => {
      setSystems((prev) =>
        prev.map((system) => ({
          ...system,
          responseTime: Math.max(10, system.responseTime + (Math.random() - 0.5) * 20),
          uptime: Math.min(100, system.uptime + (Math.random() - 0.5) * 0.1),
        })),
      )
    }, 3000)

    return () => clearInterval(interval)
  }, [])

  const getStatusBadge = (status: string) => {
    const colors = {
      operational: "bg-accent text-accent-foreground",
      degraded: "bg-chart-4 text-white",
      down: "bg-destructive text-destructive-foreground",
    }
    return <Badge className={colors[status as keyof typeof colors]}>{status}</Badge>
  }

  return (
    <Card className="bg-card border-border">
      <CardHeader>
        <CardTitle className="text-lg font-semibold text-card-foreground flex items-center">
          <Activity className="w-5 h-5 mr-2" />
          System Status
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {systems.map((system) => {
            const Icon = system.icon
            return (
              <div key={system.name} className="p-3 rounded-lg bg-muted">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    <Icon className="w-4 h-4 text-primary" />
                    <span className="font-medium text-foreground">{system.name}</span>
                  </div>
                  {getStatusBadge(system.status)}
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Uptime</span>
                    <span className="font-medium text-foreground">{system.uptime.toFixed(1)}%</span>
                  </div>
                  <Progress value={system.uptime} className="h-2" />
                  <div className="flex justify-between text-xs text-muted-foreground">
                    <span>Response Time: {Math.round(system.responseTime)}ms</span>
                    <span>Last Updated: {new Date().toLocaleTimeString()}</span>
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
