import { Sidebar } from "@/components/dashboard/sidebar"
import { Header } from "@/components/dashboard/header"
import { DashboardMetrics } from "@/components/dashboard/dashboard-metrics"
import { TrainStatusMap } from "@/components/dashboard/train-status-map"
import { RecentAlerts } from "@/components/dashboard/recent-alerts"
import { SystemOverview } from "@/components/dashboard/system-overview"
import { RealTimeFeed } from "@/components/dashboard/real-time-feed"
import { NetworkStatus } from "@/components/dashboard/network-status"
import { LiveMetrics } from "@/components/dashboard/live-metrics"

export default function DashboardPage() {
  return (
    <div className="flex h-screen bg-background">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-auto p-6">
          <div className="space-y-6">
            <LiveMetrics />

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
              <div className="lg:col-span-2">
                <DashboardMetrics />
              </div>
              <div>
                <SystemOverview />
              </div>
            </div>

            <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
              <TrainStatusMap />
              <RecentAlerts />
              <RealTimeFeed />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <NetworkStatus />
              <div className="bg-muted rounded-lg p-6 flex items-center justify-center">
                <div className="text-center">
                  <div className="text-2xl font-bold text-foreground mb-2">Real-time Monitoring Active</div>
                  <p className="text-muted-foreground">All systems are being monitored continuously</p>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}
