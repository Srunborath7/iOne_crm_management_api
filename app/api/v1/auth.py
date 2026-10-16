from typing import Annotated
from html import escape
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.domain.auth.schema import (
    AuthCreate,
    AuthResponse,
    AuthUpdate,
    ForgotPasswordRequest,
    LoginRequest,
    MessageResponse,
    RoleCreate,
    RoleData,
    RoleListResponse,
    RoleResponse,
    RoleUpdate,
    ResetPasswordRequest,
    TokenResponse,
)
from app.domain.auth.model import Auths
from app.services.auth_service import AuthService


router = APIRouter(prefix="/auths", tags=["auths"])
SessionDep = Annotated[AsyncSession, Depends(get_db)]
CurrentUserDep = Annotated[Auths, Depends(get_current_user)]


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register_user(data: AuthCreate, session: SessionDep) -> AuthResponse:
    return await AuthService(session).create_user(data)


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, session: SessionDep) -> TokenResponse:
    token = await AuthService(session).login(data)
    return TokenResponse(access_token=token)


@router.post(
    "/forgot-password",
    response_model=MessageResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def forgot_password(
    data: ForgotPasswordRequest, session: SessionDep
) -> MessageResponse:
    await AuthService(session).forgot_password(str(data.email))
    return MessageResponse(
        message="If an account exists for that email, password reset instructions will be sent."
    )


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    data: ResetPasswordRequest, session: SessionDep
) -> MessageResponse:
    await AuthService(session).reset_password(data.token, data.new_password)
    return MessageResponse(message="Password reset successfully.")


@router.get("/reset-password-page", response_class=HTMLResponse)
async def reset_password_page(
    token: str = Query(min_length=20, max_length=200),
) -> HTMLResponse:
    safe_token = escape(token, quote=True)
    page = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="referrer" content="no-referrer">
  <title>Reset password</title>
  <style>
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; min-height: 100vh; display: grid; place-items: center;
      padding: 24px; background: #f3f4f6; color: #111827;
      font-family: system-ui, sans-serif; }}
    main {{ width: min(100%, 420px); padding: 32px; background: white;
      border-radius: 16px; box-shadow: 0 12px 35px #11182718; }}
    h1 {{ margin: 0 0 8px; font-size: 1.5rem; }}
    p {{ color: #4b5563; line-height: 1.5; }}
    label {{ display: block; margin: 18px 0 6px; font-weight: 600; }}
    input {{ width: 100%; padding: 11px 12px; border: 1px solid #d1d5db;
      border-radius: 8px; font: inherit; }}
    button {{ width: 100%; margin-top: 22px; padding: 12px; border: 0;
      border-radius: 8px; background: #2563eb; color: white; font: inherit;
      font-weight: 600; cursor: pointer; }}
    button:disabled {{ opacity: .6; cursor: wait; }}
    #message {{ min-height: 24px; margin-top: 16px; }}
  </style>
</head>
<body>
  <main>
    <h1>Reset your password</h1>
    <p>Choose a new password with at least 8 characters.</p>
    <form id="reset-form">
      <input id="token" type="hidden" value="{safe_token}">
      <label for="password">New password</label>
      <input id="password" type="password" minlength="8" required
        autocomplete="new-password">
      <label for="confirm-password">Confirm new password</label>
      <input id="confirm-password" type="password" minlength="8" required
        autocomplete="new-password">
      <button id="submit" type="submit">Update password</button>
      <p id="message" role="status" aria-live="polite"></p>
    </form>
  </main>
  <script>
    const form = document.getElementById('reset-form');
    const message = document.getElementById('message');
    const submit = document.getElementById('submit');
    form.addEventListener('submit', async (event) => {{
      event.preventDefault();
      const password = document.getElementById('password').value;
      const confirmation = document.getElementById('confirm-password').value;
      if (password !== confirmation) {{
        message.textContent = 'Passwords do not match.';
        return;
      }}
      submit.disabled = true;
      message.textContent = 'Updating password…';
      try {{
        const response = await fetch('/api/v1/auths/reset-password', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            token: document.getElementById('token').value,
            new_password: password
          }})
        }});
        const result = await response.json();
        if (!response.ok) throw new Error(result.detail || 'Reset link is invalid or expired.');
        form.innerHTML = '<p>Password updated. You can now sign in with your new password.</p>';
      }} catch (error) {{
        message.textContent = error.message || 'Could not reset your password.';
        submit.disabled = false;
      }}
    }});
  </script>
</body>
</html>"""
    return HTMLResponse(
        content=page,
        headers={"Cache-Control": "no-store", "Referrer-Policy": "no-referrer"},
    )


@router.get("/me", response_model=AuthResponse)
async def get_me(current_user: CurrentUserDep) -> AuthResponse:
    return current_user


@router.get("/users", response_model=list[AuthResponse])
async def list_users(
    session: SessionDep,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> list[AuthResponse]:
    return await AuthService(session).list_users(offset=offset, limit=limit)


@router.get("/users/{user_id}", response_model=AuthResponse)
async def get_user(user_id: UUID, session: SessionDep) -> AuthResponse:
    return await AuthService(session).get_user(user_id)


@router.patch("/users/{user_id}", response_model=AuthResponse)
async def update_user(
    user_id: UUID, data: AuthUpdate, session: SessionDep
) -> AuthResponse:
    return await AuthService(session).update_user(user_id, data)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: UUID, session: SessionDep) -> Response:
    await AuthService(session).delete_user(user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/roles",
    response_model=RoleResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_role(
    data: RoleCreate, session: SessionDep
) -> RoleResponse:
    role = await AuthService(session).create_role(data)
    return RoleResponse(
        message="Role created successfully",
        data=RoleData.model_validate(role),
    )


@router.get("/roles", response_model=RoleListResponse)
async def list_roles(session: SessionDep) -> RoleListResponse:
    roles = await AuthService(session).list_roles()
    return RoleListResponse(
        message="Roles retrieved successfully",
        data=[RoleData.model_validate(role) for role in roles],
    )


@router.get("/roles/{role_id}", response_model=RoleResponse)
async def get_role(role_id: UUID, session: SessionDep) -> RoleResponse:
    role = await AuthService(session).get_role(role_id)
    return RoleResponse(
        message="Role retrieved successfully",
        data=RoleData.model_validate(role),
    )


@router.patch("/roles/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: UUID, data: RoleUpdate, session: SessionDep
) -> RoleResponse:
    role = await AuthService(session).update_role(role_id, data)
    return RoleResponse(
        message="Role updated successfully",
        data=RoleData.model_validate(role),
    )


@router.delete("/roles/{role_id}", status_code=status.HTTP_200_OK)
async def delete_role(role_id: UUID, session: SessionDep) -> Response:
    await AuthService(session).delete_role(role_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Role deleted successfully"},
    )
