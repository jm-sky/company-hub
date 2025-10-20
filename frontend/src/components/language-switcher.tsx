'use client';

import { useLocale } from 'next-intl';
import { useRouter, usePathname } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Globe } from 'lucide-react';

const languages = [
  { code: 'en', name: 'English', flag: '🇺🇸' },
  { code: 'pl', name: 'Polski', flag: '🇵🇱' }
];

export function LanguageSwitcher() {
  const locale = useLocale();
  const router = useRouter();
  const pathname = usePathname();

  const handleLanguageChange = (newLocale: string) => {
    // Remove the current locale from the pathname
    const pathWithoutLocale = pathname.replace(`/${locale}`, '') || '/';
    // Navigate to the new locale
    router.push(`/${newLocale}${pathWithoutLocale}`);
  };


  return (
    <div className="flex items-center gap-2">
      <Globe className="h-4 w-4" />
      <div className="flex gap-1">
        {languages.map((language) => (
          <Button
            key={language.code}
            variant={locale === language.code ? "default" : "ghost"}
            size="sm"
            onClick={() => handleLanguageChange(language.code)}
            className="flex items-center gap-1 px-2 py-1 text-xs"
          >
            <span>{language.flag}</span>
            <span className="hidden sm:inline">{language.name}</span>
          </Button>
        ))}
      </div>
    </div>
  );
}
