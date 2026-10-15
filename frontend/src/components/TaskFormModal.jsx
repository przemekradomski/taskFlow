import { useEffect, useState } from "react";
import { apiFetch, PRIORITY_LABELS, STATUS_LABELS } from "../api.js";

const PRIORITIES = ["low", "medium", "high", "urgent"];
const STATUSES = ["To Do", "In Progress", "Done"];

const lower = (value) => (value ? value.toLowerCase() : "");

export default function TaskFormModal({ show, task = null, onClose, onSaved }) {
  const isEdit = Boolean(task);
  const [form, setForm] = useState({ title: "", description: "", priority: "medium", status: "to do" });
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (show) {
      setForm(
        isEdit
          ? {
              title: task.title || "",
              description: task.description || "",
              priority: lower(task.priority) || "medium",
              status: lower(task.status) || "to do",
            }
          : { title: "", description: "", priority: "medium", status: "to do" }
      );
      setError("");
    }
  }, [show, isEdit, task]);

  useEffect(() => {
    const onKeyDown = (event) => {
      if (event.key === "Escape" && show) onClose();
    };
    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, [show, onClose]);

  if (!show) return null;

  const update = (field) => (event) =>
    setForm((prev) => ({ ...prev, [field]: event.target.value }));

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      const data = isEdit
        ? await apiFetch(`/api/tasks/${task.id}/`, { method: "PUT", body: form })
        : await apiFetch("/api/tasks/", { method: "POST", body: form });
      onSaved(data);
    } catch (err) {
      const fieldErrors = err.data?.errors;
      if (fieldErrors) {
        const first = Object.values(fieldErrors)[0];
        setError(Array.isArray(first) ? first.join(" ") : String(first));
      } else {
        setError(err.message);
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <>
      <div className="modal-backdrop show" onClick={onClose} />
      <div className="modal d-block" tabIndex={-1} role="dialog" onClick={(e) => e.target === e.currentTarget && onClose()}>
        <div className="modal-dialog modal-dialog-centered">
          <div className="modal-content app-modal">
            <div className="modal-header">
              <div>
                <p className="eyebrow mb-1">TaskFlow / Zadania</p>
                <h2 className="h5 mb-0">{isEdit ? "Edytuj zadanie" : "Nowe zadanie"}</h2>
              </div>
              <button type="button" className="btn-close btn-close-white" aria-label="Zamknij" onClick={onClose} />
            </div>
            <form onSubmit={handleSubmit} noValidate>
              <div className="modal-body">
                {error && <div className="alert alert-danger py-2">{error}</div>}
                <div className="mb-3">
                  <label htmlFor="taskTitle" className="form-label">Tytuł zadania</label>
                  <input
                    type="text" id="taskTitle" className="form-control" required autoFocus
                    placeholder="Np. Przygotować stronę startową"
                    value={form.title} onChange={update("title")}
                  />
                </div>
                <div className="mb-3">
                  <label htmlFor="taskDescription" className="form-label">Opis zadania</label>
                  <textarea
                    id="taskDescription" className="form-control" rows={4}
                    placeholder="Opisz, co trzeba zrobić..."
                    value={form.description} onChange={update("description")}
                  />
                </div>
                <div className="mb-3">
                  <label htmlFor="taskPriority" className="form-label">Priorytet</label>
                  <select id="taskPriority" className="form-select" value={form.priority} onChange={update("priority")}>
                    {PRIORITIES.map((value) => (
                      <option key={value} value={value}>
                        {PRIORITY_LABELS[value.charAt(0).toUpperCase() + value.slice(1)]}
                      </option>
                    ))}
                  </select>
                </div>
                {isEdit && (
                  <div className="mb-2">
                    <label htmlFor="taskStatus" className="form-label">Status</label>
                    <select id="taskStatus" className="form-select" value={form.status} onChange={update("status")}>
                      {STATUSES.map((value) => (
                        <option key={value} value={lower(value)}>
                          {STATUS_LABELS[value]}
                        </option>
                      ))}
                    </select>
                  </div>
                )}
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-outline-secondary" onClick={onClose}>
                  Anuluj
                </button>
                <button type="submit" className="btn btn-primary" disabled={submitting}>
                  {submitting ? "Zapisywanie..." : isEdit ? "Zapisz zmiany" : "Utwórz zadanie"}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </>
  );
}
