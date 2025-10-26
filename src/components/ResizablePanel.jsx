import { useState, useRef, useEffect } from "react";
import InfoPanel from "./InfoPanel";
import GlobePanel from "./GlobePanel";

export default function ResizablePanel({ country, onSelectCountry }) {
  const [leftWidth, setLeftWidth] = useState(33.33); // Start at 1/3
  const [isDragging, setIsDragging] = useState(false);
  const containerRef = useRef(null);

  const MIN_WIDTH = 25; // 1/4 of screen
  const MAX_WIDTH = 50; // 1/2 of screen

  useEffect(() => {
    const handleMouseMove = (e) => {
      if (!isDragging || !containerRef.current) return;

      const containerRect = containerRef.current.getBoundingClientRect();
      const newWidth = ((e.clientX - containerRect.left) / containerRect.width) * 100;
      
      // Clamp between min and max
      const clampedWidth = Math.max(MIN_WIDTH, Math.min(MAX_WIDTH, newWidth));
      setLeftWidth(clampedWidth);
    };

    const handleMouseUp = () => {
      setIsDragging(false);
    };

    if (isDragging) {
      document.addEventListener("mousemove", handleMouseMove);
      document.addEventListener("mouseup", handleMouseUp);
    }

    return () => {
      document.removeEventListener("mousemove", handleMouseMove);
      document.removeEventListener("mouseup", handleMouseUp);
    };
  }, [isDragging]);

  return (
    <div ref={containerRef} className="flex flex-1 overflow-hidden relative">
      {/* Left InfoPanel */}
      <div 
        className="bg-white shadow-md p-6 overflow-y-auto"
        style={{ width: `${leftWidth}%` }}
      >
        <InfoPanel country={country} />
      </div>

      {/* Draggable Divider */}
      <div
        className="w-1 bg-gray-300 hover:bg-blue-500 cursor-col-resize transition-colors relative group"
        onMouseDown={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
      >
        <div className="absolute inset-y-0 -left-1 -right-1" />
      </div>

      {/* Right GlobePanel */}
      <div 
        className="bg-gray-200"
        style={{ width: `${100 - leftWidth}%` }}
      >
        <GlobePanel onSelectCountry={onSelectCountry} />
      </div>
    </div>
  );
}
