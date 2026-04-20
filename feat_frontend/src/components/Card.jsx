import './Card.css';

export default function Card({
  children,
  variant = 'elevated',
  className = '',
  ...props
}) {
  const cardClass = [
    'card',
    `card-${variant}`,
    className,
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <div className={cardClass} {...props}>
      {children}
    </div>
  );
}
