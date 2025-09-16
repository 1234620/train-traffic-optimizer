"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { Slider } from "@/components/ui/slider"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Settings, Play, Pause, RefreshCw } from "lucide-react"

export function OptimizationControls() {
  return (
    <div className="space-y-6">
      {/* Control Panel */}
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle className="text-lg font-semibold text-card-foreground flex items-center">
            <Settings className="w-5 h-5 mr-2" />
            Optimization Controls
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Auto Optimization Toggle */}
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label className="text-sm font-medium">Auto Optimization</Label>
              <p className="text-xs text-muted-foreground">Enable automatic AI-driven optimizations</p>
            </div>
            <Switch defaultChecked />
          </div>

          {/* Optimization Intensity */}
          <div className="space-y-2">
            <Label className="text-sm font-medium">Optimization Intensity</Label>
            <Slider defaultValue={[75]} max={100} step={1} className="w-full" />
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>Conservative</span>
              <span>Aggressive</span>
            </div>
          </div>

          {/* Priority Focus */}
          <div className="space-y-2">
            <Label className="text-sm font-medium">Priority Focus</Label>
            <Select defaultValue="balanced">
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="speed">Speed Optimization</SelectItem>
                <SelectItem value="capacity">Capacity Maximization</SelectItem>
                <SelectItem value="energy">Energy Efficiency</SelectItem>
                <SelectItem value="balanced">Balanced Approach</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Manual Controls */}
          <div className="space-y-3 pt-4 border-t border-border">
            <Label className="text-sm font-medium">Manual Controls</Label>
            <div className="grid grid-cols-2 gap-2">
              <Button variant="outline" size="sm">
                <Play className="w-4 h-4 mr-2" />
                Start
              </Button>
              <Button variant="outline" size="sm">
                <Pause className="w-4 h-4 mr-2" />
                Pause
              </Button>
            </div>
            <Button variant="outline" size="sm" className="w-full bg-transparent">
              <RefreshCw className="w-4 h-4 mr-2" />
              Reset Models
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* System Status */}
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle className="text-lg font-semibold text-card-foreground">System Status</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-sm text-card-foreground">AI Engine</span>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-accent rounded-full animate-pulse" />
              <span className="text-sm text-accent">Active</span>
            </div>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-card-foreground">Model Training</span>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-chart-4 rounded-full animate-pulse" />
              <span className="text-sm text-chart-4">In Progress</span>
            </div>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-card-foreground">Data Pipeline</span>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-accent rounded-full animate-pulse" />
              <span className="text-sm text-accent">Operational</span>
            </div>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-card-foreground">Optimization Queue</span>
            <span className="text-sm text-muted-foreground">23 pending</span>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
