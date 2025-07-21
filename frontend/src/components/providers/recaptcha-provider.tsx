'use client';

import { GoogleReCaptchaProvider } from 'react-google-recaptcha-v3';
import { ReactNode } from 'react';

interface ReCaptchaProviderProps {
  children: ReactNode;
}

export function ReCaptchaProvider({ children }: ReCaptchaProviderProps) {
  const siteKey = process.env.NEXT_PUBLIC_RECAPTCHA_SITE_KEY;
  const enabled = process.env.NEXT_PUBLIC_RECAPTCHA_ENABLED === 'true';

  if (!enabled || !siteKey) {
    // reCAPTCHA disabled or not configured
    return <>{children}</>;
  }

  return (
    <GoogleReCaptchaProvider
      reCaptchaKey={siteKey}
      scriptProps={{
        async: false,
        defer: false,
        appendTo: "head",
        nonce: undefined,
      }}
      container={{
        element: 'recaptcha-container',
        parameters: {
          badge: 'bottomright',
          theme: 'light',
        },
      }}
    >
      {children}
      <div id="recaptcha-container" />
    </GoogleReCaptchaProvider>
  );
}