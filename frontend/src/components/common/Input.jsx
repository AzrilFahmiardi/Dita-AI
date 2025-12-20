import { forwardRef } from 'react';

/**
 * Input component following design system
 * @param {string} label - Input label
 * @param {string} type - Input type
 * @param {string} error - Error message
 * @param {string} helperText - Helper text below input
 * @param {boolean} required - Required field indicator
 */
const Input = forwardRef(
  ({ label, type = 'text', error, helperText, required = false, className = '', ...props }, ref) => {
    return (
      <div className="w-full">
        {label && (
          <label className="block text-sm font-medium text-slate-700 mb-1">
            {label}
            {required && <span className="text-red-500 ml-1">*</span>}
          </label>
        )}
        <input
          ref={ref}
          type={type}
          className={`
            w-full px-3 py-2 
            bg-white 
            border border-slate-300 
            rounded-lg 
            text-slate-900 
            placeholder-slate-400
            focus:outline-none 
            focus:ring-2 
            focus:ring-blue-600 
            focus:border-transparent
            disabled:bg-slate-100 
            disabled:cursor-not-allowed
            ${error ? 'border-red-500 focus:ring-red-500' : ''}
            ${className}
          `}
          {...props}
        />
        {error && <p className="mt-1 text-sm text-red-500">{error}</p>}
        {!error && helperText && <p className="mt-1 text-xs text-slate-500">{helperText}</p>}
      </div>
    );
  }
);

Input.displayName = 'Input';

export default Input;
