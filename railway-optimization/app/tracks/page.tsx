import { Sidebar } from "@/components/dashboard/sidebar"
import { Header } from "@/components/dashboard/header"
import { TrackOverview } from "@/components/tracks/track-overview"
import { TrackMap } from "@/components/tracks/track-map"
import { MaintenanceSchedule } from "@/components/tracks/maintenance-schedule"
import { TrackAlerts } from "@/components/tracks/track-alerts"

export default function TracksPage() {
  return (
    <div className="flex h-screen bg-background">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-auto p-6">
          <div className="space-y-6">
            <div>
              <h1 className="text-3xl font-bold text-foreground">Track Management</h1>
              <p className="text-muted-foreground">
                Monitor track conditions, maintenance, and capacity across the network
              </p>
            </div>

            <TrackOverview />

            <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
              <div className="xl:col-span-2">
                <TrackMap />
              </div>
              <div className="space-y-6">
                <TrackAlerts />
                <MaintenanceSchedule />
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}
