import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Building2, CheckCircle, Clock, AlertCircle } from 'lucide-react'
import { formatNip } from '@/lib/utils/nip'
import { getStatusText } from '@/lib/utils/company'
import { CompanyResponse, ProviderStatus } from '@/types/api'

interface CompanyStatusIndicatorsProps {
  companyResponse: CompanyResponse
}

function getStatusIcon(status: ProviderStatus) {
  switch (status) {
    case 'fresh':
    case 'cached':
      return <CheckCircle className="size-4 text-green-500" />
    case 'rate_limited':
      return <Clock className="size-4 text-yellow-500" />
    case 'error':
      return <AlertCircle className="size-4 text-red-500" />
    default:
      return <AlertCircle className="size-4 text-gray-500" />
  }
}

export function CompanyStatusIndicators({ companyResponse }: CompanyStatusIndicatorsProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Building2 className="size-5" />
          Company Information
        </CardTitle>
        <CardDescription>
          NIP: {formatNip(companyResponse.data.nip)}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              {getStatusIcon(companyResponse.metadata.regon?.status || 'unknown')}
              <span className="font-medium">REGON</span>
            </div>
            <p className="text-sm text-muted-foreground">
              {getStatusText(companyResponse.metadata.regon?.status || 'unknown')}
            </p>
          </div>
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              {getStatusIcon(companyResponse.metadata.mf?.status || 'unknown')}
              <span className="font-medium">MF (Biała Lista)</span>
            </div>
            <p className="text-sm text-muted-foreground">
              {getStatusText(companyResponse.metadata.mf?.status || 'unknown')}
            </p>
          </div>
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              {getStatusIcon(companyResponse.metadata.vies?.status || 'unknown')}
              <span className="font-medium">VIES</span>
            </div>
            <p className="text-sm text-muted-foreground">
              {getStatusText(companyResponse.metadata.vies?.status || 'unknown')}
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
