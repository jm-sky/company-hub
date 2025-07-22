import { redirect } from 'next/navigation';

export default function CallbackPage() {
  // This should never be reached directly
  redirect('/login');
}