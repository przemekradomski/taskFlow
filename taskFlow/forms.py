from django import forms
from django.contrib.auth.password_validation import validate_password

from taskFlow.models import Issue

class LoginForm(forms.Form):
    username = forms.CharField(label="Nazwa użytkownika", max_length=150)
    password = forms.CharField(label="Hasło", widget=forms.PasswordInput)

class FirstLoginForm(forms.Form):
    """Pierwsze logowanie: kod weryfikacyjny z maila + nowe hasło."""

    username = forms.CharField(label="Nazwa użytkownika", max_length=150)
    code = forms.CharField(label="Kod weryfikacyjny", max_length=12)
    password1 = forms.CharField(label="Nowe hasło", widget=forms.PasswordInput)
    password2 = forms.CharField(
        label="Powtórz hasło", widget=forms.PasswordInput
    )

    def clean(self):
        cleaned = super().clean()
        password1 = cleaned.get("password1")
        password2 = cleaned.get("password2")

        if password1 and password2 and password1 != password2:
            self.add_error("password2", "Hasła nie są identyczne.")
        elif password1:
            try:
                validate_password(password1)
            except forms.ValidationError as error:
                self.add_error("password1", error)

        return cleaned

class AdminCreateUserForm(forms.Form):
    """Formularz administratora do tworzenia kont (username + email)."""

    username = forms.CharField(label="Nazwa użytkownika", max_length=150)
    email = forms.EmailField(label="Adres e-mail")

class TaskForm(forms.Form):
    title = forms.CharField(label="Tytuł", max_length=100)
    description = forms.CharField(
        label="Opis", required=False, widget=forms.Textarea
    )
    priority = forms.CharField(label="Priorytet", required=False)

    def clean_priority(self):
        priority = self.cleaned_data.get("priority") or Issue.Priority.MEDIUM
        for value, _label in Issue.Priority.choices:
            if value.lower() == str(priority).lower():
                return value
        return Issue.Priority.MEDIUM

    def clean_title(self):
        return self.cleaned_data["title"].strip()

class TaskUpdateForm(TaskForm):
    """Edycja zadania - dodatkowo umożliwia zmianę statusu."""

    status = forms.CharField(label="Status", required=False)

    def clean_status(self):
        status = self.cleaned_data.get("status")
        if not status:
            return None
        for value, _label in Issue.Status.choices:
            if value.lower() == str(status).lower():
                return value
        raise forms.ValidationError("Nieprawidłowy status.")
