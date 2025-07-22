import { useGoogleReCaptcha } from 'react-google-recaptcha-v3';
import { useCallback } from 'react';

export const useRecaptcha = () => {
  const { executeRecaptcha } = useGoogleReCaptcha();

  const getToken = useCallback(async (action: string = 'submit'): Promise<string | null> => {
    const enabled = process.env.NEXT_PUBLIC_RECAPTCHA_ENABLED === 'true';
    
    if (!enabled || !executeRecaptcha) {
      return null;
    }

    try {
      const token = await executeRecaptcha(action);
      return token;
    } catch {
      return null;
    }
  }, [executeRecaptcha]);

  const isEnabled = Boolean(
    process.env.NEXT_PUBLIC_RECAPTCHA_ENABLED === 'true' && 
    process.env.NEXT_PUBLIC_RECAPTCHA_SITE_KEY
  );

  const isReady = Boolean(executeRecaptcha);

  return { getToken, isEnabled, isReady };
};