import {
  Breadcrumb,
  BreadcrumbList,
  BreadcrumbItem,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb"
import { Select, SelectContent, SelectItem, SelectValue } from "@/components/ui/select"
import { Select as SelectPrimitive } from "radix-ui"
import { useUser } from "@/lib/hooks/useAuth"
import { Button } from "@/components/ui/button"
import { ChevronsUpDown, Hourglass } from "lucide-react"

export default function TierProjectBreadcrumb() {
  const { data: user } = useUser()

  return (
    <Breadcrumb>
    <BreadcrumbList>
      <BreadcrumbItem>
        <Select defaultValue={user?.subscription_tier ?? "free"}>
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
  )
}
