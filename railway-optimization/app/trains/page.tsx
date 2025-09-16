import { Sidebar } from "@/components/dashboard/sidebar"
import { Header } from "@/components/dashboard/header"
import { TrainList } from "@/components/trains/train-list"
import { TrainFilters } from "@/components/trains/train-filters"
import { TrainStats } from "@/components/trains/train-stats"

export default function TrainsPage() {
  return (
    <div className="flex h-screen bg-background">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-auto p-6">
          <div className="space-y-6">
            <div>
              <h1 className="text-3xl font-bold text-foreground">Train Management</h1>
              <p className="text-muted-foreground">Monitor and manage all trains across the network</p>
            </div>

            <TrainStats />

            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
              <div className="lg:col-span-1">
                <TrainFilters />
              </div>
              <div className="lg:col-span-3">
                <TrainList />
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}
