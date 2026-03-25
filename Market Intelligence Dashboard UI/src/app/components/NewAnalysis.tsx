import { useState } from 'react'
import { Button } from './ui/button'
import { Input } from './ui/input'
import { Label } from './ui/label'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog'
import { useScrape } from '../hooks/useMarketIntel'
import { Loader2, ExternalLink, CheckCircle } from 'lucide-react'
import { toast } from 'sonner'

interface NewAnalysisProps {
  triggerButton?: React.ReactNode
  className?: string
}

export function NewAnalysis({ triggerButton, className = '' }: NewAnalysisProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [formData, setFormData] = useState({
    url: '',
    company: '',
    maxPages: 30
  })
  const { scrape, loading, result, error } = useScrape()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData.url || !formData.company) {
      toast.error('Please enter URL and company name')
      return
    }

    // Simple URL validation
    try {
      new URL(formData.url)
    } catch {
      toast.error('Please enter a valid URL')
      return
    }

    const companyId = formData.company.toLowerCase().replace(/[^a-z0-9]/g, '-')
    
    await scrape(formData.url, formData.company, formData.maxPages)
    
    if (result) {
      toast.success(`Scraped ${result.files_saved} files from ${formData.company}!`)
      setIsOpen(false)
      setFormData({ url: '', company: '', maxPages: 30 })
      // Auto-navigate to new company dossier
      window.location.href = `/companies/${companyId}`
    }
  }

  const handleOpenChange = (open: boolean) => {
    setIsOpen(open)
    if (!open) {
      // Reset on close
      setFormData({ url: '', company: '', maxPages: 30 })
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={handleOpenChange}>
      <DialogTrigger asChild className={className}>
        {triggerButton || (
          <Button size="lg" className="bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-lg font-medium px-8 h-14 shadow-xl">
            <ExternalLink className="w-5 h-5 mr-2" />
            + New Analysis
          </Button>
        )}
      </DialogTrigger>
      <DialogContent className="max-w-md p-0 max-h-[90vh] overflow-y-auto">
        <DialogHeader className="p-6 pb-4 border-b">
          <DialogTitle className="text-2xl font-bold text-slate-100">New Company Analysis</DialogTitle>
        </DialogHeader>
        
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* URL Input */}
          <div className="space-y-2">
            <Label htmlFor="url" className="text-sm font-medium text-slate-300">
              Company Website URL
            </Label>
            <Input
              id="url"
              type="url"
              placeholder="https://example-university.edu"
              value={formData.url}
              onChange={(e) => setFormData({ ...formData, url: e.target.value })}
              className="h-12 bg-slate-900 border-slate-700 text-slate-100 placeholder-slate-500"
              disabled={loading}
            />
          </div>

          {/* Company Name */}
          <div className="space-y-2">
            <Label htmlFor="company" className="text-sm font-medium text-slate-300">
              Company Name (for analysis)
            </Label>
            <Input
              id="company"
              placeholder="Example University"
              value={formData.company}
              onChange={(e) => setFormData({ ...formData, company: e.target.value })}
              className="h-12 bg-slate-900 border-slate-700 text-slate-100 placeholder-slate-500"
              disabled={loading}
            />
          </div>

          {/* Max Pages */}
          <div className="space-y-2">
            <Label htmlFor="maxPages" className="text-sm font-medium text-slate-300 flex items-center gap-2">
              Max Pages to Scrape <span className="text-xs text-slate-500">(30 default)</span>
            </Label>
            <Input
              id="maxPages"
              type="number"
              min="10"
              max="100"
              value={formData.maxPages}
              onChange={(e) => setFormData({ ...formData, maxPages: parseInt(e.target.value) || 30 })}
              className="h-12 bg-slate-900 border-slate-700 text-slate-100 placeholder-slate-500 w-24"
              disabled={loading}
            />
          </div>

          {/* Error Display */}
          {error && (
            <div className="p-4 bg-red-900/30 border border-red-800 rounded-lg text-red-300 text-sm">
              {error}
            </div>
          )}

          {/* Submit Button */}
          <Button 
            type="submit" 
            className="w-full h-14 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-lg font-semibold shadow-xl"
            disabled={loading || !formData.url || !formData.company}
          >
            {loading ? (
              <>
                <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                Scraping {formData.company}...
              </>
            ) : (
              <>
                <ExternalLink className="w-5 h-5 mr-2" />
                Start Analysis
              </>
            )}
          </Button>

          {result && (
            <div className="p-4 bg-green-900/30 border border-green-800 rounded-lg text-green-300 text-sm space-y-1">
              <div className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-green-400" />
                <span>✅ {result.files_saved} files scraped from {result.total_pages} pages</span>
              </div>
              <div className="text-xs opacity-75">Saved to: {result.output_dir}</div>
            </div>
          )}
        </form>
      </DialogContent>
    </Dialog>
  )
}
