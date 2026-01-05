import React from 'react';
import PropTypes from 'prop-types';

const Card = ({
  children,
  title,
  subtitle,
  hoverable = false,
  padding = 'md',
  className = '',
  ...props
}) => {
  const paddingClasses = {
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8',
  };

  const baseClasses = 'bg-white rounded-card shadow-card transition-shadow duration-300';
  const hoverClass = hoverable ? 'hover-lift cursor-pointer' : '';

  const combinedClasses = [
    baseClasses,
    hoverClass,
    paddingClasses[padding],
    className,
  ].filter(Boolean).join(' ');

  return (
    <div className={combinedClasses} {...props}>
      {title && (
        <div className="mb-4">
          <h3 className="text-xl font-semibold text-neutral-900">{title}</h3>
          {subtitle && (
            <p className="text-sm text-neutral-600 mt-1">{subtitle}</p>
          )}
        </div>
      )}
      {children}
    </div>
  );
};

Card.propTypes = {
  children: PropTypes.node.isRequired,
  title: PropTypes.string,
  subtitle: PropTypes.string,
  hoverable: PropTypes.bool,
  padding: PropTypes.oneOf(['sm', 'md', 'lg']),
  className: PropTypes.string,
};

export default Card;
