'use client'

import { useState } from 'react'
import { usePathname } from 'next/navigation'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { useAuth, useUser } from '@/lib/hooks/useAuth'
import DashboardNavbar from '@/components/navbar-components/dashboard-navbar'
import { SidebarMenuItem } from '@/components/ui/sidebar-menu-item'
import {
  Building2,
  Search,
  Settings,
  CreditCard,
  Webhook,
  User,
  LogOut,
  X,
  Home
} from 'lucide-react'

interface DashboardLayoutProps {
  children: React.ReactNode
}

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: Home, disabled: false },
  { name: 'Company Search', href: '/dashboard/search', icon: Search, disabled: false },
  { name: 'Companies', href: '/dashboard/companies', icon: Building2, disabled: true },
  { name: 'Subscription', href: '/dashboard/subscription', icon: CreditCard, disabled: true },
  { name: 'Webhooks', href: '/dashboard/webhooks', icon: Webhook, disabled: true },
  { name: 'Settings', href: '/dashboard/settings', icon: Settings, disabled: true },
]

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const { data: user } = useUser()
  const { logout } = useAuth()
  const router = useRouter()
  const pathname = usePathname()

  const handleLogout = async () => {
    await logout()
    router.push('/login')
  }

  return (
    <div className="min-h-screen bg-muted/50">
      {/* Mobile sidebar */}
      <div className={cn(
        "fixed inset-0 z-50 lg:hidden",
        sidebarOpen ? "block" : "hidden"
      )}>
        <div className="fixed inset-0 bg-background/80 backdrop-blur-sm" onClick={() => setSidebarOpen(false)} />
        <div className="relative flex w-64 flex-col bg-background shadow-xl border-r">
          <div className="flex items-center justify-between px-4 py-6">
            <h1 className="text-xl font-bold text-foreground">CompanyHub</h1>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setSidebarOpen(false)}
            >
              <X className="size-4" />
            </Button>
          </div>
          <nav className="mt-5 flex-1 space-y-1 px-2">
            {navigation.map((item) => (
              <SidebarMenuItem
                key={item.name}
                name={item.name}
                href={item.href}
                icon={item.icon}
                disabled={item.disabled}
                isActive={pathname === item.href}
              />
            ))}
          </nav>
          <div className="border-t border-border p-4">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <User className="size-8 text-muted-foreground" />
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-foreground">{user?.name || user?.email}</p>
                <p className="text-xs text-muted-foreground">{user?.subscription_tier}</p>
              </div>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleLogout}
              className="mt-3 w-full justify-start"
            >
              <LogOut className="mr-2 size-4" />
              Sign out
            </Button>
          </div>
        </div>
      </div>

      {/* Desktop sidebar */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:flex lg:w-64 lg:flex-col">
        <div className="flex min-h-0 flex-1 flex-col bg-background border-r border-border">
          <div className="flex flex-1 flex-col overflow-y-auto pt-5 pb-4">
            <div className="flex items-center flex-shrink-0 px-4">
              <h1 className="text-xl font-bold text-foreground">CompanyHub</h1>
            </div>
            <nav className="mt-5 flex-1 space-y-1 px-2">
              {navigation.map((item) => (
                <SidebarMenuItem
                  key={item.name}
                  name={item.name}
                  href={item.href}
                  icon={item.icon}
                  disabled={item.disabled}
                  isActive={pathname === item.href}
                />
              ))}
            </nav>
          </div>
          <div className="border-t border-border p-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={handleLogout}
              className="w-full justify-start"
            >
              <LogOut className="mr-2 size-4" />
              Sign out
            </Button>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="lg:pl-64">
        {/* Top navbar */}
        <div className="sticky top-0 z-10 bg-white">
          <DashboardNavbar onMobileMenuClick={() => setSidebarOpen(true)} />
        </div>

        {/* Page content */}
        <main className="py-6">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}