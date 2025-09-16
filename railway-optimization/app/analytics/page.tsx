import { Sidebar } from "@/components/dashboard/sidebar"
import { Header } from "@/components/dashboard/header"
import { AnalyticsOverview } from "@/components/analytics/analytics-overview"
import { PerformanceCharts } from "@/components/analytics/performance-charts"
import { ReportGenerator } from "@/components/analytics/report-generator"
import { KPIDashboard } from "@/components/analytics/kpi-dashboard"

export default function AnalyticsPage() {
  return (
    <div className="flex h-screen bg-background">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-auto p-6">
          <div className="space-y-6">
            <div>
              <h1 className="text-3xl font-bold text-foreground">Analytics & Reporting</h1>
              <p className="text-muted-foreground">
                Comprehensive performance analytics and automated reporting for railway operations
              </p>
            </div>

            <AnalyticsOverview />

            <div className="grid grid-cols-1 xl:grid-cols-4 gap-6">
              <div className="xl:col-span-3 space-y-6">
                <PerformanceCharts />
                <KPIDashboard />
              </div>
              <div>
                <ReportGenerator />
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}
