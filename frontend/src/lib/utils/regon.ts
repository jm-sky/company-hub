import { RegonDetailedData } from '@/types/api';

export interface RegonAddress {
  country: string;
  voivodeship: string;
  county: string;
  commune: string;
  city: string;
  postalCode: string;
  street: string;
  buildingNumber: string;
  apartmentNumber?: string;
}

export interface RegonContact {
  phone?: string;
  internalPhone?: string;
  fax?: string;
  email?: string;
  website?: string;
}

export interface ParsedRegonData {
  // Basic info
  regon: string;
  nip: string;
  name: string;
  shortName?: string;

  // Dates
  creationDate?: string;
  registrationDate?: string;
  businessStartDate?: string;
  lastChangeDate?: string;
  businessEndDate?: string;

  // Address
  address: RegonAddress

  // Contact
  contact: RegonContact

  // Legal form
  legalForm: {
    basicForm: string;
    specificForm: string;
    financingForm: string;
    ownershipForm: string;
  };

  // Registration
  registration: {
    registryNumber: string;
    registryType: string;
    registryAuthority: string;
    foundingAuthority?: string;
  };

  // Other
  localUnitsCount?: number;
}

export function parseRegonDetailedData(detailedData: RegonDetailedData): ParsedRegonData | null {
  if (!detailedData?.raw_response) return null;

  try {
    // Extract the XML data from the HTML-encoded string
    const xmlMatch = detailedData.raw_response.match(/<root>.*?<\/root>/s);
    if (!xmlMatch) return null;

    const xmlString = xmlMatch[0];

    // Parse the XML (simple approach - in production, use proper XML parser)
    const getValue = (tag: string): string => {
      const pattern = new RegExp(`<${tag}>(.*?)</${tag}>`, 's');
      const match = xmlString.match(pattern);
      return match ? match[1].trim() : '';
    };

    const parsed: ParsedRegonData = {
      regon: getValue('praw_regon9'),
      nip: getValue('praw_nip'),
      name: getValue('praw_nazwa'),
      shortName: getValue('praw_nazwaSkrocona') || undefined,

      creationDate: getValue('praw_dataPowstania') || undefined,
      registrationDate: getValue('praw_dataWpisuDoRejestruEwidencji') || undefined,
      businessStartDate: getValue('praw_dataRozpoczeciaDzialalnosci') || undefined,
      lastChangeDate: getValue('praw_dataZaistnieniaZmiany') || undefined,
      businessEndDate: getValue('praw_dataZakonczeniaDzialalnosci') || undefined,

      address: {
        country: getValue('praw_adSiedzKraj_Nazwa'),
        voivodeship: getValue('praw_adSiedzWojewodztwo_Nazwa'),
        county: getValue('praw_adSiedzPowiat_Nazwa'),
        commune: getValue('praw_adSiedzGmina_Nazwa'),
        city: getValue('praw_adSiedzMiejscowosc_Nazwa'),
        postalCode: getValue('praw_adSiedzKodPocztowy'),
        street: getValue('praw_adSiedzUlica_Nazwa'),
        buildingNumber: getValue('praw_adSiedzNumerNieruchomosci'),
        apartmentNumber: getValue('praw_adSiedzNumerLokalu') || undefined,
      },

      contact: {
        phone: getValue('praw_numerTelefonu') || undefined,
        internalPhone: getValue('praw_numerWewnetrznyTelefonu') || undefined,
        fax: getValue('praw_numerFaksu') || undefined,
        email: getValue('praw_adresEmail') || undefined,
        website: getValue('praw_adresStronyinternetowej') || undefined,
      },

      legalForm: {
        basicForm: getValue('praw_podstawowaFormaPrawna_Nazwa'),
        specificForm: getValue('praw_szczegolnaFormaPrawna_Nazwa'),
        financingForm: getValue('praw_formaFinansowania_Nazwa'),
        ownershipForm: getValue('praw_formaWlasnosci_Nazwa'),
      },

      registration: {
        registryNumber: getValue('praw_numerWRejestrzeEwidencji'),
        registryType: getValue('praw_rodzajRejestruEwidencji_Nazwa'),
        registryAuthority: getValue('praw_organRejestrowy_Nazwa'),
        foundingAuthority: getValue('praw_organZalozycielski_Nazwa') || undefined,
      },

      localUnitsCount: parseInt(getValue('praw_liczbaJednLokalnych')) || undefined,
    };

    return parsed;
  } catch (error) {
    console.error('Error parsing REGON detailed data:', error);
    return null;
  }
}

export function formatRegonAddress(data: ParsedRegonData): string {
  const parts = [];

  if (data.address.street) parts.push(data.address.street);
  if (data.address.buildingNumber) parts.push(data.address.buildingNumber);
  if (data.address.apartmentNumber) parts.push(`/${data.address.apartmentNumber}`);

  const streetAddress = parts.join(' ');

  const locationParts = [];
  if (data.address.postalCode) locationParts.push(data.address.postalCode);
  if (data.address.city) locationParts.push(data.address.city);

  const location = locationParts.join(' ');

  return [streetAddress, location].filter(Boolean).join(', ');
}

export function formatRegonPhone(phone: string): string {
  if (!phone) return '';

  // Format Polish phone number (e.g., 0222426007 -> +48 22 242 60 07)
  const cleaned = phone.replace(/\D/g, '');

  if (cleaned.length === 10 && cleaned.startsWith('0')) {
    // Remove leading 0 and format as +48 XX XXX XX XX
    const formatted = cleaned.substring(1);
    return `+48 ${formatted.substring(0, 2)} ${formatted.substring(2, 5)} ${formatted.substring(5, 7)} ${formatted.substring(7)}`;
  }

  return phone;
}

export function formatRegonDate(dateString: string): string {
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

export function getEntityTypeLabel(entityType: string): string {
  switch (entityType) {
    case 'P': return 'Osoba prawna';
    case 'F': return 'Osoba fizyczna';
    case 'LP': return 'Jednostka lokalna osoby prawnej';
    case 'LF': return 'Jednostka lokalna osoby fizycznej';
    default: return entityType;
  }
}
