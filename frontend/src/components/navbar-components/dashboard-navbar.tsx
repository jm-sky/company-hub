'use client'

import { usePathname } from 'next/navigation'

// import SettingsMenu from "@/components/navbar-components/settings-menu"
import UserMenu from "@/components/navbar-components/user-menu"
import {
  NavigationMenu,
  NavigationMenuList,
} from "@/components/ui/navigation-menu"
import { NavbarMenuItem } from "@/components/ui/navbar-menu-item"
import type { NavigationLink } from "./nav.type"
import MobileMenuTrigger from "./mobile-menu-trigger"
import TierProjectBreadcrumb from "./tier-project-breadcrumb"
import { ThemeToggle } from '../ui/theme-toggle'

// Navigation links array to be used in both desktop and mobile menus
const navigationLinks: NavigationLink[] = [
  { href: "/dashboard", label: "Dashboard", disabled: false },
  { href: "/dashboard/search", label: "Search", disabled: false },
  { href: "/dashboard/companies", label: "Companies", disabled: true },
  { href: "/dashboard/webhooks", label: "Webhooks", disabled: true },
]

interface DashboardNavbarProps {
  onMobileMenuClick: () => void
}

export default function DashboardNavbar({ onMobileMenuClick }: DashboardNavbarProps) {
  const pathname = usePathname()

  return (
    <header className="border-b px-4 md:px-6">
      <div className="flex h-16 items-center justify-between gap-4">
        {/* Left side */}
        <div className="flex items-center gap-2">
          {/* Mobile menu trigger */}
          <MobileMenuTrigger navigationLinks={navigationLinks} onMobileMenuClick={onMobileMenuClick} />
          {/* Breadcrumb */}
          <TierProjectBreadcrumb />
        </div>
        {/* Right side */}
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            {/* Nav menu */}
            <NavigationMenu className="max-md:hidden">
              <NavigationMenuList className="gap-2">
                {navigationLinks.map((link, index) => (
                  <NavbarMenuItem
                    key={index}
                    href={link.href}
                    label={link.label}
                    disabled={link.disabled}
                    isActive={pathname === link.href}
                  />
                ))}
              </NavigationMenuList>
            </NavigationMenu>
            {/* Settings */}
            {/* <SettingsMenu /> */}
            <ThemeToggle />
          </div>
          {/* User menu */}
          <UserMenu />
        </div>
      </div>
    </header>
  )
}
