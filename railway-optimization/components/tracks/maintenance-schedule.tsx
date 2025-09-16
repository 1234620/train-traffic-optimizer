"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Calendar, Clock, Wrench } from "lucide-react"

const maintenanceSchedule = [
  {
    id: 1,
    section: "SEC-006",
    name: "Jaipur-Ajmer Line",
    type: "Track Renewal",
    startDate: "2024-01-20",
    duration: "72 hours",
    status: "scheduled",
    crew: "Team Alpha",
  },
  {
    id: 2,
    section: "SEC-007",
    name: "Lucknow-Kanpur Route",
    type: "Signal Maintenance",
    startDate: "2024-01-22",
    duration: "24 hours",
    status: "scheduled",
    crew: "Team Beta",
  },
  {
    id: 3,
    section: "SEC-002",
    name: "Delhi-Agra Section",
    type: "Rail Replacement",
    startDate: "2024-01-18",
    duration: "96 hours",
    status: "in-progress",
    crew: "Team Gamma",
  },
  {
    id: 4,
    section: "SEC-008",
    name: "Surat-Vadodara Line",
    type: "Routine Inspection",
    startDate: "2024-01-25",
    duration: "8 hours",
    status: "scheduled",
    crew: "Team Delta",
  },
]

const getStatusBadge = (status: string) => {
  const colors = {
    scheduled: "bg-accent text-accent-foreground",
    "in-progress": "bg-chart-4 text-white",
    completed: "bg-secondary text-secondary-foreground",
  }
  return <Badge className={colors[status as keyof typeof colors]}>{status}</Badge>
}

export function MaintenanceSchedule() {
  return (
    <Card className="bg-card border-border">
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="text-lg font-semibold text-card-foreground flex items-center">
          <Wrench className="w-5 h-5 mr-2" />
          Maintenance Schedule
        </CardTitle>
        <Button variant="outline" size="sm">
          <Calendar className="w-4 h-4 mr-2" />
          Schedule
        </Button>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {maintenanceSchedule.map((maintenance) => (
            <div key={maintenance.id} className="p-3 rounded-lg bg-muted">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center space-x-2">
                  <span className="font-semibold text-foreground">{maintenance.section}</span>
                  {getStatusBadge(maintenance.status)}
                </div>
                <span className="text-xs text-muted-foreground">{maintenance.crew}</span>
              </div>
              <p className="text-sm text-muted-foreground mb-2">{maintenance.name}</p>
              <div className="flex items-center justify-between text-xs">
                <div className="flex items-center space-x-4">
                  <span className="text-primary font-medium">{maintenance.type}</span>
                  <div className="flex items-center text-muted-foreground">
                    <Calendar className="w-3 h-3 mr-1" />
                    {maintenance.startDate}
                  </div>
                  <div className="flex items-center text-muted-foreground">
                    <Clock className="w-3 h-3 mr-1" />
                    {maintenance.duration}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
