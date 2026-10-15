import json

from django.contrib.auth.models import User
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase

from taskFlow.models import Issue, Profile

def _request_json(client, method, url, payload):
    return client.generic(
        method,
        url,
        data=json.dumps(payload),
        content_type="application/json",
    )

def post_json(client, url, payload):
    return _request_json(client, "POST", url, payload)

def put_json(client, url, payload):
    return _request_json(client, "PUT", url, payload)

class TaskFlowBackendTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            "testadmin", "admin@example.com", "AdminPass123!"
        )
        self.admin_client = Client()
        self.admin_client.force_login(self.admin)

    def test_hasher_uses_sha512(self):
        self.admin.refresh_from_db()
        self.assertTrue(self.admin.password.startswith("sha512$"))

    def test_admin_creates_account_and_sends_code(self):
        mail.outbox = []
        response = post_json(
            self.admin_client,
            "/api/admin/users/",
            {"username": "testuser", "email": "user@example.com"},
        )
        self.assertEqual(response.status_code, 201)

        user = User.objects.get(username="testuser")
        self.assertFalse(user.is_active)
        self.assertFalse(user.has_usable_password())

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("user@example.com", mail.outbox[0].to)
        code = self._extract_code()
        self.assertRegex(code, r"^\d{6}$")

        mail.outbox = []
        response = post_json(
            self.admin_client,
            "/api/admin/users/",
            {"username": "testuser", "email": "user@example.com"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        self.assertNotEqual(
            self._extract_code(), code, "nowy kod musi być inny"
        )

    def test_first_login_activates_account(self):
        mail.outbox = []
        post_json(
            self.admin_client,
            "/api/admin/users/",
            {"username": "testuser", "email": "user@example.com"},
        )
        code = self._extract_code()

        client = Client()
        response = post_json(
            client,
            "/api/auth/first-login/",
            {
                "username": "testuser",
                "code": code,
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
        )
        self.assertEqual(response.status_code, 200)

        user = User.objects.get(username="testuser")
        self.assertTrue(user.is_active)
        self.assertTrue(user.has_usable_password())
        self.assertTrue(user.password.startswith("sha512$"))
        self.assertIsNotNone(user.verification.used_at)

    def test_first_login_rejects_wrong_code(self):
        mail.outbox = []
        post_json(
            self.admin_client,
            "/api/admin/users/",
            {"username": "testuser", "email": "user@example.com"},
        )
        client = Client()
        response = post_json(
            client,
            "/api/auth/first-login/",
            {
                "username": "testuser",
                "code": "000000",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(User.objects.get(username="testuser").is_active)

    def test_login_with_password(self):
        mail.outbox = []
        post_json(
            self.admin_client,
            "/api/admin/users/",
            {"username": "testuser", "email": "user@example.com"},
        )
        code = self._extract_code()
        client = Client()
        post_json(
            client,
            "/api/auth/first-login/",
            {
                "username": "testuser",
                "code": code,
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
        )

        fresh = Client()
        response = post_json(
            fresh,
            "/api/auth/login/",
            {"username": "testuser", "password": "WrongPass1!"},
        )
        self.assertEqual(response.status_code, 400)

        client = Client()
        response = post_json(
            client,
            "/api/auth/login/",
            {"username": "testuser", "password": "StrongPass123!"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["user"]["username"], "testuser")

    def test_task_is_assigned_to_creator(self):
        user = User.objects.create_user("testuser", password="StrongPass123!")
        client = Client()
        client.force_login(user)

        response = post_json(
            client,
            "/api/tasks/",
            {"title": "Zadanie testowe", "description": "opis", "priority": "low"},
        )
        self.assertEqual(response.status_code, 201)

        issue = Issue.objects.get(title="Zadanie testowe")
        self.assertEqual(issue.created_by, user)
        self.assertEqual(issue.priority, "Low")

    def test_tasks_api_visibility_and_counts(self):
        user = User.objects.create_user("testuser", password="StrongPass123!")
        client = Client()
        client.force_login(user)
        Issue.objects.create(title="Nowe", created_by=user)

        response = client.get("/api/tasks/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["tasks"][0]["title"], "Nowe")
        self.assertEqual(data["tasks"][0]["owner"], "testuser")
        self.assertEqual(data["counts"]["total"], 1)
        self.assertEqual(data["counts"]["to_do"], 1)

        other = User.objects.create_user("other", password="StrongPass123!")
        other_client = Client()
        other_client.force_login(other)
        response = other_client.get("/api/tasks/")
        self.assertEqual(response.json()["tasks"], [])
        self.assertEqual(response.json()["counts"]["total"], 0)

    def test_sql_injection_stays_as_plain_text(self):
        user = User.objects.create_user("testuser", password="StrongPass123!")
        client = Client()
        client.force_login(user)
        payload = "'; DROP TABLE taskFlow_issue;--"
        response = post_json(
            client,
            "/api/tasks/",
            {"title": payload, "description": "x", "priority": "high"},
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Issue.objects.filter(title=payload).exists())
        self.assertEqual(Issue.objects.count(), 1)

    def test_update_task_by_owner(self):
        user = User.objects.create_user("testuser", password="StrongPass123!")
        issue = Issue.objects.create(
            title="Do edycji", description="opis", priority="Medium", created_by=user
        )
        client = Client()
        client.force_login(user)

        response = put_json(
            client,
            f"/api/tasks/{issue.pk}/",
            {
                "title": "Po edycji",
                "description": "nowy opis",
                "priority": "high",
                "status": "done",
            },
        )
        self.assertEqual(response.status_code, 200)

        issue.refresh_from_db()
        self.assertEqual(issue.title, "Po edycji")
        self.assertEqual(issue.description, "nowy opis")
        self.assertEqual(issue.priority, "High")
        self.assertEqual(issue.status, "Done")

    def test_update_task_partial_keeps_missing_fields(self):
        user = User.objects.create_user("testuser", password="StrongPass123!")
        issue = Issue.objects.create(
            title="Tytuł", description="opis", priority="Urgent", created_by=user
        )
        client = Client()
        client.force_login(user)

        response = put_json(client, f"/api/tasks/{issue.pk}/", {"status": "In Progress"})
        self.assertEqual(response.status_code, 200)

        issue.refresh_from_db()
        self.assertEqual(issue.title, "Tytuł")
        self.assertEqual(issue.priority, "Urgent")
        self.assertEqual(issue.status, "In Progress")

    def test_update_task_forbidden_for_other_user(self):
        owner = User.objects.create_user("owner", password="StrongPass123!")
        other = User.objects.create_user("other", password="StrongPass123!")
        issue = Issue.objects.create(title="Cudze", created_by=owner)

        client = Client()
        client.force_login(other)
        response = put_json(client, f"/api/tasks/{issue.pk}/", {"title": "hack"})
        self.assertEqual(response.status_code, 403)

        issue.refresh_from_db()
        self.assertEqual(issue.title, "Cudze")

    def test_update_task_rejects_invalid_status(self):
        user = User.objects.create_user("testuser", password="StrongPass123!")
        issue = Issue.objects.create(title="Zadanie", created_by=user)
        client = Client()
        client.force_login(user)

        response = put_json(
            client, f"/api/tasks/{issue.pk}/", {"status": "Nie Wiem"}
        )
        self.assertEqual(response.status_code, 400)

    def test_admin_lists_and_deletes_users(self):
        user = User.objects.create_user("testuser", password="StrongPass123!")
        Issue.objects.create(title="Zadanie", created_by=user)

        response = self.admin_client.get("/api/admin/users/")
        self.assertEqual(response.status_code, 200)
        usernames = [u["username"] for u in response.json()["users"]]
        self.assertIn("testuser", usernames)

        response = self.admin_client.delete(f"/api/admin/users/{user.pk}/")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="testuser").exists())

    def test_admin_cannot_delete_self_or_superusers(self):
        response = self.admin_client.delete(f"/api/admin/users/{self.admin.pk}/")
        self.assertEqual(response.status_code, 400)
        self.assertTrue(User.objects.filter(username="testadmin").exists())

    def test_anonymous_cannot_access_protected_views(self):
        client = Client()
        self.assertEqual(client.get("/api/tasks/").status_code, 401)
        self.assertEqual(client.get("/api/admin/users/").status_code, 401)

        user = User.objects.create_user("testuser", password="StrongPass123!")
        client.force_login(user)
        self.assertEqual(client.get("/api/admin/users/").status_code, 403)

    def test_delete_task_by_owner(self):
        user = User.objects.create_user("testuser", password="StrongPass123!")
        issue = Issue.objects.create(title="Do usunicia", created_by=user)
        client = Client()
        client.force_login(user)

        response = client.delete(f"/api/tasks/{issue.pk}/")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Issue.objects.filter(pk=issue.pk).exists())

    def test_delete_task_forbidden_for_other_user(self):
        owner = User.objects.create_user("owner", password="StrongPass123!")
        other = User.objects.create_user("other", password="StrongPass123!")
        issue = Issue.objects.create(title="Cudze", created_by=owner)

        client = Client()
        client.force_login(other)
        response = client.delete(f"/api/tasks/{issue.pk}/")
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Issue.objects.filter(pk=issue.pk).exists())

    def test_admin_can_delete_any_task(self):
        owner = User.objects.create_user("owner", password="StrongPass123!")
        issue = Issue.objects.create(title="Zadanie", created_by=owner)

        response = self.admin_client.delete(f"/api/tasks/{issue.pk}/")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Issue.objects.filter(pk=issue.pk).exists())

    def test_delete_task_requires_login(self):
        owner = User.objects.create_user("owner", password="StrongPass123!")
        issue = Issue.objects.create(title="Zadanie", created_by=owner)

        client = Client()
        response = client.delete(f"/api/tasks/{issue.pk}/")
        self.assertEqual(response.status_code, 401)
        self.assertTrue(Issue.objects.filter(pk=issue.pk).exists())

    def test_avatar_upload_and_me_endpoint(self):
        user = User.objects.create_user("testuser", password="StrongPass123!")
        client = Client()
        client.force_login(user)

        response = client.get("/api/me/")
        data = response.json()
        self.assertTrue(data["authenticated"])
        self.assertIsNone(data["user"]["avatar"])

        avatar = SimpleUploadedFile(
            "avatar.png", b"fake-image-bytes", content_type="image/png"
        )
        response = client.post("/api/profile/", {"avatar": avatar})
        self.assertEqual(response.status_code, 200)

        profile = Profile.objects.get(user=user)
        self.assertTrue(profile.avatar)
        response = client.get("/api/me/")
        self.assertEqual(response.json()["user"]["avatar"], profile.avatar.url)

        bad = SimpleUploadedFile(
            "hack.exe", b"xx", content_type="application/octet-stream"
        )
        response = client.post("/api/profile/", {"avatar": bad})
        self.assertEqual(response.status_code, 400)
        profile.refresh_from_db()
        self.assertTrue(profile.avatar.name.endswith(".png"))

    def test_spa_serves_react_app_for_all_page_paths(self):
        client = Client()
        for url in ("/", "/login/", "/panel-admina/", "/profil/"):
            response = client.get(url)
            self.assertEqual(response.status_code, 200, url)
            self.assertContains(response, '<div id="root"></div>')

    def _extract_code(self):
        for line in mail.outbox[0].body.splitlines():
            if "kod weryfikacyjny do pierwszego logowania:" in line:
                return line.rsplit(": ", 1)[1].strip()
        self.fail("Kod nie został znaleziony w mailu")
