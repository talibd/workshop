import { useState } from 'react';

export default function KeywordToggleList({ keywords = [], onChange }) {
  const [active, setActive] = useState(() => {
    const initial = {};
    keywords.forEach((k) => {
      initial[k] = true;
    });
    return initial;
  });

  const handleToggle = (kw) => {
    const updated = { ...active, [kw]: !active[kw] };
    setActive(updated);
    if (onChange) {
      onChange(updated);
    }
  };

  if (!keywords.length) {
    return null;
  }

  return (
    <div className="keyword-toggle-list">
      {keywords.map((kw) => (
        <label key={kw} className="toggle">
          <input
            type="checkbox"
            checked={!!active[kw]}
            onChange={() => handleToggle(kw)}
          />
          <span className="slider" />
          <span className="label-text">{kw}</span>
        </label>
      ))}
      <style jsx>{`
        .keyword-toggle-list {
          margin-top: 1rem;
        }
        .toggle {
          display: flex;
          align-items: center;
          margin-bottom: 0.5rem;
          position: relative;
          padding-left: 50px;
          cursor: pointer;
          user-select: none;
        }
        .toggle input {
          opacity: 0;
          width: 0;
          height: 0;
        }
        .slider {
          position: absolute;
          left: 0;
          top: 0;
          width: 40px;
          height: 20px;
          background-color: #ccc;
          border-radius: 20px;
          transition: background-color 0.2s;
        }
        .slider:before {
          content: '';
          position: absolute;
          height: 16px;
          width: 16px;
          left: 2px;
          bottom: 2px;
          background-color: white;
          border-radius: 50%;
          transition: transform 0.2s;
        }
        input:checked + .slider {
          background-color: #2196F3;
        }
        input:checked + .slider:before {
          transform: translateX(20px);
        }
        .label-text {
          margin-left: 0.5rem;
        }
      `}</style>
    </div>
  );
}
