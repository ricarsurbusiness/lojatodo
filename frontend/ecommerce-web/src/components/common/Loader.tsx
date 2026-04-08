import React from 'react';

export type LoaderSize = 'sm' | 'md' | 'lg';
export type LoaderVariant = 'spinner' | 'dots' | 'pulse';

export interface LoaderProps {
  size?: LoaderSize;
  variant?: LoaderVariant;
  color?: string;
  className?: string;
}

export const Loader: React.FC<LoaderProps> = ({
  size = 'md',
  variant = 'spinner',
  color = 'text-blue-600',
  className = '',
}) => {
  const sizeStyles: Record<LoaderSize, string> = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
  };

  if (variant === 'dots') {
    return (
      <div className={`flex items-center justify-center gap-1 ${className}`}>
        {[0, 1, 2].map((i) => (
          <div
            key={i}
            className={`${color} rounded-full animate-pulse`}
            style={{
              width: size === 'sm' ? '6px' : size === 'md' ? '8px' : '10px',
              height: size === 'sm' ? '6px' : size === 'md' ? '8px' : '10px',
              animationDelay: `${i * 0.15}s`,
            }}
          />
        ))}
      </div>
    );
  }

  if (variant === 'pulse') {
    return (
      <div className={`flex items-center justify-center ${className}`}>
        <div
          className={`${color} rounded-full animate-ping`}
          style={{
            width: size === 'sm' ? '16px' : size === 'md' ? '24px' : '32px',
            height: size === 'sm' ? '16px' : size === 'md' ? '24px' : '32px',
          }}
        />
      </div>
    );
  }

  return (
    <div className={`flex items-center justify-center ${className}`}>
      <svg
        className={`${sizeStyles[size]} ${color} animate-spin`}
        viewBox="0 0 24 24"
        fill="none"
      >
        <circle
          className="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          strokeWidth="4"
        />
        <path
          className="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
        />
      </svg>
    </div>
  );
};

export const LoadingOverlay: React.FC<{ message?: string }> = ({ message }) => (
  <div className="fixed inset-0 bg-white bg-opacity-80 flex flex-col items-center justify-center z-50">
    <Loader size="lg" />
    {message && <p className="mt-4 text-gray-600">{message}</p>}
  </div>
);
