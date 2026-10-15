import { useCallback, useEffect, useState } from "react";
import { apiFetch } from "../api.js";
import { useAuth } from "../auth.jsx";

export default function Admin() {
  const { user } = useAuth();
  const [users, setUsers] = useState([]);
  const [form, setForm] = useState({ username: "", email: "" });
  const [message, setMessage] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [loading, setLoading] = useState(true);

  const loadUsers = useCallback(async () => {
    try {
      const data = await apiFetch("/api/admin/users/");
      setUsers(data.users || []);
    } catch (err) {
      setMessage({ type: "danger", text: err.message });
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadUsers();
  }, [loadUsers]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setMessage(null);
    setSubmitting(true);
    try {
      const data = await apiFetch("/api/admin/users/", { method: "POST", body: form });
      const parts = [data.detail];
      if (data.dev_code) {
        parts.push(`Tryb dev (SMTP nieskonfigurowany) - kod: ${data.dev_code}`);
      }
      setMessage({ type: "success", text: parts.join(" ") });
      setForm({ username: "", email: "" });
      await loadUsers();
    } catch (err) {
      setMessage({ type: "danger", text: err.message });
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (target) => {
    if (!window.confirm(`Usunąć użytkownika ${target.username}?`)) return;
    try {
      const data = await apiFetch(`/api/admin/users/${target.id}/`, { method: "DELETE" });
      setMessage({ type: "success", text: data.detail });
      await loadUsers();
    } catch (err) {
      setMessage({ type: "danger", text: err.message });
    }
  };

  return (
    <>
      <div className="mb-4">
        <p className="eyebrow mb-1">TaskFlow / Admin</p>
        <h1 className="h2 mb-1">Panel administratora</h1>
        <p className="text-body-secondary mb-0">Zarządzanie kontami użytkowników.</p>
      </div>

      {message && (
        <div className={`alert alert-${message.type}`}>{message.text}</div>
      )}

      <div className="card p-4 mb-4">
        <h2 className="h5 mb-1">Utwórz konto użytkownika</h2>
        <p className="text-body-secondary">
          Użytkownik otrzyma na maila kod weryfikacyjny, a przy pierwszym logowaniu
          sam ustawi swoje hasło.
        </p>
        <form onSubmit={handleSubmit} className="row g-3 align-items-end" noValidate>
          <div className="col-12 col-md-4">
            <label htmlFor="id_username" className="form-label">Nazwa użytkownika</label>
            <input
              type="text" id="id_username" className="form-control" maxLength={150} required
              value={form.username}
              onChange={(e) => setForm((prev) => ({ ...prev, username: e.target.value }))}
            />
          </div>
          <div className="col-12 col-md-4">
            <label htmlFor="id_email" className="form-label">Adres e-mail</label>
            <input
              type="email" id="id_email" className="form-control" required
              value={form.email}
              onChange={(e) => setForm((prev) => ({ ...prev, email: e.target.value }))}
            />
          </div>
          <div className="col-12 col-md-4">
            <button type="submit" className="btn btn-primary w-100" disabled={submitting}>
              {submitting ? "Tworzenie..." : "Utwórz konto"}
            </button>
          </div>
        </form>
      </div>

      <div className="card p-4">
        <h2 className="h5 mb-3">Użytkownicy</h2>
        <div className="table-responsive">
          <table className="table table-dark table-hover align-middle mb-0">
            <thead>
              <tr>
                <th>Nazwa użytkownika</th>
                <th>E-mail</th>
                <th>Status</th>
                <th>Zadania</th>
                <th>Akcje</th>
              </tr>
            </thead>
            <tbody>
              {users.length === 0 && !loading && (
                <tr>
                  <td colSpan={5} className="text-body-secondary">Brak użytkowników.</td>
                </tr>
              )}
              {users.map((target) => {
                const canDelete =
                  !target.is_superuser && target.id !== user?.id;
                return (
                  <tr key={target.id}>
                    <td>
                      <strong>{target.username}</strong>
                      {target.is_superuser && <span className="text-body-secondary"> (admin)</span>}
                    </td>
                    <td>{target.email || "—"}</td>
                    <td>
                      {target.is_active ? (
                        <span className="badge text-bg-success">Aktywny</span>
                      ) : (
                        <span className="badge text-bg-warning">Oczekuje na kod</span>
                      )}
                    </td>
                    <td>{target.tasks_count}</td>
                    <td>
                      {canDelete ? (
                        <button
                          type="button"
                          className="btn btn-sm btn-outline-danger"
                          onClick={() => handleDelete(target)}
                        >
                          Usuń
                        </button>
                      ) : (
                        <span className="text-body-secondary">—</span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}
