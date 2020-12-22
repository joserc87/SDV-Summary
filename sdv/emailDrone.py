import json
from flask import Flask
from flask_mail import Message
from sdv import app, connect_db, mail
import uuid
import time

sqlesc = app.sqlesc


def email_confirmation(address, user_id, key):
    title = "Confirm upload.farm registration"
    body = (
        "Hello!Someone using this email address just signed up for an account on upload.farm. To verify this is correct, please visit: http://upload.farm/verify_email?i="
        + str(user_id)
        + "&t="
        + str(key)
        + " If this is in error no action is necessary and you will not hear from us again. Verifying your email address allows us to send you password reset email. Thanks! The upload.farm devs"
    )
    html = (
        '<p>Hello! </p><p>Someone using this email address just signed up for an account on upload.farm. To verify this is correct, please <a href="http://upload.farm/verify_email?i='
        + str(user_id)
        + "&t="
        + str(key)
        + '">click here</a>.</p> <p>If this is in error no action is necessary and you will not hear from us again. Verifying your email address allows us to send you password reset email.</p><p>Thanks!<br>The upload.farm devs</p>'
    )
    send_email(address, title, body, html)


def old_email_confirmation(address, user_id, key):
    title = "Confirm upload.farm registration"
    body = (
        "Hello! Some time ago, someone using this email address signed up for an account on upload.farm. To verify this is correct, please visit: http://upload.farm/verify_email?i="
        + str(user_id)
        + "&t="
        + str(key)
        + " If this is in error no action is necessary and you will not hear from us again. Verifying your email address allows us to send you password reset email. Thanks! The upload.farm devs"
    )
    html = (
        '<p>Hello!</p><p>Some time ago, someone using this email address signed up for an account on upload.farm. To verify this is correct, please <a href="http://upload.farm/verify_email?i='
        + str(user_id)
        + "&t="
        + str(key)
        + '">click here</a>.</p> <p>If this is in error no action is necessary and you will not hear from us again. Verifying your email address allows us to send you password reset email.</p><p>Thanks!<br>The upload.farm devs</p>'
    )
    send_email(address, title, body, html)


def email_passwordreset(address, user_id, key):
    title = "Reset upload.farm password"
    body = (
        "Hello! Someone has requested a password reset for this email address on upload.farm. To reset your password, please visit: http://upload.farm/reset?i="
        + str(user_id)
        + "&t="
        + str(key)
        + " If this is in error no action is necessary."
    )
    html = (
        '<p>Hello!</p><p>Someone has requested a password reset for this email address on upload.farm. To reset your password, please <a href="http://upload.farm/reset?i='
        + str(user_id)
        + "&t="
        + str(key)
        + '">click here</a>.</p> <p>If this is in error no action is necessary.</p>'
    )
    send_email(address, title, body, html)


def send_email(address, title, body, html):
    with app.app_context():
        msg = Message(title, recipients=[address])
        msg.body = body
        msg.html = html
        mail.send(msg)


def process_email():
    start_time = time.time()
    records_handled = 0
    db = connect_db()
    cur = db.cursor()
    while True:
        cur.execute(
            "UPDATE todo SET currently_processing="
            + sqlesc
            + " WHERE id=(SELECT id FROM todo WHERE task=ANY("
            + sqlesc
            + ") AND currently_processing IS NOT TRUE LIMIT 1) RETURNING *",
            (
                True,
                ["email_confirmation", "old_email_confirmation", "email_passwordreset"],
            ),
        )
        tasks = cur.fetchall()
        db.commit()
        # print tasks
        if len(tasks) != 0:
            for task in tasks:
                if task[1] in ["email_confirmation", "old_email_confirmation"]:
                    cur.execute(
                        "UPDATE users SET email_conf_token=(CASE WHEN email_conf_token IS NULL THEN "
                        + sqlesc
                        + " WHEN email_conf_token IS NOT NULL THEN email_conf_token END) WHERE id="
                        + sqlesc
                        + " RETURNING email, id, email_conf_token",
                        (str(uuid.uuid4()), task[2]),
                    )
                    email_data = cur.fetchall()[0]
                    if task[1] == "email_confirmation":
                        email_confirmation(*email_data)
                    elif task[1] == "old_email_confirmation":
                        old_email_confirmation(*email_data)
                elif task[1] in ["email_passwordreset"]:
                    cur.execute(
                        "UPDATE users SET pw_reset_token="
                        + sqlesc
                        + " WHERE id="
                        + sqlesc
                        + " RETURNING email, id, pw_reset_token",
                        (str(uuid.uuid4()), task[2]),
                    )
                    email_data = cur.fetchall()[0]
                    email_passwordreset(*email_data)
                cur.execute("DELETE FROM todo WHERE id=(" + sqlesc + ")", (task[0],))
                db.commit()
                records_handled += 1
        else:
            db.close()
            return time.time() - start_time, records_handled


if __name__ == "__main__":
    print(process_email())
