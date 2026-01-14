export default function ChartPlaceholder({
  type,
  color = "#64ffda",
  height = "16rem",
}) {
  return (
    <div
      className="w-full bg-[#0a1929] rounded-xl flex items-center justify-center border border-[#233554] animate-pulse"
      style={{ height, color }}
    >
      <span className="text-lg font-semibold tracking-wide opacity-70">
        {`[ ${type.charAt(0).toUpperCase() + type.slice(1)} Visualization ]`}
      </span>
    </div>
  );
}
