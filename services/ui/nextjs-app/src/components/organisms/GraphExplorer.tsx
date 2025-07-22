import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Button,
  Slider,
  SliderTrack,
  SliderFilledTrack,
  SliderThumb,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  Badge,
  Tooltip,
  useColorModeValue,
  Flex,
  Spacer,
} from '@chakra-ui/react';
import { Icon } from '../atoms/Icon';
import { Spinner } from '../atoms/Spinner';
import { ChartHeader } from '../molecules/PanelHeader';
import { colors } from '../../theme/colors';
import { textStyles } from '../../theme/typography';

// Graph node and edge types for blockchain data
export interface GraphNode {
  id: string;
  label: string;
  type: 'address' | 'contract' | 'transaction' | 'block' | 'token';
  value?: number; // For sizing nodes
  riskScore?: number;
  balance?: number;
  txCount?: number;
  metadata?: Record<string, any>;
  x?: number;
  y?: number;
  color?: string;
  size?: number;
  isSelected?: boolean;
  isHovered?: boolean;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  type: 'transfer' | 'contract_call' | 'creation' | 'approval';
  value?: number;
  timestamp?: number;
  txHash?: string;
  weight?: number;
  color?: string;
  width?: number;
  isSelected?: boolean;
  isHovered?: boolean;
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

interface GraphExplorerProps {
  data: GraphData;
  isLoading?: boolean;
  width?: number;
  height?: number;
  onNodeClick?: (node: GraphNode) => void;
  onEdgeClick?: (edge: GraphEdge) => void;
  onNodeHover?: (node: GraphNode | null) => void;
  onEdgeHover?: (edge: GraphEdge | null) => void;
  onSelectionChange?: (selectedNodes: GraphNode[], selectedEdges: GraphEdge[]) => void;
  layoutType?: 'force' | 'circular' | 'hierarchical' | 'grid';
  showLabels?: boolean;
  enableZoom?: boolean;
  enablePan?: boolean;
  enableSelection?: boolean;
}

interface GraphControlsProps {
  layoutType: string;
  onLayoutChange: (layout: string) => void;
  showLabels: boolean;
  onToggleLabels: () => void;
  nodeScale: number;
  onNodeScaleChange: (scale: number) => void;
  edgeWidth: number;
  onEdgeWidthChange: (width: number) => void;
  onFitToScreen: () => void;
  onResetZoom: () => void;
  onExport: () => void;
  selectedCount: number;
  onClearSelection: () => void;
}

const GraphControls: React.FC<GraphControlsProps> = ({
  layoutType,
  onLayoutChange,
  showLabels,
  onToggleLabels,
  nodeScale,
  onNodeScaleChange,
  edgeWidth,
  onEdgeWidthChange,
  onFitToScreen,
  onResetZoom,
  onExport,
  selectedCount,
  onClearSelection,
}) => {
  const layoutOptions = [
    { value: 'force', label: 'Force Directed' },
    { value: 'circular', label: 'Circular' },
    { value: 'hierarchical', label: 'Hierarchical' },
    { value: 'grid', label: 'Grid' },
  ];

  return (
    <VStack spacing={4} align="stretch" p={4} bg={useColorModeValue('white', 'gray.800')}>
      {/* Layout Controls */}
      <Box>
        <Text fontSize="xs" fontWeight="semibold" color="gray.600" mb={2}>
          Layout
        </Text>
        <Menu>
          <MenuButton as={Button} size="sm" variant="outline" rightIcon={<Icon name="chevron-down" size="xs" />}>
            {layoutOptions.find(opt => opt.value === layoutType)?.label || 'Force Directed'}
          </MenuButton>
          <MenuList>
            {layoutOptions.map((option) => (
              <MenuItem key={option.value} onClick={() => onLayoutChange(option.value)}>
                <Icon name="graph" size="sm" mr={2} />
                {option.label}
              </MenuItem>
            ))}
          </MenuList>
        </Menu>
      </Box>

      {/* Display Controls */}
      <Box>
        <Text fontSize="xs" fontWeight="semibold" color="gray.600" mb={2}>
          Display
        </Text>
        <VStack spacing={2} align="stretch">
          <HStack>
            <Button
              size="xs"
              variant={showLabels ? 'primary' : 'outline'}
              onClick={onToggleLabels}
              leftIcon={<Icon name="tag" size="xs" />}
            >
              Labels
            </Button>
            {selectedCount > 0 && (
              <Button
                size="xs"
                variant="outline"
                onClick={onClearSelection}
                leftIcon={<Icon name="close" size="xs" />}
              >
                Clear ({selectedCount})
              </Button>
            )}
          </HStack>
        </VStack>
      </Box>

      {/* Size Controls */}
      <Box>
        <Text fontSize="xs" fontWeight="semibold" color="gray.600" mb={2}>
          Node Size
        </Text>
        <Slider
          value={nodeScale}
          onChange={onNodeScaleChange}
          min={0.5}
          max={2}
          step={0.1}
          size="sm"
        >
          <SliderTrack>
            <SliderFilledTrack />
          </SliderTrack>
          <SliderThumb />
        </Slider>
        <HStack justify="space-between" mt={1}>
          <Text fontSize="xs" color="gray.500">Small</Text>
          <Text fontSize="xs" color="gray.500">Large</Text>
        </HStack>
      </Box>

      <Box>
        <Text fontSize="xs" fontWeight="semibold" color="gray.600" mb={2}>
          Edge Width
        </Text>
        <Slider
          value={edgeWidth}
          onChange={onEdgeWidthChange}
          min={1}
          max={5}
          step={0.5}
          size="sm"
        >
          <SliderTrack>
            <SliderFilledTrack />
          </SliderTrack>
          <SliderThumb />
        </Slider>
        <HStack justify="space-between" mt={1}>
          <Text fontSize="xs" color="gray.500">Thin</Text>
          <Text fontSize="xs" color="gray.500">Thick</Text>
        </HStack>
      </Box>

      {/* View Controls */}
      <Box>
        <Text fontSize="xs" fontWeight="semibold" color="gray.600" mb={2}>
          View
        </Text>
        <VStack spacing={1}>
          <Button size="xs" variant="ghost" onClick={onFitToScreen} leftIcon={<Icon name="expand" size="xs" />}>
            Fit to Screen
          </Button>
          <Button size="xs" variant="ghost" onClick={onResetZoom} leftIcon={<Icon name="refresh" size="xs" />}>
            Reset Zoom
          </Button>
          <Button size="xs" variant="ghost" onClick={onExport} leftIcon={<Icon name="download" size="xs" />}>
            Export Image
          </Button>
        </VStack>
      </Box>
    </VStack>
  );
};

interface NodeInfoPanelProps {
  node: GraphNode | null;
  onClose: () => void;
}

const NodeInfoPanel: React.FC<NodeInfoPanelProps> = ({ node, onClose }) => {
  if (!node) return null;

  const getNodeColor = (type: string) => {
    switch (type) {
      case 'address': return colors.entity.address;
      case 'contract': return colors.entity.contract;
      case 'transaction': return colors.entity.transaction;
      case 'token': return colors.entity.token;
      case 'block': return colors.entity.block;
      default: return colors.gray[500];
    }
  };

  const getRiskColor = (score: number) => {
    if (score >= 80) return colors.risk.critical;
    if (score >= 60) return colors.risk.high;
    if (score >= 40) return colors.risk.medium;
    return colors.risk.low;
  };

  return (
    <Box
      position="absolute"
      top="20px"
      right="20px"
      width="300px"
      bg={useColorModeValue('white', 'gray.800')}
      border="1px solid"
      borderColor={useColorModeValue('gray.200', 'gray.600')}
      borderRadius="lg"
      shadow="lg"
      p={4}
      zIndex={10}
    >
      <VStack spacing={3} align="stretch">
        {/* Header */}
        <HStack>
          <Icon name={node.type as any} color={getNodeColor(node.type)} size="md" />
          <VStack spacing={0} align="start" flex="1">
            <Text {...textStyles.body}>
              {node.label}
            </Text>
            <Badge colorScheme="blue" fontSize="xs">
              {node.type.toUpperCase()}
            </Badge>
          </VStack>
          <Button size="xs" variant="ghost" onClick={onClose}>
            <Icon name="close" size="xs" />
          </Button>
        </HStack>

        {/* Risk Score */}
        {node.riskScore !== undefined && (
          <HStack justify="space-between">
            <Text fontSize="sm" color="gray.600">Risk Score</Text>
            <Badge
              colorScheme="red"
              fontSize="xs"
              bg={getRiskColor(node.riskScore)}
              color="white"
            >
              {node.riskScore}/100
            </Badge>
          </HStack>
        )}

        {/* Balance */}
        {node.balance !== undefined && (
          <HStack justify="space-between">
            <Text fontSize="sm" color="gray.600">Balance</Text>
            <Text fontSize="sm" fontWeight="medium">
              {node.balance.toLocaleString()} ETH
            </Text>
          </HStack>
        )}

        {/* Transaction Count */}
        {node.txCount !== undefined && (
          <HStack justify="space-between">
            <Text fontSize="sm" color="gray.600">Transactions</Text>
            <Text fontSize="sm" fontWeight="medium">
              {node.txCount.toLocaleString()}
            </Text>
          </HStack>
        )}

        {/* Metadata */}
        {node.metadata && Object.keys(node.metadata).length > 0 && (
          <Box>
            <Text fontSize="xs" fontWeight="semibold" color="gray.600" mb={2}>
              Additional Info
            </Text>
            <VStack spacing={1} align="stretch">
              {Object.entries(node.metadata).slice(0, 5).map(([key, value]) => (
                <HStack key={key} justify="space-between">
                  <Text fontSize="xs" color="gray.500" textTransform="capitalize">
                    {key.replace(/([A-Z])/g, ' $1')}
                  </Text>
                  <Text fontSize="xs" fontWeight="medium" noOfLines={1}>
                    {String(value)}
                  </Text>
                </HStack>
              ))}
            </VStack>
          </Box>
        )}

        {/* Actions */}
        <HStack spacing={2}>
          <Button size="xs" variant="primary" flex="1">
            <Icon name="search" size="xs" mr={1} />
            Explore
          </Button>
          <Button size="xs" variant="outline" flex="1">
            <Icon name="flag" size="xs" mr={1} />
            Flag
          </Button>
        </HStack>
      </VStack>
    </Box>
  );
};

export const GraphExplorer: React.FC<GraphExplorerProps> = ({
  data,
  isLoading = false,
  width = 800,
  height = 600,
  onNodeClick,
  onEdgeClick,
  onNodeHover,
  onEdgeHover,
  onSelectionChange,
  layoutType = 'force',
  showLabels = true,
  enableZoom = true,
  enablePan = true,
  enableSelection = true,
}) => {
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [selectedNodes, setSelectedNodes] = useState<GraphNode[]>([]);
  const [selectedEdges, setSelectedEdges] = useState<GraphEdge[]>([]);
  const [currentLayout, setCurrentLayout] = useState(layoutType);
  const [showNodeLabels, setShowNodeLabels] = useState(showLabels);
  const [nodeScale, setNodeScale] = useState(1);
  const [edgeWidth, setEdgeWidth] = useState(2);
  const [isControlsOpen, setIsControlsOpen] = useState(false);

  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Mock graph rendering - In a real implementation, this would use D3.js or similar
  const renderGraph = useCallback(() => {
    if (!canvasRef.current) return;
    
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Set canvas size
    canvas.width = width;
    canvas.height = height;

    // Draw edges first (behind nodes)
    data.edges.forEach((edge) => {
      const sourceNode = data.nodes.find(n => n.id === edge.source);
      const targetNode = data.nodes.find(n => n.id === edge.target);
      
      if (!sourceNode || !targetNode) return;

      ctx.beginPath();
      ctx.moveTo(sourceNode.x || 0, sourceNode.y || 0);
      ctx.lineTo(targetNode.x || 0, targetNode.y || 0);
      ctx.strokeStyle = edge.color || colors.gray[300];
      ctx.lineWidth = (edge.width || edgeWidth) * (edge.isSelected ? 1.5 : 1);
      ctx.stroke();
    });

    // Draw nodes
    data.nodes.forEach((node) => {
      const radius = (node.size || 10) * nodeScale * (node.isSelected ? 1.2 : 1);
      
      ctx.beginPath();
      ctx.arc(node.x || 0, node.y || 0, radius, 0, 2 * Math.PI);
      ctx.fillStyle = node.color || colors.primary[500];
      ctx.fill();
      
      if (node.isSelected) {
        ctx.strokeStyle = colors.primary[700];
        ctx.lineWidth = 2;
        ctx.stroke();
      }

      // Draw labels if enabled
      if (showNodeLabels && node.label) {
        ctx.fillStyle = useColorModeValue('black', 'white');
        ctx.font = '12px Inter';
        ctx.textAlign = 'center';
        ctx.fillText(node.label, node.x || 0, (node.y || 0) + radius + 15);
      }
    });
  }, [data, width, height, nodeScale, edgeWidth, showNodeLabels, useColorModeValue]);

  useEffect(() => {
    renderGraph();
  }, [renderGraph]);

  const handleNodeClick = useCallback((event: React.MouseEvent<HTMLCanvasElement>) => {
    if (!canvasRef.current) return;
    
    const rect = canvasRef.current.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    
    // Find clicked node (simplified hit detection)
    const clickedNode = data.nodes.find(node => {
      const nodeX = node.x || 0;
      const nodeY = node.y || 0;
      const radius = (node.size || 10) * nodeScale;
      const distance = Math.sqrt((x - nodeX) ** 2 + (y - nodeY) ** 2);
      return distance <= radius;
    });
    
    if (clickedNode) {
      setSelectedNode(clickedNode);
      if (onNodeClick) {
        onNodeClick(clickedNode);
      }
    } else {
      setSelectedNode(null);
    }
  }, [data.nodes, nodeScale, onNodeClick]);

  const handleFitToScreen = useCallback(() => {
    // In a real implementation, this would adjust the viewport to fit all nodes
    console.log('Fitting graph to screen');
  }, []);

  const handleResetZoom = useCallback(() => {
    // In a real implementation, this would reset zoom and pan
    console.log('Resetting zoom');
  }, []);

  const handleExport = useCallback(() => {
    if (!canvasRef.current) return;
    
    const link = document.createElement('a');
    link.download = 'graph-export.png';
    link.href = canvasRef.current.toDataURL();
    link.click();
  }, []);

  const handleClearSelection = useCallback(() => {
    setSelectedNodes([]);
    setSelectedEdges([]);
    setSelectedNode(null);
    if (onSelectionChange) {
      onSelectionChange([], []);
    }
  }, [onSelectionChange]);

  if (isLoading) {
    return (
      <Box
        width="100%"
        height="100%"
        display="flex"
        alignItems="center"
        justifyContent="center"
        bg={useColorModeValue('gray.50', 'gray.900')}
      >
        <VStack spacing={4}>
          <Spinner size="lg" variant="ring" />
          <Text color="gray.500" {...textStyles.body}>
            Loading graph data...
          </Text>
        </VStack>
      </Box>
    );
  }

  return (
    <Box position="relative" width="100%" height="100%" overflow="hidden">
      {/* Main Graph Canvas */}
      <Box
        ref={containerRef}
        width="100%"
        height="100%"
        bg={useColorModeValue('white', 'gray.900')}
        position="relative"
      >
        <canvas
          ref={canvasRef}
          width={width}
          height={height}
          onClick={handleNodeClick}
          style={{
            width: '100%',
            height: '100%',
            cursor: enablePan ? 'grab' : 'default',
          }}
        />
        
        {/* Graph Stats Overlay */}
        <Box
          position="absolute"
          bottom="20px"
          left="20px"
          bg={useColorModeValue('white', 'gray.800')}
          px={3}
          py={2}
          borderRadius="md"
          shadow="sm"
          border="1px solid"
          borderColor={useColorModeValue('gray.200', 'gray.600')}
        >
          <HStack spacing={4}>
            <HStack spacing={1}>
              <Icon name="graph" size="xs" color="gray.500" />
              <Text fontSize="xs" color="gray.600">
                {data.nodes.length} nodes
              </Text>
            </HStack>
            <HStack spacing={1}>
              <Icon name="link" size="xs" color="gray.500" />
              <Text fontSize="xs" color="gray.600">
                {data.edges.length} edges
              </Text>
            </HStack>
            {selectedNodes.length > 0 && (
              <HStack spacing={1}>
                <Icon name="check" size="xs" color={colors.primary[500]} />
                <Text fontSize="xs" color={colors.primary[500]}>
                  {selectedNodes.length} selected
                </Text>
              </HStack>
            )}
          </HStack>
        </Box>

        {/* Controls Toggle */}
        <Box position="absolute" top="20px" left="20px">
          <Button
            size="sm"
            variant={isControlsOpen ? 'primary' : 'outline'}
            onClick={() => setIsControlsOpen(!isControlsOpen)}
            leftIcon={<Icon name="settings" size="sm" />}
          >
            Controls
          </Button>
        </Box>
      </Box>

      {/* Controls Panel */}
      {isControlsOpen && (
        <Box
          position="absolute"
          top="0"
          left="0"
          width="300px"
          height="100%"
          bg={useColorModeValue('white', 'gray.800')}
          borderRight="1px solid"
          borderColor={useColorModeValue('gray.200', 'gray.600')}
          shadow="lg"
          zIndex={5}
        >
          <VStack spacing={0} height="100%">
            <HStack justify="space-between" w="100%" p={4} borderBottom="1px solid" borderColor={useColorModeValue('gray.200', 'gray.600')}>
              <Text {...textStyles.h4}>Graph Controls</Text>
              <Button size="xs" variant="ghost" onClick={() => setIsControlsOpen(false)}>
                <Icon name="close" size="xs" />
              </Button>
            </HStack>
            <Box flex="1" overflow="auto" width="100%">
              <GraphControls
                layoutType={currentLayout}
                onLayoutChange={(layout) => setCurrentLayout(layout as any)}
                showLabels={showNodeLabels}
                onToggleLabels={() => setShowNodeLabels(!showNodeLabels)}
                nodeScale={nodeScale}
                onNodeScaleChange={setNodeScale}
                edgeWidth={edgeWidth}
                onEdgeWidthChange={setEdgeWidth}
                onFitToScreen={handleFitToScreen}
                onResetZoom={handleResetZoom}
                onExport={handleExport}
                selectedCount={selectedNodes.length + selectedEdges.length}
                onClearSelection={handleClearSelection}
              />
            </Box>
          </VStack>
        </Box>
      )}

      {/* Node Info Panel */}
      <NodeInfoPanel
        node={selectedNode}
        onClose={() => setSelectedNode(null)}
      />
    </Box>
  );
};

export default GraphExplorer;
