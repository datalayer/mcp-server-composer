import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../api/client'
import { Play, Square, RotateCw, Trash2, Plus, AlertCircle, CheckCircle, Loader2 } from 'lucide-react'
import { useState } from 'react'

interface Server {
  id: string
  name: string
  command: string
  args: string[]
  env: Record<string, string>
  transport: string
  state: string
  pid?: number
  uptime?: number
  restart_count?: number
}

export default function Servers() {
  const queryClient = useQueryClient()
  const [selectedServer, setSelectedServer] = useState<string | null>(null)
  const [showAddDialog, setShowAddDialog] = useState(false)

  // Fetch servers
  const { data: serversData, isLoading } = useQuery({
    queryKey: ['servers'],
    queryFn: () => api.listServers().then(res => res.data),
    refetchInterval: 5000,
  })

  const servers: Server[] = serversData?.servers || []

  // Mutations
  const startMutation = useMutation({
    mutationFn: (id: string) => api.startServer(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['servers'] })
    },
  })

  const stopMutation = useMutation({
    mutationFn: (id: string) => api.stopServer(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['servers'] })
    },
  })

  const restartMutation = useMutation({
    mutationFn: (id: string) => api.restartServer(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['servers'] })
    },
  })

  const getStatusColor = (state: string) => {
    switch (state?.toLowerCase()) {
      case 'running':
        return 'text-green-600'
      case 'stopped':
        return 'text-gray-500'
      case 'starting':
        return 'text-blue-600'
      case 'stopping':
        return 'text-yellow-600'
      case 'crashed':
        return 'text-red-600'
      default:
        return 'text-gray-500'
    }
  }

  const getStatusIcon = (state: string) => {
    switch (state?.toLowerCase()) {
      case 'running':
        return <CheckCircle className="h-5 w-5 text-green-600" />
      case 'starting':
      case 'stopping':
        return <Loader2 className="h-5 w-5 text-blue-600 animate-spin" />
      case 'crashed':
        return <AlertCircle className="h-5 w-5 text-red-600" />
      default:
        return <Square className="h-5 w-5 text-gray-500" />
    }
  }

  const formatUptime = (seconds?: number) => {
    if (!seconds) return 'N/A'
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    return `${hours}h ${minutes}m`
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Servers</h1>
          <p className="mt-2 text-muted-foreground">
            Manage your MCP servers
          </p>
        </div>
        <button
          onClick={() => setShowAddDialog(true)}
          className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
        >
          <Plus className="h-4 w-4" />
          Add Server
        </button>
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      )}

      {/* Server List */}
      {!isLoading && servers.length === 0 && (
        <div className="bg-card border border-border rounded-lg p-12 text-center">
          <p className="text-muted-foreground mb-4">No servers configured</p>
          <button
            onClick={() => setShowAddDialog(true)}
            className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
          >
            Add Your First Server
          </button>
        </div>
      )}

      {!isLoading && servers.length > 0 && (
        <div className="grid gap-4">
          {servers.map((server) => (
            <div
              key={server.id}
              className={`bg-card border rounded-lg p-6 transition-colors ${
                selectedServer === server.id
                  ? 'border-primary'
                  : 'border-border hover:border-muted-foreground'
              }`}
              onClick={() => setSelectedServer(server.id)}
            >
              <div className="flex items-start justify-between">
                {/* Server Info */}
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    {getStatusIcon(server.state)}
                    <h3 className="text-lg font-semibold text-foreground">
                      {server.name}
                    </h3>
                    <span className={`text-sm font-medium ${getStatusColor(server.state)}`}>
                      {server.state}
                    </span>
                  </div>
                  
                  <div className="space-y-1 text-sm text-muted-foreground">
                    <p>
                      <span className="font-medium">Command:</span>{' '}
                      <code className="bg-muted px-1 py-0.5 rounded">
                        {server.command}
                      </code>
                    </p>
                    {server.args && server.args.length > 0 && (
                      <p>
                        <span className="font-medium">Args:</span>{' '}
                        <code className="bg-muted px-1 py-0.5 rounded">
                          {server.args.join(' ')}
                        </code>
                      </p>
                    )}
                    <p>
                      <span className="font-medium">Transport:</span> {server.transport}
                    </p>
                    {server.pid && (
                      <p>
                        <span className="font-medium">PID:</span> {server.pid}
                      </p>
                    )}
                    {server.uptime !== undefined && (
                      <p>
                        <span className="font-medium">Uptime:</span> {formatUptime(server.uptime)}
                      </p>
                    )}
                    {server.restart_count !== undefined && server.restart_count > 0 && (
                      <p>
                        <span className="font-medium">Restarts:</span> {server.restart_count}
                      </p>
                    )}
                  </div>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-2">
                  {server.state === 'stopped' || server.state === 'crashed' ? (
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        startMutation.mutate(server.id)
                      }}
                      disabled={startMutation.isPending}
                      className="p-2 text-green-600 hover:bg-green-50 dark:hover:bg-green-950 rounded-md transition-colors disabled:opacity-50"
                      title="Start server"
                    >
                      <Play className="h-5 w-5" />
                    </button>
                  ) : server.state === 'running' ? (
                    <>
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          restartMutation.mutate(server.id)
                        }}
                        disabled={restartMutation.isPending}
                        className="p-2 text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-950 rounded-md transition-colors disabled:opacity-50"
                        title="Restart server"
                      >
                        <RotateCw className="h-5 w-5" />
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          stopMutation.mutate(server.id)
                        }}
                        disabled={stopMutation.isPending}
                        className="p-2 text-red-600 hover:bg-red-50 dark:hover:bg-red-950 rounded-md transition-colors disabled:opacity-50"
                        title="Stop server"
                      >
                        <Square className="h-5 w-5" />
                      </button>
                    </>
                  ) : null}
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      // TODO: Implement delete
                    }}
                    className="p-2 text-gray-500 hover:bg-gray-50 dark:hover:bg-gray-900 rounded-md transition-colors"
                    title="Delete server"
                  >
                    <Trash2 className="h-5 w-5" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Add Server Dialog (simplified placeholder) */}
      {showAddDialog && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-card border border-border rounded-lg p-6 max-w-md w-full mx-4">
            <h2 className="text-xl font-bold mb-4">Add Server</h2>
            <p className="text-muted-foreground mb-4">
              Server configuration via UI coming in next iteration.
              For now, please add servers via the configuration file.
            </p>
            <button
              onClick={() => setShowAddDialog(false)}
              className="w-full px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
