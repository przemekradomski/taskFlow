import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../auth.jsx";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      await login({ username, password });
      navigate("/");
    } catch (err) {
      if (err.status === 403 && err.data?.first_login) {
        setError(err.message);
      } else {
        setError(err.message);
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <section className="row justify-content-center">
      <div className="col-12 col-md-6 col-lg-5">
        <div className="card auth-card p-4">
          <p className="eyebrow">TaskFlow</p>
          <h1 className="h3 mb-3">Zaloguj się</h1>

          {error && <div className="alert alert-danger py-2">{error}</div>}

          <form onSubmit={handleSubmit} noValidate>
            <div className="mb-3">
              <label htmlFor="id_username" className="form-label">
                Nazwa użytkownika
              </label>
              <input
                type="text"
                id="id_username"
                className="form-control"
                maxLength={150}
                required
                autoFocus
                value={username}
                onChange={(e) => setUsername(e.target.value)}
              />
            </div>
            <div className="mb-3">
              <label htmlFor="id_password" className="form-label">
                Hasło
              </label>
              <input
                type="password"
                id="id_password"
                className="form-control"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
            <button type="submit" className="btn btn-primary w-100" disabled={submitting}>
              {submitting ? "Logowanie..." : "Zaloguj się"}
            </button>
          </form>

          <p className="text-body-secondary mt-3 mb-0">
            Pierwsze logowanie (kod z maila)?{" "}
            <Link to="/pierwsze-logowanie">Aktywuj konto</Link>
          </p>
        </div>
      </div>
    </section>
  );
}
