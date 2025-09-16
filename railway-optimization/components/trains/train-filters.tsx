"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Checkbox } from "@/components/ui/checkbox"
import { Search, Filter } from "lucide-react"

export function TrainFilters() {
  return (
    <Card className="bg-card border-border">
      <CardHeader>
        <CardTitle className="text-lg font-semibold text-card-foreground flex items-center">
          <Filter className="w-5 h-5 mr-2" />
          Filters
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Search */}
        <div className="space-y-2">
          <Label htmlFor="search" className="text-sm font-medium">
            Search Trains
          </Label>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input id="search" placeholder="Train ID, route..." className="pl-10" />
          </div>
        </div>

        {/* Status Filter */}
        <div className="space-y-2">
          <Label className="text-sm font-medium">Status</Label>
          <div className="space-y-2">
            {["On Time", "Delayed", "Cancelled", "Maintenance"].map((status) => (
              <div key={status} className="flex items-center space-x-2">
                <Checkbox id={status.toLowerCase().replace(" ", "-")} />
                <Label htmlFor={status.toLowerCase().replace(" ", "-")} className="text-sm">
                  {status}
                </Label>
              </div>
            ))}
          </div>
        </div>

        {/* Route Filter */}
        <div className="space-y-2">
          <Label className="text-sm font-medium">Route</Label>
          <Select>
            <SelectTrigger>
              <SelectValue placeholder="Select route" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="mumbai-delhi">Mumbai - Delhi</SelectItem>
              <SelectItem value="chennai-kolkata">Chennai - Kolkata</SelectItem>
              <SelectItem value="bangalore-hyderabad">Bangalore - Hyderabad</SelectItem>
              <SelectItem value="delhi-amritsar">Delhi - Amritsar</SelectItem>
              <SelectItem value="pune-goa">Pune - Goa</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Train Type */}
        <div className="space-y-2">
          <Label className="text-sm font-medium">Train Type</Label>
          <Select>
            <SelectTrigger>
              <SelectValue placeholder="Select type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="express">Express</SelectItem>
              <SelectItem value="superfast">Superfast</SelectItem>
              <SelectItem value="passenger">Passenger</SelectItem>
              <SelectItem value="freight">Freight</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Priority Filter */}
        <div className="space-y-2">
          <Label className="text-sm font-medium">Priority</Label>
          <div className="space-y-2">
            {["High", "Medium", "Low"].map((priority) => (
              <div key={priority} className="flex items-center space-x-2">
                <Checkbox id={priority.toLowerCase()} />
                <Label htmlFor={priority.toLowerCase()} className="text-sm">
                  {priority}
                </Label>
              </div>
            ))}
          </div>
        </div>

        <Button className="w-full">Apply Filters</Button>
        <Button variant="outline" className="w-full bg-transparent">
          Clear All
        </Button>
      </CardContent>
    </Card>
  )
}
