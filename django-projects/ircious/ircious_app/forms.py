from django import newforms as forms
from ircious.ircious_app.models import User

# Custom form fields
class ChannelField(forms.CharField):
    def clean(self, value):
        if not value:
            raise forms.ValidationError("You didn't enter a channel")
        if value.startswith("#"):
            value = "#"+value
        return value

class UserField(forms.CharField):
    def clean(self, value):
        if not value:
            raise forms.ValidationError("You didn't enter a nick")
        user = User.objects.filter(nick__nickname=value)
        if not user:
            raise forms.ValidationError("That is not an existing user")
        if len(user) > 1:
            raise forms.ValidationError("There's multiple users... This is fishy :/")
        return user[0]

# Actual forms
class EditForm(forms.Form):
    comment = forms.CharField(widget=forms.Textarea)
    recheck = forms.BooleanField()

class RequestChannelForm(forms.Form):
    channel = ChannelField()
    network = forms.CharField()
    nick = UserField()
