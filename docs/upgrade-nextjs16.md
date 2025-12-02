# Plan aktualizacji do Next.js 16

## Status projektu

- **Aktualna wersja Next.js**: 15.3.5
- **Docelowa wersja Next.js**: 16.x (najnowsza stabilna)
- **React**: 19.0.0 ✅ (kompatybilna z Next.js 16)
- **TypeScript**: 5.x ✅
- **Turbopack**: Już używany w dev mode ✅

## Wprowadzenie

Next.js 16 został wydany 21 października 2024 roku i wprowadza znaczące zmiany:
- Domyślne użycie Turbopack jako bundlera
- Stabilny React Compiler
- Zmiana `middleware` na `proxy`
- Ulepszone API cache'owania
- Nowe funkcje routingu i prefetchingu

## Wymagania wstępne

- ✅ Node.js 20.9+ (sprawdź: `node --version`)
- ✅ TypeScript 5.1+
- ✅ Backup projektu (commit w git)

## Krok 1: Aktualizacja zależności

### 1.1 Aktualizacja Next.js i powiązanych pakietów

```bash
cd frontend
npm install next@latest react@latest react-dom@latest eslint-config-next@latest
```

### 1.2 Aktualizacja typów TypeScript (jeśli potrzebne)

```bash
npm install --save-dev @types/react@latest @types/react-dom@latest
```

### 1.3 Aktualizacja next-intl (sprawdź kompatybilność)

```bash
npm install next-intl@latest
```

**Uwaga**: Sprawdź dokumentację `next-intl` czy wspiera Next.js 16, szczególnie zmianę z `middleware` na `proxy`.

## Krok 2: Uruchomienie codemodów Next.js

Next.js udostępnia narzędzie do automatycznej migracji:

```bash
cd frontend
npx @next/codemod@canary upgrade latest
```

To narzędzie automatycznie:
- Zaktualizuje importy i API
- Wprowadzi niezbędne zmiany w kodzie
- Zaktualizuje konfigurację

## Krok 3: Migracja middleware → proxy

### 3.1 ⚠️ WAŻNE: Edge Runtime nie jest wspierany w proxy

**KRYTYCZNE**: W Next.js 16 `proxy.ts` **NIE wspiera edge runtime** - używa tylko `nodejs` runtime i nie można tego zmienić.

- Jeśli potrzebujesz **edge runtime**, musisz **zostać przy `middleware.ts`** (jest deprecated, ale nadal działa)
- Jeśli nie potrzebujesz edge runtime, możesz migrować do `proxy.ts`

**Dla projektu z next-intl**: Sprawdź czy `next-intl` wymaga edge runtime. Jeśli tak, możesz zostać przy `middleware.ts` na razie.

### 3.2 Zmiana nazwy pliku (jeśli migrujesz do proxy)

```bash
cd frontend/src
mv middleware.ts proxy.ts
```

### 3.3 Aktualizacja zawartości proxy.ts

Obecny plik `middleware.ts`:
```typescript
import createMiddleware from 'next-intl/middleware';
import { routing } from './i18n/routing';

export default createMiddleware(routing);

export const config = {
  matcher: ['/', '/(en|pl)/:path*']
};
```

**Po migracji do proxy.ts**:
```typescript
import createMiddleware from 'next-intl/middleware'; // lub createProxy jeśli next-intl wspiera
import { routing } from './i18n/routing';

// Zmień nazwę funkcji na 'proxy' (nawet jeśli używasz default export)
export function proxy(request: Request) {
  return createMiddleware(routing)(request);
}

// Lub jeśli next-intl ma dedykowane API:
// import createProxy from 'next-intl/proxy';
// export default createProxy(routing);

export const config = {
  matcher: ['/', '/(en|pl)/:path*']
};
```

**Uwaga**: 
- Sprawdź dokumentację `next-intl` dla Next.js 16 - może być potrzebna aktualizacja API
- Jeśli `next-intl` jeszcze nie wspiera proxy, możesz zostać przy `middleware.ts` (deprecated ale działa)

### 3.4 Aktualizacja konfiguracji next.config.ts

Jeśli używasz `skipMiddlewareUrlNormalize`, zmień na:
```typescript
const nextConfig: NextConfig = {
  skipProxyUrlNormalize: true, // było: skipMiddlewareUrlNormalize
};
```

### 3.5 Aktualizacja referencji

Sprawdź czy `middleware.ts` jest importowany gdziekolwiek w kodzie:

```bash
cd frontend
grep -r "middleware" src/
```

## Krok 4: Aktualizacja next.config.ts

### 4.1 Usunięcie flagi --turbopack z package.json

Turbopack jest teraz domyślny, więc możesz usunąć flagę:

**Przed**:
```json
{
  "scripts": {
    "dev": "next dev --turbopack"
  }
}
```

**Po**:
```json
{
  "scripts": {
    "dev": "next dev"
  }
}
```

### 4.2 Aktualizacja konfiguracji Turbopack

Jeśli używasz `experimental.turbopack`, przenieś do top-level:

**Przed**:
```typescript
const nextConfig: NextConfig = {
  experimental: {
    turbopack: {
      // options
    },
  },
};
```

**Po**:
```typescript
const nextConfig: NextConfig = {
  turbopack: {
    // options (bez experimental)
  },
};
```

### 4.3 Włączenie Cache Components (opcjonalne)

```typescript
import type { NextConfig } from "next";
import createNextIntlPlugin from 'next-intl/plugin';

const withNextIntl = createNextIntlPlugin('./src/i18n/request.ts');

const nextConfig: NextConfig = {
  // Opcjonalne: włącz Cache Components (było experimental.dynamicIO)
  // cacheComponents: true,
};

export default withNextIntl(nextConfig);
```

**Uwaga**: Jeśli używasz `experimental.dynamicIO`, zmień na `cacheComponents: true`.

### 4.4 Sprawdzenie dokumentacji next-intl

Upewnij się, że plugin `next-intl` jest kompatybilny z Next.js 16.

## Krok 5: Migracja Async Request APIs (Breaking Change)

### 5.1 ⚠️ WAŻNE: Wszystkie Request APIs są teraz asynchroniczne

W Next.js 16 wszystkie Request APIs są **tylko asynchroniczne** (synchronous access został usunięty):

- `cookies()` → `await cookies()`
- `headers()` → `await headers()`
- `draftMode()` → `await draftMode()`
- `params` w layout/page/route → `await params`
- `searchParams` w page → `await searchParams`

### 5.2 Użycie codemod do automatycznej migracji

```bash
cd frontend
npx @next/codemod@canary migrate-to-async-dynamic-apis
```

### 5.3 Ręczna migracja przykładów

**Przed (Next.js 15)**:
```typescript
export default async function Page({ params, searchParams }) {
  const { slug } = params; // synchronous
  const query = searchParams.q; // synchronous
  return <div>{slug}</div>;
}
```

**Po (Next.js 16)**:
```typescript
export default async function Page({ params, searchParams }) {
  const { slug } = await params; // async
  const query = (await searchParams).q; // async
  return <div>{slug}</div>;
}
```

### 5.4 Generowanie typów pomocniczych

Uruchom `typegen` dla type-safe migracji:

```bash
npx next typegen
```

To generuje typy pomocnicze: `PageProps`, `LayoutProps`, `RouteContext`.

**Przykład użycia**:
```typescript
import type { PageProps } from 'next';

export default async function Page(props: PageProps<'/blog/[slug]'>) {
  const { slug } = await props.params;
  const query = await props.searchParams;
  return <h1>Blog Post: {slug}</h1>;
}
```

## Krok 6: Aktualizacja TypeScript i konfiguracji

### 6.1 Sprawdzenie tsconfig.json

Upewnij się, że `tsconfig.json` jest zgodny z wymaganiami Next.js 16:

- `moduleResolution: "bundler"` ✅
- `target: "ES2018"` - może wymagać aktualizacji do ES2020+
- TypeScript 5.1+ ✅

### 6.2 Aktualizacja typów Next.js

Po aktualizacji Next.js, typy powinny być automatycznie zaktualizowane. Sprawdź czy `next-env.d.ts` jest aktualny.

### 6.3 ESLint Flat Config

Next.js 16 domyślnie używa ESLint Flat Config. Jeśli używasz `.eslintrc`, rozważ migrację:

```bash
# Sprawdź czy używasz flat config
cat frontend/eslint.config.mjs
```

Jeśli masz `.eslintrc`, zaktualizuj do flat config zgodnie z [ESLint migration guide](https://eslint.org/docs/latest/use/configure/migration-guide).

## Krok 7: Inne ważne zmiany

### 7.1 Usunięcie `next lint`

Komenda `next lint` została usunięta. Użyj ESLint bezpośrednio:

```bash
# Przed
npm run lint  # używało next lint

# Po - zaktualizuj package.json
{
  "scripts": {
    "lint": "eslint ."
  }
}
```

Codemod do migracji:
```bash
npx @next/codemod@canary next-lint-to-eslint-cli .
```

### 7.2 Parallel Routes - wymagany default.js

Wszystkie parallel route slots wymagają teraz `default.js`:

```typescript
// app/@modal/default.tsx
import { notFound } from 'next/navigation';

export default function Default() {
  notFound();
}
// lub
export default function Default() {
  return null;
}
```

### 7.3 Zmiany w next/image

- **Local images z query strings**: Wymagają konfiguracji `images.localPatterns.search`
- **minimumCacheTTL**: Domyślnie 4h zamiast 60s
- **imageSizes**: Usunięto 16px z domyślnych wartości
- **qualities**: Domyślnie tylko `[75]` zamiast wszystkich
- **Local IP restriction**: Blokowane domyślnie (wymaga `dangerouslyAllowLocalIP: true`)
- **Maximum redirects**: Domyślnie 3 zamiast unlimited

### 7.4 Scroll Behavior

Next.js 16 nie nadpisuje już `scroll-behavior: smooth` podczas nawigacji. Jeśli chcesz przywrócić poprzednie zachowanie:

```tsx
<html lang="en" data-scroll-behavior="smooth">
```

## Krok 8: Testowanie

### 8.1 Testy lokalne

```bash
cd frontend
npm run dev
```

Sprawdź:
- ✅ Aplikacja się uruchamia
- ✅ Routing działa poprawnie
- ✅ Internationalization (i18n) działa
- ✅ Wszystkie strony się ładują
- ✅ Komponenty renderują się poprawnie

### 8.2 Testy build

```bash
npm run build
```

Sprawdź:
- ✅ Build kończy się sukcesem
- ✅ Brak błędów TypeScript
- ✅ Brak ostrzeżeń

### 8.3 Testy funkcjonalne

Przetestuj kluczowe funkcjonalności:
- ✅ Nawigacja między stronami
- ✅ Przełączanie języków (en/pl)
- ✅ Formularze i walidacja
- ✅ API calls
- ✅ Komponenty UI (Radix UI, etc.)

## Krok 9: Rozwiązywanie problemów

### 9.1 Typowe problemy

1. **Błędy związane z proxy/middleware**
   - Sprawdź czy `next-intl` wspiera Next.js 16
   - Może być potrzebna aktualizacja biblioteki lub tymczasowe rozwiązanie

2. **Błędy TypeScript**
   - Uruchom `npm run type-check`
   - Zaktualizuj typy jeśli potrzebne

3. **Problemy z routingiem**
   - Sprawdź czy wszystkie ścieżki są poprawne
   - Zweryfikuj konfigurację `next-intl`

4. **Problemy z cache'owaniem**
   - Sprawdź czy komponenty cache'ują się poprawnie
   - Może być potrzebna aktualizacja logiki cache'owania

### 9.2 Sprawdzenie logów

```bash
npm run dev 2>&1 | tee upgrade-log.txt
```

## Krok 10: Aktualizacja dokumentacji

Po pomyślnej migracji zaktualizuj:
- `README.md` - wersja Next.js
- `I18N_SETUP.md` - jeśli zmieniło się API middleware/proxy
- Inne dokumenty techniczne

## Krok 11: Wdrożenie

### 11.1 Testy na środowisku staging

Przed wdrożeniem na produkcję:
- Wdróż na środowisko testowe/staging
- Przeprowadź pełne testy
- Sprawdź wydajność

### 11.2 Wdrożenie produkcyjne

Po pomyślnych testach:
- Wdróż na produkcję
- Monitoruj logi i wydajność
- Przygotuj plan rollback'u na wypadek problemów

## Checklist migracji

### Przygotowanie
- [ ] Backup projektu (commit w git)
- [ ] Sprawdzenie wersji Node.js (20.9+)
- [ ] Sprawdzenie wersji TypeScript (5.1+)

### Aktualizacja zależności
- [ ] Aktualizacja Next.js do v16
- [ ] Aktualizacja React i React DOM (19.2)
- [ ] Aktualizacja eslint-config-next
- [ ] Aktualizacja @types/react i @types/react-dom
- [ ] Aktualizacja next-intl (sprawdź kompatybilność z Next.js 16)

### Migracja kodu
- [ ] Uruchomienie codemodów Next.js (`npx @next/codemod@canary upgrade latest`)
- [ ] Migracja Async Request APIs (`npx @next/codemod@canary migrate-to-async-dynamic-apis`)
- [ ] Migracja middleware.ts → proxy.ts (lub pozostawienie middleware jeśli potrzebny edge runtime)
- [ ] Aktualizacja konfiguracji next.config.ts (turbopack, skipProxyUrlNormalize)
- [ ] Usunięcie flagi `--turbopack` z package.json
- [ ] Aktualizacja `experimental.turbopack` → `turbopack` (top-level)
- [ ] Migracja `experimental.dynamicIO` → `cacheComponents` (jeśli używane)
- [ ] Aktualizacja `next lint` → ESLint CLI (jeśli używane)
- [ ] Dodanie `default.js` dla parallel routes (jeśli używane)
- [ ] Aktualizacja użycia `next/image` (jeśli potrzebne)

### Testowanie
- [ ] Uruchomienie `npx next typegen` dla type-safe migracji
- [ ] Testy lokalne (dev mode)
- [ ] Testy build (`npm run build`)
- [ ] Testy funkcjonalne (routing, i18n, formularze, API calls)
- [ ] Rozwiązanie wszystkich błędów TypeScript
- [ ] Rozwiązanie wszystkich błędów runtime

### Wdrożenie
- [ ] Aktualizacja dokumentacji (README.md, I18N_SETUP.md)
- [ ] Testy na środowisku staging
- [ ] Wdrożenie produkcyjne
- [ ] Monitorowanie logów i wydajności

## Przydatne linki

- [Next.js 16 Upgrade Guide](https://nextjs.org/docs/app/guides/upgrading/version-16)
- [Next.js 16 Release Notes](https://nextjs.org/blog/next-16)
- [Next.js Codemods](https://nextjs.org/docs/app/getting-started/upgrading)
- [next-intl Documentation](https://next-intl-docs.vercel.app/)

## Uwagi i ostrzeżenia

1. **⚠️ next-intl i proxy**: 
   - Największym wyzwaniem może być migracja `middleware` do `proxy` w kontekście `next-intl`
   - **WAŻNE**: `proxy` NIE wspiera edge runtime - tylko nodejs runtime
   - Jeśli `next-intl` wymaga edge runtime, **zostań przy `middleware.ts`** (deprecated ale działa)
   - Sprawdź najnowszą dokumentację `next-intl` dla Next.js 16

2. **Async Request APIs**: 
   - Wszystkie Request APIs są teraz **tylko asynchroniczne**
   - Użyj codemod do automatycznej migracji
   - Uruchom `npx next typegen` dla type-safe migracji

3. **React Compiler**: 
   - Next.js 16 wspiera React Compiler (stabilny)
   - Rozważ włączenie dla lepszej wydajności: `reactCompiler: true` w next.config.ts
   - Wymaga: `npm install -D babel-plugin-react-compiler`

4. **Turbopack**: 
   - Domyślnie włączony - usuń flagę `--turbopack` z package.json
   - Konfiguracja: `experimental.turbopack` → `turbopack` (top-level)

5. **Breaking Changes**: 
   - Przeczytaj [oficjalny przewodnik Next.js 16](https://nextjs.org/docs/app/guides/upgrading/version-16) dla pełnej listy zmian
   - Najważniejsze: middleware→proxy, async APIs, next/image zmiany, usunięcie AMP, next lint

6. **next lint**: 
   - Komenda została usunięta - użyj ESLint bezpośrednio
   - Codemod: `npx @next/codemod@canary next-lint-to-eslint-cli .`

7. **Parallel Routes**: 
   - Wymagają teraz `default.js` dla każdego slotu
   - Build się nie powiedzie bez tego

8. **next/image**: 
   - Wiele zmian w domyślnych ustawieniach (cache TTL, image sizes, qualities)
   - Sprawdź czy aplikacja wymaga dostosowania konfiguracji

## Data utworzenia planu

Plan utworzony: 2025-01-27

Plan zaktualizowany na podstawie oficjalnej dokumentacji Next.js 16:
- [Next.js 16 Upgrade Guide](https://nextjs.org/docs/app/guides/upgrading/version-16)
- [Next.js 16 Release Notes](https://nextjs.org/blog/next-16)

## Status

- [ ] Nie rozpoczęto
- [ ] W trakcie
- [ ] Zakończono
- [ ] Problemy wymagają rozwiązania

