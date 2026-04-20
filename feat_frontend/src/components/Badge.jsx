import './Badge.css';

export default function Badge({
  children,
  variant = 'primary',
  size = 'medium',
  className = '',
  ...props
}) {
  const badgeClass = [
    'badge',
    `badge-${variant}`,
    `badge-${size}`,
    className,
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <span className={badgeClass} {...props}>
      {children}
    </span>
  );
}
