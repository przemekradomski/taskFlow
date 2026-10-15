export const STATUS_ORDER = ["To Do", "In Progress", "Done"];

export const STATUS_LABELS = {
  "To Do": "Do zrobienia",
  "In Progress": "W trakcie",
  Done: "Gotowe",
};

export const PRIORITY_LABELS = {
  Low: "Niska",
  Medium: "Średnia",
  High: "Wysoka",
  Urgent: "Pilna",
};

function getCookie(name) {
  const match = document.cookie.match(
    new RegExp(`(?:^|;\\s*)${name}=([^;]*)`)
  );
  return match ? decodeURIComponent(match[1]) : "";
}

export async function apiFetch(url, options = {}) {
  const opts = {
    credentials: "same-origin",
    ...options,
  };
  opts.headers = {
    "X-Requested-With": "XMLHttpRequest",
    ...(options.headers || {}),
  };

  if (options.body && !(options.body instanceof FormData)) {
    opts.headers["Content-Type"] = "application/json";
    opts.body = JSON.stringify(options.body);
  }
  if (opts.method && opts.method !== "GET" && opts.method !== "HEAD") {
    opts.headers["X-CSRFToken"] = getCookie("csrftoken");
  }

  const response = await fetch(url, opts);
  let data = {};
  if (response.status !== 204) {
    data = await response.json().catch(() => ({}));
  }
  if (!response.ok) {
    const error = new Error(data.detail || "Błąd połączenia z serwerem.");
    error.status = response.status;
    error.data = data;
    throw error;
  }
  return data;
}

export function formatDate(isoDate) {
  return new Date(isoDate).toLocaleString("pl-PL", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}
