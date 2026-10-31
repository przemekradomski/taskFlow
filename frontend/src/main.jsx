import { createRoot } from "react-dom/client";
import { useState } from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import "bootstrap/dist/css/bootstrap.min.css";
import "./styles.css";
import { AuthProvider, useAuth } from "./auth.jsx";
import Navbar from "./components/Navbar.jsx";
import RequireAuth from "./components/RequireAuth.jsx";
import Login from "./pages/Login.jsx";
import FirstLogin from "./pages/FirstLogin.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import Profile from "./pages/Profile.jsx";
import Admin from "./pages/Admin.jsx";
import SideBar from "./components/sideBar.jsx";

if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("/serviceworker.js").catch((error) => {
    console.error("Nie udało się zarejestrować service workera:", error);
  });
}

function App() {
  const { user, loading } = useAuth();
  const [selectedFilter, setSelectedFilter] = useState("all");

  if (loading) {
    return (
      <div className="d-flex vh-100 align-items-center justify-content-center">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Ładowanie...</span>
        </div>
      </div>
    );
  }

  return (
    <BrowserRouter>
      <div className="app-shell">
        {user && <Navbar />}
        <div className="app-content">
          {user && (
            <SideBar
              selectedFilter={selectedFilter}
              onFilterChange={setSelectedFilter}
            />
          )}
          <main className="app-main">
            <Routes>
              <Route path="/login" element={user ? <Navigate to="/" replace /> : <Login />} />
              <Route
                path="/pierwsze-logowanie"
                element={user ? <Navigate to="/" replace /> : <FirstLogin />}
              />
              <Route
                path="/"
                element={
                  <RequireAuth>
                    <Dashboard selectedFilter={selectedFilter} />
                  </RequireAuth>
                }
              />
              <Route
                path="/profil"
                element={
                  <RequireAuth>
                    <Profile />
                  </RequireAuth>
                }
              />
              <Route
                path="/panel-admina"
                element={
                  <RequireAuth admin>
                    <Admin />
                  </RequireAuth>
                }
              />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
        </div>
      </div>
    </BrowserRouter>
  );
}

createRoot(document.getElementById("root")).render(
  <AuthProvider>
    <App />
  </AuthProvider>
);
