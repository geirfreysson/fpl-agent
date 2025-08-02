# Authentication Implementation Guide: Clerk + FastAPI

This guide documents the complete authentication implementation used in the FPL With Robots application, using Clerk for authentication and FastAPI as the backend framework.

## Overview

The authentication system uses **Clerk** (a third-party authentication service) with the following flow:
1. Users visit the app and are redirected to a sign-in page if not authenticated
2. Clerk handles the authentication UI and session management
3. The FastAPI backend verifies session tokens on protected routes
4. Authenticated users can access the main chat interface

## Environment Variables Required

```bash
CLERK_PUBLISHABLE_KEY=pk_test_...  # Frontend key for Clerk JS SDK
CLERK_SECRET_KEY=sk_test_...       # Backend key for API verification
```

## Backend Implementation (FastAPI)

### Dependencies

```python
from clerk_backend_api import Clerk
from clerk_backend_api.jwks_helpers import AuthenticateRequestOptions
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
```

### Core Authentication Functions

#### 1. Session Verification
```python
async def verify_auth(request: Request):
    """Verify the Clerk session token"""
    # Check for session token in cookies or headers
    session_token = request.cookies.get("__session") or request.headers.get("Authorization")
    
    if not session_token:
        return None

    sdk = Clerk(bearer_auth=os.getenv("CLERK_SECRET_KEY"))
    
    request_state = sdk.authenticate_request(
        request, 
        AuthenticateRequestOptions()
    )
    if request_state.is_signed_in:
        return request_state.payload
    else:
        return None
```

#### 2. Authentication Dependency
```python
async def get_current_user(request: Request):
    """Get the current authenticated user or raise an exception"""
    user_data = await verify_auth(request)
    if not user_data:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user_data
```

#### 3. Route Protection Middleware
```python
@app.middleware("http")
async def login_required(request: Request, call_next):
    """Middleware to protect /chat path with authentication"""
    if (request.url.path == "/chat") or (request.url.path == "/chat/"):
        user = await verify_auth(request)
        if user is None:
            return RedirectResponse(url="/sign-in")  # Redirect to login page
    return await call_next(request)
```

### Route Handlers

#### 1. Root Route
```python
@app.get("/")
async def index(request: Request):
    sdk = Clerk(bearer_auth=os.getenv("CLERK_SECRET_KEY"))
    request_state = sdk.authenticate_request(request, AuthenticateRequestOptions())
    
    if request_state.is_signed_in:
        return RedirectResponse(url="/chat")  # Go to app if authenticated
    else:
        return RedirectResponse(url="/sign-in")  # Go to login if not
```

#### 2. Sign-in Page
```python
@app.get("/sign-in", response_class=HTMLResponse)
async def sign_in_page(request: Request):
    """Serve the login page with Clerk auth"""
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "clerk_publishable_key": CLERK_PUBLISHABLE_KEY},
    )
```

#### 3. Sign-out Page 
```python
@app.get("/sign-out", response_class=HTMLResponse)
async def signout_page(request: Request):
    """Serve the logout page with Clerk auth"""
    return templates.TemplateResponse(
        "logout.html",
        {"request": request, "clerk_publishable_key": CLERK_PUBLISHABLE_KEY},
    )
```

## Frontend Implementation (Templates)

### 1. Login Page Template (`templates/login.html`)

**Key Components:**
- Loads Clerk JS SDK with publishable key
- Automatically redirects authenticated users to `/chat/`
- Mounts Clerk's sign-in UI component

```html
<!-- Load Clerk SDK -->
<script
    async
    crossorigin="anonymous"
    data-clerk-publishable-key="{{clerk_publishable_key}}"
    src="https://organic-seal-95.clerk.accounts.dev/npm/@clerk/clerk-js@5/dist/clerk.browser.js"
    type="text/javascript">
</script>

<script>
    window.addEventListener('load', async function () {
        await Clerk.load()

        if (Clerk.user) {
            // Already signed in - redirect to app
            window.location.href = "/chat/";
        } else {
            // Mount sign-in UI
            document.getElementById('app').innerHTML = `<div id="sign-in"></div>`
            const signInDiv = document.getElementById('sign-in')
            Clerk.mountSignIn(signInDiv)
        }
    })
</script>
```

### 2. Logout Page Template (`templates/logout.html`)

**Key Components:**
- Calls Clerk's sign-out method
- Redirects to sign-in page

```html
<script>
    window.addEventListener('load', async function () {
        await Clerk.load()

        if (Clerk.user) {
            Clerk.signOut()  // Sign out current user
            window.location.href = "/sign-in/";
        } else {
            window.location.href = "/sign-in/";
        }
    })
</script>
```

### 3. Auth Check Template (`templates/auth-check.html`)

**Note:** This template appears to be legacy code not actively used in the current flow. It contains more complex session handling with cookies and localStorage.

## Protected Resources

### Main Chat Interface
- **Route:** `/chat` 
- **Protection:** Middleware checks authentication
- **Implementation:** Gradio app mounted to FastAPI
- **Redirect:** Unauthenticated users go to `/sign-in`

```python
# Mount protected Gradio app
app = gr.mount_gradio_app(
    app, 
    demo, 
    path="/chat", 
    favicon_path="/assets/favicon/favicon.ico",
    app_kwargs={"root_path": "/chat"})
```

## Authentication Flow

1. **User visits root (`/`)**
   - Backend checks authentication status
   - Redirects to `/chat` if authenticated, `/sign-in` if not

2. **User visits sign-in page (`/sign-in`)**
   - Frontend loads Clerk SDK
   - If already authenticated: redirect to `/chat/`
   - If not: show Clerk sign-in UI

3. **User signs in via Clerk UI**
   - Clerk handles authentication process
   - Session cookie `__session` is set automatically
   - User can now access protected routes

4. **User visits protected route (`/chat`)**
   - Middleware checks for `__session` cookie
   - Verifies session with Clerk backend API
   - Allows access if valid, redirects to `/sign-in` if not

5. **User signs out (`/sign-out`)**
   - Frontend calls `Clerk.signOut()`
   - Redirects to sign-in page

## Session Management

- **Storage:** HTTP-only cookies (automatically managed by Clerk)
- **Token Name:** `__session` (checked in `verify_auth` function)
- **Verification:** Backend uses Clerk SDK to verify tokens
- **Fallback:** Also checks `Authorization` header for API requests

## Security Considerations

1. **Environment Variables:** Clerk keys stored as environment variables
2. **HTTP-Only Cookies:** Session tokens not accessible via JavaScript
3. **Backend Verification:** All protected routes verify tokens server-side
4. **Middleware Protection:** Automatic redirect for unauthenticated users
5. **No Custom JWT:** Relies on Clerk's managed authentication

## Implementation Checklist

To implement this authentication system elsewhere:

1. **Setup Clerk Account**
   - Create Clerk application
   - Get publishable and secret keys
   - Configure allowed domains

2. **Backend Setup**
   - Install `clerk-backend-api` package
   - Add environment variables
   - Implement `verify_auth()` function
   - Add middleware for route protection
   - Create sign-in/sign-out route handlers

3. **Frontend Setup**
   - Create login template with Clerk SDK
   - Create logout template
   - Add publishable key to templates
   - Implement redirect logic

4. **Route Protection**
   - Add middleware to protect sensitive routes
   - Use `get_current_user()` dependency for API endpoints
   - Handle authentication failures with redirects

5. **Testing**
   - Test authentication flow
   - Verify protected routes block unauthenticated users
   - Test sign-out functionality
   - Check session persistence across browser sessions

## Key Files

- `app.py:99-142` - Core authentication logic
- `templates/login.html` - Sign-in page with Clerk UI
- `templates/logout.html` - Sign-out page
- Environment variables for Clerk configuration