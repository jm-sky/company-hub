'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import Link from 'next/link';
import { ArrowLeft, Mail, AlertCircle } from 'lucide-react';
import { useTranslations, useLocale } from 'next-intl';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useAuth } from '@/lib/hooks/useAuth';
import { forgotPasswordSchema, ForgotPasswordFormData } from '@/lib/schemas/auth';

export default function ForgotPasswordPage() {
  const [emailSent, setEmailSent] = useState(false);
  const locale = useLocale();
  const t = useTranslations('auth');
  const { forgotPassword } = useAuth();

  const {
    register,
    handleSubmit,
    formState: { errors },
    getValues,
  } = useForm<ForgotPasswordFormData>({
    resolver: zodResolver(forgotPasswordSchema),
  });

  const onSubmit = async (data: ForgotPasswordFormData) => {
    try {
      await forgotPassword.mutateAsync(data.email);
      setEmailSent(true);
    } catch (error) {
      console.error('Forgot password failed:', error);
    }
  };

  if (emailSent) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background py-12 px-4 sm:px-6 lg:px-8">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <div className="mx-auto w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mb-4">
              <Mail className="h-6 w-6 text-green-600" />
            </div>
            <CardTitle className="text-2xl font-bold">{t('checkYourEmail')}</CardTitle>
            <CardDescription>
              {t('weveSentResetLink')}{' '}
              <span className="font-medium">{getValues('email')}</span>
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-center space-y-4">
              <p className="text-sm text-muted-foreground">
                {t('didntReceiveEmail')}
              </p>
              <Button
                variant="outline"
                onClick={() => setEmailSent(false)}
                className="w-full"
              >
                {t('tryAgain')}
              </Button>
              <div className="text-sm">
                <Link href={`/${locale}/login`} className="text-brand hover:text-brand/80">
                  {t('backToSignIn')}
                </Link>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl font-bold">{t('resetYourPassword')}</CardTitle>
          <CardDescription>
            {t('enterEmailForResetLink')}
          </CardDescription>
        </CardHeader>
        <CardContent>
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

            <Button
              type="submit"
              className="w-full"
              disabled={forgotPassword.isPending}
            >
              {forgotPassword.isPending ? (
                <>
                  <div className="size-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                  {t('sending')}
                </>
              ) : (
                <>
                  <Mail className="size-4 mr-2" />
                  {t('sendResetLink')}
                </>
              )}
            </Button>

            {forgotPassword.error && (
              <Alert variant="destructive">
                <AlertCircle className="size-4" />
                <AlertDescription>
                  {forgotPassword.error instanceof Error ? forgotPassword.error.message : t('failedToSendResetLink')}
                </AlertDescription>
              </Alert>
            )}
          </form>

          <div className="mt-6 text-center">
            <Link href={`/${locale}/login`} className="text-sm text-brand hover:text-brand/80 flex items-center justify-center">
              <ArrowLeft className="size-4 mr-1" />
              {t('backToSignIn')}
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
