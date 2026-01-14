import { Settings } from "lucide-react";
import DashboardCard from "../components/DashboardCard";

export default function SettingsPage() {
  return (
    <div className="p-6 md:p-10">
      <h1 className="text-4xl font-bold text-white mb-6 flex items-center">
        <Settings className="w-8 h-8 mr-3 text-[#64ffda]" />
        Settings
      </h1>

      <DashboardCard title="App Preferences">
        <div className="space-y-4 text-[#ccd6f6]">
          <div className="flex items-center">
            <input type="checkbox" className="mr-3" />
            Enable Dark Mode
          </div>
          <div className="flex items-center">
            <input type="checkbox" className="mr-3" />
            Auto-refresh dashboard data
          </div>
          <div className="flex items-center">
            <input type="checkbox" className="mr-3" />
            Enable email alerts
          </div>
        </div>
      </DashboardCard>
    </div>
  );
}
