import { useQuery, useMutation } from '@tanstack/react-query'
import api from '../api/client'
import { Search, Wrench, Play, ChevronRight, Loader2, AlertCircle } from 'lucide-react'
import { useState } from 'react'

interface Tool {
  name: string
  description?: string
  server_name: string
  input_schema?: {
    type: string
    properties?: Record<string, any>
    required?: string[]
  }
}

export default function Tools() {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedServer, setSelectedServer] = useState<string>('')
  const [selectedTool, setSelectedTool] = useState<Tool | null>(null)
  const [toolArgs, setToolArgs] = useState<Record<string, string>>({})
  const [page, setPage] = useState(1)
  const pageSize = 20

  // Fetch tools
  const { data: toolsData, isLoading } = useQuery({
    queryKey: ['tools', selectedServer, page],
    queryFn: () => api.listTools({ 
      server_name: selectedServer || undefined,
      page,
      page_size: pageSize,
    }).then(res => res.data),
  })

  // Fetch servers for filter
  const { data: serversData } = useQuery({
    queryKey: ['servers'],
    queryFn: () => api.listServers().then(res => res.data),
  })

  // Invoke tool mutation
  const invokeMutation = useMutation({
    mutationFn: ({ name, arguments: args }: { name: string, arguments: Record<string, any> }) =>
      api.invokeTool(name, args),
  })

  const tools: Tool[] = toolsData?.tools || []
  const servers = serversData?.servers || []

  // Filter tools by search query
  const filteredTools = tools.filter(tool =>
    tool.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    tool.description?.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const handleInvokeTool = () => {
    if (!selectedTool) return

    // Parse arguments
    const parsedArgs: Record<string, any> = {}
    for (const [key, value] of Object.entries(toolArgs)) {
      try {
        parsedArgs[key] = JSON.parse(value)
      } catch {
        parsedArgs[key] = value
      }
    }

    invokeMutation.mutate({ name: selectedTool.name, arguments: parsedArgs })
  }

  const getRequiredFields = (tool: Tool): string[] => {
    return tool.input_schema?.required || []
  }

  const getProperties = (tool: Tool): Record<string, any> => {
    return tool.input_schema?.properties || {}
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-foreground">Tools</h1>
        <p className="mt-2 text-muted-foreground">
          Browse and invoke MCP tools
        </p>
      </div>

      {/* Filters */}
      <div className="flex gap-4">
        {/* Search */}
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search tools..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-background border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>

        {/* Server Filter */}
        <select
          value={selectedServer}
          onChange={(e) => {
            setSelectedServer(e.target.value)
            setPage(1)
          }}
          className="px-4 py-2 bg-background border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
        >
          <option value="">All Servers</option>
          {servers.map((server: any) => (
            <option key={server.id} value={server.name}>
              {server.name}
            </option>
          ))}
        </select>
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      )}

      {/* Tools Grid */}
      {!isLoading && (
        <div className="grid md:grid-cols-2 gap-6">
          {/* Tools List */}
          <div className="space-y-3">
            <h2 className="text-lg font-semibold text-foreground">
              Available Tools ({filteredTools.length})
            </h2>
            
            {filteredTools.length === 0 && (
              <div className="bg-card border border-border rounded-lg p-6 text-center">
                <p className="text-muted-foreground">No tools found</p>
              </div>
            )}

            <div className="space-y-2">
              {filteredTools.map((tool) => (
                <button
                  key={tool.name}
                  onClick={() => {
                    setSelectedTool(tool)
                    setToolArgs({})
                    invokeMutation.reset()
                  }}
                  className={`w-full text-left p-4 rounded-lg border transition-colors ${
                    selectedTool?.name === tool.name
                      ? 'bg-primary/10 border-primary'
                      : 'bg-card border-border hover:border-muted-foreground'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <Wrench className="h-4 w-4 text-muted-foreground" />
                        <h3 className="font-medium text-foreground">{tool.name}</h3>
                      </div>
                      {tool.description && (
                        <p className="mt-1 text-sm text-muted-foreground line-clamp-2">
                          {tool.description}
                        </p>
                      )}
                      <p className="mt-1 text-xs text-muted-foreground">
                        Server: {tool.server_name}
                      </p>
                    </div>
                    <ChevronRight className="h-5 w-5 text-muted-foreground flex-shrink-0" />
                  </div>
                </button>
              ))}
            </div>

            {/* Pagination */}
            {toolsData?.total && toolsData.total > pageSize && (
              <div className="flex items-center justify-between pt-4">
                <button
                  onClick={() => setPage(p => Math.max(1, p - 1))}
                  disabled={page === 1}
                  className="px-4 py-2 bg-card border border-border rounded-md hover:bg-accent disabled:opacity-50"
                >
                  Previous
                </button>
                <span className="text-sm text-muted-foreground">
                  Page {page} of {Math.ceil(toolsData.total / pageSize)}
                </span>
                <button
                  onClick={() => setPage(p => p + 1)}
                  disabled={page >= Math.ceil(toolsData.total / pageSize)}
                  className="px-4 py-2 bg-card border border-border rounded-md hover:bg-accent disabled:opacity-50"
                >
                  Next
                </button>
              </div>
            )}
          </div>

          {/* Tool Details & Invocation */}
          <div className="space-y-3">
            <h2 className="text-lg font-semibold text-foreground">Tool Details</h2>
            
            {!selectedTool && (
              <div className="bg-card border border-border rounded-lg p-6 text-center">
                <p className="text-muted-foreground">Select a tool to view details and invoke</p>
              </div>
            )}

            {selectedTool && (
              <div className="bg-card border border-border rounded-lg p-6 space-y-4">
                <div>
                  <h3 className="text-lg font-semibold text-foreground">{selectedTool.name}</h3>
                  {selectedTool.description && (
                    <p className="mt-2 text-sm text-muted-foreground">{selectedTool.description}</p>
                  )}
                  <p className="mt-2 text-xs text-muted-foreground">
                    Server: {selectedTool.server_name}
                  </p>
                </div>

                {/* Input Schema */}
                {Object.keys(getProperties(selectedTool)).length > 0 && (
                  <div>
                    <h4 className="text-sm font-semibold text-foreground mb-2">Parameters</h4>
                    <div className="space-y-3">
                      {Object.entries(getProperties(selectedTool)).map(([key, schema]: [string, any]) => (
                        <div key={key}>
                          <label className="block text-sm font-medium text-foreground mb-1">
                            {key}
                            {getRequiredFields(selectedTool).includes(key) && (
                              <span className="text-red-500 ml-1">*</span>
                            )}
                          </label>
                          <input
                            type="text"
                            value={toolArgs[key] || ''}
                            onChange={(e) => setToolArgs({ ...toolArgs, [key]: e.target.value })}
                            placeholder={schema.description || `Enter ${key}`}
                            className="w-full px-3 py-2 bg-background border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-primary text-sm"
                          />
                          {schema.description && (
                            <p className="mt-1 text-xs text-muted-foreground">{schema.description}</p>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Invoke Button */}
                <button
                  onClick={handleInvokeTool}
                  disabled={invokeMutation.isPending}
                  className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 disabled:opacity-50 transition-colors"
                >
                  {invokeMutation.isPending ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin" />
                      Invoking...
                    </>
                  ) : (
                    <>
                      <Play className="h-4 w-4" />
                      Invoke Tool
                    </>
                  )}
                </button>

                {/* Result */}
                {invokeMutation.isError && (
                  <div className="p-4 bg-destructive/10 border border-destructive rounded-md">
                    <div className="flex items-start gap-2">
                      <AlertCircle className="h-5 w-5 text-destructive flex-shrink-0 mt-0.5" />
                      <div>
                        <p className="font-medium text-destructive">Error</p>
                        <p className="text-sm text-destructive/80 mt-1">
                          {(invokeMutation.error as any)?.response?.data?.message || 'Failed to invoke tool'}
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                {invokeMutation.isSuccess && (
                  <div className="p-4 bg-green-50 dark:bg-green-950 border border-green-200 dark:border-green-800 rounded-md">
                    <p className="font-medium text-green-900 dark:text-green-100 mb-2">Result</p>
                    <pre className="text-xs text-green-800 dark:text-green-200 overflow-auto">
                      {JSON.stringify(invokeMutation.data?.data, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
