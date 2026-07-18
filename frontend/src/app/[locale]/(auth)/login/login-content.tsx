'use client';

import { useState, useEffect, useMemo } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import Link from 'next/link';
import { useRouter, useSearchParams } from 'next/navigation';
import { Eye, EyeOff, LogIn, AlertCircle } from 'lucide-react';
import { useTranslations, useLocale } from 'next-intl';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useAuth, useUser } from '@/lib/hooks/useAuth';
import { loginSchema, LoginFormData } from '@/lib/schemas/auth';
import { LogoText } from '@/components/ui/logo-text';
import { OAuthButtons } from '@/components/auth/OAuthButtons';
import { useRecaptcha } from '@/lib/hooks/useRecaptcha';

export function LoginContent() {
  const [showPassword, setShowPassword] = useState(false);
  const [isRedirecting, setIsRedirecting] = useState(false);
  const router = useRouter();
  const locale = useLocale();
  const t = useTranslations('auth');
  const common = useTranslations('common');
  const searchParams = useSearchParams();
  const { login } = useAuth();
  const { data: user, isLoading } = useUser();
  const { getToken: getRecaptchaToken, isEnabled: recaptchaEnabled } = useRecaptcha();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    defaultValues: {
      email: process.env.NEXT_PUBLIC_DEFAULT_LOGIN_EMAIL,
      password: process.env.NEXT_PUBLIC_DEFAULT_LOGIN_PASSWORD,
    },
    resolver: zodResolver(loginSchema),
  });

  useEffect(() => {
    // Redirect authenticated users to dashboard
    if (!isLoading && user) {
      router.push(`/${locale}/dashboard`);
    }
  }, [user, isLoading, router, locale]);

  const sessionExpiredMessage = useMemo(() => {
    const reason = searchParams.get('reason');
    const error = searchParams.get('error');

    if (reason === 'session-expired') {
      return t('sessionExpired');
    }
    if (error) {
      switch (error) {
        case 'oauth-denied':
          return t('oauthCancelled');
        case 'oauth-failed':
          return t('oauthFailed');
        case 'oauth-invalid':
          return t('oauthInvalid');
        default:
          return t('oauthGenericError');
      }
    }
    return null;
  }, [searchParams, t]);

  const onSubmit = async (data: LoginFormData) => {
    try {
      // Get reCAPTCHA token if enabled
      let recaptchaToken = null;
      if (recaptchaEnabled) {
        recaptchaToken = await getRecaptchaToken('login');
        if (!recaptchaToken) {
          throw new Error(t('recaptchaVerificationFailed'));
        }
      }

      await login.mutateAsync({ ...data, recaptchaToken });
      setIsRedirecting(true);
      router.push(`/${locale}/dashboard`);
    } catch (error) {
      console.error('Login failed:', error);
      setIsRedirecting(false);
    }
  };

  // Show loading while checking authentication status
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
        <div className="w-full max-w-md space-y-4">
          <div className="h-8 bg-muted rounded animate-pulse" />
          <div className="h-32 bg-muted rounded animate-pulse" />
          <div className="h-10 bg-muted rounded animate-pulse" />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl font-bold">{t('signInTo')} <LogoText size="lg" /></CardTitle>
          <CardDescription>
            {t('enterEmailAndPasswordToAccess')}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {sessionExpiredMessage && (
            <Alert variant="destructive" className="mb-4">
              <AlertCircle className="size-4" />
              <AlertDescription>{sessionExpiredMessage}</AlertDescription>
            </Alert>
          )}
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email">{t('email')}</Label>
              <Input
                id="email"
                type="email"
                placeholder={t('enterYourEmail')}
                {...register('email')}
                aria-invalid={errors.email ? 'true' : 'false'}
              />
              {errors.email && (
                <p className="text-sm text-destructive">{errors.email.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="password">{t('password')}</Label>
              <div className="relative">
                <Input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  placeholder={t('enterYourPassword')}
                  {...register('password')}
                  aria-invalid={errors.password ? 'true' : 'false'}
                />
                <button
                  type="button"
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? (
                    <EyeOff className="size-4 text-muted-foreground" />
                  ) : (
                    <Eye className="size-4 text-muted-foreground" />
                  )}
                </button>
              </div>
              {errors.password && (
                <p className="text-sm text-destructive">{errors.password.message}</p>
              )}
            </div>

            <div className="flex items-center justify-between">
              <div className="text-sm">
                <Link href={`/${locale}/forgot-password`} className="text-brand hover:text-brand/80">
                  {t('forgotYourPassword')}
                </Link>
              </div>
            </div>

            <Button
              type="submit"
              className="w-full"
              disabled={login.isPending || isRedirecting}
            >
              {login.isPending ? (
                <>
                  <div className="size-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                  {t('signingIn')}
                </>
              ) : isRedirecting ? (
                <>
                  <div className="size-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                  {t('redirectingToDashboard')}
                </>
              ) : (
                <>
                  <LogIn className="size-4 mr-2" />
                  {t('signIn')}
                </>
              )}
            </Button>

            {login.error && (
              <Alert variant="destructive">
                <AlertCircle className="size-4" />
                <AlertDescription>
                  {login.error instanceof Error ? login.error.message : t('loginFailed')}
                </AlertDescription>
              </Alert>
            )}
          </form>

          <div className="mt-6">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <span className="w-full border-t" />
              </div>
              <div className="relative flex justify-center text-xs uppercase">
                <span className="bg-background px-2 text-muted-foreground">
                  {common('orContinueWith')}
                </span>
              </div>
            </div>

            <OAuthButtons className="mt-4" />
          </div>

          <div className="mt-6 text-center text-sm">
            <span className="text-muted-foreground">{t('dontHaveAccount')} </span>
            <Link href={`/${locale}/register`} className="text-brand hover:text-brand/80 font-medium">
              {t('signUp')}
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
