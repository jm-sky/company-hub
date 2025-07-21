'use client'

import { MailIcon, MapPinIcon } from "lucide-react"
import LinkUnderline from "../ui/link-underline"
import { LogoText } from "../ui/logo-text"

export default function AddressFooter() {
  return (
    <section className="py-20 bg-black text-white">
      <div className="container mx-auto px-4 md:px-6 grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="flex flex-col gap-2">
          <LogoText size="xl" foreground="text-white" />
          <p className="text-sm text-muted-foreground">
            by <LinkUnderline href="https://dev-made.it" className="font-bold hover:text-white">DEV Made IT</LinkUnderline>
          </p>
        </div>
        <div className="flex flex-col gap-4">
          <div className="flex items-center gap-4">
            <MapPinIcon className="size-4" />
            <LinkUnderline href="https://maps.app.goo.gl/PL25JfivD77t9LuSA">
              Warszawa, Poland
            </LinkUnderline>
          </div>
          <div className="flex items-center gap-4">
            <MailIcon className="size-4" />
            <LinkUnderline href="mailto:contact@dev-made.it">
              contact@dev-made.it
            </LinkUnderline>
          </div>
        </div>
      </div>
    </section>
  )
}
