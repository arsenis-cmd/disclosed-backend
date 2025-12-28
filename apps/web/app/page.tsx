'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@clerk/nextjs'
import { SignInButton, SignUpButton, SignedIn, SignedOut, UserButton } from '@clerk/nextjs'
import { APIClient } from '@/lib/api'
import Link from 'next/link'

export default function Home() {
  const [text, setText] = useState('')
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const router = useRouter()
  const { getToken } = useAuth()

  const wordCount = text.trim().split(/\s+/).filter(w => w.length > 0).length
  const isValid = wordCount >= 50 && wordCount <= 10000

  const handleAnalyze = async () => {
    if (!isValid) {
      setError('Please enter between 50 and 10,000 words')
      return
    }

    setIsAnalyzing(true)
    setError(null)

    try {
      const api = new APIClient(getToken)
      const result = await api.detectText(text, true)

      // Store result in sessionStorage and navigate to results page
      sessionStorage.setItem('detectionResult', JSON.stringify(result))
      sessionStorage.setItem('detectionText', text)
      router.push(`/detect?id=${result.id}`)
    } catch (err: any) {
      console.error('Detection error:', err)
      setError(err.message || 'Failed to analyze text. Please try again.')
    } finally {
      setIsAnalyzing(false)
    }
  }

  return (
    <div className="min-h-screen bg-background-primary relative overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-accent-primary/20 rounded-full filter blur-3xl animate-float" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-accent-cyan/20 rounded-full filter blur-3xl animate-float" style={{ animationDelay: '1s' }} />
        <div className="absolute top-1/2 right-1/3 w-96 h-96 bg-accent-pink/20 rounded-full filter blur-3xl animate-float" style={{ animationDelay: '2s' }} />
      </div>

      {/* Header */}
      <header className="relative border-b border-border/50 glass-strong">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold gradient-text">AI Content Detector</h1>
          <div className="flex gap-4 items-center">
            <SignedOut>
              <SignInButton mode="modal">
                <button className="px-4 py-2 text-sm font-medium text-text-secondary hover:text-text-primary transition-colors">
                  Sign In
                </button>
              </SignInButton>
              <SignUpButton mode="modal">
                <button className="btn-cyber">
                  Get Started
                </button>
              </SignUpButton>
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

      {/* Hero */}
      <main className="relative container mx-auto px-4 py-12">
        <div className="max-w-5xl mx-auto space-y-8 animate-fade-up">
          {/* Hero Text */}
          <div className="text-center space-y-4">
            <div className="inline-block">
              <span className="badge-glow text-xs">
                Powered by 6-Dimensional Analysis
              </span>
            </div>

            <h2 className="text-5xl md:text-6xl font-bold tracking-tight leading-tight">
              Detect AI-Generated{' '}
              <span className="cyber-text">Content</span>
            </h2>

            <p className="text-lg md:text-xl text-text-secondary max-w-2xl mx-auto leading-relaxed">
              Advanced AI detection analyzing perplexity, coherence, burstiness, originality,
              personal voice, and pattern recognition.
            </p>
          </div>

          {/* Detection Input */}
          <div className="card-glass p-8 space-y-4">
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <label className="text-sm font-medium text-text-primary">
                  Paste your text to analyze
                </label>
                <div className="text-sm">
                  <span className={wordCount < 50 ? 'text-warning' : wordCount > 10000 ? 'text-error' : 'text-success'}>
                    {wordCount}
                  </span>
                  <span className="text-text-tertiary"> / 10,000 words</span>
                  {wordCount < 50 && (
                    <span className="text-warning ml-2">(min 50)</span>
                  )}
                </div>
              </div>

              <textarea
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="Paste your essay, article, or any text content here. Minimum 50 words required for accurate detection..."
                className="w-full h-64 px-4 py-3 bg-background-secondary border border-border rounded-lg
                         text-text-primary placeholder-text-tertiary resize-none
                         focus:outline-none focus:border-accent-primary focus:ring-1 focus:ring-accent-primary
                         transition-colors"
                disabled={isAnalyzing}
              />
            </div>

            {error && (
              <div className="p-4 bg-error/10 border border-error/30 rounded-lg text-error text-sm">
                {error}
              </div>
            )}

            <button
              onClick={handleAnalyze}
              disabled={!isValid || isAnalyzing}
              className="w-full btn-primary py-4 text-lg font-medium disabled:opacity-50 disabled:cursor-not-allowed
                       flex items-center justify-center gap-2"
            >
              {isAnalyzing ? (
                <>
                  <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Analyzing...
                </>
              ) : (
                'Check Now →'
              )}
            </button>
          </div>

          {/* Features */}
          <div className="grid md:grid-cols-3 gap-4 mt-12">
            <div className="card-glass text-center p-6">
              <div className="text-3xl mb-2">🎯</div>
              <h3 className="font-semibold mb-1 text-text-primary">6D Analysis</h3>
              <p className="text-sm text-text-secondary">
                Multi-dimensional scoring for accurate detection
              </p>
            </div>
            <div className="card-glass text-center p-6">
              <div className="text-3xl mb-2">⚡</div>
              <h3 className="font-semibold mb-1 text-text-primary">Instant Results</h3>
              <p className="text-sm text-text-secondary">
                Get detailed analysis in seconds
              </p>
            </div>
            <div className="card-glass text-center p-6">
              <div className="text-3xl mb-2">🔒</div>
              <h3 className="font-semibold mb-1 text-text-primary">Blockchain Proof</h3>
              <p className="text-sm text-text-secondary">
                Verify human authorship permanently
              </p>
            </div>
          </div>

          {/* How It Works */}
          <div className="mt-16 space-y-6">
            <h3 className="text-3xl font-bold text-center gradient-text">How It Works</h3>

            <div className="grid md:grid-cols-2 gap-6">
              {[
                {
                  title: 'Perplexity Analysis',
                  desc: 'Measures text unpredictability using GPT-2. AI text tends to be more predictable.'
                },
                {
                  title: 'Coherence Detection',
                  desc: 'Analyzes logical flow and connections. Human writing has natural imperfections.'
                },
                {
                  title: 'Burstiness Score',
                  desc: 'Detects complexity variation. Humans vary sentence structure more than AI.'
                },
                {
                  title: 'Originality Check',
                  desc: 'Identifies AI-typical phrases and clichés vs. unique human phrasing.'
                },
                {
                  title: 'Personal Voice',
                  desc: 'Detects personal perspective and subjective language markers.'
                },
                {
                  title: 'Pattern Recognition',
                  desc: 'Identifies structural patterns common in AI-generated text.'
                }
              ].map((feature, i) => (
                <div key={i} className="card-glass p-4 hover:border-accent-primary/30 transition-all">
                  <h4 className="font-semibold mb-1 text-text-primary">{feature.title}</h4>
                  <p className="text-sm text-text-secondary">{feature.desc}</p>
                </div>
              ))}
            </div>
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
