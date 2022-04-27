export const Overlay = ({ enabled }: { enabled?: boolean }) => {
  if (enabled === undefined) enabled = true;
  return (
    <div className={`fixed inset-0 z-10 ${enabled ? "visible" : "invisible"}`}>
      <div
        className={`h-full bg-white transition-all ${
          enabled ? "opacity-60" : "opacity-0"
        }`}
      ></div>
    </div>
  );
};

export default Overlay;
