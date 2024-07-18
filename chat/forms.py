from django import forms


class BannerMessageForm(forms.Form):
    """Banner message form"""

    content = forms.CharField(
        widget=forms.Textarea, label="Message Content", required=True
    )
