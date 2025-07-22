import React, { useState, useCallback, useRef } from 'react';
import {
  Box,
  Grid,
  GridItem,
  VStack,
  HStack,
  Flex,
  useColorModeValue,
  Portal,
} from '@chakra-ui/react';
import { DndProvider, useDrag, useDrop, DragSourceMonitor } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import { PanelHeader } from '../molecules/PanelHeader';
import { colors } from '../../theme/colors';
import { transitionPresets } from '../../theme/motion';

// Panel types for different content
export type PanelType = 
  | 'graph-explorer'
  | 'timeseries-chart'
  | 'compliance-map'
  | 'data-table'
  | 'code-console'
  | 'workspace-builder'
  | 'custom';

export interface PanelConfig {
  id: string;
  type: PanelType;
  title: string;
  subtitle?: string;
  component: React.ComponentType<any>;
  props?: Record<string, any>;
  position: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
  isCollapsed?: boolean;
  isMinimized?: boolean;
  isMaximized?: boolean;
  isResizable?: boolean;
  isDraggable?: boolean;
  zIndex?: number;
}

interface DockableLayoutProps {
  panels: PanelConfig[];
  onPanelUpdate?: (panelId: string, updates: Partial<PanelConfig>) => void;
  onPanelClose?: (panelId: string) => void;
  onPanelAdd?: (panel: Omit<PanelConfig, 'id'>) => void;
  gridSize?: number;
  snapToGrid?: boolean;
  showGrid?: boolean;
  maxPanels?: number;
}

interface DraggablePanelProps {
  panel: PanelConfig;
  onUpdate: (updates: Partial<PanelConfig>) => void;
  onClose: () => void;
  gridSize: number;
  snapToGrid: boolean;
}

interface DropZone {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
}

// Custom hook for panel resizing
const useResizable = (
  panel: PanelConfig,
  onUpdate: (updates: Partial<PanelConfig>) => void,
  gridSize: number,
  snapToGrid: boolean
) => {
  const [isResizing, setIsResizing] = useState(false);
  const resizeRef = useRef<HTMLDivElement | null>(null);
  const startPos = useRef({ x: 0, y: 0 });
  const startSize = useRef({ width: 0, height: 0 });

  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    if (!panel.isResizable) return;
    
    setIsResizing(true);
    startPos.current = { x: e.clientX, y: e.clientY };
    startSize.current = { 
      width: panel.position.width, 
      height: panel.position.height 
    };
    
    e.preventDefault();
    e.stopPropagation();
  }, [panel.isResizable, panel.position]);

  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (!isResizing) return;

    const deltaX = e.clientX - startPos.current.x;
    const deltaY = e.clientY - startPos.current.y;
    
    let newWidth = startSize.current.width + deltaX;
    let newHeight = startSize.current.height + deltaY;
    
    // Apply minimum sizes
    newWidth = Math.max(newWidth, gridSize * 3);
    newHeight = Math.max(newHeight, gridSize * 2);
    
    // Snap to grid if enabled
    if (snapToGrid) {
      newWidth = Math.round(newWidth / gridSize) * gridSize;
      newHeight = Math.round(newHeight / gridSize) * gridSize;
    }

    onUpdate({
      position: {
        ...panel.position,
        width: newWidth,
        height: newHeight,
      }
    });
  }, [isResizing, gridSize, snapToGrid, panel.position, onUpdate]);

  const handleMouseUp = useCallback(() => {
    setIsResizing(false);
  }, []);

  React.useEffect(() => {
    if (isResizing) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = 'se-resize';
      document.body.style.userSelect = 'none';
      
      return () => {
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
        document.body.style.cursor = '';
        document.body.style.userSelect = '';
      };
    }
  }, [isResizing, handleMouseMove, handleMouseUp]);

  return {
    resizeRef,
    isResizing,
    handleMouseDown,
  };
};

const DraggablePanel: React.FC<DraggablePanelProps> = ({
  panel,
  onUpdate,
  onClose,
  gridSize,
  snapToGrid,
}) => {
  const { resizeRef, isResizing, handleMouseDown } = useResizable(
    panel,
    onUpdate,
    gridSize,
    snapToGrid
  );

  const [{ isDragging }, drag, dragPreview] = useDrag({
    type: 'panel',
    item: { id: panel.id, type: panel.type },
    canDrag: panel.isDraggable && !isResizing,
    collect: (monitor: DragSourceMonitor) => ({
      isDragging: monitor.isDragging(),
    }),
  });

  const [, drop] = useDrop({
    accept: 'panel',
    hover: (draggedItem: { id: string; type: string }, monitor) => {
      if (draggedItem.id === panel.id) return;
      
      const hoverBoundingRect = resizeRef.current?.getBoundingClientRect();
      if (!hoverBoundingRect) return;

      const clientOffset = monitor.getClientOffset();
      if (!clientOffset) return;

      // Calculate new position
      let newX = clientOffset.x - hoverBoundingRect.width / 2;
      let newY = clientOffset.y - hoverBoundingRect.height / 2;
      
      if (snapToGrid) {
        newX = Math.round(newX / gridSize) * gridSize;
        newY = Math.round(newY / gridSize) * gridSize;
      }
      
      // Ensure panel stays within bounds
      newX = Math.max(0, newX);
      newY = Math.max(0, newY);
      
      onUpdate({
        position: {
          ...panel.position,
          x: newX,
          y: newY,
        }
      });
    },
  });

  const attachRef = (el: HTMLDivElement) => {
    resizeRef.current = el;
    drag(drop(el));
  };

  const bgColor = useColorModeValue('white', 'gray.900');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const shadowColor = useColorModeValue('rgba(0, 0, 0, 0.1)', 'rgba(0, 0, 0, 0.3)');

  const PanelComponent = panel.component;

  if (panel.isMinimized) {
    return (
      <Box
        ref={attachRef}
        position="absolute"
        bottom="20px"
        left={`${panel.position.x}px`}
        width="200px"
        height="40px"
        bg={bgColor}
        border="1px solid"
        borderColor={borderColor}
        borderRadius="md"
        shadow="md"
        opacity={isDragging ? 0.5 : 1}
        cursor={panel.isDraggable ? 'move' : 'default'}
        zIndex={panel.zIndex || 1}
        transition={transitionPresets.panel}
      >
        <PanelHeader
          title={panel.title}
          onMaximize={() => onUpdate({ isMinimized: false })}
          onClose={onClose}
          isDraggable={panel.isDraggable}
          dragHandle
        />
      </Box>
    );
  }

  return (
    <Box
      ref={attachRef}
      position="absolute"
      left={`${panel.position.x}px`}
      top={`${panel.position.y}px`}
      width={`${panel.position.width}px`}
      height={`${panel.position.height}px`}
      bg={bgColor}
      border="1px solid"
      borderColor={borderColor}
      borderRadius="lg"
      shadow={isDragging ? `0 8px 25px ${shadowColor}` : `0 4px 12px ${shadowColor}`}
      opacity={isDragging ? 0.8 : 1}
      zIndex={panel.zIndex || 1}
      overflow="hidden"
      transition={transitionPresets.panel}
      _hover={{
        shadow: `0 6px 20px ${shadowColor}`,
      }}
    >
      <VStack spacing={0} height="100%">
        {/* Panel Header */}
        <PanelHeader
          title={panel.title}
          subtitle={panel.subtitle}
          onClose={onClose}
          onMinimize={() => onUpdate({ isMinimized: true })}
          onMaximize={() => onUpdate({ 
            isMaximized: !panel.isMaximized,
            position: panel.isMaximized ? panel.position : {
              x: 0, y: 0, width: window.innerWidth, height: window.innerHeight
            }
          })}
          isCollapsible={true}
          isCollapsed={panel.isCollapsed}
          onToggleCollapse={() => onUpdate({ isCollapsed: !panel.isCollapsed })}
          isResizable={panel.isResizable}
          isDraggable={panel.isDraggable}
          dragHandle
        />

        {/* Panel Content */}
        {!panel.isCollapsed && (
          <Box flex="1" width="100%" overflow="hidden">
            <PanelComponent {...panel.props} />
          </Box>
        )}
      </VStack>

      {/* Resize Handle */}
      {panel.isResizable && !panel.isCollapsed && (
        <Box
          position="absolute"
          bottom="0"
          right="0"
          width="15px"
          height="15px"
          cursor="se-resize"
          onMouseDown={handleMouseDown}
          _hover={{
            bg: colors.primary[100],
          }}
        >
          <Box
            position="absolute"
            bottom="2px"
            right="2px"
            width="10px"
            height="10px"
            borderRight="2px solid"
            borderBottom="2px solid"
            borderColor="gray.400"
            opacity={0.6}
          />
        </Box>
      )}
    </Box>
  );
};

// Grid background component
const GridBackground: React.FC<{ gridSize: number; show: boolean }> = ({
  gridSize,
  show,
}) => {
  if (!show) return null;

  return (
    <Box
      position="absolute"
      top={0}
      left={0}
      right={0}
      bottom={0}
      opacity={0.1}
      pointerEvents="none"
      backgroundImage={`
        linear-gradient(to right, ${colors.gray[300]} 1px, transparent 1px),
        linear-gradient(to bottom, ${colors.gray[300]} 1px, transparent 1px)
      `}
      backgroundSize={`${gridSize}px ${gridSize}px`}
    />
  );
};

export const DockableLayout: React.FC<DockableLayoutProps> = ({
  panels,
  onPanelUpdate,
  onPanelClose,
  onPanelAdd,
  gridSize = 20,
  snapToGrid = false,
  showGrid = false,
  maxPanels = 10,
}) => {
  const handlePanelUpdate = useCallback((panelId: string, updates: Partial<PanelConfig>) => {
    if (onPanelUpdate) {
      onPanelUpdate(panelId, updates);
    }
  }, [onPanelUpdate]);

  const handlePanelClose = useCallback((panelId: string) => {
    if (onPanelClose) {
      onPanelClose(panelId);
    }
  }, [onPanelClose]);

  return (
    <DndProvider backend={HTML5Backend}>
      <Box
        position="relative"
        width="100%"
        height="100vh"
        bg={useColorModeValue('gray.50', 'gray.800')}
        overflow="hidden"
      >
        <GridBackground gridSize={gridSize} show={showGrid} />
        
        {panels.map((panel) => (
          <DraggablePanel
            key={panel.id}
            panel={panel}
            onUpdate={(updates) => handlePanelUpdate(panel.id, updates)}
            onClose={() => handlePanelClose(panel.id)}
            gridSize={gridSize}
            snapToGrid={snapToGrid}
          />
        ))}
      </Box>
    </DndProvider>
  );
};

// Predefined layout templates
export const layoutTemplates = {
  explorer: (windowWidth: number, windowHeight: number): Partial<PanelConfig>[] => [
    {
      type: 'graph-explorer',
      title: 'Network Graph',
      position: { x: 0, y: 0, width: windowWidth * 0.6, height: windowHeight * 0.7 },
    },
    {
      type: 'data-table',
      title: 'Transaction Details',
      position: { x: windowWidth * 0.6, y: 0, width: windowWidth * 0.4, height: windowHeight * 0.5 },
    },
    {
      type: 'timeseries-chart',
      title: 'Activity Timeline',
      position: { x: 0, y: windowHeight * 0.7, width: windowWidth, height: windowHeight * 0.3 },
    },
  ],
  
  dashboard: (windowWidth: number, windowHeight: number): Partial<PanelConfig>[] => [
    {
      type: 'timeseries-chart',
      title: 'Transaction Volume',
      position: { x: 0, y: 0, width: windowWidth * 0.5, height: windowHeight * 0.4 },
    },
    {
      type: 'compliance-map',
      title: 'Risk Heatmap',
      position: { x: windowWidth * 0.5, y: 0, width: windowWidth * 0.5, height: windowHeight * 0.4 },
    },
    {
      type: 'data-table',
      title: 'High Risk Addresses',
      position: { x: 0, y: windowHeight * 0.4, width: windowWidth, height: windowHeight * 0.6 },
    },
  ],
  
  analysis: (windowWidth: number, windowHeight: number): Partial<PanelConfig>[] => [
    {
      type: 'graph-explorer',
      title: 'Address Cluster',
      position: { x: 0, y: 0, width: windowWidth * 0.7, height: windowHeight * 0.6 },
    },
    {
      type: 'code-console',
      title: 'Analysis Console',
      position: { x: 0, y: windowHeight * 0.6, width: windowWidth * 0.7, height: windowHeight * 0.4 },
    },
    {
      type: 'data-table',
      title: 'Evidence Table',
      position: { x: windowWidth * 0.7, y: 0, width: windowWidth * 0.3, height: windowHeight },
    },
  ],
};

export default DockableLayout;
