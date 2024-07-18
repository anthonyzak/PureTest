from django import forms


class BannerMessageForm(forms.Form):
    content = forms.CharField(
        widget=forms.Textarea, label="Message Content", required=True
    )
