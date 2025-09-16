"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Radio, Pause, Play, Settings } from "lucide-react"
import { useState, useEffect } from "react"

interface LiveEvent {
  id: string
  timestamp: string
  type: "train" | "track" | "signal" | "alert"
  severity: "info" | "warning" | "critical"
  title: string
  description: string
  location?: string
}

const mockEvents: LiveEvent[] = [
  {
    id: "1",
    timestamp: new Date().toISOString(),
    type: "train",
    severity: "info",
    title: "Train T-2401 Departed",
    description: "Rajdhani Express departed Mumbai Central on schedule",
    location: "Mumbai Central",
  },
  {
    id: "2",
    timestamp: new Date(Date.now() - 120000).toISOString(),
    type: "alert",
    severity: "warning",
    title: "Platform Overcrowding",
    description: "Platform 7 at Delhi Junction exceeding capacity",
    location: "Delhi Junction",
  },
  {
    id: "3",
    timestamp: new Date(Date.now() - 300000).toISOString(),
    type: "signal",
    severity: "critical",
    title: "Signal Failure",
    description: "Signal system malfunction at Junction 45",
    location: "Junction 45",
  },
]

const getEventIcon = (type: string) => {
  switch (type) {
    case "train":
      return "🚂"
    case "track":
      return "🛤️"
    case "signal":
      return "🚦"
    case "alert":
      return "⚠️"
    default:
      return "ℹ️"
  }
}

const getSeverityBadge = (severity: string) => {
  const colors = {
    info: "bg-primary text-primary-foreground",
    warning: "bg-chart-4 text-white",
    critical: "bg-destructive text-destructive-foreground",
  }
  return <Badge className={colors[severity as keyof typeof colors]}>{severity}</Badge>
}

export function RealTimeFeed() {
  const [events, setEvents] = useState<LiveEvent[]>(mockEvents)
  const [isLive, setIsLive] = useState(true)

  useEffect(() => {
    if (!isLive) return

    const interval = setInterval(() => {
      const newEvent: LiveEvent = {
        id: Date.now().toString(),
        timestamp: new Date().toISOString(),
        type: ["train", "track", "signal", "alert"][Math.floor(Math.random() * 4)] as any,
        severity: ["info", "warning", "critical"][Math.floor(Math.random() * 3)] as any,
        title: "Live Event Update",
        description: "Real-time system update from network monitoring",
        location: "Network Node " + Math.floor(Math.random() * 100),
      }

      setEvents((prev) => [newEvent, ...prev.slice(0, 19)])
    }, 5000)

    return () => clearInterval(interval)
  }, [isLive])

  return (
    <Card className="bg-card border-border">
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="text-lg font-semibold text-card-foreground flex items-center">
          <Radio className="w-5 h-5 mr-2" />
          Live Event Feed
          {isLive && <div className="w-2 h-2 bg-accent rounded-full animate-pulse ml-2" />}
        </CardTitle>
        <div className="flex space-x-2">
          <Button variant="outline" size="sm" onClick={() => setIsLive(!isLive)}>
            {isLive ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
          </Button>
          <Button variant="outline" size="sm">
            <Settings className="w-4 h-4" />
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-80">
          <div className="space-y-3">
            {events.map((event) => (
              <div key={event.id} className="flex items-start space-x-3 p-3 rounded-lg bg-muted">
                <div className="text-lg">{getEventIcon(event.type)}</div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2 mb-1">
                    <h4 className="text-sm font-medium text-foreground">{event.title}</h4>
                    {getSeverityBadge(event.severity)}
                  </div>
                  <p className="text-sm text-muted-foreground mb-1">{event.description}</p>
                  <div className="flex items-center justify-between text-xs text-muted-foreground">
                    <span>{event.location}</span>
                    <span>{new Date(event.timestamp).toLocaleTimeString()}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  )
}
