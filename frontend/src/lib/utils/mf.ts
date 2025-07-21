import { MfAddress } from "@/types/api";

export function formatMfDate(dateString: string): string {
  if (!dateString) return '';

  try {
    const date = new Date(dateString);
    return date.toLocaleDateString('pl-PL', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  } catch {
    return dateString;
  }
}

export function formatMfVatStatus(status: string): string {
  switch (status) {
    case 'Czynny': return 'Aktywny podatnik VAT';
    case 'Zwolniony': return 'Zwolniony z VAT';
    case 'Niezarejestrowany': return 'Niezarejestrowany';
    default: return status;
  }
}

export function formatMfAddress(address: MfAddress): string {
  if (!address) return '';

  const parts = [];

  if (address.street) parts.push(address.street);
  if (address.building_number) parts.push(address.building_number);
  if (address.apartment_number) parts.push(`/${address.apartment_number}`);

  const streetAddress = parts.join(' ');

  const locationParts = [];
  if (address.postal_code) locationParts.push(address.postal_code);
  if (address.city) locationParts.push(address.city);

  const location = locationParts.join(' ');

  return [streetAddress, location].filter(Boolean).join(', ');
}

export function formatMfBankAccount(account: string): string {
  if (!account) return '';

  // Format Polish bank account number (26 digits)
  const cleaned = account.replace(/\s/g, '');
  if (cleaned.length === 26) {
    return cleaned.replace(/(.{2})(.{4})(.{4})(.{4})(.{4})(.{4})(.{4})/, '$1 $2 $3 $4 $5 $6 $7');
  }

  return account;
}

export function getMfStatusBadgeVariant(status: string): 'default' | 'secondary' | 'destructive' | 'outline' {
  switch (status) {
    case 'Czynny': return 'default';
    case 'Zwolniony': return 'secondary';
    case 'Niezarejestrowany': return 'destructive';
    default: return 'outline';
  }
}
