import { useQuery } from '@tanstack/react-query'
import api from '../api/client'
import { Activity, Server, Wrench, AlertCircle } from 'lucide-react'

export default function Dashboard() {
  const { data: status } = useQuery({
    queryKey: ['status'],
    queryFn: () => api.getStatus().then(res => res.data),
    refetchInterval: 5000,
  })

  const { data: health } = useQuery({
    queryKey: ['health'],
    queryFn: () => api.getHealth().then(res => res.data),
    refetchInterval: 5000,
  })

  const stats = [
    {
      name: 'Active Servers',
      value: status?.servers_running || 0,
      icon: Server,
      color: 'text-blue-600',
    },
    {
      name: 'Total Tools',
      value: status?.total_tools || 0,
      icon: Wrench,
      color: 'text-green-600',
    },
    {
      name: 'System Health',
      value: health?.status || 'unknown',
      icon: health?.status === 'healthy' ? Activity : AlertCircle,
      color: health?.status === 'healthy' ? 'text-green-600' : 'text-red-600',
    },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground">Dashboard</h1>
        <p className="mt-2 text-muted-foreground">
          Overview of your MCP Server Composer
        </p>
      </div>

      {/* Stats */}
      <div className="grid gap-6 md:grid-cols-3">
        {stats.map((stat) => {
          const Icon = stat.icon
          return (
            <div
              key={stat.name}
              className="bg-card border border-border rounded-lg p-6"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">
                    {stat.name}
                  </p>
                  <p className="mt-2 text-3xl font-bold text-foreground">
                    {stat.value}
                  </p>
                </div>
                <Icon className={`h-8 w-8 ${stat.color}`} />
              </div>
            </div>
          )
        })}
      </div>

      {/* Quick Info */}
      <div className="grid gap-6 md:grid-cols-2">
        <div className="bg-card border border-border rounded-lg p-6">
          <h2 className="text-lg font-semibold text-foreground mb-4">
            System Information
          </h2>
          <dl className="space-y-2">
            <div className="flex justify-between">
              <dt className="text-muted-foreground">Version</dt>
              <dd className="font-medium">{status?.version || 'N/A'}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-muted-foreground">Uptime</dt>
              <dd className="font-medium">{status?.uptime || 'N/A'}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-muted-foreground">Platform</dt>
              <dd className="font-medium">{status?.platform || 'N/A'}</dd>
            </div>
          </dl>
        </div>

        <div className="bg-card border border-border rounded-lg p-6">
          <h2 className="text-lg font-semibold text-foreground mb-4">
            Quick Actions
          </h2>
          <div className="space-y-2">
            <button className="w-full px-4 py-2 text-left rounded-md hover:bg-accent transition-colors">
              View All Servers
            </button>
            <button className="w-full px-4 py-2 text-left rounded-md hover:bg-accent transition-colors">
              Browse Tools
            </button>
            <button className="w-full px-4 py-2 text-left rounded-md hover:bg-accent transition-colors">
              Check Logs
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
