'use client'

import { ChevronsUpDown, Hourglass } from "lucide-react"
import { Select as SelectPrimitive } from "radix-ui"
import { useUser } from '@/lib/hooks/useAuth'
import { usePathname } from 'next/navigation'

import SettingsMenu from "@/components/navbar-components/settings-menu"
import UserMenu from "@/components/navbar-components/user-menu"
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbList,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb"
import { Button } from "@/components/ui/button"
import {
  NavigationMenu,
  NavigationMenuList,
} from "@/components/ui/navigation-menu"
import { NavbarMenuItem, MobileNavbarMenuItem } from "@/components/ui/navbar-menu-item"
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectValue,
} from "@/components/ui/select"

// Navigation links array to be used in both desktop and mobile menus
const navigationLinks = [
  { href: "/dashboard", label: "Dashboard", disabled: false },
  { href: "/dashboard/search", label: "Search", disabled: true },
  { href: "/dashboard/companies", label: "Companies", disabled: true },
  { href: "/dashboard/webhooks", label: "Webhooks", disabled: true },
]

interface DashboardNavbarProps {
  onMobileMenuClick: () => void
}

export default function DashboardNavbar({ onMobileMenuClick }: DashboardNavbarProps) {
  const { data: user } = useUser()
  const pathname = usePathname()

  return (
    <header className="border-b px-4 md:px-6">
      <div className="flex h-16 items-center justify-between gap-4">
        {/* Left side */}
        <div className="flex items-center gap-2">
          {/* Mobile menu trigger */}
          <Popover>
            <PopoverTrigger asChild>
              <Button
                className="group size-8 md:hidden"
                variant="ghost"
                size="icon"
                onClick={onMobileMenuClick}
              >
                <svg
                  className="pointer-events-none"
                  width={16}
                  height={16}
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    d="M4 12L20 12"
                    className="origin-center -translate-y-[7px] transition-all duration-300 ease-[cubic-bezier(.5,.85,.25,1.1)] group-aria-expanded:translate-x-0 group-aria-expanded:translate-y-0 group-aria-expanded:rotate-[315deg]"
                  />
                  <path
                    d="M4 12H20"
                    className="origin-center transition-all duration-300 ease-[cubic-bezier(.5,.85,.25,1.8)] group-aria-expanded:rotate-45"
                  />
                  <path
                    d="M4 12H20"
                    className="origin-center translate-y-[7px] transition-all duration-300 ease-[cubic-bezier(.5,.85,.25,1.1)] group-aria-expanded:translate-y-0 group-aria-expanded:rotate-[135deg]"
                  />
                </svg>
              </Button>
            </PopoverTrigger>
            <PopoverContent align="start" className="w-36 p-1 md:hidden">
              <NavigationMenu className="max-w-none *:w-full">
                <NavigationMenuList className="flex-col items-start gap-0 md:gap-2">
                  {navigationLinks.map((link, index) => (
                    <MobileNavbarMenuItem
                      key={index}
                      href={link.href}
                      label={link.label}
                      disabled={link.disabled}
                      isActive={pathname === link.href}
                    />
                  ))}
                </NavigationMenuList>
              </NavigationMenu>
            </PopoverContent>
          </Popover>
          {/* Breadcrumb */}
          <Breadcrumb>
            <BreadcrumbList>
              <BreadcrumbItem>
                <Select defaultValue={user?.subscription_tier || "free"}>
                  <SelectPrimitive.SelectTrigger
                    aria-label="Select subscription tier"
                    asChild
                  >
                    <Button
                      variant="ghost"
                      className="focus-visible:bg-accent text-foreground h-8 p-1.5 focus-visible:ring-0"
                    >
                      <SelectValue placeholder="Select tier" />
                      <ChevronsUpDown
                        size={14}
                        className="text-muted-foreground/80"
                      />
                    </Button>
                  </SelectPrimitive.SelectTrigger>
                  <SelectContent className="[&_*[role=option]]:ps-2 [&_*[role=option]]:pe-8 [&_*[role=option]>span]:start-auto [&_*[role=option]>span]:end-2">
                    <SelectItem value="free">Free</SelectItem>
                    <SelectItem value="premium" disabled>
                      <div className="flex items-center gap-2">
                        Premium
                        <Hourglass className="size-3 text-muted-foreground" />
                      </div>
                    </SelectItem>
                    <SelectItem value="enterprise" disabled>
                      <div className="flex items-center gap-2">
                        Enterprise
                        <Hourglass className="size-3 text-muted-foreground" />
                      </div>
                    </SelectItem>
                  </SelectContent>
                </Select>
              </BreadcrumbItem>
              <BreadcrumbSeparator> / </BreadcrumbSeparator>
              <BreadcrumbItem>
                <Select defaultValue="main">
                  <SelectPrimitive.SelectTrigger
                    aria-label="Select project"
                    asChild
                  >
                    <Button
                      variant="ghost"
                      className="focus-visible:bg-accent text-foreground h-8 p-1.5 focus-visible:ring-0"
                    >
                      <SelectValue placeholder="Select project" />
                      <ChevronsUpDown
                        size={14}
                        className="text-muted-foreground/80"
                      />
                    </Button>
                  </SelectPrimitive.SelectTrigger>
                  <SelectContent className="[&_*[role=option]]:ps-2 [&_*[role=option]]:pe-8 [&_*[role=option]>span]:start-auto [&_*[role=option]>span]:end-2">
                    <SelectItem value="main">Main Project</SelectItem>
                    <SelectItem value="api" disabled>
                      <div className="flex items-center gap-2">
                        API Testing
                        <Hourglass className="size-3 text-muted-foreground" />
                      </div>
                    </SelectItem>
                    <SelectItem value="webhook" disabled>
                      <div className="flex items-center gap-2">
                        Webhook Testing
                        <Hourglass className="size-3 text-muted-foreground" />
                      </div>
                    </SelectItem>
                  </SelectContent>
                </Select>
              </BreadcrumbItem>
            </BreadcrumbList>
          </Breadcrumb>
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
            <SettingsMenu />
          </div>
          {/* User menu */}
          <UserMenu />
        </div>
      </div>
    </header>
  )
}