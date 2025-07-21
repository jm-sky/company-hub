import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { AlertCircle, Building, MapPin, Phone, Calendar, FileText, Globe, CreditCard, Users, ShieldCheck } from 'lucide-react'
import { CompanyResponse, RegonCompanyData, MfCompanyData } from '@/types/api'
import {
  parseRegonDetailedData,
  formatRegonAddress,
  formatRegonPhone,
  formatRegonDate,
  getEntityTypeLabel,
} from '@/lib/utils/regon'
import {
  formatMfDate,
  formatMfVatStatus,
  formatMfAddress,
  getMfStatusBadgeVariant,
} from '@/lib/utils/mf'
import { BankAccountCard } from './BankAccountCard'

interface CompanyDataDisplayProps {
  companyResponse: CompanyResponse
}

interface RegonDataCardProps {
  regonData: RegonCompanyData
}

function RegonDataCard({ regonData }: RegonDataCardProps) {
  const parsedData = regonData.detailed_data ? parseRegonDetailedData(regonData.detailed_data) : null;
  const searchData = regonData.search_result?.data;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Building className="size-5" />
          Dane REGON
        </CardTitle>
        <CardDescription>
          Oficjalne dane z rejestru działalności gospodarczej
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {/* Basic Company Information */}
          <div className="space-y-3">
            <h4 className="font-semibold text-lg">Informacje podstawowe</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label className="text-sm font-medium text-muted-foreground">Nazwa firmy</Label>
                <p className="text-sm font-medium">{parsedData?.name || searchData?.Nazwa || 'N/A'}</p>
              </div>
              <div>
                <Label className="text-sm font-medium text-muted-foreground">Skrócona nazwa</Label>
                <p className="text-sm">{parsedData?.shortName || 'N/A'}</p>
              </div>
              <div>
                <Label className="text-sm font-medium text-muted-foreground">NIP</Label>
                <p className="text-sm font-mono">{regonData.nip}</p>
              </div>
              <div>
                <Label className="text-sm font-medium text-muted-foreground">REGON</Label>
                <p className="text-sm font-mono">{regonData.regon || searchData?.Regon || 'N/A'}</p>
              </div>
              <div>
                <Label className="text-sm font-medium text-muted-foreground">Typ podmiotu</Label>
                <Badge variant="outline">{getEntityTypeLabel(regonData.entity_type || 'N/A')}</Badge>
              </div>
            </div>
          </div>

          {/* Address Information */}
          <div className="space-y-3">
            <h4 className="font-semibold text-lg flex items-center gap-2">
              <MapPin className="size-4" />
              Adres siedziby
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label className="text-sm font-medium text-muted-foreground">Pełny adres</Label>
                <p className="text-sm">
                  {parsedData ? formatRegonAddress(parsedData) :
                   `${searchData?.Ulica || ''} ${searchData?.NrNieruchomosci || ''}, ${searchData?.KodPocztowy || ''} ${searchData?.Miejscowosc || ''}`}
                </p>
              </div>
              <div>
                <Label className="text-sm font-medium text-muted-foreground">Województwo</Label>
                <p className="text-sm">{parsedData?.address.voivodeship || searchData?.Wojewodztwo || 'N/A'}</p>
              </div>
              <div>
                <Label className="text-sm font-medium text-muted-foreground">Powiat</Label>
                <p className="text-sm">{parsedData?.address.county || searchData?.Powiat || 'N/A'}</p>
              </div>
              <div>
                <Label className="text-sm font-medium text-muted-foreground">Gmina</Label>
                <p className="text-sm">{parsedData?.address.commune || searchData?.Gmina || 'N/A'}</p>
              </div>
            </div>
          </div>

          {/* Contact Information */}
          {parsedData?.contact && (
            <div className="space-y-3">
              <h4 className="font-semibold text-lg flex items-center gap-2">
                <Phone className="size-4" />
                Kontakt
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {parsedData.contact.phone && (
                  <div>
                    <Label className="text-sm font-medium text-muted-foreground">Telefon</Label>
                    <p className="text-sm font-mono">{formatRegonPhone(parsedData.contact.phone)}</p>
                  </div>
                )}
                {parsedData.contact.fax && (
                  <div>
                    <Label className="text-sm font-medium text-muted-foreground">Faks</Label>
                    <p className="text-sm font-mono">{formatRegonPhone(parsedData.contact.fax)}</p>
                  </div>
                )}
                {parsedData.contact.email && (
                  <div>
                    <Label className="text-sm font-medium text-muted-foreground">Email</Label>
                    <p className="text-sm">{parsedData.contact.email}</p>
                  </div>
                )}
                {parsedData.contact.website && (
                  <div>
                    <Label className="text-sm font-medium text-muted-foreground">Strona internetowa</Label>
                    <p className="text-sm">
                      <a href={parsedData.contact.website} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                        {parsedData.contact.website}
                      </a>
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Dates */}
          {parsedData && (
            <div className="space-y-3">
              <h4 className="font-semibold text-lg flex items-center gap-2">
                <Calendar className="size-4" />
                Daty ważne
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {parsedData.creationDate && (
                  <div>
                    <Label className="text-sm font-medium text-muted-foreground">Data powstania</Label>
                    <p className="text-sm">{formatRegonDate(parsedData.creationDate)}</p>
                  </div>
                )}
                {parsedData.businessStartDate && (
                  <div>
                    <Label className="text-sm font-medium text-muted-foreground">Rozpoczęcie działalności</Label>
                    <p className="text-sm">{formatRegonDate(parsedData.businessStartDate)}</p>
                  </div>
                )}
                {parsedData.registrationDate && (
                  <div>
                    <Label className="text-sm font-medium text-muted-foreground">Data wpisu do rejestru</Label>
                    <p className="text-sm">{formatRegonDate(parsedData.registrationDate)}</p>
                  </div>
                )}
                {parsedData.lastChangeDate && (
                  <div>
                    <Label className="text-sm font-medium text-muted-foreground">Ostatnia zmiana</Label>
                    <p className="text-sm">{formatRegonDate(parsedData.lastChangeDate)}</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Legal Form */}
          {parsedData?.legalForm && (
            <div className="space-y-3">
              <h4 className="font-semibold text-lg flex items-center gap-2">
                <FileText className="size-4" />
                Forma prawna
              </h4>
              <div className="grid grid-cols-1 gap-4">
                <div>
                  <Label className="text-sm font-medium text-muted-foreground">Podstawowa forma prawna</Label>
                  <p className="text-sm">{parsedData.legalForm.basicForm}</p>
                </div>
                <div>
                  <Label className="text-sm font-medium text-muted-foreground">Szczegółowa forma prawna</Label>
                  <p className="text-sm">{parsedData.legalForm.specificForm}</p>
                </div>
                <div>
                  <Label className="text-sm font-medium text-muted-foreground">Forma finansowania</Label>
                  <p className="text-sm">{parsedData.legalForm.financingForm}</p>
                </div>
                <div>
                  <Label className="text-sm font-medium text-muted-foreground">Forma własności</Label>
                  <p className="text-sm">{parsedData.legalForm.ownershipForm}</p>
                </div>
              </div>
            </div>
          )}

          {/* Registration Details */}
          {parsedData?.registration && (
            <div className="space-y-3">
              <h4 className="font-semibold text-lg flex items-center gap-2">
                <Globe className="size-4" />
                Rejestracja
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label className="text-sm font-medium text-muted-foreground">Numer rejestru</Label>
                  <p className="text-sm font-mono">{parsedData.registration.registryNumber}</p>
                </div>
                <div>
                  <Label className="text-sm font-medium text-muted-foreground">Rodzaj rejestru</Label>
                  <p className="text-sm">{parsedData.registration.registryType}</p>
                </div>
                <div className="md:col-span-2">
                  <Label className="text-sm font-medium text-muted-foreground">Organ rejestrowy</Label>
                  <p className="text-sm">{parsedData.registration.registryAuthority}</p>
                </div>
                {parsedData.localUnitsCount !== undefined && (
                  <div>
                    <Label className="text-sm font-medium text-muted-foreground">Liczba jednostek lokalnych</Label>
                    <p className="text-sm">{parsedData.localUnitsCount}</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Fetch Information */}
          <div className="pt-4 border-t">
            <div className="flex items-center justify-between text-sm text-muted-foreground">
              <span>Pobrano: {formatRegonDate(regonData.fetched_at)}</span>
              <Badge variant="outline" className="text-xs">
                {regonData.report_type || 'Raport podstawowy'}
              </Badge>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

interface MfDataCardProps {
  mfData: MfCompanyData
}

function MfDataCard({ mfData }: MfDataCardProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <ShieldCheck className="size-5" />
          Dane MF (Biała Lista)
        </CardTitle>
        <CardDescription>
          Informacje o podatniku VAT z białej listy Ministerstwa Finansów
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {/* Basic Information */}
          <div className="space-y-3">
            <h4 className="font-semibold text-lg">Informacje podstawowe</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label className="text-sm font-medium text-muted-foreground">Nazwa firmy</Label>
                <p className="text-sm font-medium">{mfData.name || 'N/A'}</p>
              </div>
              <div>
                <Label className="text-sm font-medium text-muted-foreground">NIP</Label>
                <p className="text-sm font-mono">{mfData.nip}</p>
              </div>
              <div>
                <Label className="text-sm font-medium text-muted-foreground">REGON</Label>
                <p className="text-sm font-mono">{mfData.regon || 'N/A'}</p>
              </div>
              <div>
                <Label className="text-sm font-medium text-muted-foreground">KRS</Label>
                <p className="text-sm font-mono">{mfData.krs || 'N/A'}</p>
              </div>
              <div>
                <Label className="text-sm font-medium text-muted-foreground">Status VAT</Label>
                <Badge variant={getMfStatusBadgeVariant(mfData.status_vat || '')}>
                  {formatMfVatStatus(mfData.status_vat || '')}
                </Badge>
              </div>
              <div>
                <Label className="text-sm font-medium text-muted-foreground">Data sprawdzenia</Label>
                <p className="text-sm">{formatMfDate(mfData.date)}</p>
              </div>
            </div>
          </div>

          {/* VAT Registration Details */}
          {(mfData.registration_legal_date || mfData.registration_denial_date || mfData.restoration_date || mfData.removal_date) && (
            <div className="space-y-3">
              <h4 className="font-semibold text-lg flex items-center gap-2">
                <Calendar className="size-4" />
                Historia rejestracji VAT
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {mfData.registration_legal_date && (
                  <div>
                    <Label className="text-sm font-medium text-muted-foreground">Data rejestracji</Label>
                    <p className="text-sm">{formatMfDate(mfData.registration_legal_date)}</p>
                  </div>
                )}
                {mfData.registration_denial_date && (
                  <div>
                    <Label className="text-sm font-medium text-muted-foreground">Data odmowy rejestracji</Label>
                    <p className="text-sm">{formatMfDate(mfData.registration_denial_date)}</p>
                  </div>
                )}
                {mfData.restoration_date && (
                  <div>
                    <Label className="text-sm font-medium text-muted-foreground">Data przywrócenia</Label>
                    <p className="text-sm">{formatMfDate(mfData.restoration_date)}</p>
                  </div>
                )}
                {mfData.removal_date && (
                  <div>
                    <Label className="text-sm font-medium text-muted-foreground">Data wykreślenia</Label>
                    <p className="text-sm">{formatMfDate(mfData.removal_date)}</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Address Information */}
          {mfData.address && (
            <div className="space-y-3">
              <h4 className="font-semibold text-lg flex items-center gap-2">
                <MapPin className="size-4" />
                Adres działalności
              </h4>
              <div className="grid grid-cols-1 gap-4">
                <div>
                  <Label className="text-sm font-medium text-muted-foreground">Pełny adres</Label>
                  <p className="text-sm">{formatMfAddress(mfData.address)}</p>
                </div>
              </div>
            </div>
          )}

          {/* Residence Address */}
          {mfData.residence_address && (
            <div className="space-y-3">
              <h4 className="font-semibold text-lg flex items-center gap-2">
                <MapPin className="size-4" />
                Adres zamieszkania
              </h4>
              <div className="grid grid-cols-1 gap-4">
                <div>
                  <Label className="text-sm font-medium text-muted-foreground">Pełny adres</Label>
                  <p className="text-sm">{formatMfAddress(mfData.residence_address)}</p>
                </div>
              </div>
            </div>
          )}

          {/* Bank Accounts */}
          {mfData.bank_accounts && mfData.bank_accounts.length > 0 && (
            <div className="space-y-3">
              <h4 className="font-semibold text-lg flex items-center gap-2">
                <CreditCard className="size-4" />
                Rachunki bankowe
              </h4>
              <div className="space-y-3">
                {mfData.bank_accounts.map((account, index) => (
                  <BankAccountCard key={index} account={account} index={index} />
                ))}
                {mfData.has_virtual_accounts && (
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <AlertCircle className="size-4" />
                    Posiada rachunki wirtualne
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Representatives */}
          {mfData.representatives && mfData.representatives.length > 0 && (
            <div className="space-y-3">
              <h4 className="font-semibold text-lg flex items-center gap-2">
                <Users className="size-4" />
                Reprezentanci
              </h4>
              <div className="space-y-2">
                {mfData.representatives.map((rep, index) => (
                  <div key={index} className="p-3 bg-muted rounded-lg">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                      <div>
                        <Label className="text-xs font-medium text-muted-foreground">Nazwa/Imię i nazwisko</Label>
                        <p className="text-sm">
                          {rep.company_name || `${rep.first_name} ${rep.last_name}`.trim()}
                        </p>
                      </div>
                      <div>
                        <Label className="text-xs font-medium text-muted-foreground">NIP</Label>
                        <p className="text-sm font-mono">{rep.nip || 'N/A'}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Authorized Persons */}
          {mfData.authorized_persons && mfData.authorized_persons.length > 0 && (
            <div className="space-y-3">
              <h4 className="font-semibold text-lg flex items-center gap-2">
                <Users className="size-4" />
                Osoby upoważnione
              </h4>
              <div className="space-y-2">
                {mfData.authorized_persons.map((person, index) => (
                  <div key={index} className="p-3 bg-muted rounded-lg">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                      <div>
                        <Label className="text-xs font-medium text-muted-foreground">Nazwa/Imię i nazwisko</Label>
                        <p className="text-sm">
                          {person.company_name || `${person.first_name} ${person.last_name}`.trim()}
                        </p>
                      </div>
                      <div>
                        <Label className="text-xs font-medium text-muted-foreground">NIP</Label>
                        <p className="text-sm font-mono">{person.nip || 'N/A'}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Partners */}
          {mfData.partners && mfData.partners.length > 0 && (
            <div className="space-y-3">
              <h4 className="font-semibold text-lg flex items-center gap-2">
                <Users className="size-4" />
                Wspólnicy
              </h4>
              <div className="space-y-2">
                {mfData.partners.map((partner, index) => (
                  <div key={index} className="p-3 bg-muted rounded-lg">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                      <div>
                        <Label className="text-xs font-medium text-muted-foreground">Nazwa/Imię i nazwisko</Label>
                        <p className="text-sm">
                          {partner.company_name || `${partner.first_name} ${partner.last_name}`.trim()}
                        </p>
                      </div>
                      <div>
                        <Label className="text-xs font-medium text-muted-foreground">NIP</Label>
                        <p className="text-sm font-mono">{partner.nip || 'N/A'}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Fetch Information */}
          <div className="pt-4 border-t">
            <div className="flex items-center justify-between text-sm text-muted-foreground">
              <span>Pobrano: {formatMfDate(mfData.fetched_at)}</span>
              <Badge variant="outline" className="text-xs">
                {mfData.request_id ? `ID: ${mfData.request_id}` : 'Biała Lista MF'}
              </Badge>
            </div>
          </div>
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

function hasCompanyData(companyResponse: CompanyResponse): boolean {
  return !!(companyResponse.data.regon?.found || companyResponse.data.mf?.found || companyResponse.data.vies);
}

export function CompanyDataDisplay({ companyResponse }: CompanyDataDisplayProps) {
  return (
    <div className="space-y-6">
      {/* REGON Data */}
      {companyResponse.data.regon?.found && (
        <RegonDataCard regonData={companyResponse.data.regon} />
      )}

      {/* REGON Error */}
      {companyResponse.data.regon && !companyResponse.data.regon.found && (
        <Alert>
          <AlertCircle className="size-4" />
          <AlertDescription>
            {companyResponse.data.regon.message || 'Nie znaleziono danych w rejestrze REGON'}
          </AlertDescription>
        </Alert>
      )}

      {/* MF Data */}
      {companyResponse.data.mf?.found && (
        <MfDataCard mfData={companyResponse.data.mf} />
      )}

      {/* MF Error */}
      {companyResponse.data.mf && !companyResponse.data.mf.found && (
        <Alert>
          <AlertCircle className="size-4" />
          <AlertDescription>
            {companyResponse.data.mf.message || 'Nie znaleziono danych w białej liście MF'}
          </AlertDescription>
        </Alert>
      )}

      {/* VIES Data */}
      {companyResponse.data.vies && (
        <DataCard
          title="Dane VIES"
          description="Informacje o walidacji VAT w UE"
          data={companyResponse.data.vies}
        />
      )}

      {/* No Data Message */}
      {!hasCompanyData(companyResponse) && <NoDataAlert />}
    </div>
  )
}
