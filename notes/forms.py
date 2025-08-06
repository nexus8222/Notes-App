# notes/forms.py
from django import forms

# Custom classes for multiple file uploads (no changes here)
class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

# --- MODIFIED ---
class NoteForm(forms.Form):
    title = forms.CharField(max_length=200, widget=forms.TextInput(
        attrs={"class": "form-control", "placeholder": "Title"}))
    content = forms.CharField(widget=forms.Textarea(
        attrs={"class": "form-control", "rows": 10, "placeholder": "Content (Markdown supported)"}))
    tags = forms.CharField(required=False, help_text="Comma-separated values", widget=forms.TextInput(
        attrs={"class": "form-control", "placeholder": "e.g., python, django, ideas"}))
    is_pinned = forms.BooleanField(required=False, widget=forms.CheckboxInput(
        attrs={"class": "form-check-input"}))
    attachments = MultipleFileField(required=False)
    
    # NEW - Password fields
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Leave blank for no password"}),
        help_text="To remove the password, submit an empty password field."
    )
    confirm_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Confirm password"})
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        
        return cleaned_data

# NEW - Form for unlocking a note
class NoteUnlockForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Enter password"}))

class SearchForm(forms.Form):
    q = forms.CharField(required=False, widget=forms.TextInput(
        attrs={"class": "form-control me-2", "placeholder": "Search"}))
