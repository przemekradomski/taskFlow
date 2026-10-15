import { useCallback, useEffect, useState } from "react";
import { apiFetch } from "../api.js";
import { useAuth } from "../auth.jsx";

export default function Profile() {
  const { user, refresh } = useAuth();
  const [avatar, setAvatar] = useState(null);
  const [message, setMessage] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const loadProfile = useCallback(async () => {
    try {
      const data = await apiFetch("/api/profile/");
      setAvatar(data.avatar);
    } catch (err) {
      setMessage({ type: "danger", text: err.message });
    }
  }, []);

  useEffect(() => {
    loadProfile();
  }, [loadProfile]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    const file = event.target.elements.avatar.files[0];
    setMessage(null);
    setSubmitting(true);
    try {
      const formData = new FormData();
      formData.append("avatar", file);
      const data = await apiFetch("/api/profile/", { method: "POST", body: formData });
      setMessage({ type: "success", text: data.detail });
      await Promise.all([loadProfile(), refresh()]);
    } catch (err) {
      setMessage({ type: "danger", text: err.message });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <section className="row justify-content-center">
      <div className="col-12 col-lg-7">
        <div className="card p-4">
          <div className="d-flex align-items-center gap-3 mb-4">
            {avatar ? (
              <img className="avatar avatar-big" src={avatar} alt="Zdjęcie profilowe" />
            ) : (
              <span className="avatar avatar-big avatar-fallback">
                {user?.username?.charAt(0).toUpperCase()}
              </span>
            )}
            <div>
              <p className="eyebrow mb-1">TaskFlow / Profil</p>
              <h1 className="h3 mb-0">{user?.username}</h1>
              <p className="text-body-secondary mb-0">{user?.email || "Brak adresu e-mail"}</p>
            </div>
          </div>

          {message && (
            <div className={`alert alert-${message.type} py-2`}>{message.text}</div>
          )}

          <form onSubmit={handleSubmit}>
            <div className="mb-3">
              <label htmlFor="id_avatar" className="form-label">
                Zdjęcie profilowe (JPG, PNG, GIF, WEBP, maks. 5 MB)
              </label>
              <input type="file" name="avatar" id="id_avatar" className="form-control" accept="image/*" />
            </div>
            <button type="submit" className="btn btn-primary" disabled={submitting}>
              {submitting ? "Wgrywanie..." : "Wgraj zdjęcie"}
            </button>
          </form>
        </div>
      </div>
    </section>
  );
}
