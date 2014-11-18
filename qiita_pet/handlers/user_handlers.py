from tornado.web import authenticated
from future.utils import viewitems
from wtforms import Form, StringField, validators

from qiita_pet.handlers.base_handlers import BaseHandler
from qiita_db.user import User
from qiita_db.logger import LogEntry
from qiita_db.exceptions import QiitaDBUnknownIDError
from qiita_core.util import send_email


class UserProfile(Form):
    name = StringField("Name", [validators.required()])
    affiliation = StringField("Affiliation")
    address = StringField("Address")
    phone = StringField("Phone")


class UserProfileHandler(BaseHandler):
    """Displays user profile page and handles profile updates"""
    @authenticated
    def get(self):
        user = self.current_user
        profile = UserProfile()
        profile.process(data=User(user).info)
        self.render("user_profile.html", user=user, profile=profile, msg="",
                    passmsg="")

    @authenticated
    def post(self):
        passmsg = ""
        msg = ""
        user = User(self.current_user)
        action = self.get_argument("action")
        if action == "profile":
            # tuple of colmns available for profile
            # FORM INPUT NAMES MUST MATCH DB COLUMN NAMES
            form_data = UserProfile()
            form_data.process(data=self.request.arguments)
            profile = {name: data[0] for name, data in
                       viewitems(form_data.data)}

            # Turn default value as list into default strings
            for field in form_data:
                field.data = field.data[0]
            try:
                user.info = profile
                msg = "Profile updated successfully"
            except Exception as e:
                msg = "ERROR: profile could not be updated"
                LogEntry.create('Runtime', "Cound not update profile: %s" %
                                str(e), info={'User': user.id})

        elif action == "password":
            form_data = UserProfile()
            form_data.process(data=user.info)
            oldpass = self.get_argument("oldpass")
            newpass = self.get_argument("newpass")
            try:
                user.change_password(oldpass, newpass)
            except Exception as e:
                passmsg = "ERROR: could not change password"
                LogEntry.create('Runtime', "Cound not change password: %s" %
                                str(e), info={'User': user.id})
            else:
                passmsg = "Password changed successfully"
        self.render("user_profile.html", user=user.id, profile=form_data,
                    msg=msg, passmsg=passmsg)


class ForgotPasswordHandler(BaseHandler):
    """Displays forgot password page and generates code for lost passwords"""
    def get(self):
        self.render("lost_pass.html", user=None, message="", level="")

    def post(self):
        message = ""
        level = ""
        page = "lost_pass.html"
        user_id = None

        try:
            user = User(self.get_argument("email"))
        except QiitaDBUnknownIDError:
            message = "ERROR: Unknown user."
            level = "danger"
        else:
            user_id = user.id
            user.generate_reset_code()
            info = user.info
            try:
                send_email(user.id, "Qiita: Password Reset", "Please go to "
                           "the following URL to reset your password: "
                           "http://qiita.colorado.edu/auth/reset/%s" %
                           info["pass_reset_code"])
                message = ("Check your email for the reset code.")
                level = "success"
                page = "index.html"
            except Exception as e:
                message = ("Unable to send email. Error has been registered. "
                           "Your password has not been reset.")
                level = "danger"
                LogEntry.create('Runtime', "Unable to send forgot password "
                                "email: %s" % str(e), info={'User': user.id})

        self.render(page, user=user_id, message=message, level=level)


class ChangeForgotPasswordHandler(BaseHandler):
    """Displays change password page and handles password reset"""
    def get(self, code):
            self.render("change_lost_pass.html", user=None, message="",
                        level="", code=code)

    def post(self, code):
        message = ""
        level = ""
        page = "change_lost_pass.html"
        user = None

        try:
            user = User(self.get_argument("email"))
        except QiitaDBUnknownIDError:
            message = "Unable to reset password"
            level = "danger"
        else:
            newpass = self.get_argument("newpass")
            changed = user.change_forgot_password(code, newpass)
            user = self.current_user

            if changed:
                message = ("Password reset successful. Please log in to "
                           "continue.")
                level = "success"
                page = "index.html"
            else:
                message = "Unable to reset password"
                level = "danger"

        self.render(page, user=user, message=message, level=level, code=code)
