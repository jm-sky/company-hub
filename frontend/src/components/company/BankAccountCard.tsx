import { formatMfDate, formatMfBankAccount } from '@/lib/utils/mf'
import { StatusBadge } from "@/components/ui/status-badge"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { AlertCircle } from "lucide-react"
import { MfBankAccount } from '@/types/api'

export function BankAccountCard({ account, index }: { account: MfBankAccount, index: number }) {
  return (
    <div key={index} className="p-4 bg-muted rounded-lg border">
      <div className="space-y-3">
        {/* Account number and validation status */}
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <p className="text-sm font-mono font-medium">{formatMfBankAccount(account.account_number)}</p>
            <p className="text-xs text-muted-foreground">
              Zweryfikowany: {formatMfDate(account.date)}
            </p>
          </div>
          <StatusBadge
            status={account.validated ? "success" : "warning"}
            label={account.validated ? 'Zweryfikowany' : 'Niezweryfikowany'}
          />
        </div>

        {/* IBAN enrichment data */}
        {account.enrichment_available && (
          <div className="pt-2 border-t border-border/50">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <div>
                <Label className="text-xs font-medium text-muted-foreground">Nazwa banku</Label>
                <p className="text-sm font-medium">{account.bank_name ?? 'N/A'}</p>
              </div>
              <div>
                <Label className="text-xs font-medium text-muted-foreground">Kod BIC/SWIFT</Label>
                <p className="text-sm font-mono">{account.bic ?? 'N/A'}</p>
              </div>
              {account.formatted_iban && account.formatted_iban !== account.account_number && (
                <div>
                  <Label className="text-xs font-medium text-muted-foreground">Sformatowany IBAN</Label>
                  <p className="text-sm font-mono">{account.formatted_iban}</p>
                </div>
              )}
              {account.enrichment?.bank_country && (
                <div>
                  <Label className="text-xs font-medium text-muted-foreground">Kraj banku</Label>
                  <p className="text-sm">{account.enrichment.bank_country}</p>
                </div>
              )}
            </div>
            <div className="flex items-center gap-2 mt-2">
              <Badge variant="outline" className="text-xs">
                Wzbogacone przez {account.enrichment?.enrichment_source ?? 'IBAN API'}
              </Badge>
            </div>
          </div>
        )}

        {/* Enrichment error */}
        {account.enrichment_available === false && account.enrichment_error && (
          <div className="pt-2 border-t border-border/50">
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <AlertCircle className="size-3" />
              Nie udało się wzbogacić danych: {account.enrichment_error}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
