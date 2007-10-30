from django import newforms as forms

class EditForm(forms.Form):
    comment = forms.CharField(widget=forms.Textarea)
    recheck = forms.BooleanField()
