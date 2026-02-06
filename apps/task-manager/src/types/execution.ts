export interface ExecutionArtifact {
  name: string
  content: string
  lastModified: number
}

export interface ActiveTask {
  id: string
  subject: string
  phase: string
}

export interface CompletedTask {
  id: string
  subject: string
  result: string
}

export interface ExecutionProgress {
  status: string
  wave: number
  totalWaves: number
  maxParallel?: number
  updated: string
  activeTasks: ActiveTask[]
  completedTasks: CompletedTask[]
}

export interface ExecutionContext {
  executionDir: string
  artifacts: ExecutionArtifact[]
  progress?: ExecutionProgress | null
}
