import { formatDate, PRIORITY_LABELS } from "../api.js";

const PRIORITY_CLASS = {
  Low: "text-bg-secondary",
  Medium: "text-bg-info",
  High: "text-bg-warning",
  Urgent: "text-bg-danger",
};

export default function TaskItem({ task, onEdit, onDelete }) {
  return (
    <div className="task-item">
      <div className="d-flex justify-content-between align-items-start gap-2">
        <strong className="task-item-title">{task.title}</strong>
        <div className="d-flex align-items-center gap-1">
          <span className={`badge ${PRIORITY_CLASS[task.priority] || "text-bg-secondary"}`}>
            {PRIORITY_LABELS[task.priority] || task.priority}
          </span>
          <button
            type="button"
            className="btn-icon-ghost"
            title={`Edytuj zadanie ${task.title}`}
            aria-label={`Edytuj zadanie ${task.title}`}
            onClick={() => onEdit(task)}
          >
            ✎
          </button>
          <button
            type="button"
            className="btn-close btn-close-white small"
            title={`Usuń zadanie ${task.title}`}
            aria-label={`Usuń zadanie ${task.title}`}
            onClick={() => onDelete(task)}
          />
        </div>
      </div>
      {task.description && <p className="task-item-desc mb-1">{task.description}</p>}
      <small className="text-body-secondary">{formatDate(task.created_at)}</small>
    </div>
  );
}
