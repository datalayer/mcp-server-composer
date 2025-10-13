import { useState, useEffect, useRef } from 'react'
import { useQuery } from '@tanstack/react-query'
import { api } from '../api/client'
import { Search, Download, Trash2, Filter, Loader2, Terminal, AlertCircle } from 'lucide-react'

interface LogEntry {
  timestamp: string
  level: 'DEBUG' | 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL'
  server?: string
  message: string
}

export default function Logs() {
  const [filter, setFilter] = useState<string>('')
  const [levelFilter, setLevelFilter] = useState<string>('ALL')
  const [serverFilter, setServerFilter] = useState<string>('ALL')
  const [autoScroll, setAutoScroll] = useState(true)
  const [maxLines, setMaxLines] = useState<number>(500)
  const logsEndRef = useRef<HTMLDivElement>(null)
  const logsContainerRef = useRef<HTMLDivElement>(null)

  // Fetch servers for filter
  const { data: servers } = useQuery({
    queryKey: ['servers'],
    queryFn: () => api.listServers().then(res => res.data),
  })

  // Mock log entries (in real implementation, this would use WebSocket or SSE)
  const [logs, setLogs] = useState<LogEntry[]>([
    { timestamp: new Date().toISOString(), level: 'INFO', server: 'filesystem', message: 'Server started successfully' },
    { timestamp: new Date().toISOString(), level: 'INFO', server: 'calculator', message: 'Initializing calculator tools' },
    { timestamp: new Date().toISOString(), level: 'DEBUG', server: 'filesystem', message: 'Loading file system configuration' },
    { timestamp: new Date().toISOString(), level: 'WARNING', server: 'calculator', message: 'Deprecated function called' },
  ])

  // Simulate real-time log streaming
  useEffect(() => {
    const interval = setInterval(() => {
      const levels: LogEntry['level'][] = ['DEBUG', 'INFO', 'WARNING', 'ERROR']
      const messages = [
        'Processing request',
        'Tool invoked successfully',
        'Configuration updated',
        'Health check passed',
        'Connection established',
        'Cache cleared',
        'Request completed in 45ms',
      ]
      const serverList = servers?.servers?.map(s => s.name) || ['filesystem', 'calculator']
      
      const newLog: LogEntry = {
        timestamp: new Date().toISOString(),
        level: levels[Math.floor(Math.random() * levels.length)],
        server: serverList[Math.floor(Math.random() * serverList.length)],
        message: messages[Math.floor(Math.random() * messages.length)],
      }
      
      setLogs(prev => {
        const updated = [...prev, newLog]
        return updated.slice(-maxLines) // Keep only last N lines
      })
    }, 2000) // New log every 2 seconds

    return () => clearInterval(interval)
  }, [servers, maxLines])

  // Auto-scroll to bottom
  useEffect(() => {
    if (autoScroll && logsEndRef.current) {
      logsEndRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [logs, autoScroll])

  // Filter logs
  const filteredLogs = logs.filter(log => {
    if (filter && !log.message.toLowerCase().includes(filter.toLowerCase())) {
      return false
    }
    if (levelFilter !== 'ALL' && log.level !== levelFilter) {
      return false
    }
    if (serverFilter !== 'ALL' && log.server !== serverFilter) {
      return false
    }
    return true
  })

  const clearLogs = () => {
    setLogs([])
  }

  const downloadLogs = () => {
    const logText = filteredLogs.map(log => 
      `${log.timestamp} [${log.level}] ${log.server ? `[${log.server}] ` : ''}${log.message}`
    ).join('\n')
    
    const blob = new Blob([logText], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `logs-${new Date().toISOString()}.txt`
    a.click()
    URL.revokeObjectURL(url)
  }

  const getLevelColor = (level: LogEntry['level']) => {
    switch (level) {
      case 'DEBUG': return 'text-muted-foreground'
      case 'INFO': return 'text-blue-500'
      case 'WARNING': return 'text-yellow-500'
      case 'ERROR': return 'text-red-500'
      case 'CRITICAL': return 'text-red-600 font-bold'
      default: return 'text-foreground'
    }
  }

  const getLevelBg = (level: LogEntry['level']) => {
    switch (level) {
      case 'DEBUG': return 'bg-muted'
      case 'INFO': return 'bg-blue-500/10'
      case 'WARNING': return 'bg-yellow-500/10'
      case 'ERROR': return 'bg-red-500/10'
      case 'CRITICAL': return 'bg-red-600/20'
      default: return 'bg-muted'
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Logs</h1>
          <p className="mt-2 text-muted-foreground">
            Real-time system and server logs
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={downloadLogs}
            className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors flex items-center gap-2"
          >
            <Download className="h-4 w-4" />
            Download
          </button>
          <button
            onClick={clearLogs}
            className="px-4 py-2 bg-destructive text-destructive-foreground rounded-md hover:bg-destructive/90 transition-colors flex items-center gap-2"
          >
            <Trash2 className="h-4 w-4" />
            Clear
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-card border border-border rounded-lg p-4">
        <div className="flex items-center gap-4 flex-wrap">
          <div className="flex-1 min-w-[200px]">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <input
                type="text"
                placeholder="Search logs..."
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
                className="w-full pl-10 pr-4 py-2 bg-background border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-ring"
              />
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <Filter className="h-4 w-4 text-muted-foreground" />
            <select
              value={levelFilter}
              onChange={(e) => setLevelFilter(e.target.value)}
              className="px-3 py-2 bg-background border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-ring"
            >
              <option value="ALL">All Levels</option>
              <option value="DEBUG">Debug</option>
              <option value="INFO">Info</option>
              <option value="WARNING">Warning</option>
              <option value="ERROR">Error</option>
              <option value="CRITICAL">Critical</option>
            </select>
          </div>

          <div className="flex items-center gap-2">
            <Terminal className="h-4 w-4 text-muted-foreground" />
            <select
              value={serverFilter}
              onChange={(e) => setServerFilter(e.target.value)}
              className="px-3 py-2 bg-background border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-ring"
            >
              <option value="ALL">All Servers</option>
              {servers?.servers?.map(server => (
                <option key={server.id} value={server.name}>{server.name}</option>
              ))}
            </select>
          </div>

          <div className="flex items-center gap-2">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={autoScroll}
                onChange={(e) => setAutoScroll(e.target.checked)}
                className="w-4 h-4 rounded border-input"
              />
              <span className="text-sm text-muted-foreground">Auto-scroll</span>
            </label>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-sm text-muted-foreground">Max lines:</span>
            <select
              value={maxLines}
              onChange={(e) => setMaxLines(Number(e.target.value))}
              className="px-3 py-2 bg-background border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-ring"
            >
              <option value={100}>100</option>
              <option value={500}>500</option>
              <option value={1000}>1000</option>
              <option value={5000}>5000</option>
            </select>
          </div>
        </div>
      </div>

      {/* Log Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <div className="bg-card border border-border rounded-lg p-4">
          <div className="text-sm text-muted-foreground">Total Lines</div>
          <div className="text-2xl font-bold">{filteredLogs.length}</div>
        </div>
        <div className="bg-card border border-border rounded-lg p-4">
          <div className="text-sm text-muted-foreground">Errors</div>
          <div className="text-2xl font-bold text-red-500">
            {filteredLogs.filter(l => l.level === 'ERROR' || l.level === 'CRITICAL').length}
          </div>
        </div>
        <div className="bg-card border border-border rounded-lg p-4">
          <div className="text-sm text-muted-foreground">Warnings</div>
          <div className="text-2xl font-bold text-yellow-500">
            {filteredLogs.filter(l => l.level === 'WARNING').length}
          </div>
        </div>
        <div className="bg-card border border-border rounded-lg p-4">
          <div className="text-sm text-muted-foreground">Info</div>
          <div className="text-2xl font-bold text-blue-500">
            {filteredLogs.filter(l => l.level === 'INFO').length}
          </div>
        </div>
      </div>

      {/* Logs Display */}
      <div className="bg-card border border-border rounded-lg overflow-hidden">
        <div className="bg-muted px-4 py-2 border-b border-border flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Terminal className="h-4 w-4" />
            <span className="font-mono text-sm">Console Output</span>
          </div>
          <div className="text-sm text-muted-foreground">
            {filteredLogs.length} / {logs.length} lines
          </div>
        </div>
        
        <div
          ref={logsContainerRef}
          className="h-[600px] overflow-y-auto bg-black/5 dark:bg-black/20 p-4 font-mono text-xs"
        >
          {filteredLogs.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-muted-foreground">
              <AlertCircle className="h-12 w-12 mb-4" />
              <p>No logs to display</p>
              <p className="text-xs mt-2">Logs will appear here as they are generated</p>
            </div>
          ) : (
            filteredLogs.map((log, index) => (
              <div
                key={index}
                className={`py-1 px-2 rounded mb-1 ${getLevelBg(log.level)} hover:bg-muted/50 transition-colors`}
              >
                <span className="text-muted-foreground">
                  {new Date(log.timestamp).toLocaleTimeString()}
                </span>
                {' '}
                <span className={`font-bold ${getLevelColor(log.level)}`}>
                  [{log.level}]
                </span>
                {log.server && (
                  <>
                    {' '}
                    <span className="text-purple-500">[{log.server}]</span>
                  </>
                )}
                {' '}
                <span className="text-foreground">{log.message}</span>
              </div>
            ))
          )}
          <div ref={logsEndRef} />
        </div>
      </div>
    </div>
  )
}
