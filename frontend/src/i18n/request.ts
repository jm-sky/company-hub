import { notFound } from 'next/navigation';
import { getRequestConfig } from 'next-intl/server';

const locales = ['en', 'pl'];

export default getRequestConfig(async ({ locale }) => {
  if (!locales.includes(locale as 'en' | 'pl')) notFound();

  return {
    locale: locale as 'en' | 'pl',
    messages: (await import(`../../messages/${locale}.json`)).default,
  };
});
