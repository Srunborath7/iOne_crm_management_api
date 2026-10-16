from __future__ import annotations

import os
from html import escape
from urllib.parse import quote

import httpx


class EmailConfigurationError(Exception):
    pass


def get_email_settings() -> tuple[str, str, str | None]:
    api_key = os.getenv("RESEND_API_KEY")
    sender = os.getenv("PASSWORD_RESET_FROM_EMAIL")
    if not api_key or not sender:
        raise EmailConfigurationError(
            "RESEND_API_KEY and PASSWORD_RESET_FROM_EMAIL must be configured."
        )
    return api_key, sender, os.getenv("FRONTEND_RESET_PASSWORD_URL")


async def send_password_reset_email(recipient: str, token: str) -> None:
    api_key, sender, reset_url = get_email_settings()
    reset_link = None
    if reset_url:
        separator = "&" if "?" in reset_url else "?"
        reset_link = f"{reset_url}{separator}token={quote(token)}"

    text_body = [
        "We received a request to reset your CRM password.",
        "",
        "This link expires in 15 minutes and can only be used once:",
        reset_link or f"Reset token: {token}",
        "",
        "If you did not request this, you can ignore this email.",
    ]

    if reset_link:
        safe_link = escape(reset_link, quote=True)
        html_body = f"""<!doctype html>
<html lang="en">
  <body style="margin:0;padding:32px 16px;background:#f3f6fb;font-family:Arial,Helvetica,sans-serif;color:#172033;">
    <div style="max-width:560px;margin:0 auto;background:#ffffff;border:1px solid #e5eaf2;border-radius:14px;overflow:hidden;">
      <div style="padding:24px 32px;background:#173b70;color:#ffffff;font-size:20px;font-weight:700;">CRM Account Security</div>
      <div style="padding:32px;">
        <h1 style="margin:0 0 16px;font-size:24px;line-height:1.3;color:#172033;">Reset your password</h1>
        <p style="margin:0 0 24px;font-size:15px;line-height:1.6;color:#4b5565;">We received a request to reset the password for your CRM account. Use the button below to choose a new password.</p>
        <p style="margin:0 0 24px;"><a href="{safe_link}" style="display:inline-block;padding:13px 22px;border-radius:8px;background:#2563eb;color:#ffffff;text-decoration:none;font-size:15px;font-weight:700;">Reset password</a></p>
        <p style="margin:0 0 8px;font-size:13px;line-height:1.6;color:#667085;">This link expires in 15 minutes and can only be used once.</p>
        <p style="margin:24px 0 8px;font-size:13px;color:#667085;">If the button does not work, copy this link into your browser:</p>
        <p style="margin:0;word-break:break-all;font-size:13px;line-height:1.6;"><a href="{safe_link}" style="color:#2563eb;">{safe_link}</a></p>
        <p style="margin:24px 0 0;font-size:13px;line-height:1.6;color:#667085;">If you did not request a password reset, you can ignore this email. Your password will not change.</p>
      </div>
    </div>
    <p style="max-width:560px;margin:16px auto 0;text-align:center;font-size:12px;color:#98a2b3;">This is an automated message. Please do not reply.</p>
  </body>
</html>"""
    else:
        html_body = None

    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "from": sender,
                "to": [recipient],
                "subject": "Reset your CRM password",
                "text": "\n".join(text_body),
                **({"html": html_body} if html_body else {}),
            },
        )
        response.raise_for_status()
