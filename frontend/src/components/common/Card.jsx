/**
 * Card component for content containers
 * @param {string} className - Additional CSS classes
 * @param {ReactNode} children - Card content
 * @param {function} onClick - Optional click handler
 */
const Card = ({ className = '', children, onClick, ...props }) => {
  const baseStyles = 'bg-white border border-slate-200 rounded-lg p-6';
  const clickableStyles = onClick ? 'cursor-pointer transition-shadow' : '';

  return (
    <div
      className={`${baseStyles} ${clickableStyles} ${className}`}
      onClick={onClick}
      {...props}
    >
      {children}
    </div>
  );
};

export default Card;
