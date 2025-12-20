/**
 * Loading spinner component
 * @param {string} size - Spinner size: sm | md | lg
 * @param {string} color - Spinner color
 */
const LoadingSpinner = ({ size = 'md', color = 'blue-600' }) => {
  const sizeStyles = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-12 w-12',
  };

  return (
    <div className="flex items-center justify-center">
      <div
        className={`animate-spin rounded-full border-b-2 border-${color} ${sizeStyles[size]}`}
      ></div>
    </div>
  );
};

export default LoadingSpinner;
