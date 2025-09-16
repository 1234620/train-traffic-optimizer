"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { MoreHorizontal, MapPin, Clock, Users, Fuel } from "lucide-react"
import { useEffect, useState } from "react"
import { fetchApi } from "@/lib/utils"

interface ApiTrain {
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
  route: string[]
  estimated_arrival: string
}

const getStatusBadge = (status: string, delay: number) => {
  if (status === "on-time") {
    return <Badge className="bg-accent text-accent-foreground">On Time</Badge>
  } else if (delay > 0) {
    return <Badge className="bg-destructive text-destructive-foreground">Delayed {delay}m</Badge>
  }
  return <Badge variant="secondary">{status}</Badge>
}

const getPriorityBadge = (priority: string) => {
  const colors = {
    high: "bg-destructive text-destructive-foreground",
    medium: "bg-chart-4 text-white",
    low: "bg-secondary text-secondary-foreground",
  }
  return <Badge className={colors[priority as keyof typeof colors]}>{priority}</Badge>
}

export function TrainList() {
  const [trains, setTrains] = useState<ApiTrain[]>([])

  useEffect(() => {
    let mounted = true
    const load = async () => {
      try {
        const data = await fetchApi<ApiTrain[]>("/api/trains")
        if (mounted) setTrains(data)
      } catch (e) {
        // ignore
      }
    }
    load()
    const interval = setInterval(load, 10000)
    return () => {
      mounted = false
      clearInterval(interval)
    }
  }, [])
  return (
    <Card className="bg-card border-border">
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="text-lg font-semibold text-card-foreground">Active Trains</CardTitle>
        <div className="flex space-x-2">
          <Button variant="outline" size="sm">
            Export
          </Button>
          <Button size="sm">Add Train</Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Train Details</TableHead>
                <TableHead>Route</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Location</TableHead>
                <TableHead>Passengers</TableHead>
                <TableHead>Fuel</TableHead>
                <TableHead>Priority</TableHead>
                <TableHead className="w-[50px]"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {trains.map((train) => (
                <TableRow key={train.id}>
                  <TableCell>
                    <div>
                      <div className="font-medium text-foreground">{train.id}</div>
                      <div className="text-sm text-muted-foreground">{train.name}</div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="text-sm">
                      <div className="font-medium text-foreground">{train.route.join(" → ")}</div>
                      <div className="text-muted-foreground flex items-center mt-1">
                        <Clock className="w-3 h-3 mr-1" />
                        ETA: {new Date(train.estimated_arrival).toLocaleTimeString()}
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>{getStatusBadge(train.status.replace("_", "-"), train.delay)}</TableCell>
                  <TableCell>
                    <div className="text-sm">
                      <div className="font-medium text-foreground flex items-center">
                        <MapPin className="w-3 h-3 mr-1" />
                        Track {train.current_track} @ {Math.round(train.position)}%
                      </div>
                      <div className="text-muted-foreground mt-1">Dest: {train.destination}</div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="text-sm">
                      <div className="font-medium text-foreground flex items-center">
                        <Users className="w-3 h-3 mr-1" />
                        {train.passengers}
                      </div>
                      <div className="text-muted-foreground">
                        Priority: {train.priority}
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="text-sm">
                      <div className="font-medium text-foreground flex items-center">
                        <Fuel className="w-3 h-3 mr-1" />
                        {Math.round(train.fuel_level)}%
                      </div>
                      <div className={`text-xs ${train.fuel_level < 60 ? "text-destructive" : "text-muted-foreground"}`}>
                        {train.fuel_level < 60 ? "Low fuel" : "Normal"}
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>{getPriorityBadge(train.priority)}</TableCell>
                  <TableCell>
                    <Button variant="ghost" size="sm">
                      <MoreHorizontal className="w-4 h-4" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  )
}
