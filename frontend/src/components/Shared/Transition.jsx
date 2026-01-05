import React from 'react';
import PropTypes from 'prop-types';

const Transition = ({ children, type = 'fadeIn', delay = 0, className = '' }) => {
  const transitionTypes = {
    fadeIn: 'animate-fadeIn',
    slideUp: 'animate-slideUp',
    slideDown: 'animate-slideDown',
    slideInLeft: 'animate-slideInLeft',
    slideInRight: 'animate-slideInRight',
    scaleIn: 'animate-scaleIn',
  };

  const delayClasses = {
    0: '',
    100: 'animate-delay-100',
    200: 'animate-delay-200',
    300: 'animate-delay-300',
    400: 'animate-delay-400',
    500: 'animate-delay-500',
  };

  const combinedClasses = [
    transitionTypes[type] || transitionTypes.fadeIn,
    delayClasses[delay] || '',
    className,
  ].filter(Boolean).join(' ');

  return <div className={combinedClasses}>{children}</div>;
};

Transition.propTypes = {
  children: PropTypes.node.isRequired,
  type: PropTypes.oneOf(['fadeIn', 'slideUp', 'slideDown', 'slideInLeft', 'slideInRight', 'scaleIn']),
  delay: PropTypes.oneOf([0, 100, 200, 300, 400, 500]),
  className: PropTypes.string,
};

export default Transition;
