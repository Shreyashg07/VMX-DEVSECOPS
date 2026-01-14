export default function DashboardCard({ title, description, children }) {
  return (
    <div className="bg-[#112240] rounded-xl p-6 border border-[#233554] shadow-[0_0_10px_rgba(100,255,218,0.05)] hover:shadow-[0_0_18px_rgba(100,255,218,0.15)] transition-shadow duration-300">
      <div className="mb-4">
        <h3 className="text-xl font-semibold text-[#64ffda] tracking-wide">
          {title}
        </h3>

        {description && (
          <p className="text-sm text-[#8892b0] mt-1">{description}</p>
        )}

        <div className="mt-4 border-b border-[#233554]" />
      </div>

      {children}
    </div>
  );
}
