'use client';

import { useEffect, useRef } from 'react';
import { useSearchParams, useParams, useRouter } from 'next/navigation';
import { useOAuthCallback } from '@/lib/hooks/useOAuth';
import { useRecaptcha } from '@/lib/hooks/useRecaptcha';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Loader2 } from 'lucide-react';

export default function OAuthCallbackPage() {
  const searchParams = useSearchParams();
  const params = useParams();
  const router = useRouter();
  const oauthCallback = useOAuthCallback();
  const { getToken: getRecaptchaToken, isEnabled: recaptchaEnabled, isReady: recaptchaReady } = useRecaptcha();
  const processingRef = useRef(false);

  const provider = params?.provider as string;
  const code = searchParams?.get('code');
  const state = searchParams?.get('state');
  const error = searchParams?.get('error');

  useEffect(() => {
    const processCallback = async () => {
      // Prevent duplicate processing using ref
      if (processingRef.current) {
        return;
      }
      processingRef.current = true;

      try {
        // Handle OAuth error (user denied)
        if (error) {
          router.push('/login?error=oauth-denied');
          return;
        }

        // Validate required parameters
        if (!provider || !code || !state) {
          router.push('/login?error=oauth-invalid');
          return;
        }

        // Validate provider
        if (!['github', 'google'].includes(provider)) {
          router.push('/login?error=oauth-invalid');
          return;
        }

        // Wait for reCAPTCHA to be ready if enabled
        if (recaptchaEnabled && !recaptchaReady) {
          processingRef.current = false; // Reset flag to retry when ready
          return;
        }

        // Get reCAPTCHA token if enabled and process OAuth callback
        const recaptchaToken = recaptchaEnabled ? await getRecaptchaToken('oauth_callback') : null;
        oauthCallback.mutate({ provider, code, state, recaptchaToken });
      } catch {
        processingRef.current = false; // Reset flag on error
        router.push('/login?error=oauth-failed');
      }
    };
    
    processCallback();
  }, [provider, code, state, error, router, oauthCallback, recaptchaEnabled, recaptchaReady, getRecaptchaToken]);

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Card className="w-96">
          <CardHeader>
            <CardTitle className="text-destructive">Authentication Error</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              OAuth authentication was cancelled or failed. Redirecting to login...
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (oauthCallback.error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Card className="w-96">
          <CardHeader>
            <CardTitle className="text-destructive">Authentication Failed</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground mb-4">
              {oauthCallback.error.message || 'An error occurred during authentication.'}
            </p>
            <p className="text-xs text-muted-foreground">
              Redirecting to login page...
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center">
      <Card className="w-96">
        <CardHeader>
          <CardTitle className="flex items-center">
            <Loader2 className="mr-2 size-4 animate-spin" />
            Signing you in...
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            Processing your {provider} authentication. Please wait...
          </p>
        </CardContent>
      </Card>
    </div>
  );
}