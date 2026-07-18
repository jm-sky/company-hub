'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import Link from 'next/link';
import { useRouter, useSearchParams } from 'next/navigation';
import { Eye, EyeOff, Lock, AlertCircle } from 'lucide-react';
import { useTranslations, useLocale } from 'next-intl';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useAuth } from '@/lib/hooks/useAuth';
import { resetPasswordSchema, ResetPasswordFormData } from '@/lib/schemas/auth';

export function ResetPasswordContent() {
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const router = useRouter();
  const locale = useLocale();
  const t = useTranslations('auth');
  const searchParams = useSearchParams();
  const token = searchParams.get('token');
  const { resetPassword } = useAuth();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ResetPasswordFormData>({
    resolver: zodResolver(resetPasswordSchema),
  });

  const onSubmit = async (data: ResetPasswordFormData) => {
    if (!token) return;

    try {
      await resetPassword.mutateAsync({
        token,
        password: data.password,
      });
      router.push(`/${locale}/login?message=password-reset-success`);
    } catch (error) {
      console.error('Reset password failed:', error);
    }
  };

  if (!token) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background py-12 px-4 sm:px-6 lg:px-8">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl font-bold">{t('invalidResetLink')}</CardTitle>
            <CardDescription>
              {t('resetLinkInvalidOrExpired')}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-center space-y-4">
              <p className="text-sm text-muted-foreground">
                {t('requestNewResetLink')}
              </p>
              <Button asChild className="w-full">
                <Link href={`/${locale}/forgot-password`}>
                  {t('requestNewLink')}
                </Link>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-background py-12 px-4 sm:px-6 lg:px-8">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl font-bold">{t('setNewPassword')}</CardTitle>
          <CardDescription>
            {t('enterNewPasswordBelow')}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="password">{t('newPassword')}</Label>
              <div className="relative">
                <Input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  placeholder={t('enterNewPassword')}
                  {...register('password')}
                  className={errors.password ? 'border-destructive pr-10' : 'pr-10'}
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

            <div className="space-y-2">
              <Label htmlFor="confirmPassword">{t('confirmNewPassword')}</Label>
              <div className="relative">
                <Input
                  id="confirmPassword"
                  type={showConfirmPassword ? 'text' : 'password'}
                  placeholder={t('confirmNewPasswordPlaceholder')}
                  {...register('confirmPassword')}
                  className={errors.confirmPassword ? 'border-destructive pr-10' : 'pr-10'}
                />
                <button
                  type="button"
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                >
                  {showConfirmPassword ? (
                    <EyeOff className="size-4 text-muted-foreground" />
                  ) : (
                    <Eye className="size-4 text-muted-foreground" />
                  )}
                </button>
              </div>
              {errors.confirmPassword && (
                <p className="text-sm text-destructive">{errors.confirmPassword.message}</p>
              )}
            </div>

            <Button
              type="submit"
              className="w-full"
              disabled={resetPassword.isPending}
            >
              {resetPassword.isPending ? (
                <>
                  <div className="size-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                  {t('resetting')}
                </>
              ) : (
                <>
                  <Lock className="size-4 mr-2" />
                  {t('resetPasswordButton')}
                </>
              )}
            </Button>

            {resetPassword.error && (
              <Alert variant="destructive">
                <AlertCircle className="size-4" />
                <AlertDescription>
                  {resetPassword.error instanceof Error ? resetPassword.error.message : t('failedToResetPassword')}
                </AlertDescription>
              </Alert>
            )}
          </form>

          <div className="mt-6 text-center">
            <Link href={`/${locale}/login`} className="text-sm text-blue-600 hover:text-blue-500">
              {t('backToSignIn')}
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
