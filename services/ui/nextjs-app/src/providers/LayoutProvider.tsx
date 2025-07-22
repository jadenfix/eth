import React, { createContext, useContext, useReducer, useCallback, useEffect } from 'react';
import { PanelConfig, PanelType } from '../components/organisms/DockableLayout';

// Layout state interface
interface LayoutState {
  panels: PanelConfig[];
  activePanel: string | null;
  isGridVisible: boolean;
  snapToGrid: boolean;
  gridSize: number;
  layoutHistory: LayoutSnapshot[];
  currentHistoryIndex: number;
  maxHistoryLength: number;
}

interface LayoutSnapshot {
  id: string;
  timestamp: number;
  panels: PanelConfig[];
  name?: string;
}

// Action types
type LayoutAction =
  | { type: 'ADD_PANEL'; panel: Omit<PanelConfig, 'id'> }
  | { type: 'UPDATE_PANEL'; id: string; updates: Partial<PanelConfig> }
  | { type: 'REMOVE_PANEL'; id: string }
  | { type: 'SET_ACTIVE_PANEL'; id: string | null }
  | { type: 'TOGGLE_GRID'; visible?: boolean }
  | { type: 'TOGGLE_SNAP_TO_GRID'; enabled?: boolean }
  | { type: 'SET_GRID_SIZE'; size: number }
  | { type: 'LOAD_LAYOUT'; panels: PanelConfig[] }
  | { type: 'SAVE_SNAPSHOT'; name?: string }
  | { type: 'RESTORE_SNAPSHOT'; index: number }
  | { type: 'CLEAR_LAYOUT' }
  | { type: 'ARRANGE_PANELS'; arrangement: 'tile' | 'cascade' | 'stack' };

// Initial state
const initialState: LayoutState = {
  panels: [],
  activePanel: null,
  isGridVisible: false,
  snapToGrid: true,
  gridSize: 20,
  layoutHistory: [],
  currentHistoryIndex: -1,
  maxHistoryLength: 20,
};

// Reducer
const layoutReducer = (state: LayoutState, action: LayoutAction): LayoutState => {
  switch (action.type) {
    case 'ADD_PANEL': {
      const newPanel: PanelConfig = {
        ...action.panel,
        id: `panel_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        zIndex: Math.max(...state.panels.map(p => p.zIndex || 0), 0) + 1,
      };

      return {
        ...state,
        panels: [...state.panels, newPanel],
        activePanel: newPanel.id,
      };
    }

    case 'UPDATE_PANEL': {
      return {
        ...state,
        panels: state.panels.map(panel =>
          panel.id === action.id
            ? { ...panel, ...action.updates }
            : panel
        ),
      };
    }

    case 'REMOVE_PANEL': {
      const newPanels = state.panels.filter(panel => panel.id !== action.id);
      return {
        ...state,
        panels: newPanels,
        activePanel: state.activePanel === action.id 
          ? (newPanels.length > 0 ? newPanels[0].id : null)
          : state.activePanel,
      };
    }

    case 'SET_ACTIVE_PANEL': {
      // Bring active panel to front
      const newPanels = action.id
        ? state.panels.map(panel => ({
            ...panel,
            zIndex: panel.id === action.id 
              ? Math.max(...state.panels.map(p => p.zIndex || 0)) + 1
              : panel.zIndex,
          }))
        : state.panels;

      return {
        ...state,
        panels: newPanels,
        activePanel: action.id,
      };
    }

    case 'TOGGLE_GRID': {
      return {
        ...state,
        isGridVisible: action.visible !== undefined ? action.visible : !state.isGridVisible,
      };
    }

    case 'TOGGLE_SNAP_TO_GRID': {
      return {
        ...state,
        snapToGrid: action.enabled !== undefined ? action.enabled : !state.snapToGrid,
      };
    }

    case 'SET_GRID_SIZE': {
      return {
        ...state,
        gridSize: action.size,
      };
    }

    case 'LOAD_LAYOUT': {
      return {
        ...state,
        panels: action.panels,
        activePanel: action.panels.length > 0 ? action.panels[0].id : null,
      };
    }

    case 'SAVE_SNAPSHOT': {
      const snapshot: LayoutSnapshot = {
        id: `snapshot_${Date.now()}`,
        timestamp: Date.now(),
        panels: JSON.parse(JSON.stringify(state.panels)), // Deep clone
        name: action.name || `Layout ${state.layoutHistory.length + 1}`,
      };

      const newHistory = [
        ...state.layoutHistory.slice(0, state.currentHistoryIndex + 1),
        snapshot,
      ].slice(-state.maxHistoryLength);

      return {
        ...state,
        layoutHistory: newHistory,
        currentHistoryIndex: newHistory.length - 1,
      };
    }

    case 'RESTORE_SNAPSHOT': {
      const snapshot = state.layoutHistory[action.index];
      if (!snapshot) return state;

      return {
        ...state,
        panels: JSON.parse(JSON.stringify(snapshot.panels)), // Deep clone
        activePanel: snapshot.panels.length > 0 ? snapshot.panels[0].id : null,
        currentHistoryIndex: action.index,
      };
    }

    case 'CLEAR_LAYOUT': {
      return {
        ...state,
        panels: [],
        activePanel: null,
      };
    }

    case 'ARRANGE_PANELS': {
      const arrangedPanels = arrangePanels(state.panels, action.arrangement);
      return {
        ...state,
        panels: arrangedPanels,
      };
    }

    default:
      return state;
  }
};

// Panel arrangement functions
const arrangePanels = (panels: PanelConfig[], arrangement: string): PanelConfig[] => {
  const windowWidth = typeof window !== 'undefined' ? window.innerWidth : 1200;
  const windowHeight = typeof window !== 'undefined' ? window.innerHeight : 800;

  switch (arrangement) {
    case 'tile': {
      const cols = Math.ceil(Math.sqrt(panels.length));
      const rows = Math.ceil(panels.length / cols);
      const panelWidth = Math.floor(windowWidth / cols);
      const panelHeight = Math.floor(windowHeight / rows);

      return panels.map((panel, index) => ({
        ...panel,
        position: {
          ...panel.position,
          x: (index % cols) * panelWidth,
          y: Math.floor(index / cols) * panelHeight,
          width: panelWidth - 10,
          height: panelHeight - 10,
        },
      }));
    }

    case 'cascade': {
      const offset = 30;
      return panels.map((panel, index) => ({
        ...panel,
        position: {
          ...panel.position,
          x: index * offset,
          y: index * offset,
          width: Math.min(600, windowWidth - index * offset - 50),
          height: Math.min(400, windowHeight - index * offset - 50),
        },
      }));
    }

    case 'stack': {
      const maxWidth = Math.min(800, windowWidth - 100);
      const maxHeight = Math.min(600, windowHeight - 100);
      const centerX = (windowWidth - maxWidth) / 2;
      const centerY = (windowHeight - maxHeight) / 2;

      return panels.map((panel, index) => ({
        ...panel,
        position: {
          ...panel.position,
          x: centerX + index * 5,
          y: centerY + index * 5,
          width: maxWidth,
          height: maxHeight,
        },
        zIndex: panels.length - index,
      }));
    }

    default:
      return panels;
  }
};

// Context
interface LayoutContextValue {
  state: LayoutState;
  dispatch: React.Dispatch<LayoutAction>;
  addPanel: (panel: Omit<PanelConfig, 'id'>) => void;
  updatePanel: (id: string, updates: Partial<PanelConfig>) => void;
  removePanel: (id: string) => void;
  setActivePanel: (id: string | null) => void;
  clearLayout: () => void;
  saveSnapshot: (name?: string) => void;
  restoreSnapshot: (index: number) => void;
  arrangeLayout: (arrangement: 'tile' | 'cascade' | 'stack') => void;
  loadTemplate: (templateName: string) => void;
}

const LayoutContext = createContext<LayoutContextValue | undefined>(undefined);

// Provider component
interface LayoutProviderProps {
  children: React.ReactNode;
  initialPanels?: PanelConfig[];
  persistLayout?: boolean;
  storageKey?: string;
}

export const LayoutProvider: React.FC<LayoutProviderProps> = ({
  children,
  initialPanels = [],
  persistLayout = true,
  storageKey = 'palantir_layout',
}) => {
  const [state, dispatch] = useReducer(layoutReducer, {
    ...initialState,
    panels: initialPanels,
    activePanel: initialPanels.length > 0 ? initialPanels[0].id : null,
  });

  // Load layout from localStorage on mount
  useEffect(() => {
    if (!persistLayout || typeof window === 'undefined') return;

    try {
      const savedLayout = localStorage.getItem(storageKey);
      if (savedLayout) {
        const { panels, settings } = JSON.parse(savedLayout);
        if (panels && Array.isArray(panels)) {
          dispatch({ type: 'LOAD_LAYOUT', panels });
          if (settings) {
            if (settings.isGridVisible !== undefined) {
              dispatch({ type: 'TOGGLE_GRID', visible: settings.isGridVisible });
            }
            if (settings.snapToGrid !== undefined) {
              dispatch({ type: 'TOGGLE_SNAP_TO_GRID', enabled: settings.snapToGrid });
            }
            if (settings.gridSize !== undefined) {
              dispatch({ type: 'SET_GRID_SIZE', size: settings.gridSize });
            }
          }
        }
      }
    } catch (error) {
      console.warn('Failed to load saved layout:', error);
    }
  }, [persistLayout, storageKey]);

  // Save layout to localStorage when state changes
  useEffect(() => {
    if (!persistLayout || typeof window === 'undefined') return;

    try {
      const layoutData = {
        panels: state.panels,
        settings: {
          isGridVisible: state.isGridVisible,
          snapToGrid: state.snapToGrid,
          gridSize: state.gridSize,
        },
        lastSaved: Date.now(),
      };
      localStorage.setItem(storageKey, JSON.stringify(layoutData));
    } catch (error) {
      console.warn('Failed to save layout:', error);
    }
  }, [state.panels, state.isGridVisible, state.snapToGrid, state.gridSize, persistLayout, storageKey]);

  // Action creators
  const addPanel = useCallback((panel: Omit<PanelConfig, 'id'>) => {
    dispatch({ type: 'ADD_PANEL', panel });
  }, []);

  const updatePanel = useCallback((id: string, updates: Partial<PanelConfig>) => {
    dispatch({ type: 'UPDATE_PANEL', id, updates });
  }, []);

  const removePanel = useCallback((id: string) => {
    dispatch({ type: 'REMOVE_PANEL', id });
  }, []);

  const setActivePanel = useCallback((id: string | null) => {
    dispatch({ type: 'SET_ACTIVE_PANEL', id });
  }, []);

  const clearLayout = useCallback(() => {
    dispatch({ type: 'CLEAR_LAYOUT' });
  }, []);

  const saveSnapshot = useCallback((name?: string) => {
    dispatch({ type: 'SAVE_SNAPSHOT', name });
  }, []);

  const restoreSnapshot = useCallback((index: number) => {
    dispatch({ type: 'RESTORE_SNAPSHOT', index });
  }, []);

  const arrangeLayout = useCallback((arrangement: 'tile' | 'cascade' | 'stack') => {
    dispatch({ type: 'ARRANGE_PANELS', arrangement });
  }, []);

  const loadTemplate = useCallback((templateName: string) => {
    // Import layout templates dynamically
    import('../components/organisms/DockableLayout').then(({ layoutTemplates }) => {
      const windowWidth = typeof window !== 'undefined' ? window.innerWidth : 1200;
      const windowHeight = typeof window !== 'undefined' ? window.innerHeight : 800;
      
      const template = (layoutTemplates as any)[templateName];
      if (template && typeof template === 'function') {
        const templatePanels = template(windowWidth, windowHeight);
        const panels = templatePanels.map((panel: any, index: number) => ({
          ...panel,
          id: `template_${templateName}_${index}_${Date.now()}`,
          isDraggable: true,
          isResizable: true,
          zIndex: index + 1,
        }));
        dispatch({ type: 'LOAD_LAYOUT', panels });
      }
    }).catch(error => {
      console.error('Failed to load template:', error);
    });
  }, []);

  const value: LayoutContextValue = {
    state,
    dispatch,
    addPanel,
    updatePanel,
    removePanel,
    setActivePanel,
    clearLayout,
    saveSnapshot,
    restoreSnapshot,
    arrangeLayout,
    loadTemplate,
  };

  return (
    <LayoutContext.Provider value={value}>
      {children}
    </LayoutContext.Provider>
  );
};

// Hook to use layout context
export const useLayout = (): LayoutContextValue => {
  const context = useContext(LayoutContext);
  if (context === undefined) {
    throw new Error('useLayout must be used within a LayoutProvider');
  }
  return context;
};

export default LayoutProvider;
