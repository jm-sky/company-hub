# Internationalization (i18n) Setup

This project uses `next-intl` for internationalization support with English (EN) and Polish (PL) languages.

## Structure

```
frontend/
├── messages/
│   ├── en.json          # English translations
│   └── pl.json          # Polish translations
├── src/
│   ├── i18n.ts          # i18n configuration
│   ├── middleware.ts     # Locale detection middleware
│   ├── app/
│   │   ├── [locale]/    # Locale-based routing
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx
│   │   │   └── ...
│   │   └── layout.tsx    # Root layout
│   ├── components/
│   │   └── language-switcher.tsx
│   └── hooks/
│       └── use-translations.ts
```

## Usage

### 1. Using Translations in Components

```tsx
import { useTranslations } from 'next-intl';
// or use the custom hook
import { useAppTranslations } from '@/hooks/use-translations';

export function MyComponent() {
  const t = useTranslations('common');
  // or
  const { common, navigation } = useAppTranslations();

  return (
    <div>
      <h1>{t('welcome')}</h1>
      <button>{common('save')}</button>
    </div>
  );
}
```

### 2. Server Components

```tsx
import { getTranslations } from 'next-intl/server';

export async function ServerComponent() {
  const t = await getTranslations('common');

  return <h1>{t('welcome')}</h1>;
}
```

### 3. Navigation with Locale

```tsx
import { useRouter, usePathname } from 'next/navigation';
import { useLocale } from 'next-intl';

export function Navigation() {
  const router = useRouter();
  const pathname = usePathname();
  const locale = useLocale();

  const navigateToPage = (page: string) => {
    router.push(`/${locale}${page}`);
  };

  return (
    <nav>
      <button onClick={() => navigateToPage('/dashboard')}>
        Dashboard
      </button>
    </nav>
  );
}
```

### 4. Language Switcher

The `LanguageSwitcher` component is already created and ready to use:

```tsx
import { LanguageSwitcher } from '@/components/language-switcher';

export function Header() {
  return (
    <header>
      <LanguageSwitcher />
    </header>
  );
}
```

## Adding New Translations

1. Add new keys to both `messages/en.json` and `messages/pl.json`
2. Use the translations in your components as shown above

## URL Structure

- English: `/en/page` or `/page` (default)
- Polish: `/pl/page`

## Configuration

- **Default locale**: English (`en`)
- **Supported locales**: English (`en`), Polish (`pl`)
- **Middleware**: Automatically detects locale from URL and browser preferences
- **Fallback**: Falls back to English if locale is not supported

## Migration Notes

- All existing routes are now prefixed with locale (`/[locale]/...`)
- Update any hardcoded navigation links to include locale
- Use `useLocale()` hook to get current locale in components
- Use `useRouter()` and `usePathname()` for navigation with locale support
