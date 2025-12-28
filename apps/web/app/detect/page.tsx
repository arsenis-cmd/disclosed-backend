'use client'

import { useEffect, useState } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { SignInButton, SignedIn, SignedOut, UserButton } from '@clerk/nextjs'
import Link from 'next/link'

interface DetectionResult {
  id: string
  score: number
  verdict: string
  confidence: number
  word_count: number
  analysis?: {
    perplexity: { score: number; interpretation: string }
    coherence: { score: number; interpretation: string }
    burstiness: { score: number; interpretation: string }
    originality: { score: number; interpretation: string }
    personal_voice: { score: number; interpretation: string }
    pattern_score: { score: number; interpretation: string }
  }
  can_verify: boolean
  created_at: string
}

export default function DetectPage() {
  const [result, setResult] = useState<DetectionResult | null>(null)
  const [text, setText] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const router = useRouter()
  const searchParams = useSearchParams()

  useEffect(() => {
    // Get result from sessionStorage
    const storedResult = sessionStorage.getItem('detectionResult')
    const storedText = sessionStorage.getItem('detectionText')

    if (storedResult && storedText) {
      setResult(JSON.parse(storedResult))
      setText(storedText)
      setLoading(false)
    } else {
      // No result found, redirect to home
      router.push('/')
    }
  }, [router])

  if (loading) {
    return (
      <div className="min-h-screen bg-background-primary flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-accent-primary mx-auto"></div>
          <p className="mt-4 text-text-secondary">Loading results...</p>
        </div>
      </div>
    )
  }

  if (!result) {
    return null
  }

  const getVerdictColor = (verdict: string) => {
    switch (verdict) {
      case 'likely_ai':
        return 'text-error'
      case 'mixed':
        return 'text-warning'
      case 'likely_human':
        return 'text-success'
      case 'highly_human':
        return 'text-accent-primary'
      default:
        return 'text-text-primary'
    }
  }

  const getVerdictBg = (verdict: string) => {
    switch (verdict) {
      case 'likely_ai':
        return 'bg-error/10 border-error/30'
      case 'mixed':
        return 'bg-warning/10 border-warning/30'
      case 'likely_human':
        return 'bg-success/10 border-success/30'
      case 'highly_human':
        return 'bg-accent-primary/10 border-accent-primary/30'
      default:
        return 'bg-background-secondary border-border'
    }
  }

  const getVerdictLabel = (verdict: string) => {
    switch (verdict) {
      case 'likely_ai':
        return 'Likely AI-Generated'
      case 'mixed':
        return 'Mixed Signals'
      case 'likely_human':
        return 'Likely Human-Written'
      case 'highly_human':
        return 'Highly Human-Written'
      default:
        return verdict
    }
  }

  const ScoreBar = ({ score, label, interpretation }: { score: number; label: string; interpretation: string }) => (
    <div className="space-y-2">
      <div className="flex justify-between items-center">
        <span className="text-sm font-medium text-text-primary">{label}</span>
        <span className="text-sm font-bold text-accent-primary">{(score * 100).toFixed(1)}%</span>
      </div>
      <div className="w-full bg-background-secondary rounded-full h-2 overflow-hidden">
        <div
          className="h-full bg-gradient-to-r from-accent-primary to-accent-secondary transition-all duration-500"
          style={{ width: `${score * 100}%` }}
        />
      </div>
      <p className="text-xs text-text-tertiary">{interpretation}</p>
    </div>
  )

  return (
    <div className="min-h-screen bg-background-primary relative overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-accent-primary/20 rounded-full filter blur-3xl animate-float" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-accent-cyan/20 rounded-full filter blur-3xl animate-float" style={{ animationDelay: '1s' }} />
      </div>

      {/* Header */}
      <header className="relative border-b border-border/50 glass-strong">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <Link href="/">
            <h1 className="text-2xl font-bold gradient-text cursor-pointer">AI Content Detector</h1>
          </Link>
          <div className="flex gap-4 items-center">
            <SignedOut>
              <SignInButton mode="modal">
                <button className="px-4 py-2 text-sm font-medium text-text-secondary hover:text-text-primary transition-colors">
                  Sign In
                </button>
              </SignInButton>
            </SignedOut>
            <SignedIn>
              <Link href="/dashboard" className="px-4 py-2 text-sm font-medium text-text-secondary hover:text-text-primary transition-colors">
                Dashboard
              </Link>
              <UserButton afterSignOutUrl="/" />
            </SignedIn>
          </div>
        </div>
      </header>

      {/* Results */}
      <main className="relative container mx-auto px-4 py-12">
        <div className="max-w-5xl mx-auto space-y-8">
          {/* Overall Verdict */}
          <div className={`card-glass p-8 text-center border-2 ${getVerdictBg(result.verdict)}`}>
            <div className="space-y-4">
              <div className="inline-block px-4 py-1 rounded-full bg-background-primary/50 text-xs font-medium text-text-tertiary">
                Detection ID: {result.id}
              </div>

              <h2 className={`text-4xl md:text-5xl font-bold ${getVerdictColor(result.verdict)}`}>
                {getVerdictLabel(result.verdict)}
              </h2>

              <div className="flex justify-center items-center gap-8 text-sm">
                <div>
                  <div className="text-text-tertiary">Human Score</div>
                  <div className="text-2xl font-bold gradient-text">{(result.score * 100).toFixed(1)}%</div>
                </div>
                <div className="h-12 w-px bg-border" />
                <div>
                  <div className="text-text-tertiary">Confidence</div>
                  <div className="text-2xl font-bold text-accent-cyan">{(result.confidence * 100).toFixed(1)}%</div>
                </div>
                <div className="h-12 w-px bg-border" />
                <div>
                  <div className="text-text-tertiary">Word Count</div>
                  <div className="text-2xl font-bold text-accent-pink">{result.word_count}</div>
                </div>
              </div>
            </div>
          </div>

          {/* Detailed Analysis */}
          {result.analysis && (
            <div className="card-glass p-8 space-y-6">
              <h3 className="text-2xl font-bold gradient-text mb-6">6-Dimensional Analysis</h3>

              <div className="grid md:grid-cols-2 gap-6">
                <ScoreBar
                  score={result.analysis.perplexity.score}
                  label="Perplexity (Unpredictability)"
                  interpretation={result.analysis.perplexity.interpretation}
                />
                <ScoreBar
                  score={result.analysis.coherence.score}
                  label="Coherence (Natural Flow)"
                  interpretation={result.analysis.coherence.interpretation}
                />
                <ScoreBar
                  score={result.analysis.burstiness.score}
                  label="Burstiness (Complexity Variation)"
                  interpretation={result.analysis.burstiness.interpretation}
                />
                <ScoreBar
                  score={result.analysis.originality.score}
                  label="Originality (Unique Phrasing)"
                  interpretation={result.analysis.originality.interpretation}
                />
                <ScoreBar
                  score={result.analysis.personal_voice.score}
                  label="Personal Voice (Author Perspective)"
                  interpretation={result.analysis.personal_voice.interpretation}
                />
                <ScoreBar
                  score={result.analysis.pattern_score.score}
                  label="Pattern Score (AI Detection)"
                  interpretation={result.analysis.pattern_score.interpretation}
                />
              </div>
            </div>
          )}

          {/* Text Preview */}
          <div className="card-glass p-8 space-y-4">
            <h3 className="text-xl font-bold text-text-primary">Analyzed Text</h3>
            <div className="bg-background-secondary p-4 rounded-lg border border-border max-h-64 overflow-y-auto">
              <p className="text-text-secondary text-sm leading-relaxed whitespace-pre-wrap">
                {text}
              </p>
            </div>
          </div>

          {/* Actions */}
          <div className="flex flex-col sm:flex-row gap-4">
            <Link href="/" className="btn-secondary flex-1 text-center py-4">
              Try Another Text
            </Link>

            {result.can_verify ? (
              <SignedIn>
                <button className="btn-primary flex-1 py-4">
                  Verify on Blockchain →
                </button>
              </SignedIn>
            ) : null}

            {result.can_verify ? (
              <SignedOut>
                <SignInButton mode="modal">
                  <button className="btn-primary flex-1 py-4">
                    Sign In to Verify →
                  </button>
                </SignInButton>
              </SignedOut>
            ) : null}
          </div>

          {/* Info Boxes */}
          <div className="grid md:grid-cols-2 gap-4">
            <div className="card-glass p-6">
              <h4 className="font-semibold mb-2 text-text-primary">What does this mean?</h4>
              <p className="text-sm text-text-secondary leading-relaxed">
                Our 6-dimensional analysis examines multiple aspects of your text to determine
                if it was written by a human or AI. Scores closer to 100% indicate human-written content.
              </p>
            </div>

            {result.can_verify && (
              <div className="card-glass p-6 border-accent-primary/30">
                <h4 className="font-semibold mb-2 text-accent-primary">Blockchain Verification Available</h4>
                <p className="text-sm text-text-secondary leading-relaxed">
                  Your text scored {(result.score * 100).toFixed(0)}%, which qualifies for permanent blockchain
                  verification. Get a tamper-proof certificate of human authorship.
                </p>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="relative border-t border-border/50 mt-16 py-8">
        <div className="container mx-auto px-4 text-center text-text-tertiary">
          <p>© 2025 AI Content Detector. All rights reserved.</p>
        </div>
      </footer>
    </div>
  )
}
