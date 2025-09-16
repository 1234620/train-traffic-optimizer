"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { MapPin, Layers, ZoomIn, ZoomOut } from "lucide-react"
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

const getStatusBadge = (status: string) => {
  const colors = {
    good: "bg-accent text-accent-foreground",
    maintenance_required: "bg-chart-4 text-white",
    critical: "bg-destructive text-destructive-foreground",
  }
  return <Badge className={colors[status as keyof typeof colors] || colors.good}>{status.replace("_", " ")}</Badge>
}

const getConditionColor = (condition: string) => {
  switch (condition) {
    case "clear":
      return "text-accent"
    case "rainy":
      return "text-primary"
    case "foggy":
      return "text-destructive"
    case "cloudy":
      return "text-chart-4"
    default:
      return "text-muted-foreground"
  }
}

export function TrackMap() {
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

  if (loading) {
    return (
      <Card className="bg-card border-border">
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="text-lg font-semibold text-card-foreground flex items-center">
            <MapPin className="w-5 h-5 mr-2" />
            Network Track Map
          </CardTitle>
          <div className="flex space-x-2">
            <div className="h-8 w-20 bg-muted rounded"></div>
            <div className="h-8 w-20 bg-muted rounded"></div>
            <div className="h-8 w-20 bg-muted rounded"></div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="relative bg-muted rounded-lg h-96 mb-4 flex items-center justify-center">
            <div className="text-center">
              <MapPin className="w-12 h-12 text-muted-foreground mx-auto mb-2" />
              <p className="text-muted-foreground">Loading track data...</p>
            </div>
          </div>
          <div className="space-y-3">
            <div className="h-4 bg-muted rounded w-24"></div>
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div key={i} className="h-16 bg-muted rounded"></div>
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  const trackSections = Object.entries(tracks).map(([id, track]) => ({
    id: track.id,
    name: `Track ${track.id} - ${track.capacity} capacity`,
    status: track.maintenance_status,
    utilization: Math.round(track.utilization * 100),
    length: `${track.length} km`,
    condition: track.weather_condition,
    lastMaintenance: "2024-01-15", // This would come from backend
    speedLimit: track.speed_limit,
    signalStatus: track.signal_status
  }))

  return (
    <Card className="bg-card border-border">
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="text-lg font-semibold text-card-foreground flex items-center">
          <MapPin className="w-5 h-5 mr-2" />
          Network Track Map
        </CardTitle>
        <div className="flex space-x-2">
          <Button variant="outline" size="sm">
            <ZoomIn className="w-4 h-4 mr-2" />
            Zoom In
          </Button>
          <Button variant="outline" size="sm">
            <ZoomOut className="w-4 h-4 mr-2" />
            Zoom Out
          </Button>
          <Button variant="outline" size="sm">
            <Layers className="w-4 h-4 mr-2" />
            Layers
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {/* Map Placeholder - In a real app, this would be an interactive map */}
        <div className="relative bg-muted rounded-lg h-96 mb-4 flex items-center justify-center">
          <div className="text-center">
            <MapPin className="w-12 h-12 text-muted-foreground mx-auto mb-2" />
            <p className="text-muted-foreground">Interactive Track Network Map</p>
            <p className="text-sm text-muted-foreground">Real-time track status and conditions</p>
          </div>
        </div>

        {/* Track Sections List */}
        <div className="space-y-3">
          <h4 className="text-sm font-semibold text-foreground">Track Sections ({trackSections.length} active)</h4>
          {trackSections.map((section) => (
            <div key={section.id} className="flex items-center justify-between p-3 rounded-lg bg-muted">
              <div className="flex-1">
                <div className="flex items-center space-x-2 mb-1">
                  <span className="font-semibold text-foreground">{section.id}</span>
                  {getStatusBadge(section.status)}
                </div>
                <p className="text-sm text-muted-foreground">{section.name}</p>
                <div className="flex items-center space-x-4 mt-1 text-xs text-muted-foreground">
                  <span>Length: {section.length}</span>
                  <span>Utilization: {section.utilization}%</span>
                  <span className={getConditionColor(section.condition)}>Weather: {section.condition}</span>
                  <span>Speed: {section.speedLimit} km/h</span>
                </div>
              </div>
              <div className="text-right">
                <p className="text-xs text-muted-foreground">Signal Status</p>
                <p className="text-sm font-medium text-foreground capitalize">{section.signalStatus}</p>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
