import { useState, useEffect } from 'react'

// Types for frontend
interface BackendInsight {
  title: string
  description: string
  impact: string
  evidence: string
  recommended_action: string
  source: string
}

export function useCompanies() {
  const [companies, setCompanies] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('/api/companies')
      .then(res => res.json())
      .then((data) => setCompanies(data.companies || []))
      .catch(err => console.error(err))
      .finally(() => setLoading(false))
  }, [])

  return { companies, loading }
}

export function useInsights() {
  const [insights, setInsights] = useState<BackendInsight[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('/api/insights')
      .then(res => res.json())
      .then((data) => setInsights(data.insights || []))
      .catch(err => console.error(err))
      .finally(() => setLoading(false))
  }, [])

  return { insights, loading }
}

interface ScrapeResult {
  status: string
  company: string
  files_saved: number
  total_pages: number
  output_dir: string
}

export function useScrape() {
  const [result, setResult] = useState<ScrapeResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const scrape = async (url: string, company: string, maxPages = 30) => {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch('/api/scrape', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url, company, max_pages: maxPages })
      })
      if (!res.ok) throw new Error(`Scrape failed: ${res.status}`)
      const data = await res.json()
      setResult(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  return { scrape, result, loading, error }
}
