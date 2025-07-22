# Palantir Intelligence Frontend

A blockchain intelligence platform frontend built with atomic design principles, featuring a sophisticated visualization layer and dockable workspace interface.

## Architecture

### Atomic Design System

The frontend follows atomic design methodology with a strict component hierarchy:

```
src/
├── components/
│   ├── atoms/           # Basic UI elements
│   │   ├── Button.tsx   # Configurable button component
│   │   ├── Icon.tsx     # SVG icon system with 50+ blockchain icons
│   │   └── Spinner.tsx  # Loading states (default, dots, pulse, bars, ring)
│   ├── molecules/       # Compound components
│   │   ├── NavBar.tsx   # Top navigation with search and user menu
│   │   ├── SideBar.tsx  # Collapsible sidebar navigation
│   │   └── PanelHeader.tsx # Draggable panel headers with controls
│   └── organisms/       # Complex UI sections
│       ├── DockableLayout.tsx # Drag-and-drop workspace manager
│       └── GraphExplorer.tsx  # Interactive network visualization
├── theme/              # Design tokens
│   ├── colors.ts       # Color palette, risk levels, entity types
│   ├── typography.ts   # Font system, text styles, responsive sizing
│   └── motion.ts       # Animation presets, transitions, keyframes
└── providers/          # Application state
    ├── ThemeProvider.tsx   # Chakra UI theme configuration
    └── LayoutProvider.tsx  # Workspace layout management
```

## Key Features

### 🎨 Design System
- **Color System**: Semantic colors, risk levels (low/medium/high/critical), entity types (address/contract/token/transaction/block)
- **Typography**: Inter font for UI, JetBrains Mono for code, responsive sizing
- **Motion**: Consistent transitions, hover effects, loading animations

### 🧩 Component Library

#### Atoms
- **Button**: 6 variants (primary, secondary, ghost, outline, danger, success)
- **Icon**: 50+ blockchain-specific icons with risk/status variants
- **Spinner**: 5 loading styles with overlay and full-page options

#### Molecules
- **NavBar**: Search, notifications, user menu, breadcrumbs
- **SideBar**: Collapsible navigation with nested items and quick actions
- **PanelHeader**: Draggable headers with minimize/maximize/close controls

#### Organisms
- **DockableLayout**: Foundry-style workspace with drag-and-drop panels
- **GraphExplorer**: Interactive network visualization with controls

### 🔧 Workspace Management
- **Panel System**: Drag, resize, minimize, maximize, and dock panels
- **Layout Templates**: Predefined arrangements (explorer, dashboard, analysis)
- **Persistence**: Auto-save layouts to localStorage
- **History**: Undo/redo layout changes

### 📊 Visualization Integration
- **Graph Explorer**: Network visualization with node/edge interactions
- **Canvas Rendering**: High-performance rendering for large datasets
- **Controls**: Layout algorithms, filtering, zoom/pan, export

## Technology Stack

- **Framework**: Next.js 14 with TypeScript
- **UI Library**: Chakra UI with custom theme
- **Animations**: Framer Motion
- **Drag & Drop**: React DnD with HTML5 backend
- **Visualization**: Canvas API (ready for D3.js/Deck.GL integration)
- **State Management**: React Context with useReducer

## Getting Started

### Prerequisites
- Node.js 18+
- npm 9+

### Installation
```bash
cd services/ui/nextjs-app
npm install
npm run dev
```

### Development
```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run type-check   # TypeScript validation
npm run lint         # ESLint validation
```

## Component Usage

### Basic Components
```tsx
import { Button, Icon, Spinner } from '@/components';

<Button variant="primary" leftIcon={<Icon name="search" />}>
  Search Addresses
</Button>
```

### Layout Components
```tsx
import { NavBar, SideBar } from '@/components';

<NavBar 
  user={user}
  onSearch={handleSearch}
  notifications={3}
/>

<SideBar
  items={navigationItems}
  onItemClick={handleNavigation}
  isCollapsed={isCollapsed}
/>
```

### Workspace System
```tsx
import { DockableLayout, LayoutProvider } from '@/components';

<LayoutProvider>
  <DockableLayout
    panels={panels}
    onPanelUpdate={updatePanel}
    onPanelClose={removePanel}
    snapToGrid={true}
  />
</LayoutProvider>
```

## Customization

### Theme Configuration
```tsx
// Extend colors in theme/colors.ts
export const colors = {
  primary: { ... },
  risk: {
    low: '#10B981',
    medium: '#F59E0B',
    high: '#EF4444',
    critical: '#DC2626'
  }
};
```

### Component Variants
```tsx
// Add new button variants
const customVariant = {
  bg: 'purple.500',
  color: 'white',
  _hover: { bg: 'purple.600' }
};
```

### Layout Templates
```tsx
// Create custom layout templates
const myTemplate = (width: number, height: number) => [
  {
    type: 'graph-explorer',
    position: { x: 0, y: 0, width: width * 0.6, height: height }
  }
];
```

## Integration Points

### Visualization Services
The frontend integrates with the following visualization services:

- **DeckGL Explorer** (`services/visualization/deckgl_explorer/`)
- **TimeSeries Canvas** (`services/visualization/timeseries_canvas/`)
- **Compliance Map** (`services/visualization/compliance_map/`)
- **Workspace Builder** (`services/visualization/workspace/`)

### API Integration
```tsx
// GraphQL integration ready
const { data, loading } = useQuery(GET_TRANSACTION_GRAPH, {
  variables: { address: selectedAddress }
});
```

## Performance

### Optimization Features
- Component lazy loading
- Virtualized lists for large datasets
- Canvas rendering for complex visualizations
- Memoized expensive calculations
- Bundle splitting and code splitting

### Accessibility
- ARIA labels on interactive elements
- Keyboard navigation support
- Screen reader compatibility
- Color contrast compliance (WCAG 2.1 AA)

## Testing

The component library is designed for comprehensive testing:

```bash
npm run test         # Jest test runner
npm run test:watch   # Watch mode
npm run test:coverage # Coverage reports
```

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Contributing

### Component Development
1. Follow atomic design principles
2. Use TypeScript for all components
3. Include comprehensive prop types
4. Add JSDoc documentation
5. Create Storybook stories
6. Write unit tests

### Naming Conventions
- Components: PascalCase (`NavBar`, `GraphExplorer`)
- Files: Match component name (`NavBar.tsx`)
- Props: camelCase with descriptive names
- Events: `on` prefix (`onNodeClick`, `onPanelClose`)

This frontend implementation provides a solid foundation for building complex blockchain intelligence applications with professional-grade UI components and workspace management capabilities.
