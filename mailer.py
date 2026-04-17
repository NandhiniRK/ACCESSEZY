import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_otp_email(to_email: str, otp: str, name: str):
    """Send a 6-digit OTP verification email via Gmail SMTP."""
    sender   = os.environ.get("MAIL_USER")
    password = os.environ.get("MAIL_PASSWORD")

    if not sender or not password:
        raise RuntimeError(
            "MAIL_USER and MAIL_PASSWORD environment variables must be set. "
            "See README or .env.example for instructions."
        )

    subject = "Your Accessezy verification code"

    # Plain-text body
    text_body = f"""Hi {name},

Your Accessezy email verification code is:

    {otp}

This code expires in 10 minutes.
If you did not register for Accessezy, you can safely ignore this email.

— The Accessezy Team
"""

    # HTML body (nicer in most email clients)
    html_body = f"""
<!DOCTYPE html>
<html>
<body style="margin:0;padding:0;background:#f5f5f0;font-family:sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0">
    <tr>
      <td align="center" style="padding:40px 16px;">
        <table width="480" cellpadding="0" cellspacing="0"
               style="background:#ffffff;border-radius:12px;
                      border:1px solid #e0ddd7;overflow:hidden;">
          <!-- Header -->
          <tr>
            <td style="background:#4a7c59;padding:28px 36px;">
              <p style="margin:0;font-size:22px;font-weight:700;color:#ffffff;
                         letter-spacing:-0.5px;">Accessezy ✨</p>
            </td>
          </tr>
          <!-- Body -->
          <tr>
            <td style="padding:36px 36px 28px;">
              <p style="margin:0 0 8px;font-size:18px;font-weight:700;color:#1a1a1a;">
                Hi {name}, verify your email
              </p>
              <p style="margin:0 0 28px;font-size:14px;color:#666;line-height:1.6;">
                Enter the code below to complete your Accessezy registration.
                It expires in <strong>10 minutes</strong>.
              </p>
              <!-- OTP box -->
              <div style="background:#f0f7f3;border:2px solid #4a7c59;border-radius:10px;
                          padding:22px;text-align:center;margin-bottom:28px;">
                <p style="margin:0;font-size:38px;font-weight:800;
                           letter-spacing:12px;color:#4a7c59;font-family:monospace;">
                  {otp}
                </p>
              </div>
              <p style="margin:0;font-size:13px;color:#999;line-height:1.6;">
                If you did not create an Accessezy account, you can safely ignore this email.
              </p>
            </td>
          </tr>
          <!-- Footer -->
          <tr>
            <td style="background:#f5f5f0;padding:18px 36px;
                        border-top:1px solid #e0ddd7;">
              <p style="margin:0;font-size:12px;color:#aaa;">
                © Accessezy · Built for neurodivergent learners
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

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = f"Accessezy ✨ <{sender}>"
    msg["To"]      = to_email

    msg.attach(MIMEText(text_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(sender, password)
        smtp.sendmail(sender, to_email, msg.as_string())
