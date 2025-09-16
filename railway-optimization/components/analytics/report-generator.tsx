"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Checkbox } from "@/components/ui/checkbox"
import { Calendar } from "@/components/ui/calendar"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Badge } from "@/components/ui/badge"
import { FileText, Download, CalendarIcon, Clock, Send } from "lucide-react"
import { useState } from "react"
import { format } from "date-fns"

const reportTypes = [
  { id: "performance", name: "Performance Report", description: "Network efficiency and KPI analysis" },
  { id: "operational", name: "Operational Report", description: "Train operations and scheduling" },
  { id: "financial", name: "Financial Report", description: "Revenue and cost analysis" },
  { id: "safety", name: "Safety Report", description: "Incident and compliance tracking" },
]

const scheduledReports = [
  {
    id: 1,
    name: "Daily Operations Summary",
    type: "Operational",
    frequency: "Daily",
    nextRun: "2024-01-19 06:00",
    recipients: 3,
    status: "active",
  },
  {
    id: 2,
    name: "Weekly Performance Analysis",
    type: "Performance",
    frequency: "Weekly",
    nextRun: "2024-01-22 09:00",
    recipients: 5,
    status: "active",
  },
  {
    id: 3,
    name: "Monthly Financial Review",
    type: "Financial",
    frequency: "Monthly",
    nextRun: "2024-02-01 10:00",
    recipients: 8,
    status: "active",
  },
]

export function ReportGenerator() {
  const [date, setDate] = useState<Date>()

  return (
    <div className="space-y-6">
      {/* Report Generator */}
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle className="text-lg font-semibold text-card-foreground flex items-center">
            <FileText className="w-5 h-5 mr-2" />
            Generate Report
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Report Type */}
          <div className="space-y-2">
            <Label className="text-sm font-medium">Report Type</Label>
            <Select>
              <SelectTrigger>
                <SelectValue placeholder="Select report type" />
              </SelectTrigger>
              <SelectContent>
                {reportTypes.map((type) => (
                  <SelectItem key={type.id} value={type.id}>
                    <div>
                      <div className="font-medium">{type.name}</div>
                      <div className="text-xs text-muted-foreground">{type.description}</div>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Date Range */}
          <div className="space-y-2">
            <Label className="text-sm font-medium">Date Range</Label>
            <Popover>
              <PopoverTrigger asChild>
                <Button variant="outline" className="w-full justify-start text-left font-normal bg-transparent">
                  <CalendarIcon className="mr-2 h-4 w-4" />
                  {date ? format(date, "PPP") : "Pick a date"}
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-auto p-0">
                <Calendar mode="single" selected={date} onSelect={setDate} initialFocus />
              </PopoverContent>
            </Popover>
          </div>

          {/* Sections */}
          <div className="space-y-2">
            <Label className="text-sm font-medium">Include Sections</Label>
            <div className="space-y-2">
              {["Executive Summary", "Performance Metrics", "Trend Analysis", "Recommendations"].map((section) => (
                <div key={section} className="flex items-center space-x-2">
                  <Checkbox id={section.toLowerCase().replace(" ", "-")} defaultChecked />
                  <Label htmlFor={section.toLowerCase().replace(" ", "-")} className="text-sm">
                    {section}
                  </Label>
                </div>
              ))}
            </div>
          </div>

          {/* Format */}
          <div className="space-y-2">
            <Label className="text-sm font-medium">Format</Label>
            <Select defaultValue="pdf">
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="pdf">PDF Document</SelectItem>
                <SelectItem value="excel">Excel Spreadsheet</SelectItem>
                <SelectItem value="powerpoint">PowerPoint Presentation</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <Button className="w-full">
            <Download className="w-4 h-4 mr-2" />
            Generate Report
          </Button>
        </CardContent>
      </Card>

      {/* Scheduled Reports */}
      <Card className="bg-card border-border">
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="text-lg font-semibold text-card-foreground flex items-center">
            <Clock className="w-5 h-5 mr-2" />
            Scheduled Reports
          </CardTitle>
          <Button variant="outline" size="sm">
            <Send className="w-4 h-4 mr-2" />
            Schedule
          </Button>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {scheduledReports.map((report) => (
              <div key={report.id} className="p-3 rounded-lg bg-muted">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium text-foreground">{report.name}</h4>
                  <Badge className="bg-accent text-accent-foreground">{report.status}</Badge>
                </div>
                <div className="text-sm text-muted-foreground space-y-1">
                  <div className="flex justify-between">
                    <span>Type:</span>
                    <span className="text-foreground">{report.type}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Frequency:</span>
                    <span className="text-foreground">{report.frequency}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Next Run:</span>
                    <span className="text-foreground">{report.nextRun}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Recipients:</span>
                    <span className="text-foreground">{report.recipients} users</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
