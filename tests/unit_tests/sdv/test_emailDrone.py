from flask_mail import Mail
from sdv.emailDrone import (
    mail,
    email_confirmation,
    old_email_confirmation,
)


def test_email_confirmation():
    with mail.record_messages() as outbox:
        email_confirmation("foo@bar.com", 123, "randomkey")

        assert len(outbox) == 1
        m = outbox[0]
        assert m.subject == "Confirm upload.farm registration"
        assert (
            m.body
            == "Hello!Someone using this email address just signed up for an account on upload.farm. To verify this is correct, please visit: http://upload.farm/verify_email?i=123&t=randomkey If this is in error no action is necessary and you will not hear from us again. Verifying your email address allows us to send you password reset email. Thanks! The upload.farm devs"
        )
        assert (
            m.html
            == '<p>Hello! </p><p>Someone using this email address just signed up for an account on upload.farm. To verify this is correct, please <a href="http://upload.farm/verify_email?i=123&t=randomkey">click here</a>.</p> <p>If this is in error no action is necessary and you will not hear from us again. Verifying your email address allows us to send you password reset email.</p><p>Thanks!<br>The upload.farm devs</p>'
        )


def test_old_email_confirmation():
    with mail.record_messages() as outbox:
        old_email_confirmation("foo@bar.com", 123, "randomkey")

        assert len(outbox) == 1
        m = outbox[0]
        assert m.subject == "Confirm upload.farm registration"
        assert (
            m.body
            == "Hello! Some time ago, someone using this email address signed up for an account on upload.farm. To verify this is correct, please visit: http://upload.farm/verify_email?i=123&t=randomkey If this is in error no action is necessary and you will not hear from us again. Verifying your email address allows us to send you password reset email. Thanks! The upload.farm devs"
        )
        assert (
            m.html
            == '<p>Hello!</p><p>Some time ago, someone using this email address signed up for an account on upload.farm. To verify this is correct, please <a href="http://upload.farm/verify_email?i=123&t=randomkey">click here</a>.</p> <p>If this is in error no action is necessary and you will not hear from us again. Verifying your email address allows us to send you password reset email.</p><p>Thanks!<br>The upload.farm devs</p>'
        )
