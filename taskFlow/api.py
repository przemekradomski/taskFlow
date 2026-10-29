import json
import secrets

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods

from taskFlow.forms import FirstLoginForm, LoginForm, TaskForm, TaskUpdateForm
from taskFlow.models import AccountVerification, Issue, Profile

def _json_body(request):
    if request.content_type and "json" in request.content_type:
        try:
            data = json.loads(request.body or "{}")
            return data if isinstance(data, dict) else {}
        except (ValueError, TypeError):
            return {}
    return request.POST

def _error(status, detail=None, errors=None, **extra):
    payload = {}
    if detail:
        payload["detail"] = detail
    if errors:
        payload["errors"] = errors
    payload.update(extra)
    return JsonResponse(payload, status=status)

def _unauthorized():
    return _error(401, "Wymagane zalogowanie.")

def _forbidden(detail="Brak uprawnień."):
    return _error(403, detail)

def _serialize_issue(issue):
    return {
        "id": issue.pk,
        "title": issue.title,
        "description": issue.description,
        "status": issue.status,
        "priority": issue.priority,
        "created_at": issue.created_at.isoformat(),
        "owner": issue.created_by.username if issue.created_by else None,
    }

def _serialize_user(user, avatar=None):
    return {
        "id": user.pk,
        "username": user.username,
        "email": user.email,
        "is_superuser": user.is_superuser,
        "avatar": avatar,
    }

def _generate_code():
    return "".join(secrets.choice("0123456789") for _ in range(6))

def _send_verification_code(user, code):
    send_mail(
        subject="TaskFlow - kod weryfikacyjny",
        message=(
            f"Cześć {user.username}!\n\n"
            f"Twoje konto zostało utworzone przez administratora.\n"
            f"Twój kod weryfikacyjny do pierwszego logowania: {code}\n\n"
            "Wejdź na stronę pierwszego logowania, podaj kod oraz ustaw swoje hasło.\n"
            "Kod jest ważny 24 godziny."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )

def _email_configured():
    return bool(getattr(settings, "TASKFLOW_EMAIL_USER", ""))

def _create_account_with_code(username, email):
    existing = User.objects.filter(username__iexact=username).first()
    if existing is not None:
        if existing.is_active:
            return 400, {"detail": f"Użytkownik „{username}” już istnieje."}

        code = _generate_code()
        verification, _created = AccountVerification.objects.get_or_create(
            user=existing,
            defaults={"code_hash": make_password(code, hasher="sha512")},
        )
        if not _created:
            verification.code_hash = make_password(code, hasher="sha512")
            verification.created_at = timezone.now()
            verification.used_at = None
            verification.save()
        try:
            _send_verification_code(existing, code)
        except Exception:
            return 500, {"detail": "Nie udało się wysłać maila z kodem."}
        payload = {
            "detail": f"Konto „{username}” czeka na aktywację - wysłano nowy kod na {email}."
        }
        if not _email_configured():
            payload["dev_code"] = code
        return 200, payload

    if User.objects.filter(email__iexact=email).exists():
        return 400, {"detail": "Ten adres e-mail jest już używany."}

    user = User(username=username, email=email, is_active=False)
    user.set_unusable_password()
    user.full_clean(exclude=["password"])
    user.save()

    code = _generate_code()
    AccountVerification.objects.create(
        user=user, code_hash=make_password(code, hasher="sha512")
    )

    try:
        _send_verification_code(user, code)
        detail = f"Utworzono konto „{username}”. Kod weryfikacyjny wysłano na {email}."
        status = 201
    except Exception:
        detail = f"Utworzono konto „{username}”, ale nie udało się wysłać maila z kodem."
        status = 201

    payload = {"detail": detail}
    if not _email_configured():
        payload["dev_code"] = code
    return status, payload

@ensure_csrf_cookie
@require_http_methods(["GET"])
def me(request):
    if not request.user.is_authenticated:
        return JsonResponse({"authenticated": False})
    profile, _created = Profile.objects.get_or_create(user=request.user)
    return JsonResponse(
        {
            "authenticated": True,
            "user": _serialize_user(
                request.user,
                avatar=profile.avatar.url if profile.avatar else None,
            ),
        }
    )

@require_http_methods(["POST"])
def login_view(request):
    data = _json_body(request)
    form = LoginForm(data)
    if not form.is_valid():
        return _error(400, errors=dict(form.errors))

    user = authenticate(
        request,
        username=form.cleaned_data["username"],
        password=form.cleaned_data["password"],
    )
    if user is None:
        pending = User.objects.filter(
            username__iexact=form.cleaned_data["username"], is_active=False
        ).first()
        if pending is not None:
            return _error(
                403,
                "To konto nie ma jeszcze hasła. Użyj strony pierwszego logowania.",
                first_login=True,
            )
        return _error(
            400,
            errors={"__all__": ["Nieprawidłowa nazwa użytkownika lub hasło."]},
        )

    login(request, user)
    return JsonResponse({"user": _serialize_user(user)})

@require_http_methods(["POST"])
def first_login_view(request):
    data = _json_body(request)
    form = FirstLoginForm(data)
    if not form.is_valid():
        return _error(400, errors=dict(form.errors))

    username = form.cleaned_data["username"]
    user = User.objects.filter(username__iexact=username).first()
    verification = getattr(user, "verification", None) if user else None

    if user is None:
        return _error(400, detail="Nie znaleziono takiego konta.")
    if user.is_active:
        return _error(
            400,
            "Konto jest już aktywne - zaloguj się hasłem na stronie logowania.",
        )
    if verification is None or verification.used_at is not None:
        return _error(400, "Brak aktywnego kodu. Poproś administratora o nowy.")
    if verification.is_expired():
        return _error(400, "Kod wygasł. Poproś administratora o nowy.")
    if not check_password(form.cleaned_data["code"], verification.code_hash):
        return _error(400, "Nieprawidłowy kod weryfikacyjny.")

    user.set_password(form.cleaned_data["password1"])
    user.is_active = True
    user.save()
    verification.used_at = timezone.now()
    verification.save()
    login(request, user)
    return JsonResponse({"detail": "Konto aktywowane. Witaj w TaskFlow!"})

@require_http_methods(["POST"])
def logout_view(request):
    logout(request)
    return JsonResponse({"detail": "Wylogowano."})

@require_http_methods(["GET", "POST"])
def tasks(request):
    if not request.user.is_authenticated:
        return _unauthorized()

    issues = Issue.objects.select_related("created_by")
    if not request.user.is_superuser:
        issues = issues.filter(created_by=request.user)

    if request.method == "GET":
        ordered = issues.order_by("-created_at")
        task_list = [_serialize_issue(issue) for issue in ordered]
        return JsonResponse(
            {
                "tasks": task_list,
                "counts": {
                    "to_do": sum(1 for t in task_list if t["status"] == Issue.Status.TO_DO),
                    "in_progress": sum(
                        1 for t in task_list if t["status"] == Issue.Status.IN_PROGRESS
                    ),
                    "done": sum(1 for t in task_list if t["status"] == Issue.Status.DONE),
                    "total": len(task_list),
                },
            }
        )

    form = TaskForm(_json_body(request))
    if not form.is_valid():
        return _error(400, errors=dict(form.errors))
    issue = Issue.objects.create(
        title=form.cleaned_data["title"],
        description=form.cleaned_data["description"],
        priority=form.cleaned_data["priority"],
        created_by=request.user,
    )
    return JsonResponse(_serialize_issue(issue), status=201)

def _get_task_for_user(request, issue_id):
    issue = Issue.objects.filter(pk=issue_id).first()
    if issue is None:
        return None, _error(404, "Nie znaleziono zadania.")
    if issue.created_by_id != request.user.pk and not request.user.is_superuser:
        return None, _error(403, "Nie masz uprawnień do tego zadania.")
    return issue, None

def _update_issue(request, issue):

    data = _json_body(request)
    data.setdefault("title", issue.title)
    data.setdefault("description", issue.description)
    data.setdefault("priority", issue.priority)
    data.setdefault("status", issue.status)

    form = TaskUpdateForm(data)
    if not form.is_valid():
        return _error(400, errors=dict(form.errors))

    for field in ("title", "description", "priority"):
        setattr(issue, field, form.cleaned_data[field])
    if form.cleaned_data["status"] is not None:
        issue.status = form.cleaned_data["status"]
    issue.save()
    return JsonResponse(_serialize_issue(issue))

@require_http_methods(["DELETE", "PUT", "PATCH"])
def task_detail(request, issue_id):
    if not request.user.is_authenticated:
        return _unauthorized()

    issue, denied = _get_task_for_user(request, issue_id)
    if denied:
        return denied

    if request.method == "DELETE":
        title = issue.title
        issue.delete()
        return JsonResponse({"detail": f"Usunięto zadanie „{title}”."})
    return _update_issue(request, issue)

def _require_superuser(request):
    if not request.user.is_authenticated:
        return _unauthorized()
    if not request.user.is_superuser:
        return _forbidden()
    return None

@require_http_methods(["GET", "POST"])
def admin_users(request):
    denied = _require_superuser(request)
    if denied:
        return denied

    if request.method == "GET":
        users = [
            {
                "id": user.pk,
                "username": user.username,
                "email": user.email,
                "is_active": user.is_active,
                "is_superuser": user.is_superuser,
                "date_joined": user.date_joined.isoformat(),
                "tasks_count": user.issues.count(),
            }
            for user in User.objects.order_by("username")
        ]
        return JsonResponse({"users": users})

    data = _json_body(request)
    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip()
    if not username or not email or "@" not in email:
        return _error(400, "Podaj poprawną nazwę użytkownika i e-mail.")

    status, payload = _create_account_with_code(username, email)
    return JsonResponse(payload, status=status)

@require_http_methods(["DELETE"])
def admin_user_delete(request, user_id):
    denied = _require_superuser(request)
    if denied:
        return denied

    target = User.objects.filter(pk=user_id).first()
    if target is None:
        return _error(404, "Nie znaleziono użytkownika.")

    if target.pk == request.user.pk:
        return _error(400, "Nie możesz usunąć własnego konta.")
    if target.is_superuser:
        return _error(400, "Nie można usunąć konta administratora.")

    username = target.username
    target.delete()
    return JsonResponse({"detail": f"Usunięto użytkownika „{username}”."})

MAX_AVATAR_SIZE_MB = 5

@require_http_methods(["GET", "POST"])
def profile(request):
    if not request.user.is_authenticated:
        return _unauthorized()

    profile_obj, _created = Profile.objects.get_or_create(user=request.user)

    if request.method == "GET":
        return JsonResponse(
            {
                "username": request.user.username,
                "email": request.user.email,
                "avatar": profile_obj.avatar.url if profile_obj.avatar else None,
            }
        )

    avatar = request.FILES.get("avatar")
    if avatar is None:
        return _error(400, "Wybierz plik ze zdjęciem.")
    if avatar.size > MAX_AVATAR_SIZE_MB * 1024 * 1024:
        return _error(400, f"Plik jest za duży (maksymalnie {MAX_AVATAR_SIZE_MB} MB).")

    extension = (
        avatar.name.rsplit(".", 1)[-1].lower() if "." in avatar.name else ""
    )
    if extension not in Profile.ALLOWED_AVATAR_EXTENSIONS:
        return _error(400, "Dozwolone formaty: JPG, PNG, GIF, WEBP.")

    if profile_obj.avatar:
        profile_obj.avatar.delete(save=False)
    profile_obj.avatar = avatar
    profile_obj.save()
    return JsonResponse(
        {"detail": "Zdjęcie profilowe zostało zaktualizowane.", "avatar": profile_obj.avatar.url}
    )
