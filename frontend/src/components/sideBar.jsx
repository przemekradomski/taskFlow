export default function SideBar({ selectedFilter, onFilterChange }) {
  return (
    <aside className="sidebar d-flex flex-column gap-2 p-3" aria-label="Filtry zadań">
      <button
        className="sidebar-filter"
        type="button"
        aria-pressed={selectedFilter === "all"}
        onClick={() => onFilterChange("all")}
      >
        Dla ciebie
      </button>
      <button
        className="sidebar-filter"
        type="button"
        aria-pressed={selectedFilter === "created_at"}
        onClick={() => onFilterChange("created_at")}
      >
        Ostatnie
      </button>
      <button
        className="sidebar-filter"
        type="button"
        aria-pressed={selectedFilter === "urgent"}
        onClick={() => onFilterChange("urgent")}
      >
        Pilne
      </button>
    </aside>
  );
}