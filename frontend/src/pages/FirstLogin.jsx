import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { apiFetch } from "../api.js";
import { useAuth } from "../auth.jsx";

export default function FirstLogin() {
  const { refresh } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    username: "",
    code: "",
    password1: "",
    password2: "",
  });
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const update = (field) => (event) =>
    setForm((prev) => ({ ...prev, [field]: event.target.value }));

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      await apiFetch("/api/auth/first-login/", { method: "POST", body: form });
      await refresh();
      navigate("/");
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <section className="row justify-content-center">
      <div className="col-12 col-md-6 col-lg-5">
        <div className="card auth-card p-4">
          <p className="eyebrow">TaskFlow / Aktywacja</p>
          <h1 className="h3 mb-2">Pierwsze logowanie</h1>
          <p className="text-body-secondary">
            Podaj kod weryfikacyjny wysłany na Twój adres e-mail oraz ustaw swoje hasło.
          </p>

          {error && <div className="alert alert-danger py-2">{error}</div>}

          <form onSubmit={handleSubmit} noValidate>
            <div className="mb-3">
              <label htmlFor="id_username" className="form-label">Nazwa użytkownika</label>
              <input
                type="text" id="id_username" className="form-control"
                maxLength={150} required autoFocus
                value={form.username} onChange={update("username")}
              />
            </div>
            <div className="mb-3">
              <label htmlFor="id_code" className="form-label">Kod weryfikacyjny</label>
              <input
                type="text" id="id_code" className="form-control"
                maxLength={12} required inputMode="numeric"
                value={form.code} onChange={update("code")}
              />
            </div>
            <div className="mb-3">
              <label htmlFor="id_password1" className="form-label">Nowe hasło</label>
              <input
                type="password" id="id_password1" className="form-control" required
                value={form.password1} onChange={update("password1")}
              />
            </div>
            <div className="mb-3">
              <label htmlFor="id_password2" className="form-label">Powtórz hasło</label>
              <input
                type="password" id="id_password2" className="form-control" required
                value={form.password2} onChange={update("password2")}
              />
            </div>
            <button type="submit" className="btn btn-primary w-100" disabled={submitting}>
              {submitting ? "Aktywacja..." : "Aktywuj konto"}
            </button>
          </form>

          <p className="text-body-secondary mt-3 mb-0">
            Masz już hasło? <Link to="/login">Zaloguj się</Link>
          </p>
        </div>
      </div>
    </section>
  );
}
