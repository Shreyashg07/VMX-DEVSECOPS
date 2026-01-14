import { useState, useRef, useEffect } from "react";
import { LogOut, Calendar } from "lucide-react";

export default function ProfileMenu({ user, onLogout }) {
  const [open, setOpen] = useState(false);
  const ref = useRef(null);

  /* ============================
     CLOSE ON OUTSIDE CLICK
     ============================ */
  useEffect(() => {
    const handler = (e) => {
      if (ref.current && !ref.current.contains(e.target)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  /* ============================
     SAFE USER FIELDS
     ============================ */
  const username = user?.username || user?.name || "User";

  // 🔑 Support ALL common backend date formats
  const joinedRaw =
    user?.created_at ||
    user?.createdAt ||
    user?.created_date ||
    user?.created ||
    null;

  const joined = joinedRaw
    ? new Date(joinedRaw).toLocaleDateString("en-IN", {
        day: "numeric",
        month: "short",
        year: "numeric",
      })
    : "—";

  return (
    <div className="relative" ref={ref}>
      {/* ================= AVATAR ================= */}
      <button
        onClick={() => setOpen((o) => !o)}
        className="w-9 h-9 rounded-full bg-blue-600 text-white
                   flex items-center justify-center font-semibold
                   hover:ring-2 hover:ring-blue-400 transition"
      >
        {username.charAt(0).toUpperCase()}
      </button>

      {/* ================= PROFILE CARD ================= */}
      {open && (
        <div
          className="absolute right-0 mt-3 w-64 bg-[#0B1E3B]
                     border border-[#233554] rounded-lg shadow-xl z-50"
        >
          {/* Header */}
          <div className="p-4 border-b border-[#233554] flex items-center gap-3">
            <div
              className="w-10 h-10 rounded-full bg-blue-600 text-white
                         flex items-center justify-center font-bold"
            >
              {username.charAt(0).toUpperCase()}
            </div>

            <div>
              <p className="text-white font-medium">{username}</p>
              <p className="text-xs text-gray-400 flex items-center gap-1 mt-1">
                <Calendar size={12} />
                Joined {joined}
              </p>
            </div>
          </div>

          {/* Logout */}
          <button
            onClick={onLogout}
            className="w-full px-4 py-3 flex items-center gap-2
                       text-red-400 hover:bg-red-500/10 transition"
          >
            <LogOut size={16} />
            Logout
          </button>
        </div>
      )}
    </div>
  );
}
