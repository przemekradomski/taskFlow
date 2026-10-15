import { Navigate } from "react-router-dom";
import { useAuth } from "../auth.jsx";

export default function RequireAuth({ admin = false, children }) {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="d-flex vh-100 align-items-center justify-content-center">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Ładowanie...</span>
        </div>
      </div>
    );
  }
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  if (admin && !user.is_superuser) {
    return <Navigate to="/" replace />;
  }
  return children;
}
