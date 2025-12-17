import Link from 'next/link'
import { SignInButton, SignUpButton, SignedIn, SignedOut, UserButton } from '@clerk/nextjs'

export default function Home() {
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
          <h1 className="text-2xl font-bold gradient-text">Proof of Consideration</h1>
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
              <UserButton afterSignOutUrl="/" />
            </SignedIn>
          </div>
        </div>
      </header>

      {/* Hero */}
      <main className="relative container mx-auto px-4 py-20">
        <div className="max-w-5xl mx-auto text-center space-y-8 animate-fade-up">
          <div className="inline-block">
            <span className="badge-glow text-xs mb-8">
              ✨ The Future of Human Attention
            </span>
          </div>

          <h2 className="text-6xl md:text-7xl font-bold tracking-tight leading-tight">
            Get Paid for{' '}
            <span className="cyber-text">Genuine Attention</span>
          </h2>

          <p className="text-xl md:text-2xl text-text-secondary max-w-3xl mx-auto leading-relaxed">
            The first Web3 marketplace where buyers pay for verified human consideration,
            and considerers earn money by demonstrating real cognitive engagement.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center pt-8">
            <Link href="/tasks" className="btn-primary text-base px-8 py-4">
              Browse Tasks →
            </Link>
            <Link href="/campaigns/new" className="btn-secondary text-base px-8 py-4">
              Create Campaign
            </Link>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-3 gap-8 pt-16 max-w-3xl mx-auto">
            <div className="card-glass text-center p-6">
              <div className="text-3xl font-bold gradient-text">$12K+</div>
              <div className="text-sm text-text-tertiary mt-2">Paid Out</div>
            </div>
            <div className="card-glass text-center p-6">
              <div className="text-3xl font-bold gradient-text">2.5K+</div>
              <div className="text-sm text-text-tertiary mt-2">Verifications</div>
            </div>
            <div className="card-glass text-center p-6">
              <div className="text-3xl font-bold gradient-text">92%</div>
              <div className="text-sm text-text-tertiary mt-2">Pass Rate</div>
            </div>
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-2 gap-6 mt-32 max-w-6xl mx-auto">
          <div className="card-glass hover:-translate-y-1 transition-all duration-300 group">
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-accent-primary to-accent-secondary flex items-center justify-center flex-shrink-0 group-hover:shadow-accent-glow transition-shadow">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                </svg>
              </div>
              <div>
                <h3 className="text-xl font-semibold mb-2 text-text-primary">For Considerers</h3>
                <p className="text-text-secondary leading-relaxed">
                  Browse tasks, provide thoughtful responses, and earn money when your genuine
                  consideration is verified by our AI engine.
                </p>
              </div>
            </div>
          </div>

          <div className="card-glass hover:-translate-y-1 transition-all duration-300 group">
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-success to-success-light flex items-center justify-center flex-shrink-0 group-hover:shadow-cyan-glow transition-shadow">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div>
                <h3 className="text-xl font-semibold mb-2 text-text-primary">For Buyers</h3>
                <p className="text-text-secondary leading-relaxed">
                  Create campaigns, set your criteria, and receive verified responses from
                  real humans who've genuinely engaged with your content.
                </p>
              </div>
            </div>
          </div>

          <div className="card-glass hover:-translate-y-1 transition-all duration-300 group">
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-accent-secondary to-accent-pink flex items-center justify-center flex-shrink-0 group-hover:shadow-purple-glow transition-shadow">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <div>
                <h3 className="text-xl font-semibold mb-2 text-text-primary">AI Verification</h3>
                <p className="text-text-secondary leading-relaxed">
                  Our verification engine scores responses on relevance, novelty, coherence,
                  effort, and authenticity to ensure genuine consideration.
                </p>
              </div>
            </div>
          </div>

          <div className="card-glass hover:-translate-y-1 transition-all duration-300 group">
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-warning to-warning-light flex items-center justify-center flex-shrink-0 group-hover:shadow-pink-glow transition-shadow">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div>
                <h3 className="text-xl font-semibold mb-2 text-text-primary">Instant Payouts</h3>
                <p className="text-text-secondary leading-relaxed">
                  Get paid immediately when your response passes verification.
                  Secure payments processed through Stripe Connect.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* How it Works */}
        <div className="mt-32 max-w-4xl mx-auto">
          <h3 className="text-4xl font-bold text-center mb-4 gradient-text">How It Works</h3>
          <p className="text-center text-text-secondary mb-16">Start earning in four simple steps</p>

          <div className="space-y-6">
            {[
              {
                num: '01',
                title: 'Browse Available Tasks',
                desc: 'Find tasks that match your interests. Each task shows the bounty amount and what type of response is needed.'
              },
              {
                num: '02',
                title: 'Engage with Content',
                desc: 'Read, watch, or review the content. Take your time to form genuine thoughts and insights about what you\'ve considered.'
              },
              {
                num: '03',
                title: 'Submit Your Response',
                desc: 'Write your thoughtful response. Our AI checks for relevance, originality, coherence, effort, and authenticity.'
              },
              {
                num: '04',
                title: 'Get Paid Instantly',
                desc: 'If your response passes verification, you get paid immediately. See your scores and build your reputation.'
              }
            ].map((step, i) => (
              <div key={i} className="card-glass hover:border-accent-primary/30 transition-all group">
                <div className="flex gap-6 items-start">
                  <div className="flex-shrink-0">
                    <div className="text-5xl font-bold bg-gradient-to-br from-accent-primary to-accent-cyan bg-clip-text text-transparent">
                      {step.num}
                    </div>
                  </div>
                  <div className="flex-1">
                    <h4 className="text-xl font-semibold mb-2 text-text-primary group-hover:gradient-text transition-all">
                      {step.title}
                    </h4>
                    <p className="text-text-secondary leading-relaxed">
                      {step.desc}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* CTA Section */}
        <div className="mt-32 relative">
          <div className="card-glass p-12 md:p-16 text-center relative overflow-hidden">
            <div className="absolute inset-0 bg-cyber-gradient opacity-10" />
            <div className="relative z-10">
              <h3 className="text-4xl md:text-5xl font-bold mb-4 gradient-text">
                Ready to Get Started?
              </h3>
              <p className="text-lg md:text-xl mb-8 text-text-secondary max-w-2xl mx-auto">
                Join the marketplace for genuine human attention and start earning today
              </p>
              <SignUpButton mode="modal">
                <button className="btn-cyber text-base px-8 py-4 text-lg">
                  Create Free Account →
                </button>
              </SignUpButton>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="relative border-t border-border/50 mt-32 py-8">
        <div className="container mx-auto px-4 text-center text-text-tertiary">
          <p>© 2024 Proof of Consideration. All rights reserved.</p>
        </div>
      </footer>
    </div>
  )
}
