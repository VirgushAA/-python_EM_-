Initial README state, mod later.

## Authentication

- Users authenticate using email and password
- Passwords are stored using bcrypt
- After login, the server issues a JWT token
- The token is passed via Authorization: Bearer header
- Custom middleware extracts the token and identifies the user

## Authorization

The system uses role-based access control with ownership support.

- Users can have multiple roles
- Roles contain permissions
- Permission defines:
  - resource
  - action
  - scope (own / all)

# server
start
- uvicorn main:app --reload
docs
- http://127.0.0.1:8000/docs

экстренная остановка
- taskkill /IM python.exe /F
- taskkill /IM uvicorn.exe /F


DB engine can be switched to PostgreSQL without changes in ORM layer
JWT-based auth, logout is handled client-side
selectinload