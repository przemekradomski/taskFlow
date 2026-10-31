export default function SideBar() {
  return (
    <aside className="sidebar d-flex flex-column gap-2 p-3" aria-label="Filtry zadań">
      <span>Dla ciebie</span>
      <span>Ostatnie</span>
      <span>Pilne</span>
      <span>Filtry</span>
    </aside>
  );
}