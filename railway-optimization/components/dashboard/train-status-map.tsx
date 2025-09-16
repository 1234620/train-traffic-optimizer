"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { MapPin, Clock } from "lucide-react"
import { useState, useEffect } from "react"
import { fetchApi } from "@/lib/utils"

interface Train {
  id: string
  name: string
  current_track: string
  speed: number
  position: number
  destination: string
  priority: string
  passengers: number
  delay: number
  status: string
  efficiency: number
  fuel_level: number
  maintenance_due: boolean
  route: string[]
  estimated_arrival: string
}

export function TrainStatusMap() {
  const [trains, setTrains] = useState<Train[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const loadTrains = async () => {
      try {
        const data = await fetchApi<Train[]>("/api/trains")
        setTrains(data)
      } catch (error) {
        console.error("Failed to load trains:", error)
        // Fallback data
        setTrains([
          { id: "T001", name: "Rajdhani Express", current_track: "T1", speed: 115, position: 45, destination: "J1", priority: "high", passengers: 1200, delay: 0, status: "on_time", efficiency: 0.92, fuel_level: 85.5, maintenance_due: false, route: ["T1", "T2", "T3"], estimated_arrival: new Date().toISOString() },
          { id: "T002", name: "Shatabdi Express", current_track: "T2", speed: 95, position: 30, destination: "J2", priority: "high", passengers: 800, delay: 15, status: "delayed", efficiency: 0.78, fuel_level: 72.3, maintenance_due: true, route: ["T2", "T3", "T4"], estimated_arrival: new Date().toISOString() },
          { id: "T003", name: "Duronto Express", current_track: "T3", speed: 105, position: 80, destination: "J3", priority: "medium", passengers: 1500, delay: 0, status: "on_time", efficiency: 0.88, fuel_level: 91.2, maintenance_due: false, route: ["T3", "T4", "T5"], estimated_arrival: new Date().toISOString() },
          { id: "T004", name: "Mail Express", current_track: "T4", speed: 85, position: 20, destination: "J3", priority: "low", passengers: 2000, delay: 5, status: "on_time", efficiency: 0.82, fuel_level: 68.7, maintenance_due: false, route: ["T4", "T5", "T6"], estimated_arrival: new Date().toISOString() },
          { id: "T005", name: "Tejas Express", current_track: "T5", speed: 125, position: 60, destination: "J4", priority: "high", passengers: 600, delay: -3, status: "early", efficiency: 0.95, fuel_level: 88.9, maintenance_due: false, route: ["T5", "T6"], estimated_arrival: new Date().toISOString() }
        ])
      } finally {
        setLoading(false)
      }
    }

    loadTrains()
    const interval = setInterval(loadTrains, 5000)
    return () => clearInterval(interval)
  }, [])

  const getStatusDisplay = (status: string) => {
    switch (status) {
      case "on_time": return "on-time"
      case "delayed": return "delayed"
      case "early": return "early"
      case "cancelled": return "cancelled"
      case "maintenance": return "maintenance"
      default: return "unknown"
    }
  }

  const getLocationDisplay = (train: Train) => {
    const trackNames: { [key: string]: string } = {
      "T1": "Mumbai-Delhi Line",
      "T2": "Chennai-Kolkata Line", 
      "T3": "Bangalore-Hyderabad Line",
      "T4": "Delhi-Amritsar Line",
      "T5": "Pune-Goa Line",
      "T6": "Kolkata-Guwahati Line"
    }
    return `${trackNames[train.current_track] || train.current_track} (${Math.round(train.position)}%)`
  }

  if (loading) {
    return (
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle className="text-lg font-semibold text-card-foreground flex items-center">
            <MapPin className="w-5 h-5 mr-2" />
            Live Train Status
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center p-8">
            <div className="text-muted-foreground">Loading train data...</div>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="bg-card border-border">
      <CardHeader>
        <CardTitle className="text-lg font-semibold text-card-foreground flex items-center">
          <MapPin className="w-5 h-5 mr-2" />
          Live Train Status
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {trains.slice(0, 5).map((train) => (
            <div key={train.id} className="flex items-center justify-between p-3 rounded-lg bg-muted">
              <div className="flex-1">
                <div className="flex items-center space-x-2 mb-1">
                  <span className="font-semibold text-foreground">{train.id}</span>
                  <Badge
                    variant={train.status === "on_time" ? "default" : "destructive"}
                    className={
                      train.status === "on_time"
                        ? "bg-accent text-accent-foreground"
                        : train.status === "early"
                        ? "bg-green-500 text-white"
                        : "bg-destructive text-destructive-foreground"
                    }
                  >
                    {getStatusDisplay(train.status)}
                  </Badge>
                </div>
                <p className="text-sm text-muted-foreground">{train.name}</p>
                <p className="text-xs text-muted-foreground flex items-center mt-1">
                  <MapPin className="w-3 h-3 mr-1" />
                  {getLocationDisplay(train)}
                </p>
              </div>
              <div className="text-right">
                {train.delay > 0 ? (
                  <div className="flex items-center text-destructive">
                    <Clock className="w-4 h-4 mr-1" />
                    <span className="text-sm font-medium">+{train.delay}m</span>
                  </div>
                ) : train.delay < 0 ? (
                  <div className="flex items-center text-green-500">
                    <Clock className="w-4 h-4 mr-1" />
                    <span className="text-sm font-medium">{Math.abs(train.delay)}m early</span>
                  </div>
                ) : (
                  <div className="flex items-center text-accent">
                    <Clock className="w-4 h-4 mr-1" />
                    <span className="text-sm font-medium">On Time</span>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
