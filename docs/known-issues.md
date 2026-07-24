# Known issues

## postcss: Arbitrary file read / information disclosure via sourceMappingURL (2026-07-24)

- **Gdzie:** `frontend/pnpm-lock.yaml` — `postcss@8.4.31`, wciągnięty jako wewnętrzna (dokładnie przypięta) zależność `next@16.2.10`. Next.js sam wskazuje `postcss: 8.4.31` w swoim `package.json`, więc zwykły `pnpm update` tego nie ruszy.
- **Podatność:** parsowanie komentarza `sourceMappingURL` w CSS pozwala atakującemu wskazać dowolną ścieżkę na dysku, którą narzędzie budujące odczyta i ujawni jako "source" w mapie źródeł → dowolny odczyt pliku + information disclosure. Podatne <8.5.12, poprawka od 8.5.12+.
- **Status:** Dependabot to zgłosił, ale nie mógł auto-zbindować (przypięta wersja w `next`). **Nie naprawione jeszcze** — zdecydowano celowo odłożyć w ramach przeglądu z 2026-07-24, żeby nie robić tego bez świadomej decyzji na tym repo (poza rodziną gear-stack, gdzie ten sam problem już naprawiono przez `pnpm.overrides`).
- **Rekomendowany fix, gdy będzie czas:** dodać do `frontend/package.json`:
  ```json
  "pnpm": {
    "overrides": {
      "postcss@<8.5.12": "8.5.19"
    }
  }
  ```
  (8.5.19 już rozwiązuje się poprawnie gdzie indziej w tym samym lockfile — patrz `postcss@8.5.19` w `pnpm-lock.yaml`), potem `pnpm install` i weryfikacja builda Next.js (`pnpm build`).
- **Ryzyko regresji:** niskie — postcss 8.x zachowuje kompatybilność wsteczną API między patch/minor; Next.js używa go tylko do własnego pipeline'u CSS.
