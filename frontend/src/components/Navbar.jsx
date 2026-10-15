import { Link, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../auth.jsx";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  return (
    <nav className="navbar navbar-expand-lg navbar-dark border-bottom app-navbar">
      <div className="container-xxl">
        <Link className="navbar-brand fw-bold" to="/">
          <span className="brand-accent">Task</span>Flow
        </Link>
        <ul className="navbar-nav flex-row gap-2 me-auto">
          <li className="nav-item">
            <NavLink className={({ isActive }) => "nav-link" + (isActive ? " active" : "")} to="/" end>
              Dashboard
            </NavLink>
          </li>
          {user?.is_superuser && (
            <li className="nav-item">
              <NavLink className={({ isActive }) => "nav-link" + (isActive ? " active" : "")} to="/panel-admina">
                Panel admina
              </NavLink>
            </li>
          )}
        </ul>
        <div className="d-flex align-items-center gap-2">
          <Link to="/profil" title="Twój profil" className="nav-profile">
            {user?.avatar ? (
              <img className="avatar" src={user.avatar} alt={`Zdjęcie profilowe ${user.username}`} />
            ) : (
              <span className="avatar avatar-fallback">
                {user?.username?.charAt(0).toUpperCase()}
              </span>
            )}
          </Link>
          <span className="nav-username d-none d-sm-inline">{user?.username}</span>
          <button type="button" className="btn btn-sm btn-outline-secondary" onClick={handleLogout}>
            Wyloguj
          </button>
        </div>
      </div>
    </nav>
  );
}
