/**
 * Foundry-style Workspace - Drag & Drop Dashboard Builder
 * Panel-based layout system for blockchain intelligence dashboards
 */

import React, { useState, useEffect, useCallback } from 'react';
import { DndProvider, useDrag, useDrop } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import DeckGLExplorer from '../deckgl_explorer';
import ComplianceMap from '../compliance_map/map';
import { createTimeSeriesChart } from '../timeseries_canvas/chart';

interface Panel {
  id: string;
  type: 'deckgl_explorer' | 'timeseries_canvas' | 'compliance_map' | 'custom';
  title: string;
  position: { x: number; y: number };
  size: { width: number; height: number };
  config: Record<string, any>;
  minimized?: boolean;
  maximized?: boolean;
}

interface WorkspaceLayout {
  version: string;
  panels: Panel[];
  grid: {
    columns: number;
    rows: number;
    cell_height: number;
  };
  theme: Record<string, string>;
  auto_refresh: boolean;
  refresh_interval: number;
  data_sources: Record<string, any>;
}

interface WorkspaceProps {
  initialLayout?: WorkspaceLayout;
  onLayoutChange?: (layout: WorkspaceLayout) => void;
  readOnly?: boolean;
}

const PANEL_TYPES = {
  deckgl_explorer: {
    name: 'Network Graph',
    icon: '🕸️',
    component: DeckGLExplorer
  },
  timeseries_canvas: {
    name: 'Time Series',
    icon: '📊',
    component: null // Special handling for canvas
  },
  compliance_map: {
    name: 'Compliance Map',
    icon: '🗺️',
    component: ComplianceMap
  },
  custom: {
    name: 'Custom Widget',
    icon: '🔧',
    component: null
  }
};

export default function Workspace({
  initialLayout,
  onLayoutChange,
  readOnly = false
}: WorkspaceProps) {
  const [layout, setLayout] = useState<WorkspaceLayout | null>(null);
  const [selectedPanel, setSelectedPanel] = useState<string | null>(null);
  const [draggedPanel, setDraggedPanel] = useState<Panel | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Load initial layout
  useEffect(() => {
    if (initialLayout) {
      setLayout(initialLayout);
      setIsLoading(false);
    } else {
      // Load default layout
      import('./layout.json')
        .then(defaultLayout => {
          setLayout(defaultLayout as WorkspaceLayout);
          setIsLoading(false);
        })
        .catch(error => {
          console.error('Error loading layout:', error);
          setIsLoading(false);
        });
    }
  }, [initialLayout]);

  // Handle layout changes
  const updateLayout = useCallback((newLayout: WorkspaceLayout) => {
    setLayout(newLayout);
    onLayoutChange?.(newLayout);
  }, [onLayoutChange]);

  // Move panel to new position
  const movePanel = useCallback((panelId: string, newPosition: { x: number; y: number }) => {
    if (!layout || readOnly) return;

    const updatedLayout = {
      ...layout,
      panels: layout.panels.map(panel =>
        panel.id === panelId ? { ...panel, position: newPosition } : panel
      )
    };
    
    updateLayout(updatedLayout);
  }, [layout, readOnly, updateLayout]);

  // Resize panel
  const resizePanel = useCallback((panelId: string, newSize: { width: number; height: number }) => {
    if (!layout || readOnly) return;

    const updatedLayout = {
      ...layout,
      panels: layout.panels.map(panel =>
        panel.id === panelId ? { ...panel, size: newSize } : panel
      )
    };
    
    updateLayout(updatedLayout);
  }, [layout, readOnly, updateLayout]);

  // Toggle panel state (minimize/maximize)
  const togglePanelState = useCallback((panelId: string, state: 'minimized' | 'maximized') => {
    if (!layout || readOnly) return;

    const updatedLayout = {
      ...layout,
      panels: layout.panels.map(panel => {
        if (panel.id === panelId) {
          const newPanel = { ...panel };
          if (state === 'minimized') {
            newPanel.minimized = !newPanel.minimized;
            newPanel.maximized = false;
          } else if (state === 'maximized') {
            newPanel.maximized = !newPanel.maximized;
            newPanel.minimized = false;
          }
          return newPanel;
        }
        return panel;
      })
    };
    
    updateLayout(updatedLayout);
  }, [layout, readOnly, updateLayout]);

  // Remove panel
  const removePanel = useCallback((panelId: string) => {
    if (!layout || readOnly) return;

    const updatedLayout = {
      ...layout,
      panels: layout.panels.filter(panel => panel.id !== panelId)
    };
    
    updateLayout(updatedLayout);
  }, [layout, readOnly, updateLayout]);

  // Add new panel
  const addPanel = useCallback((panelType: string) => {
    if (!layout || readOnly) return;

    const newPanel: Panel = {
      id: `panel_${Date.now()}`,
      type: panelType as any,
      title: `New ${PANEL_TYPES[panelType as keyof typeof PANEL_TYPES]?.name || 'Panel'}`,
      position: { x: 0, y: 0 },
      size: { width: 4, height: 3 },
      config: {}
    };

    const updatedLayout = {
      ...layout,
      panels: [...layout.panels, newPanel]
    };
    
    updateLayout(updatedLayout);
  }, [layout, readOnly, updateLayout]);

  if (isLoading || !layout) {
    return (
      <div className="flex items-center justify-center h-full bg-gray-50">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  const gridStyle = {
    display: 'grid',
    gridTemplateColumns: `repeat(${layout.grid.columns}, 1fr)`,
    gridTemplateRows: `repeat(${layout.grid.rows}, ${layout.grid.cell_height}px)`,
    gap: '8px',
    padding: '16px',
    minHeight: '100vh',
    backgroundColor: layout.theme.background
  };

  return (
    <DndProvider backend={HTML5Backend}>
      <div className="workspace-container">
        {/* Toolbar */}
        {!readOnly && (
          <div className="workspace-toolbar bg-white border-b px-4 py-2 flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <h2 className="text-lg font-semibold">Blockchain Intelligence Dashboard</h2>
              <div className="flex items-center space-x-2">
                {Object.entries(PANEL_TYPES).map(([type, config]) => (
                  <button
                    key={type}
                    onClick={() => addPanel(type)}
                    className="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 text-sm flex items-center space-x-1"
                    title={`Add ${config.name}`}
                  >
                    <span>{config.icon}</span>
                    <span>{config.name}</span>
                  </button>
                ))}
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              <button
                className="px-3 py-1 bg-gray-500 text-white rounded hover:bg-gray-600 text-sm"
                onClick={() => {
                  const blob = new Blob([JSON.stringify(layout, null, 2)], { type: 'application/json' });
                  const url = URL.createObjectURL(blob);
                  const a = document.createElement('a');
                  a.href = url;
                  a.download = 'workspace_layout.json';
                  a.click();
                  URL.revokeObjectURL(url);
                }}
              >
                Export Layout
              </button>
              
              <div className="flex items-center space-x-1 text-sm text-gray-600">
                <div className={`w-2 h-2 rounded-full ${layout.auto_refresh ? 'bg-green-500' : 'bg-gray-400'}`}></div>
                <span>Auto-refresh: {layout.auto_refresh ? 'On' : 'Off'}</span>
              </div>
            </div>
          </div>
        )}

        {/* Main Grid */}
        <div style={gridStyle} className="workspace-grid">
          {layout.panels.map(panel => (
            <WorkspacePanel
              key={panel.id}
              panel={panel}
              layout={layout}
              onMove={movePanel}
              onResize={resizePanel}
              onToggleState={togglePanelState}
              onRemove={removePanel}
              onSelect={setSelectedPanel}
              isSelected={selectedPanel === panel.id}
              readOnly={readOnly}
            />
          ))}
        </div>

        {/* Panel Configuration Sidebar */}
        {selectedPanel && !readOnly && (
          <PanelConfigSidebar
            panel={layout.panels.find(p => p.id === selectedPanel)!}
            onConfigChange={(config) => {
              const updatedLayout = {
                ...layout,
                panels: layout.panels.map(p =>
                  p.id === selectedPanel ? { ...p, config } : p
                )
              };
              updateLayout(updatedLayout);
            }}
            onClose={() => setSelectedPanel(null)}
          />
        )}
      </div>
    </DndProvider>
  );
}

// Individual panel component
interface WorkspacePanelProps {
  panel: Panel;
  layout: WorkspaceLayout;
  onMove: (id: string, position: { x: number; y: number }) => void;
  onResize: (id: string, size: { width: number; height: number }) => void;
  onToggleState: (id: string, state: 'minimized' | 'maximized') => void;
  onRemove: (id: string) => void;
  onSelect: (id: string) => void;
  isSelected: boolean;
  readOnly: boolean;
}

function WorkspacePanel({
  panel,
  layout,
  onMove,
  onResize,
  onToggleState,
  onRemove,
  onSelect,
  isSelected,
  readOnly
}: WorkspacePanelProps) {
  const [{ isDragging }, drag] = useDrag({
    type: 'panel',
    item: { id: panel.id, type: panel.type },
    collect: (monitor) => ({
      isDragging: monitor.isDragging()
    }),
    canDrag: !readOnly
  });

  const [, drop] = useDrop({
    accept: 'panel',
    drop: (item: { id: string }, monitor) => {
      if (item.id !== panel.id && !readOnly) {
        // Handle drop logic here
        console.log('Dropped', item.id, 'onto', panel.id);
      }
    }
  });

  const panelStyle: React.CSSProperties = {
    gridColumn: `${panel.position.x + 1} / span ${panel.size.width}`,
    gridRow: `${panel.position.y + 1} / span ${panel.size.height}`,
    backgroundColor: layout.theme.panel_background,
    border: `2px solid ${isSelected ? '#3b82f6' : layout.theme.border_color}`,
    borderRadius: '8px',
    display: 'flex',
    flexDirection: 'column',
    overflow: 'hidden',
    opacity: isDragging ? 0.5 : 1,
    cursor: readOnly ? 'default' : 'move'
  };

  const renderPanelContent = () => {
    if (panel.minimized) {
      return (
        <div className="flex items-center justify-center h-full text-gray-500">
          Panel minimized
        </div>
      );
    }

    switch (panel.type) {
      case 'deckgl_explorer':
        return (
          <DeckGLExplorer
            {...panel.config}
            width="100%"
            height="100%"
          />
        );
      
      case 'compliance_map':
        return (
          <ComplianceMap
            {...panel.config}
            width="100%"
            height="100%"
          />
        );
      
      case 'timeseries_canvas':
        // Special handling for canvas-based charts
        return (
          <div 
            id={`chart_${panel.id}`}
            className="w-full h-full"
            ref={(el) => {
              if (el && !el.hasChildNodes()) {
                // Initialize chart
                createTimeSeriesChart({
                  container: `chart_${panel.id}`,
                  ...panel.config
                });
              }
            }}
          />
        );
      
      default:
        return (
          <div className="flex items-center justify-center h-full text-gray-500">
            Unknown panel type: {panel.type}
          </div>
        );
    }
  };

  return (
    <div
      ref={(node) => drag(drop(node))}
      style={panelStyle}
      onClick={() => onSelect(panel.id)}
      className="workspace-panel"
    >
      {/* Panel Header */}
      <div className="panel-header flex items-center justify-between px-3 py-2 bg-gray-50 border-b">
        <div className="flex items-center space-x-2">
          <span>{PANEL_TYPES[panel.type]?.icon}</span>
          <span className="font-medium text-sm">{panel.title}</span>
        </div>
        
        {!readOnly && (
          <div className="flex items-center space-x-1">
            <button
              onClick={(e) => {
                e.stopPropagation();
                onToggleState(panel.id, 'minimized');
              }}
              className="p-1 hover:bg-gray-200 rounded"
              title="Minimize"
            >
              {panel.minimized ? '🔼' : '🔽'}
            </button>
            
            <button
              onClick={(e) => {
                e.stopPropagation();
                onToggleState(panel.id, 'maximized');
              }}
              className="p-1 hover:bg-gray-200 rounded"
              title="Maximize"
            >
              {panel.maximized ? '⊡' : '⊞'}
            </button>
            
            <button
              onClick={(e) => {
                e.stopPropagation();
                onRemove(panel.id);
              }}
              className="p-1 hover:bg-red-200 rounded text-red-600"
              title="Remove"
            >
              ✕
            </button>
          </div>
        )}
      </div>

      {/* Panel Content */}
      <div className="panel-content flex-1 overflow-hidden">
        {renderPanelContent()}
      </div>
    </div>
  );
}

// Panel configuration sidebar
interface PanelConfigSidebarProps {
  panel: Panel;
  onConfigChange: (config: Record<string, any>) => void;
  onClose: () => void;
}

function PanelConfigSidebar({ panel, onConfigChange, onClose }: PanelConfigSidebarProps) {
  const [config, setConfig] = useState(panel.config);

  const handleConfigUpdate = (key: string, value: any) => {
    const newConfig = { ...config, [key]: value };
    setConfig(newConfig);
    onConfigChange(newConfig);
  };

  return (
    <div className="fixed right-0 top-0 h-full w-80 bg-white border-l shadow-lg z-50 overflow-y-auto">
      <div className="p-4 border-b">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold">Panel Configuration</h3>
          <button
            onClick={onClose}
            className="p-1 hover:bg-gray-200 rounded"
          >
            ✕
          </button>
        </div>
        <p className="text-sm text-gray-600 mt-1">{panel.title}</p>
      </div>

      <div className="p-4 space-y-4">
        {/* Panel type-specific configuration options */}
        {panel.type === 'deckgl_explorer' && (
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium mb-1">Risk Threshold</label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={config.risk_threshold || 0.5}
                onChange={(e) => handleConfigUpdate('risk_threshold', parseFloat(e.target.value))}
                className="w-full"
              />
              <div className="text-xs text-gray-500">{config.risk_threshold || 0.5}</div>
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-1">Entity Types</label>
              {['address', 'contract', 'token', 'transaction'].map(type => (
                <label key={type} className="flex items-center mt-1">
                  <input
                    type="checkbox"
                    checked={config.entity_types?.includes(type) || false}
                    onChange={(e) => {
                      const types = config.entity_types || [];
                      const newTypes = e.target.checked 
                        ? [...types, type]
                        : types.filter((t: string) => t !== type);
                      handleConfigUpdate('entity_types', newTypes);
                    }}
                    className="mr-2"
                  />
                  <span className="text-sm capitalize">{type}</span>
                </label>
              ))}
            </div>
          </div>
        )}

        {panel.type === 'timeseries_canvas' && (
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium mb-1">Time Range</label>
              <select
                value={config.time_range || '24h'}
                onChange={(e) => handleConfigUpdate('time_range', e.target.value)}
                className="w-full p-2 border rounded"
              >
                <option value="1h">1 Hour</option>
                <option value="6h">6 Hours</option>
                <option value="24h">24 Hours</option>
                <option value="7d">7 Days</option>
                <option value="30d">30 Days</option>
              </select>
            </div>
            
            <div>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={config.realtime || false}
                  onChange={(e) => handleConfigUpdate('realtime', e.target.checked)}
                  className="mr-2"
                />
                <span className="text-sm">Real-time Updates</span>
              </label>
            </div>
          </div>
        )}

        {panel.type === 'compliance_map' && (
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium mb-1">Map Type</label>
              <select
                value={config.map_type || 'choropleth'}
                onChange={(e) => handleConfigUpdate('map_type', e.target.value)}
                className="w-full p-2 border rounded"
              >
                <option value="choropleth">Choropleth</option>
                <option value="sankey">Sankey Flow</option>
              </select>
            </div>
            
            <div>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={config.show_sanctions || false}
                  onChange={(e) => handleConfigUpdate('show_sanctions', e.target.checked)}
                  className="mr-2"
                />
                <span className="text-sm">Highlight Sanctions</span>
              </label>
            </div>
          </div>
        )}

        {/* General configuration options */}
        <div className="pt-4 border-t space-y-3">
          <div>
            <label className="block text-sm font-medium mb-1">Panel Title</label>
            <input
              type="text"
              value={panel.title}
              onChange={(e) => {
                // This would need to be handled at the workspace level
                console.log('Title change:', e.target.value);
              }}
              className="w-full p-2 border rounded"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">Refresh Interval (seconds)</label>
            <input
              type="number"
              min="5"
              max="300"
              value={config.refresh_interval || 30}
              onChange={(e) => handleConfigUpdate('refresh_interval', parseInt(e.target.value))}
              className="w-full p-2 border rounded"
            />
          </div>
        </div>
      </div>
    </div>
  );
}
