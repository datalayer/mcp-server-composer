import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '../api/client'
import { Radio, Trash2, Plus, CheckCircle, Loader2, AlertCircle, ArrowRightLeft } from 'lucide-react'

type TranslatorType = 'stdio-to-sse' | 'sse-to-stdio'

interface Translator {
  name: string
  type: TranslatorType
  sse_url?: string
  command?: string
  args?: string[]
  created_at?: string
}

export default function Translators() {
  const queryClient = useQueryClient()
  const [showAddDialog, setShowAddDialog] = useState(false)
  const [translatorType, setTranslatorType] = useState<TranslatorType>('stdio-to-sse')
  
  // STDIO to SSE form
  const [stdioName, setStdioName] = useState('')
  const [sseUrl, setSseUrl] = useState('')
  
  // SSE to STDIO form
  const [sseName, setSseName] = useState('')
  const [command, setCommand] = useState('')
  const [args, setArgs] = useState('')

  // Fetch translators
  const { data: translators, isLoading, error } = useQuery({
    queryKey: ['translators'],
    queryFn: () => api.listTranslators().then(res => res.data),
    refetchInterval: 10000,
  })

  // Create STDIO to SSE mutation
  const createStdioToSseMutation = useMutation({
    mutationFn: (data: { name: string; sse_url: string }) =>
      api.createStdioToSse(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['translators'] })
      resetForm()
    },
  })

  // Create SSE to STDIO mutation
  const createSseToStdioMutation = useMutation({
    mutationFn: (data: { name: string; command: string; args?: string[] }) =>
      api.createSseToStdio(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['translators'] })
      resetForm()
    },
  })

  // Delete translator mutation
  const deleteMutation = useMutation({
    mutationFn: (name: string) => api.deleteTranslator(name),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['translators'] })
    },
  })

  const resetForm = () => {
    setShowAddDialog(false)
    setStdioName('')
    setSseUrl('')
    setSseName('')
    setCommand('')
    setArgs('')
  }

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault()
    
    if (translatorType === 'stdio-to-sse') {
      if (stdioName.trim() && sseUrl.trim()) {
        createStdioToSseMutation.mutate({
          name: stdioName.trim(),
          sse_url: sseUrl.trim(),
        })
      }
    } else {
      if (sseName.trim() && command.trim()) {
        createSseToStdioMutation.mutate({
          name: sseName.trim(),
          command: command.trim(),
          args: args.trim() ? args.trim().split(' ') : undefined,
        })
      }
    }
  }

  const handleDelete = (name: string) => {
    if (confirm(`Are you sure you want to delete translator "${name}"?`)) {
      deleteMutation.mutate(name)
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-destructive mx-auto mb-4" />
          <p className="text-destructive">Failed to load translators</p>
        </div>
      </div>
    )
  }

  const translatorList = translators?.translators || []

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Translators</h1>
          <p className="mt-2 text-muted-foreground">
            Manage protocol translators for MCP servers
          </p>
        </div>
        <button
          onClick={() => setShowAddDialog(true)}
          className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors flex items-center gap-2"
        >
          <Plus className="h-4 w-4" />
          Add Translator
        </button>
      </div>

      {/* Info Banner */}
      <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <Radio className="h-5 w-5 text-blue-500 mt-0.5" />
          <div>
            <h3 className="font-semibold text-blue-500">About Protocol Translators</h3>
            <p className="text-sm text-muted-foreground mt-1">
              Protocol translators enable communication between different MCP transport protocols:
            </p>
            <ul className="text-sm text-muted-foreground mt-2 space-y-1 list-disc list-inside">
              <li><strong>STDIO → SSE:</strong> Exposes STDIO servers via Server-Sent Events for web clients</li>
              <li><strong>SSE → STDIO:</strong> Connects to SSE servers using STDIO interface</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Translators List */}
      {translatorList.length > 0 ? (
        <div className="grid gap-4">
          {translatorList.map((translator: Translator) => (
            <div
              key={translator.name}
              className="bg-card border border-border rounded-lg p-6 hover:border-primary/50 transition-colors"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-primary/10 rounded-lg">
                      <ArrowRightLeft className="h-5 w-5 text-primary" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-lg">{translator.name}</h3>
                      <p className="text-sm text-muted-foreground mt-1">
                        {translator.type === 'stdio-to-sse' ? 'STDIO → SSE' : 'SSE → STDIO'}
                      </p>
                    </div>
                  </div>

                  <div className="mt-4 space-y-2">
                    {translator.type === 'stdio-to-sse' && translator.sse_url && (
                      <div className="p-3 bg-muted rounded-md">
                        <p className="text-xs text-muted-foreground">SSE Endpoint</p>
                        <p className="text-sm font-mono text-foreground mt-1">{translator.sse_url}</p>
                      </div>
                    )}
                    {translator.type === 'sse-to-stdio' && translator.command && (
                      <div className="p-3 bg-muted rounded-md">
                        <p className="text-xs text-muted-foreground">Command</p>
                        <p className="text-sm font-mono text-foreground mt-1">
                          {translator.command}
                          {translator.args && translator.args.length > 0 && ` ${translator.args.join(' ')}`}
                        </p>
                      </div>
                    )}
                  </div>

                  {translator.created_at && (
                    <div className="mt-3 text-xs text-muted-foreground">
                      Created: {new Date(translator.created_at).toLocaleString()}
                    </div>
                  )}
                </div>

                <button
                  onClick={() => handleDelete(translator.name)}
                  disabled={deleteMutation.isPending}
                  className="p-2 hover:bg-destructive/10 text-destructive rounded-md transition-colors disabled:opacity-50 ml-4"
                  title="Delete translator"
                >
                  <Trash2 className="h-5 w-5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-card border border-border rounded-lg p-12">
          <div className="text-center">
            <Radio className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">No translators configured</h3>
            <p className="text-muted-foreground mb-6">
              Create a translator to enable cross-protocol communication
            </p>
            <button
              onClick={() => setShowAddDialog(true)}
              className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors inline-flex items-center gap-2"
            >
              <Plus className="h-4 w-4" />
              Add Your First Translator
            </button>
          </div>
        </div>
      )}

      {/* Add Translator Dialog */}
      {showAddDialog && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-card border border-border rounded-lg p-6 max-w-lg w-full mx-4 max-h-[90vh] overflow-y-auto">
            <h2 className="text-xl font-bold mb-4">Add Protocol Translator</h2>
            
            {/* Translator Type Selection */}
            <div className="mb-6">
              <label className="block text-sm font-medium mb-3">Translator Type</label>
              <div className="grid grid-cols-2 gap-3">
                <button
                  type="button"
                  onClick={() => setTranslatorType('stdio-to-sse')}
                  className={`p-4 border-2 rounded-lg transition-all ${
                    translatorType === 'stdio-to-sse'
                      ? 'border-primary bg-primary/10'
                      : 'border-border hover:border-primary/50'
                  }`}
                >
                  <ArrowRightLeft className="h-6 w-6 mx-auto mb-2" />
                  <div className="font-semibold text-sm">STDIO → SSE</div>
                  <div className="text-xs text-muted-foreground mt-1">
                    Expose STDIO via SSE
                  </div>
                </button>
                <button
                  type="button"
                  onClick={() => setTranslatorType('sse-to-stdio')}
                  className={`p-4 border-2 rounded-lg transition-all ${
                    translatorType === 'sse-to-stdio'
                      ? 'border-primary bg-primary/10'
                      : 'border-border hover:border-primary/50'
                  }`}
                >
                  <ArrowRightLeft className="h-6 w-6 mx-auto mb-2 rotate-180" />
                  <div className="font-semibold text-sm">SSE → STDIO</div>
                  <div className="text-xs text-muted-foreground mt-1">
                    Connect to SSE via STDIO
                  </div>
                </button>
              </div>
            </div>

            <form onSubmit={handleCreate} className="space-y-4">
              {translatorType === 'stdio-to-sse' ? (
                <>
                  <div>
                    <label className="block text-sm font-medium mb-2">
                      Translator Name <span className="text-destructive">*</span>
                    </label>
                    <input
                      type="text"
                      value={stdioName}
                      onChange={(e) => setStdioName(e.target.value)}
                      placeholder="my-translator"
                      className="w-full px-3 py-2 bg-background border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-ring"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">
                      SSE URL <span className="text-destructive">*</span>
                    </label>
                    <input
                      type="url"
                      value={sseUrl}
                      onChange={(e) => setSseUrl(e.target.value)}
                      placeholder="http://localhost:3001/sse"
                      className="w-full px-3 py-2 bg-background border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-ring"
                      required
                    />
                    <p className="text-xs text-muted-foreground mt-2">
                      The SSE endpoint to expose the STDIO server through
                    </p>
                  </div>
                </>
              ) : (
                <>
                  <div>
                    <label className="block text-sm font-medium mb-2">
                      Translator Name <span className="text-destructive">*</span>
                    </label>
                    <input
                      type="text"
                      value={sseName}
                      onChange={(e) => setSseName(e.target.value)}
                      placeholder="my-translator"
                      className="w-full px-3 py-2 bg-background border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-ring"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">
                      Command <span className="text-destructive">*</span>
                    </label>
                    <input
                      type="text"
                      value={command}
                      onChange={(e) => setCommand(e.target.value)}
                      placeholder="python -m mcp_server"
                      className="w-full px-3 py-2 bg-background border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-ring"
                      required
                    />
                    <p className="text-xs text-muted-foreground mt-2">
                      The command to launch the STDIO process
                    </p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">
                      Arguments (optional)
                    </label>
                    <input
                      type="text"
                      value={args}
                      onChange={(e) => setArgs(e.target.value)}
                      placeholder="--port 8080 --debug"
                      className="w-full px-3 py-2 bg-background border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-ring"
                    />
                    <p className="text-xs text-muted-foreground mt-2">
                      Space-separated command arguments
                    </p>
                  </div>
                </>
              )}

              {(createStdioToSseMutation.isError || createSseToStdioMutation.isError) && (
                <div className="p-3 bg-destructive/10 border border-destructive/20 rounded-md">
                  <p className="text-sm text-destructive">
                    Failed to create translator. Please check your inputs and try again.
                  </p>
                </div>
              )}

              <div className="flex justify-end gap-2 pt-4">
                <button
                  type="button"
                  onClick={resetForm}
                  className="px-4 py-2 bg-muted rounded-md hover:bg-muted/80 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={createStdioToSseMutation.isPending || createSseToStdioMutation.isPending}
                  className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors disabled:opacity-50 flex items-center gap-2"
                >
                  {(createStdioToSseMutation.isPending || createSseToStdioMutation.isPending) ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin" />
                      Creating...
                    </>
                  ) : (
                    'Create'
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Success Toast */}
      {(createStdioToSseMutation.isSuccess || createSseToStdioMutation.isSuccess) && (
        <div className="fixed bottom-4 right-4 bg-green-500 text-white px-4 py-3 rounded-lg shadow-lg flex items-center gap-2 animate-in slide-in-from-right">
          <CheckCircle className="h-5 w-5" />
          <span>Translator created successfully!</span>
        </div>
      )}
    </div>
  )
}
