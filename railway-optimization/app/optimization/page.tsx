import { Sidebar } from "@/components/dashboard/sidebar"
import { Header } from "@/components/dashboard/header"
import { AIOptimizationOverview } from "@/components/optimization/ai-optimization-overview"
import { OptimizationModels } from "@/components/optimization/optimization-models"
import { OptimizationResults } from "@/components/optimization/optimization-results"
import { OptimizationControls } from "@/components/optimization/optimization-controls"
import { MaintenancePredictions } from "@/components/ml/maintenance-predictions"

export default function OptimizationPage() {
  return (
    <div className="flex h-screen bg-background">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-auto p-6">
          <div className="space-y-6">
            <div>
              <h1 className="text-3xl font-bold text-foreground">AI Optimization Center</h1>
              <p className="text-muted-foreground">
                Intelligent traffic optimization and predictive analytics for enhanced railway operations
              </p>
            </div>

            <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
              <div className="xl:col-span-2 space-y-6">
                <OptimizationResults />
                <OptimizationModels />
                <MaintenancePredictions />
              </div>
              <div className="space-y-6">
                <AIOptimizationOverview />
                <OptimizationControls />
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}
