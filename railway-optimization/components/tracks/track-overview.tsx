"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Route, Wrench, AlertTriangle, CheckCircle } from "lucide-react"
import { useState, useEffect } from "react"
import { fetchApi } from "@/lib/utils"

interface Track {
  id: string
  capacity: number
  speed_limit: number
  length: number
  utilization: number
  maintenance_status: string
  weather_condition: string
  signal_status: string
}

export function TrackOverview() {
  const [tracks, setTracks] = useState<Record<string, Track>>({})
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const loadTracks = async () => {
      try {
        const data = await fetchApi<Record<string, Track>>("/api/tracks")
        setTracks(data)
      } catch (error) {
        console.error("Failed to load tracks:", error)
        // Fallback data
        setTracks({
          "T1": { id: "T1", capacity: 3, speed_limit: 120, length: 200, utilization: 0.85, maintenance_status: "good", weather_condition: "clear", signal_status: "green" },
          "T2": { id: "T2", capacity: 4, speed_limit: 100, length: 150, utilization: 0.75, maintenance_status: "good", weather_condition: "clear", signal_status: "green" },
          "T3": { id: "T3", capacity: 2, speed_limit: 110, length: 180, utilization: 0.90, maintenance_status: "maintenance_required", weather_condition: "foggy", signal_status: "yellow" },
          "T4": { id: "T4", capacity: 5, speed_limit: 90, length: 120, utilization: 0.60, maintenance_status: "good", weather_condition: "clear", signal_status: "green" },
          "T5": { id: "T5", capacity: 3, speed_limit: 130, length: 220, utilization: 0.80, maintenance_status: "good", weather_condition: "rainy", signal_status: "green" },
          "T6": { id: "T6", capacity: 2, speed_limit: 95, length: 160, utilization: 0.95, maintenance_status: "good", weather_condition: "clear", signal_status: "green" }
        })
      } finally {
        setLoading(false)
      }
    }

    loadTracks()
    const interval = setInterval(loadTracks, 10000)
    return () => clearInterval(interval)
  }, [])

  // Calculate stats from real data
  const totalLength = Object.values(tracks).reduce((sum, track) => sum + track.length, 0)
  const operationalTracks = Object.values(tracks).filter(track => track.maintenance_status === "good").length
  const maintenanceTracks = Object.values(tracks).filter(track => track.maintenance_status === "maintenance_required").length
  const criticalTracks = Object.values(tracks).filter(track => track.utilization > 0.9).length
  const avgUtilization = Object.values(tracks).reduce((sum, track) => sum + track.utilization, 0) / Object.keys(tracks).length

  const trackStats = [
    {
      title: "Total Track Length",
      value: `${totalLength.toLocaleString()} km`,
      subtitle: "Across network",
      icon: Route,
      color: "text-primary",
    },
    {
      title: "Operational Tracks",
      value: `${operationalTracks}/${Object.keys(tracks).length}`,
      subtitle: `${Math.round((operationalTracks / Object.keys(tracks).length) * 100)}% available`,
      icon: CheckCircle,
      color: "text-accent",
    },
    {
      title: "Under Maintenance",
      value: `${maintenanceTracks} tracks`,
      subtitle: `${Math.round((maintenanceTracks / Object.keys(tracks).length) * 100)}% of network`,
      icon: Wrench,
      color: "text-chart-4",
    },
    {
      title: "High Utilization",
      value: `${criticalTracks} tracks`,
      subtitle: `${Math.round((criticalTracks / Object.keys(tracks).length) * 100)}% requiring attention`,
      icon: AlertTriangle,
      color: "text-destructive",
    },
  ]

  const sectionUtilization = Object.entries(tracks).map(([id, track]) => ({
    name: `Track ${id}`,
    utilization: Math.round(track.utilization * 100),
    status: track.utilization > 0.9 ? "critical" : track.utilization > 0.8 ? "high" : "optimal",
    maintenance: track.maintenance_status,
    weather: track.weather_condition,
    signal: track.signal_status
  }))

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
            <CardTitle className="text-lg font-semibold text-card-foreground">Track Utilization</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {[1, 2, 3, 4, 5, 6].map((i) => (
                <div key={i} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="h-4 bg-muted rounded w-20"></div>
                    <div className="h-4 bg-muted rounded w-12"></div>
                  </div>
                  <div className="h-2 bg-muted rounded"></div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {trackStats.map((stat) => {
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

      {/* Track Utilization */}
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle className="text-lg font-semibold text-card-foreground">Track Utilization & Status</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {sectionUtilization.map((section) => (
              <div key={section.name} className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <span className="text-sm font-medium text-card-foreground">{section.name}</span>
                    <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                      section.maintenance === "maintenance_required" ? "bg-orange-500 text-white" : "bg-green-500 text-white"
                    }`}>
                      {section.maintenance === "maintenance_required" ? "Maintenance" : "Good"}
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="text-sm text-muted-foreground">{section.utilization}%</span>
                    <div
                      className={`px-2 py-1 rounded-full text-xs font-medium ${
                        section.status === "critical"
                          ? "bg-destructive text-destructive-foreground"
                          : section.status === "high"
                            ? "bg-chart-4 text-white"
                            : "bg-accent text-accent-foreground"
                      }`}
                    >
                      {section.status}
                    </div>
                  </div>
                </div>
                <Progress value={section.utilization} className="h-2" />
                <div className="flex items-center justify-between text-xs text-muted-foreground">
                  <span>Weather: {section.weather}</span>
                  <span>Signal: {section.signal}</span>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
