# 🏗️ Architektura systemu — CompanyHub

Centralny serwis API do pobierania, agregowania i udostępniania danych o firmach z publicznych źródeł w Polsce. Wspiera REST API, webhooki, cache i rozbudowany panel użytkownika.

---

## Tech-stack
- Pyton
- FastApi

---

## 1. 🕓 Historia danych

**Czy zapisywać historię zmian danych firm?**  
✅ Tak, zmiany będą zapisywane:
- różnice (diff)
- czas i źródło aktualizacji
- identyfikator firmy (np. NIP)

**Zastosowanie:** webhooki, audyt, analityka.

---

## 2. 📡 Źródła danych zewnętrznych

**Jakie źródła danych planujemy?**
- [x] REGON (GUS API)
- [x] MF (Biała Lista)
- [x] VIES
- [x] IBAN API

**Tryby pobierania danych:**
- [x] Na żądanie (np. `GET /companies/{nip}`)
- [x] Asynchroniczne CRON / kolejka
- [x] Fallback i retry przy błędach

**Czy możliwa konfiguracja częstotliwości i źródeł?**  
✅ Tak, przez panel lub konfigurację klienta.

---

## 3. 🌐 API

**Styl API:**  
✅ REST (wersjonowane, np. `/api/v1/companies/{nip}`)

**Autoryzacja:**  
✅ Wymagana (token API)

**Format odpowiedzi:**  
✅ JSON

---

## 4. 🗃️ Cache i aktualizacja danych

**Czy dane będą cache’owane lokalnie?**  
✅ Tak, z lokalnym TTL.

**Domyślne TTL:**  
🕒 1 dzień (źródłospecyficzne)

**Czy możliwe wymuszenie odświeżenia?**  
✅ Tak: `?refresh=true`

**Czy fallback działa z cache?**  
✅ Tak, np. w razie błędu z zewnętrznym źródłem.

---

## 5. 🔐 Tokeny i limity

**Typ tokenów:**  
🔸 Do ustalenia (JWT vs prosty `X-Api-Key`)

**Rate limiting:**  
🔸 Do ustalenia (np. Redis + token bucket)
- plan freemium: 200 zapytań miesięcznie
- pakiety płatne: większe limity

---

## 6. 📬 Webhooki

**Jakie typy webhooków planujemy?**
- `dataChanged`
- `dataChanged.by.[provider]` (np. `dataChanged.by.MF`)
- `dataChanged.in.[section]` (np. `in.bankAccounts`, `in.addresses`)

**Czy retry/backoff?**  
✅ Tak, kolejka + retry + logi

**Czy historia wywołań?**  
✅ Tak, z kodami odpowiedzi, czasem, payloadem

**Czy wiele endpointów per klient?**  
✅ Planowane

---

## 7. 🗂️ Baza danych

**Jakie modele danych?**  
🔸 Do ustalenia:
- centralna tabela firm + źródła?
- osobne tabele na dane z GUS, MF itd.?
- wersjonowanie lub diff? (historia)

**Czy dane będą oznaczane jako nieaktualne?**  
✅ Tak (np. `outdated = true` lub daty ważności)

---

## 8. 📈 Monitoring i obserwowalność

🔸 Do ustalenia:

**Co mierzymy?**
- Czas odpowiedzi źródeł
- Błędy i timeouty
- Statystyki użycia API per klient
- Dostarczalność webhooków

**Narzędzia?**  
🔸 Do ustalenia (Sentry, Prometheus, self-hosted?)

---

## 9. ⚙️ Kolejki i harmonogramy

**Czy używamy kolejek?**  
✅ Tak (np. Redis Queue / Celery)

**Zadania CRON:**  
- Cykliczne odświeżanie firm (np. co 24h)
- Retry nieudanych webhooków
- Cleanup nieaktualnych danych

---

## 10. 🔒 Bezpieczeństwo

🔸 Do ustalenia:

**Zagadnienia:**
- Ograniczenia IP (per token?)
- Podpisy webhooków (HMAC?)
- Wymuszone HTTPS
- Rate limit także per IP?

---

## 11. 🖥️ Panel użytkownika

**Typ UI:**  
✅ SSR + HTMX (lekki, szybki)

**Funkcje panelu:**
- Rejestracja / logowanie
- Statystyki API
- Zarządzanie tokenami
- Webhooki: dodawanie, testowanie, historia
- Billing + faktury (Stripe)
- Podgląd logów zapytań

---

## 12. 📦 Deployment i CI/CD

🔸 Do ustalenia:

**Wstępnie:**
- VPS (np. Hetzner, OVH)
- Docker
- CI/CD: GitHub Actions
- Monitorowanie: uptime, kolejki, webhooki

---

## ✅ Podsumowanie: rzeczy do ustalenia

| Obszar | Status |
|-------|--------|
| Tokeny API (typ, TTL) | 🔸 Do ustalenia |
| Rate limiting (mechanizm, Redis?) | 🔸 Do ustalenia |
| Struktura bazy danych | 🔸 Do ustalenia |
| Monitoring i alerty | 🔸 Do ustalenia |
| Szczegóły bezpieczeństwa (HMAC, CORS) | 🔸 Do ustalenia |
| Deployment: Docker, VPS, CI/CD | 🔸 Do ustalenia |

