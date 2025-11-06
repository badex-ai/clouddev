FAMILY_MEMBER_WELCOME_EMAIL = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; }}
    </style>
</head>
<body>
    <h1>Welcome to Kaban App, {name}! 👋</h1>
    <p>You've been added to a family on <strong>Kaban App</strong> by {admin_name}.</p>
    <p><strong>Next Steps:</strong></p>
    <p><strong>Set Your Password:</strong></p>
    <p>Click the button below to set your password and activate your account:</p>
    
    <p>
        <a href="{password_reset_url}" style="background-color: #4F46E5; color: #FFFFFF; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block; margin: 20px 0;">Set My Password</a>
    </p>
    
    <p>Or copy and paste this link into your browser:</p>
    <p style="word-break: break-all; color: #4F46E5;">{password_reset_url}</p>
    
    <p><strong>This link will expire in 7 days.</strong></p>
    <hr>
    <p style="color: #666; font-size: 12px;">
        If you didn't expect this invitation, please contact {admin_name}.
    </p>
</body>
</html>
"""


VERIFICATION_EMAIL = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; }}
        .button {{
            background-color: #4F46E5;
            color: white;
            padding: 12px 24px;
            text-decoration: none;
            border-radius: 6px;
            display: inline-block;
        }}
    </style>
</head>
<body>
    <h1>Welcome, {name}! 👋</h1>
    <p>Thank you for signing up for <strong>Kaban App</strong>!</p>
    <p>A verification email has been sent to your address through Auth0.</p>
    <p>If you don't see the email in your inbox, please check your spam or junk folder.</p>
    <hr>
    <p style="color: #666; font-size: 12px;">
        If you didn't create this account, you can safely ignore this message.
    </p>
</body>
</html>
"""
