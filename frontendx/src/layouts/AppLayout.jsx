import Sidebar from "../components/Sidebar";
import { Outlet } from "react-router-dom";
import ProfileMenu from "../components/ProfileMenu";

export default function AppLayout({ handleLogout, user }) {
  return (
    <div className="flex min-h-screen">
      {/* Sidebar */}
      <Sidebar />

      {/* Main Content */}
      <div className="flex-1 flex flex-col bg-[#061328]">
        {/* Top Bar */}
        <header className="h-14 flex items-center justify-end px-6 border-b border-[#233554]">
          <ProfileMenu user={user} onLogout={handleLogout} />
        </header>

        {/* Page Content */}
        <main className="flex-1">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
