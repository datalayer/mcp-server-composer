import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { api } from '../api/client'
import {
  LineChart, Line, AreaChart, Area, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts'
import { Activity, TrendingUp, TrendingDown, Clock, Zap, Server, AlertCircle } from 'lucide-react'

interface MetricsData {
  timestamp: string
  requests: number
  tools: number
  latency: number
  memory: number
  cpu: number
}

export default function Metrics() {
  const [timeRange, setTimeRange] = useState<'1h' | '6h' | '24h' | '7d'>('1h')
  const [metricsHistory, setMetricsHistory] = useState<MetricsData[]>([])

  // Fetch current metrics
  const { data: metrics, isLoading } = useQuery({
    queryKey: ['metrics'],
    queryFn: () => api.getMetrics().then(res => res.data),
    refetchInterval: 5000,
  })

  const { data: status } = useQuery({
    queryKey: ['status'],
    queryFn: () => api.getStatus().then(res => res.data),
    refetchInterval: 5000,
  })

  // Build metrics history for charts
  useEffect(() => {
    if (metrics) {
      const now = new Date()
      const newDataPoint: MetricsData = {
        timestamp: now.toLocaleTimeString(),
        requests: metrics.http_requests_total || 0,
        tools: metrics.tool_invocations_total || 0,
        latency: Math.random() * 100 + 20, // Mock latency
        memory: Math.random() * 50 + 30, // Mock memory %
        cpu: Math.random() * 40 + 10, // Mock CPU %
      }

      setMetricsHistory(prev => {
        const updated = [...prev, newDataPoint]
        // Keep last 60 data points
        return updated.slice(-60)
      })
    }
  }, [metrics])

  // Calculate trends
  const calculateTrend = (current: number, previous: number): { value: number; isUp: boolean } => {
    if (!previous) return { value: 0, isUp: true }
    const diff = ((current - previous) / previous) * 100
    return { value: Math.abs(diff), isUp: diff > 0 }
  }

  const requestsTrend = metricsHistory.length > 1
    ? calculateTrend(
        metricsHistory[metricsHistory.length - 1].requests,
        metricsHistory[metricsHistory.length - 2].requests
      )
    : { value: 0, isUp: true }

  const toolsTrend = metricsHistory.length > 1
    ? calculateTrend(
        metricsHistory[metricsHistory.length - 1].tools,
        metricsHistory[metricsHistory.length - 2].tools
      )
    : { value: 0, isUp: true }

  const avgLatency = metricsHistory.length > 0
    ? metricsHistory.reduce((sum, m) => sum + m.latency, 0) / metricsHistory.length
    : 0

  const avgCpu = metricsHistory.length > 0
    ? metricsHistory.reduce((sum, m) => sum + m.cpu, 0) / metricsHistory.length
    : 0

  const avgMemory = metricsHistory.length > 0
    ? metricsHistory.reduce((sum, m) => sum + m.memory, 0) / metricsHistory.length
    : 0

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Activity className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Metrics</h1>
          <p className="mt-2 text-muted-foreground">
            System performance and usage statistics
          </p>
        </div>
        <div className="flex items-center gap-2">
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value as any)}
            className="px-4 py-2 bg-background border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-ring"
          >
            <option value="1h">Last Hour</option>
            <option value="6h">Last 6 Hours</option>
            <option value="24h">Last 24 Hours</option>
            <option value="7d">Last 7 Days</option>
          </select>
        </div>
      </div>

      {/* Key Metrics Cards */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <div className="bg-card border border-border rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Total Requests</p>
              <p className="text-3xl font-bold mt-2">{metrics?.http_requests_total || 0}</p>
              <div className="flex items-center gap-1 mt-2">
                {requestsTrend.isUp ? (
                  <TrendingUp className="h-4 w-4 text-green-500" />
                ) : (
                  <TrendingDown className="h-4 w-4 text-red-500" />
                )}
                <span className={`text-sm ${requestsTrend.isUp ? 'text-green-500' : 'text-red-500'}`}>
                  {requestsTrend.value.toFixed(1)}%
                </span>
              </div>
            </div>
            <div className="p-3 bg-blue-500/10 rounded-lg">
              <Activity className="h-6 w-6 text-blue-500" />
            </div>
          </div>
        </div>

        <div className="bg-card border border-border rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Tool Invocations</p>
              <p className="text-3xl font-bold mt-2">{metrics?.tool_invocations_total || 0}</p>
              <div className="flex items-center gap-1 mt-2">
                {toolsTrend.isUp ? (
                  <TrendingUp className="h-4 w-4 text-green-500" />
                ) : (
                  <TrendingDown className="h-4 w-4 text-red-500" />
                )}
                <span className={`text-sm ${toolsTrend.isUp ? 'text-green-500' : 'text-red-500'}`}>
                  {toolsTrend.value.toFixed(1)}%
                </span>
              </div>
            </div>
            <div className="p-3 bg-purple-500/10 rounded-lg">
              <Zap className="h-6 w-6 text-purple-500" />
            </div>
          </div>
        </div>

        <div className="bg-card border border-border rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Avg Latency</p>
              <p className="text-3xl font-bold mt-2">{avgLatency.toFixed(0)}ms</p>
              <p className="text-sm text-muted-foreground mt-2">Response time</p>
            </div>
            <div className="p-3 bg-yellow-500/10 rounded-lg">
              <Clock className="h-6 w-6 text-yellow-500" />
            </div>
          </div>
        </div>

        <div className="bg-card border border-border rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Active Servers</p>
              <p className="text-3xl font-bold mt-2">{status?.servers_running || 0}</p>
              <p className="text-sm text-muted-foreground mt-2">
                of {status?.servers_total || 0} total
              </p>
            </div>
            <div className="p-3 bg-green-500/10 rounded-lg">
              <Server className="h-6 w-6 text-green-500" />
            </div>
          </div>
        </div>
      </div>

      {/* Request Rate Chart */}
      <div className="bg-card border border-border rounded-lg p-6">
        <h2 className="text-xl font-bold mb-4">Request Rate Over Time</h2>
        {metricsHistory.length > 0 ? (
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={metricsHistory}>
              <defs>
                <linearGradient id="colorRequests" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#333" />
              <XAxis dataKey="timestamp" stroke="#888" />
              <YAxis stroke="#888" />
              <Tooltip
                contentStyle={{ backgroundColor: '#1f1f1f', border: '1px solid #333' }}
                labelStyle={{ color: '#fff' }}
              />
              <Legend />
              <Area
                type="monotone"
                dataKey="requests"
                stroke="#3b82f6"
                fillOpacity={1}
                fill="url(#colorRequests)"
                name="Requests"
              />
            </AreaChart>
          </ResponsiveContainer>
        ) : (
          <div className="flex items-center justify-center h-[300px] text-muted-foreground">
            <div className="text-center">
              <AlertCircle className="h-12 w-12 mx-auto mb-4" />
              <p>Collecting metrics data...</p>
            </div>
          </div>
        )}
      </div>

      {/* Tool Invocations and Latency */}
      <div className="grid gap-6 md:grid-cols-2">
        <div className="bg-card border border-border rounded-lg p-6">
          <h2 className="text-xl font-bold mb-4">Tool Invocations</h2>
          {metricsHistory.length > 0 ? (
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={metricsHistory.slice(-20)}>
                <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                <XAxis dataKey="timestamp" stroke="#888" />
                <YAxis stroke="#888" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1f1f1f', border: '1px solid #333' }}
                  labelStyle={{ color: '#fff' }}
                />
                <Bar dataKey="tools" fill="#a855f7" name="Invocations" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-[250px] text-muted-foreground">
              <p>No data available</p>
            </div>
          )}
        </div>

        <div className="bg-card border border-border rounded-lg p-6">
          <h2 className="text-xl font-bold mb-4">Response Latency</h2>
          {metricsHistory.length > 0 ? (
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={metricsHistory.slice(-20)}>
                <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                <XAxis dataKey="timestamp" stroke="#888" />
                <YAxis stroke="#888" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1f1f1f', border: '1px solid #333' }}
                  labelStyle={{ color: '#fff' }}
                />
                <Line
                  type="monotone"
                  dataKey="latency"
                  stroke="#eab308"
                  strokeWidth={2}
                  dot={false}
                  name="Latency (ms)"
                />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-[250px] text-muted-foreground">
              <p>No data available</p>
            </div>
          )}
        </div>
      </div>

      {/* System Resources */}
      <div className="bg-card border border-border rounded-lg p-6">
        <h2 className="text-xl font-bold mb-4">System Resources</h2>
        {metricsHistory.length > 0 ? (
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={metricsHistory}>
              <CartesianGrid strokeDasharray="3 3" stroke="#333" />
              <XAxis dataKey="timestamp" stroke="#888" />
              <YAxis stroke="#888" />
              <Tooltip
                contentStyle={{ backgroundColor: '#1f1f1f', border: '1px solid #333' }}
                labelStyle={{ color: '#fff' }}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="cpu"
                stroke="#10b981"
                strokeWidth={2}
                dot={false}
                name="CPU %"
              />
              <Line
                type="monotone"
                dataKey="memory"
                stroke="#f59e0b"
                strokeWidth={2}
                dot={false}
                name="Memory %"
              />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <div className="flex items-center justify-center h-[300px] text-muted-foreground">
            <div className="text-center">
              <AlertCircle className="h-12 w-12 mx-auto mb-4" />
              <p>Collecting resource metrics...</p>
            </div>
          </div>
        )}
      </div>

      {/* Performance Summary */}
      <div className="grid gap-6 md:grid-cols-3">
        <div className="bg-card border border-border rounded-lg p-6">
          <h3 className="font-semibold mb-2">Average CPU Usage</h3>
          <p className="text-3xl font-bold text-green-500">{avgCpu.toFixed(1)}%</p>
          <div className="mt-2 h-2 bg-muted rounded-full overflow-hidden">
            <div
              className="h-full bg-green-500 transition-all duration-300"
              style={{ width: `${Math.min(avgCpu, 100)}%` }}
            />
          </div>
        </div>

        <div className="bg-card border border-border rounded-lg p-6">
          <h3 className="font-semibold mb-2">Average Memory Usage</h3>
          <p className="text-3xl font-bold text-orange-500">{avgMemory.toFixed(1)}%</p>
          <div className="mt-2 h-2 bg-muted rounded-full overflow-hidden">
            <div
              className="h-full bg-orange-500 transition-all duration-300"
              style={{ width: `${Math.min(avgMemory, 100)}%` }}
            />
          </div>
        </div>

        <div className="bg-card border border-border rounded-lg p-6">
          <h3 className="font-semibold mb-2">Uptime</h3>
          <p className="text-3xl font-bold text-blue-500">{status?.uptime || '0m'}</p>
          <p className="text-sm text-muted-foreground mt-2">System running</p>
        </div>
      </div>
    </div>
  )
}
