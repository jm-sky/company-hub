import { useTranslations } from 'next-intl';

export function useAppTranslations() {
  const common = useTranslations('common');
  const navigation = useTranslations('navigation');
  const auth = useTranslations('auth');
  const company = useTranslations('company');
  const dashboard = useTranslations('dashboard');
  const errors = useTranslations('errors');

  return {
    common,
    navigation,
    auth,
    company,
    dashboard,
    errors
  };
}
