import { NavLink } from "react-router-dom";
import Icon from "./Icon";

interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
  inboxCount: number;
  reviewCount: number;
}

const navItems = [
  { to: "/", icon: "dashboard", label: "Overview", end: true },
  { to: "/customers", icon: "groups", label: "Customers", badge: "inbox" as const },
  { to: "/review", icon: "fact_check", label: "Review", badge: "review" as const },
  { to: "/insights", icon: "insights", label: "Reporting" },
  { to: "/genie", icon: "auto_awesome", label: "Genie AI" },
];

export default function Sidebar({ collapsed, onToggle, inboxCount, reviewCount }: SidebarProps) {
  const badges: Record<string, number> = { inbox: inboxCount, review: reviewCount };

  return (
    <aside
      className={`fixed left-0 top-0 h-screen flex flex-col z-50 transition-all duration-300 ease-in-out overflow-hidden ${
        collapsed ? "w-[68px]" : "w-64"
      }`}
    >
      <div
        className={`flex flex-col items-center w-full flex-shrink-0 ${
          collapsed ? "px-2 py-3" : "px-6 py-5"
        }`}
        style={{ backgroundColor: "#450350" }}
      >
        <img
          src="/royal-london-logo.png"
          alt="Royal London"
          className={`object-contain transition-all duration-300 ${
            collapsed ? "h-[78px]" : "h-[120px]"
          }`}
        />
        {!collapsed && (
          <span className="mt-3 block w-full text-center text-white/40 text-[10px] font-label tracking-[0.25em] uppercase">
            DocuParse
          </span>
        )}
      </div>

      {/* Rest of sidebar — exact same purple as the logo */}
      <div className="flex-1 flex flex-col min-h-0" style={{ backgroundColor: "#450350" }}>
        {/* Upload batch button */}
        {!collapsed && (
          <div className="px-4 pt-3 pb-2">
            <button className="w-full py-2.5 px-4 rounded-md bg-white/10 text-white font-label text-sm tracking-wide hover:bg-white/[0.15] transition-colors flex items-center justify-center gap-2 border border-white/[0.08]">
              <Icon name="add" fill size={18} />
              Upload Batch
            </button>
          </div>
        )}

        {/* Navigation */}
        <nav className="flex-1 flex flex-col gap-0.5 px-2 pt-2 overflow-y-auto">
          {navItems.map(({ to, icon, label, end, badge }) => {
            const count = badge ? badges[badge] : 0;
            return (
              <NavLink
                key={to}
                to={to}
                end={end}
                className={({ isActive }) =>
                  `group flex items-center gap-3 py-2.5 transition-all duration-200 font-body text-[13px] tracking-wide ${
                    collapsed ? "justify-center px-2 rounded-lg" : "px-4 rounded-lg"
                  } ${
                    isActive
                      ? "bg-white/[0.12] text-white font-semibold"
                      : "text-white/50 hover:text-white/80 hover:bg-white/[0.06]"
                  }`
                }
              >
                {({ isActive }) => (
                  <>
                    <div className="relative flex-shrink-0">
                      <Icon name={icon} fill={isActive} size={20} />
                      {count > 0 && collapsed && (
                        <span className="absolute -top-1 -right-1 w-3.5 h-3.5 bg-white text-[#450350] text-[8px] font-bold rounded-full flex items-center justify-center">
                          {count}
                        </span>
                      )}
                    </div>
                    {!collapsed && (
                      <>
                        <span className="flex-1 truncate">{label}</span>
                        {count > 0 && (
                          <span className="px-1.5 py-0.5 bg-white/[0.12] text-white/80 text-[10px] font-semibold rounded">
                            {count}
                          </span>
                        )}
                      </>
                    )}
                  </>
                )}
              </NavLink>
            );
          })}
        </nav>

        {/* Bottom */}
        <div className="px-2 space-y-0.5 pb-4 pt-2 flex-shrink-0">
          <button
            className={`flex items-center gap-3 py-2.5 rounded-lg text-white/40 hover:text-white/70 hover:bg-white/[0.06] transition-all duration-200 font-body text-[13px] tracking-wide w-full ${
              collapsed ? "justify-center px-2" : "px-4"
            }`}
          >
            <Icon name="settings" size={20} />
            {!collapsed && <span>Settings</span>}
          </button>
          <button
            onClick={onToggle}
            className={`flex items-center gap-3 py-2.5 rounded-lg text-white/40 hover:text-white/70 hover:bg-white/[0.06] transition-all duration-200 font-body text-[13px] tracking-wide w-full ${
              collapsed ? "justify-center px-2" : "px-4"
            }`}
          >
            <Icon name={collapsed ? "chevron_right" : "chevron_left"} size={20} />
            {!collapsed && <span>Collapse</span>}
          </button>
        </div>
      </div>
    </aside>
  );
}
