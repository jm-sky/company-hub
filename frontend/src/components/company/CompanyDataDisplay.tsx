import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { AlertCircle } from 'lucide-react'
import { getRegonProperty, hasCompanyData } from '@/lib/utils/company'
import { CompanyResponse } from '@/types/api'

interface CompanyDataDisplayProps {
  companyResponse: CompanyResponse
}

interface RegonDataCardProps {
  regonData: Record<string, unknown>
}

function RegonDataCard({ regonData }: RegonDataCardProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>REGON Data</CardTitle>
        <CardDescription>
          Official business registry information
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {getRegonProperty(regonData, 'name') && (
            <div>
              <Label className="text-sm font-medium">Company Name</Label>
              <p className="text-sm">{getRegonProperty(regonData, 'name')}</p>
            </div>
          )}
          {getRegonProperty(regonData, 'regon') && (
            <div>
              <Label className="text-sm font-medium">REGON</Label>
              <p className="text-sm font-mono">{getRegonProperty(regonData, 'regon')}</p>
            </div>
          )}
          {getRegonProperty(regonData, 'address') && (
            <div>
              <Label className="text-sm font-medium">Address</Label>
              <p className="text-sm">{getRegonProperty(regonData, 'address')}</p>
            </div>
          )}
          {getRegonProperty(regonData, 'status') && (
            <div>
              <Label className="text-sm font-medium">Status</Label>
              <p className="text-sm">{getRegonProperty(regonData, 'status')}</p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}

interface DataCardProps {
  title: string
  description: string
  data: Record<string, unknown>
}

function DataCard({ title, description, data }: DataCardProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        <CardDescription>{description}</CardDescription>
      </CardHeader>
      <CardContent>
        <pre className="text-sm bg-muted p-3 rounded-md overflow-x-auto">
          {JSON.stringify(data, null, 2)}
        </pre>
      </CardContent>
    </Card>
  )
}

function NoDataAlert() {
  return (
    <Alert>
      <AlertCircle className="size-4" />
      <AlertDescription>
        No data available for this NIP. This could be due to rate limiting or the company not being found in the databases.
      </AlertDescription>
    </Alert>
  )
}

export function CompanyDataDisplay({ companyResponse }: CompanyDataDisplayProps) {
  return (
    <div className="space-y-6">
      {/* REGON Data */}
      {companyResponse.data.regon && (
        <RegonDataCard regonData={companyResponse.data.regon} />
      )}

      {/* MF Data */}
      {companyResponse.data.mf && (
        <DataCard
          title="MF Data (Biała Lista)"
          description="VAT taxpayer whitelist information"
          data={companyResponse.data.mf}
        />
      )}

      {/* VIES Data */}
      {companyResponse.data.vies && (
        <DataCard
          title="VIES Data"
          description="EU VAT validation information"
          data={companyResponse.data.vies}
        />
      )}

      {/* No Data Message */}
      {!hasCompanyData(companyResponse) && <NoDataAlert />}
    </div>
  )
}