import { Link, useLocation } from "react-router-dom";
import {
  LayoutDashboard,
  FileText,
  GitBranch,
  Activity,
  Users,
  Settings,
  HelpCircle,
  Gauge,
} from "lucide-react";

export default function Sidebar() {
  const location = useLocation();

  // 🔄 REORDERED NAV LINKS
  const navLinks = [
    { label: "Dashboard", icon: LayoutDashboard, path: "/dashboard" },

    {
      label: "Dashboard Pipelines",
      icon: Gauge,
      path: "/dashboard/pipelines",
    },

    { label: "Pipelines", icon: GitBranch, path: "/pipelines" },

    { label: "Reports", icon: FileText, path: "/reports" },

    { label: "Log Activity", icon: Activity, path: "/activity" },

    { label: "About Developers", icon: Users, path: "/about" },
  ];

  const toolLinks = [
    { label: "Settings", icon: Settings, path: "/settings" },
    { label: "Help", icon: HelpCircle, path: "/help" },
  ];

  const isActive = (path) => {
    if (location.pathname === path) return true;

    if (path !== "/dashboard" && location.pathname.startsWith(path + "/"))
      return true;

    return false;
  };

  const renderLink = (link) => {
    const Icon = link.icon;
    const active = isActive(link.path);

    return (
      <Link
        key={link.path}
        to={link.path}
        className={`w-full flex items-center px-8 py-3 transition-colors ${
          active
            ? "bg-[#1a2a42] text-[#64ffda] border-l-4 border-[#64ffda]"
            : "text-[#ccd6f6] hover:bg-[#1a2a42] hover:text-[#64ffda]"
        }`}
      >
        <Icon className="w-5 h-5 mr-3" />
        {link.label}
      </Link>
    );
  };

  return (
    <aside className="w-64 bg-[#112240] border-r border-[#233554] min-h-screen">
      <div className="py-5">
        <div className="px-8 py-2 mb-2 text-xs uppercase text-[#8892b0] border-b border-[#233554]">
          Navigation
        </div>

        {navLinks.map(renderLink)}

        <div className="px-8 py-2 mb-2 mt-5 text-xs uppercase text-[#8892b0] border-b border-[#233554]">
          Tools
        </div>

        {toolLinks.map(renderLink)}
      </div>
    </aside>
  );
}
