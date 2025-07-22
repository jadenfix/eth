// Motion and animation design tokens
export const transitions = {
  // Duration
  duration: {
    fast: '150ms',
    normal: '250ms',
    slow: '350ms',
    slower: '500ms',
  },
  
  // Easing functions
  easing: {
    ease: 'ease',
    easeIn: 'cubic-bezier(0.4, 0, 1, 1)',
    easeOut: 'cubic-bezier(0, 0, 0.2, 1)',
    easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
    
    // Custom easing for specific interactions
    bounce: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
    smooth: 'cubic-bezier(0.25, 0.46, 0.45, 0.94)',
  },
  
  // Common transition properties
  properties: {
    all: 'all',
    opacity: 'opacity',
    transform: 'transform',
    colors: 'background-color, border-color, color, fill, stroke',
    shadow: 'box-shadow',
    filter: 'filter',
  },
};

// Pre-defined transition combinations
export const transitionPresets = {
  // UI interactions
  button: `${transitions.properties.all} ${transitions.duration.fast} ${transitions.easing.easeOut}`,
  hover: `${transitions.properties.transform} ${transitions.duration.fast} ${transitions.easing.easeOut}`,
  focus: `${transitions.properties.shadow} ${transitions.duration.fast} ${transitions.easing.easeOut}`,
  
  // Panel and layout animations
  panel: `${transitions.properties.all} ${transitions.duration.normal} ${transitions.easing.easeInOut}`,
  slide: `${transitions.properties.transform} ${transitions.duration.normal} ${transitions.easing.smooth}`,
  fade: `${transitions.properties.opacity} ${transitions.duration.normal} ${transitions.easing.easeInOut}`,
  
  // Data visualization animations
  chart: `${transitions.properties.all} ${transitions.duration.slow} ${transitions.easing.easeInOut}`,
  graph: `${transitions.properties.transform} ${transitions.duration.slower} ${transitions.easing.smooth}`,
  
  // Modal and overlay animations
  modal: `${transitions.properties.all} ${transitions.duration.normal} ${transitions.easing.easeOut}`,
  tooltip: `${transitions.properties.opacity} ${transitions.duration.fast} ${transitions.easing.easeOut}`,
};

// Animation keyframes
export const keyframes = {
  // Loading animations
  spin: {
    '0%': { transform: 'rotate(0deg)' },
    '100%': { transform: 'rotate(360deg)' },
  },
  
  pulse: {
    '0%, 100%': { opacity: 1 },
    '50%': { opacity: 0.5 },
  },
  
  bounce: {
    '0%, 20%, 53%, 80%, 100%': {
      animationTimingFunction: 'cubic-bezier(0.215, 0.61, 0.355, 1)',
      transform: 'translate3d(0, 0, 0)',
    },
    '40%, 43%': {
      animationTimingFunction: 'cubic-bezier(0.755, 0.05, 0.855, 0.06)',
      transform: 'translate3d(0, -30px, 0)',
    },
    '70%': {
      animationTimingFunction: 'cubic-bezier(0.755, 0.05, 0.855, 0.06)',
      transform: 'translate3d(0, -15px, 0)',
    },
    '90%': {
      transform: 'translate3d(0, -4px, 0)',
    },
  },
  
  // Data animation effects
  slideInUp: {
    '0%': {
      transform: 'translate3d(0, 100%, 0)',
      visibility: 'visible',
    },
    '100%': {
      transform: 'translate3d(0, 0, 0)',
    },
  },
  
  slideInRight: {
    '0%': {
      transform: 'translate3d(100%, 0, 0)',
      visibility: 'visible',
    },
    '100%': {
      transform: 'translate3d(0, 0, 0)',
    },
  },
  
  fadeIn: {
    '0%': {
      opacity: 0,
    },
    '100%': {
      opacity: 1,
    },
  },
  
  zoomIn: {
    '0%': {
      opacity: 0,
      transform: 'scale3d(0.3, 0.3, 0.3)',
    },
    '50%': {
      opacity: 1,
    },
    '100%': {
      transform: 'scale3d(1, 1, 1)',
    },
  },
  
  // Graph and network animations
  nodeAppear: {
    '0%': {
      opacity: 0,
      transform: 'scale(0)',
    },
    '50%': {
      opacity: 1,
    },
    '100%': {
      opacity: 1,
      transform: 'scale(1)',
    },
  },
  
  edgeGrow: {
    '0%': {
      strokeDasharray: '0, 100',
    },
    '100%': {
      strokeDasharray: '100, 0',
    },
  },
};

// Animation utilities
export const animations = {
  // Loading states
  spinner: {
    animation: `spin ${transitions.duration.slower} linear infinite`,
  },
  
  pulse: {
    animation: `pulse ${transitions.duration.slow} ${transitions.easing.easeInOut} infinite`,
  },
  
  // Entry animations
  fadeInUp: {
    animation: `slideInUp ${transitions.duration.slow} ${transitions.easing.easeOut}`,
  },
  
  fadeInRight: {
    animation: `slideInRight ${transitions.duration.slow} ${transitions.easing.easeOut}`,
  },
  
  zoomIn: {
    animation: `zoomIn ${transitions.duration.slow} ${transitions.easing.easeOut}`,
  },
  
  // Interactive states
  hover: {
    transform: 'translateY(-2px)',
    transition: transitionPresets.hover,
  },
  
  press: {
    transform: 'translateY(0px) scale(0.98)',
    transition: transitionPresets.button,
  },
};

// Framer Motion variants for complex animations
export const motionVariants = {
  // Panel animations
  panel: {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: -20 },
    transition: { duration: 0.25, ease: 'easeOut' },
  },
  
  // List item staggered animations
  listContainer: {
    initial: { opacity: 0 },
    animate: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  },
  
  listItem: {
    initial: { opacity: 0, x: -20 },
    animate: { opacity: 1, x: 0 },
    exit: { opacity: 0, x: 20 },
  },
  
  // Modal animations
  modal: {
    initial: { opacity: 0, scale: 0.9 },
    animate: { opacity: 1, scale: 1 },
    exit: { opacity: 0, scale: 0.9 },
    transition: { duration: 0.2, ease: 'easeOut' },
  },
  
  modalBackdrop: {
    initial: { opacity: 0 },
    animate: { opacity: 1 },
    exit: { opacity: 0 },
  },
  
  // Graph node animations
  graphNode: {
    initial: { scale: 0, opacity: 0 },
    animate: { scale: 1, opacity: 1 },
    hover: { scale: 1.1 },
    tap: { scale: 0.95 },
  },
  
  // Dashboard layout animations
  dashboard: {
    initial: { opacity: 0 },
    animate: { opacity: 1 },
    exit: { opacity: 0 },
    transition: { duration: 0.3, ease: 'easeInOut' },
  },
};

// Chakra UI theme integration
export const chakraMotion = {
  transition: {
    property: transitions.properties,
    easing: transitions.easing,
    duration: transitions.duration,
  },
};
