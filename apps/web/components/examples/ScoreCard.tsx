// Example component showing the new design system in action
// This demonstrates how to build a verification score display
// with the new UI components

import { Card } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { cn } from '@/lib/utils'

interface ScoreCardProps {
  combinedScore: number
  relevanceScore: number
  noveltyScore: number
  coherenceScore: number
  effortScore: number
  aiDetectionScore: number
  passed: boolean
  className?: string
}

export function ScoreCard({
  combinedScore,
  relevanceScore,
  noveltyScore,
  coherenceScore,
  effortScore,
  aiDetectionScore,
  passed,
  className,
}: ScoreCardProps) {
  const formatScore = (score: number) => Math.round(score * 100)

  return (
    <Card className={cn('p-8', className)}>
      {/* Main Score Display */}
      <div className="text-center mb-8">
        <div className="mb-4">
          <div className={cn(
            'text-6xl font-mono font-semibold tracking-tighter mb-3',
            passed
              ? 'bg-gradient-to-br from-accent-primary to-accent-secondary bg-clip-text text-transparent'
              : 'text-error'
          )}>
            {formatScore(combinedScore)}%
          </div>
          <p className="text-xs font-semibold uppercase tracking-wider text-text-tertiary mb-4">
            Combined Score
          </p>
          <Badge variant={passed ? 'success' : 'error'}>
            {passed ? 'Passed' : 'Failed'}
          </Badge>
        </div>
      </div>

      {/* Individual Scores Grid */}
      <div className="grid grid-cols-2 gap-3">
        <ScoreItem label="Relevance" score={relevanceScore} />
        <ScoreItem label="Novelty" score={noveltyScore} />
        <ScoreItem label="Coherence" score={coherenceScore} />
        <ScoreItem label="Effort" score={effortScore} />
      </div>

      {/* AI Detection (full width) */}
      <div className="mt-3">
        <div className="bg-background-secondary rounded-lg p-4">
          <div className="flex items-center justify-between">
            <span className="text-sm text-text-tertiary">AI Detection</span>
            <div className="flex items-center gap-2">
              <span className="text-lg font-mono font-semibold text-text-primary">
                {formatScore(aiDetectionScore)}%
              </span>
              {aiDetectionScore >= 0.7 ? (
                <Badge variant="success">Human</Badge>
              ) : (
                <Badge variant="warning">Review</Badge>
              )}
            </div>
          </div>
        </div>
      </div>
    </Card>
  )
}

interface ScoreItemProps {
  label: string
  score: number
}

function ScoreItem({ label, score }: ScoreItemProps) {
  const percentage = Math.round(score * 100)

  const getColor = (score: number) => {
    if (score >= 0.7) return 'text-success'
    if (score >= 0.5) return 'text-warning'
    return 'text-error'
  }

  return (
    <div className="bg-background-secondary rounded-lg p-4">
      <p className="text-sm text-text-tertiary mb-2">{label}</p>
      <p className={cn('text-2xl font-mono font-semibold', getColor(score))}>
        {percentage}%
      </p>
    </div>
  )
}
