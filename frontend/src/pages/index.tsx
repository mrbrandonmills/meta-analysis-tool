import React from 'react'
import Head from 'next/head'
import dynamic from 'next/dynamic'
import Hero from '@/components/landing/Hero'
import FeaturesShowcase from '@/components/landing/FeaturesShowcase'

// Dynamic import to fix Framer Motion SSR hydration with Next.js 15
const HighlightDemo = dynamic(
  () => import('@/components/demo/HighlightDemo').then(mod => mod.HighlightDemo),
  { ssr: false }
)

const LandingPage: React.FC = () => {
  return (
    <>
      <Head>
        <title>Academic Research Platform - AI-Powered Meta-Analysis & Peer Review</title>
        <meta
          name="description"
          content="Transform your research workflow with AI agents. Meta-analysis, peer review, and research discovery in hours, not weeks."
        />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className="min-h-screen">
        <Hero />
        <FeaturesShowcase />

        {/* ESPN-Style Highlight Demo */}
        <section className="relative h-screen bg-black">
          <HighlightDemo autoPlay={true} />
        </section>
      </main>
    </>
  )
}

export default LandingPage
