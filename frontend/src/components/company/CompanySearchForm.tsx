import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { RefreshCcw, Search, X } from 'lucide-react'
import { normalizeNip, isValidNipFormat } from '@/lib/utils/nip'
import { useCompanyRefresh } from '@/lib/hooks/useCompanies'

interface CompanySearchFormProps {
  onSearch: (nip: string) => void
  onClear: () => void
  isLoading?: boolean
  currentNip?: string
}

export function CompanySearchForm({
  onSearch,
  onClear,
  isLoading = false,
  currentNip
}: CompanySearchFormProps) {
  const [searchNip, setSearchNip] = useState('')
  const refreshMutation = useCompanyRefresh()

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (!searchNip.trim()) return

    const normalized = normalizeNip(searchNip)
    if (!isValidNipFormat(normalized)) {
      // Could add toast notification here
      return
    }

    onSearch(normalized)
  }

  const handleClear = () => {
    setSearchNip('')
    onClear()
  }

  const handleRefresh = () => {
    if (currentNip) {
      refreshMutation.mutate(currentNip)
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Search className="size-5" />
          Search Company
        </CardTitle>
        <CardDescription>
          Enter a Polish NIP to get company information from official sources
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSearch} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="nip">NIP (Tax Identification Number)</Label>
            <div className="flex gap-2">
              <Input
                id="nip"
                type="text"
                placeholder="e.g., 123-456-78-90 or 1234567890"
                value={searchNip}
                onChange={(e) => setSearchNip(e.target.value)}
                className="flex-1"
              />
              <Button type="submit" disabled={!searchNip.trim() || isLoading}>
                {isLoading ? 'Searching...' : 'Search'}
              </Button>
              {currentNip && (
                <>
                  <Button
                    type="button"
                    variant="outline"
                    onClick={handleRefresh}
                    disabled={refreshMutation.isPending || currentNip !== searchNip}
                  >
                    <RefreshCcw className="size-4" />
                    Refresh
                  </Button>
                  <Button type="button" variant="outline" onClick={handleClear}>
                    <X className="size-4" />
                  </Button>
                </>
              )}
            </div>
          </div>
          <p className="text-sm text-muted-foreground">
            NIP should be 10 digits long. Spaces and dashes are automatically removed.
          </p>
        </form>
      </CardContent>
    </Card>
  )
}
