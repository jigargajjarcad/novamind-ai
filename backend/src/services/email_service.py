import asyncio

import resend
import structlog

from src.core.config import settings

logger = structlog.get_logger()


async def send_verification_email(email: str, full_name: str | None, token: str) -> None:
    verify_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
    name = full_name or "there"

    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Verify your NovaMind AI account</title>
</head>
<body style="margin:0;padding:0;background:#0a0a0f;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#0a0a0f;padding:48px 16px;">
    <tr>
      <td align="center">
        <table width="560" cellpadding="0" cellspacing="0" style="background:#111118;border:1px solid #1f2937;border-radius:12px;overflow:hidden;">

          <!-- Header -->
          <tr>
            <td style="padding:32px 40px 24px;border-bottom:1px solid #1f2937;">
              <p style="margin:0;font-size:20px;font-weight:700;background:linear-gradient(90deg,#818cf8,#a78bfa);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">
                NovaMind AI
              </p>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="padding:40px;">
              <h1 style="margin:0 0 12px;font-size:24px;font-weight:700;color:#f9fafb;">
                Verify your email address
              </h1>
              <p style="margin:0 0 24px;font-size:15px;color:#9ca3af;line-height:1.6;">
                Hi {name},<br /><br />
                Thanks for creating a NovaMind AI account. Click the button below to verify
                your email address and start querying your documents.
              </p>

              <!-- CTA -->
              <table cellpadding="0" cellspacing="0" style="margin:0 0 32px;">
                <tr>
                  <td style="border-radius:8px;background:#4f46e5;">
                    <a href="{verify_url}"
                       style="display:inline-block;padding:14px 32px;font-size:15px;font-weight:600;color:#ffffff;text-decoration:none;border-radius:8px;">
                      Verify email address
                    </a>
                  </td>
                </tr>
              </table>

              <p style="margin:0 0 8px;font-size:13px;color:#6b7280;">
                Or copy and paste this link into your browser:
              </p>
              <p style="margin:0 0 32px;font-size:13px;color:#818cf8;word-break:break-all;">
                {verify_url}
              </p>

              <p style="margin:0;font-size:13px;color:#6b7280;line-height:1.6;">
                This link expires in <strong style="color:#9ca3af;">24 hours</strong>. If you didn&apos;t
                create a NovaMind AI account you can safely ignore this email.
              </p>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="padding:24px 40px;border-top:1px solid #1f2937;">
              <p style="margin:0;font-size:12px;color:#4b5563;">
                &copy; 2026 NovaMind AI &mdash; AI-powered document intelligence
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""

    def _send() -> None:
        resend.api_key = settings.RESEND_API_KEY
        resend.Emails.send({
            "from": f"NovaMind AI <{settings.RESEND_FROM_EMAIL}>",
            "to": [email],
            "subject": "Verify your NovaMind AI account",
            "html": html,
        })

    try:
        await asyncio.to_thread(_send)
        logger.info("email.verification.sent", to=email)
    except Exception as exc:
        # Log but don't surface email failures as HTTP errors —
        # the user record is already created and can resend from the login page.
        logger.error("email.verification.failed", to=email, error=str(exc))


async def send_password_reset_email(email: str, full_name: str | None, token: str) -> None:
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    name = full_name or "there"

    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Reset your NovaMind AI password</title>
</head>
<body style="margin:0;padding:0;background:#0a0a0f;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#0a0a0f;padding:48px 16px;">
    <tr>
      <td align="center">
        <table width="560" cellpadding="0" cellspacing="0" style="background:#111118;border:1px solid #1f2937;border-radius:12px;overflow:hidden;">

          <!-- Header -->
          <tr>
            <td style="padding:32px 40px 24px;border-bottom:1px solid #1f2937;">
              <p style="margin:0;font-size:20px;font-weight:700;background:linear-gradient(90deg,#818cf8,#a78bfa);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">
                NovaMind AI
              </p>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="padding:40px;">
              <h1 style="margin:0 0 12px;font-size:24px;font-weight:700;color:#f9fafb;">
                Reset your password
              </h1>
              <p style="margin:0 0 24px;font-size:15px;color:#9ca3af;line-height:1.6;">
                Hi {name},<br /><br />
                We received a request to reset the password for your NovaMind AI account. Click
                the button below to choose a new password.
              </p>

              <!-- CTA -->
              <table cellpadding="0" cellspacing="0" style="margin:0 0 32px;">
                <tr>
                  <td style="border-radius:8px;background:#4f46e5;">
                    <a href="{reset_url}"
                       style="display:inline-block;padding:14px 32px;font-size:15px;font-weight:600;color:#ffffff;text-decoration:none;border-radius:8px;">
                      Reset password
                    </a>
                  </td>
                </tr>
              </table>

              <p style="margin:0 0 8px;font-size:13px;color:#6b7280;">
                Or copy and paste this link into your browser:
              </p>
              <p style="margin:0 0 32px;font-size:13px;color:#818cf8;word-break:break-all;">
                {reset_url}
              </p>

              <p style="margin:0;font-size:13px;color:#6b7280;line-height:1.6;">
                This link expires in <strong style="color:#9ca3af;">1 hour</strong>. If you
                didn&apos;t request a password reset you can safely ignore this email &mdash;
                your password will not change.
              </p>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="padding:24px 40px;border-top:1px solid #1f2937;">
              <p style="margin:0;font-size:12px;color:#4b5563;">
                &copy; 2026 NovaMind AI &mdash; AI-powered document intelligence
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""

    def _send() -> None:
        resend.api_key = settings.RESEND_API_KEY
        resend.Emails.send({
            "from": f"NovaMind AI <{settings.RESEND_FROM_EMAIL}>",
            "to": [email],
            "subject": "Reset your NovaMind AI password",
            "html": html,
        })

    try:
        await asyncio.to_thread(_send)
        logger.info("email.password_reset.sent", to=email)
    except Exception as exc:
        logger.error("email.password_reset.failed", to=email, error=str(exc))
