import './PageLayout.css';

export default function PageLayout({ children, topbar, footer, className = '' }) {
  return (
    <div className={`page ${className}`}>
      {topbar}
      <div className="content">
        {children}
      </div>
      {footer && <div className="bottombar">{footer}</div>}
    </div>
  );
}
