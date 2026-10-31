import { useCallback, useEffect, useState } from "react";
import { apiFetch, STATUS_LABELS, STATUS_ORDER } from "../api.js";
import TaskFormModal from "../components/TaskFormModal.jsx";
import TaskItem from "../components/TaskItem.jsx";

const COUNT_FIELDS = {
  "To Do": "to_do",
  "In Progress": "in_progress",
  Done: "done",
};

export default function Dashboard({ selectedFilter }) {
  const [tasks, setTasks] = useState([]);
  const [counts, setCounts] = useState({ to_do: 0, in_progress: 0, done: 0, total: 0 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [editingTask, setEditingTask] = useState(null);
  const loadTasks = useCallback(async () => {
    try {
      const data = await apiFetch("/api/tasks/");
      setTasks(data.tasks || []);
      setCounts(data.counts || { to_do: 0, in_progress: 0, done: 0, total: 0 });
      setError("");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadTasks();
  }, [loadTasks]);

  const deleteTask = async (task) => {
    if (!window.confirm(`Usunąć zadanie „${task.title}”?`)) return;
    try {
      await apiFetch(`/api/tasks/${task.id}/`, { method: "DELETE" });
      await loadTasks();
    } catch (err) {
      setError(err.message);
    }
  };

  const filteredTasks =
    selectedFilter === "all"
      ? tasks
      : selectedFilter === "urgent"
        ? tasks.filter((task) => task.priority?.toLowerCase() === "urgent")
        : selectedFilter === "created_at"
          ? [...tasks].sort(
              (a, b) => new Date(b.created_at) - new Date(a.created_at)
            )
          : tasks;

  return (
    <>
      <div className="d-flex flex-wrap justify-content-between align-items-end mb-4 gap-3">
        <div>
          <p className="eyebrow mb-1">Workspace</p>
          <h1 className="h2 mb-1">TaskFlow</h1>
          <p className="text-body-secondary mb-0">
            Witamy w systemie TaskFlow. Tutaj możesz zarządzać swoimi zadaniami i projektami.
          </p>
        </div>
        <div className="d-flex align-items-center gap-3">
          <div className="card stat-card-total text-center px-4 py-2 mb-0">
            <small className="text-body-secondary">Wszystkie zadania</small>
            <h2 className="h3 mb-0">{counts.total}</h2>
          </div>
          <button
            className="btn btn-primary"
            type="button"
            onClick={() => {
              setEditingTask(null);
              setShowModal(true);
            }}
          >
            + Nowe zadanie
          </button>
        </div>
      </div>

      {error && <div className="alert alert-danger">{error}</div>}

      {loading ? (
        <div className="d-flex justify-content-center py-5">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Ładowanie...</span>
          </div>
        </div>
      ) : (
        <div className="row g-3">
          {STATUS_ORDER.map((status) => {
            const groupTasks = filteredTasks.filter((task) => task.status === status);
            return (
              <div className="col-12 col-lg-4" key={status}>
                <div className="card stat-card h-100">
                  <div className="d-flex justify-content-between align-items-center mb-3">
                    <span className="fw-semibold">{STATUS_LABELS[status]}</span>
                    <span className="badge text-bg-primary rounded-pill">
                      {selectedFilter === "all"
                        ? counts[COUNT_FIELDS[status]] ?? groupTasks.length
                        : groupTasks.length}
                    </span>
                  </div>
                  <div className="d-flex flex-column gap-2">
                    {groupTasks.length === 0 && (
                      <p className="text-body-secondary mb-0">Brak zadań.</p>
                    )}
                    {groupTasks.map((task) => (
                      <TaskItem
                        key={task.id}
                        task={task}
                        onEdit={(edited) => {
                          setEditingTask(edited);
                          setShowModal(true);
                        }}
                        onDelete={deleteTask}
                      />
                    ))}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      <TaskFormModal
        show={showModal}
        task={editingTask}
        onClose={() => {
          setShowModal(false);
          setEditingTask(null);
        }}
        onSaved={async () => {
          setShowModal(false);
          setEditingTask(null);
          await loadTasks();
        }}
      />
    </>
  );
}
