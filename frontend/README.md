# TaskFlow - frontend (React + Bootstrap)

Aplikacja napisana w React 19 + Bootstrap 5, budowana przez Vite.
Wynik builda trafia do `../static/spa` i jest serwowany przez Django
(widok `taskFlow.views.spa` czyta manifest Vite).

## Tryb developerski

```bash
# terminal 1 - backend
python manage.py runserver

# terminal 2 - frontend (HMR)
cd frontend
npm install
npm run dev
```

Aplikacja deweloperska: http://localhost:5173 (proxy `/api`, `/media`
i `/static` na Django pod adresem `127.0.0.1:8000`).

## Build produkcyjny

```bash
cd frontend
npm run build
```

Po zbudowaniu wystarczy uruchomić samo Django - wszystkie ścieżki
(`/`, `/login`, `/pierwsze-logowanie`, `/profil`, `/panel-admina`)
serwują aplikację React (routing po stronie klienta).

## Struktura

- `src/api.js` - fetch z CSRF i obsługą błędów + etykiety statusów/priorytetów
- `src/auth.jsx` - kontekst uwierzytelniania (`/api/me/`, login, logout)
- `src/components/` - Navbar, RequireAuth, TaskItem, TaskFormModal
- `src/pages/` - Login, FirstLogin, Dashboard, Profile, Admin
- `src/styles.css` - motyw (ciemny + fiolet) na zmiennych Bootstrapa
