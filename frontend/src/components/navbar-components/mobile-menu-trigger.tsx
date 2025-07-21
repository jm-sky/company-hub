import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover"
import { MobileNavbarMenuItem } from "@/components/ui/navbar-menu-item"
import { Button } from "@/components/ui/button"
import { NavigationMenu, NavigationMenuList } from "@/components/ui/navigation-menu"
import type { NavigationLink } from "./nav.type"
import { usePathname } from "next/navigation"

export default function MobileMenuTrigger({
  navigationLinks,
  onMobileMenuClick,
}: {
  navigationLinks: NavigationLink[]
  onMobileMenuClick: () => void
}) {
  const pathname = usePathname()

  return (
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
  )
}
