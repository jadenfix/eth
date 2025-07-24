/**
 * Enhanced Palantir-style Network Graph Component
 * Real-time blockchain entity visualization with premium aesthetics
 */

import React, { useRef, useEffect, useState, useCallback } from 'react';
import { Box, VStack, HStack, Text, Badge, IconButton, Tooltip, useColorMode } from '@chakra-ui/react';
import { SearchIcon, SettingsIcon, DownloadIcon, ViewIcon, RepeatIcon } from '@chakra-ui/icons';
import { motion, AnimatePresence } from 'framer-motion';
import * as d3 from 'd3';

const MotionBox = motion(Box);
const MotionVStack = motion(VStack);

interface Node {
  id: string;
  address: string;
  type: 'wallet' | 'contract' | 'token' | 'exchange';
  riskScore: number;
  transactionCount: number;
  balance?: number;
  x?: number;
  y?: number;
  vx?: number;
  vy?: number;
  fx?: number | null;
  fy?: number | null;
}

interface Link {
  source: string | Node;
  target: string | Node;
  value: number;
  type: 'transfer' | 'approval' | 'interaction';
  timestamp: string;
}

interface GraphData {
  nodes: Node[];
  links: Link[];
}

interface PalantirNetworkGraphProps {
  data?: GraphData;
  onNodeClick?: (node: Node) => void;
  onLinkClick?: (link: Link) => void;
  height?: number;
  width?: number;
  enablePhysics?: boolean;
  showLabels?: boolean;
}

const PalantirNetworkGraph: React.FC<PalantirNetworkGraphProps> = ({
  data,
  onNodeClick,
  onLinkClick,
  height = 600,
  width = 800,
  enablePhysics = true,
  showLabels = true
}) => {
  const { colorMode } = useColorMode();
  const svgRef = useRef<SVGSVGElement>(null);
  const simulationRef = useRef<d3.Simulation<Node, Link> | null>(null);
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const [isSimulationRunning, setIsSimulationRunning] = useState(false);
  const [hoveredNode, setHoveredNode] = useState<Node | null>(null);

  // Color scales for different node types
  const nodeColorScale = d3.scaleOrdinal<string>()
    .domain(['wallet', 'contract', 'token', 'exchange'])
    .range(['#60A5FA', '#F59E0B', '#10B981', '#EF4444']);

  // Risk score color scale
  const riskColorScale = d3.scaleSequential(d3.interpolateRdYlGn)
    .domain([1, 0]); // High risk = red, low risk = green

  // Node size scale based on transaction count
  const nodeSizeScale = d3.scaleSqrt()
    .domain([0, 1000])
    .range([4, 20]);

  // Link width scale based on value
  const linkWidthScale = d3.scaleSqrt()
    .domain([0, 100])
    .range([1, 8]);

  const initializeGraph = useCallback(() => {
    if (!data || !svgRef.current) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    // Create container groups
    const container = svg.append("g");
    const linksGroup = container.append("g").attr("class", "links");
    const nodesGroup = container.append("g").attr("class", "nodes");
    const labelsGroup = container.append("g").attr("class", "labels");

    // Add zoom behavior
    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.1, 10])
      .on("zoom", (event: any) => {
        container.attr("transform", event.transform);
      });

    svg.call(zoom);

    // Initialize force simulation
    if (enablePhysics) {
      simulationRef.current = d3.forceSimulation(data.nodes)
        .force("link", d3.forceLink(data.links).id((d: any) => d.id).strength(0.1))
        .force("charge", d3.forceManyBody().strength(-300))
        .force("center", d3.forceCenter(width / 2, height / 2))
        .force("collision", d3.forceCollide().radius((d: any) => nodeSizeScale(d.transactionCount) + 2))
        .alpha(0.3);

      setIsSimulationRunning(true);
    } else {
      // Static layout - arrange in a circle
      data.nodes.forEach((node, i) => {
        const angle = (i / data.nodes.length) * 2 * Math.PI;
        const radius = Math.min(width, height) / 3;
        node.x = width / 2 + radius * Math.cos(angle);
        node.y = height / 2 + radius * Math.sin(angle);
      });
    }

    // Draw links
    const links = linksGroup
      .selectAll("line")
      .data(data.links)
      .enter()
      .append("line")
      .attr("stroke", "#64748B")
      .attr("stroke-opacity", 0.6)
      .attr("stroke-width", (d: Link) => linkWidthScale(d.value))
      .style("cursor", "pointer")
      .on("click", (event: any, d: Link) => {
        event.stopPropagation();
        onLinkClick?.(d);
      })
      .on("mouseover", function(this: SVGLineElement, event: any, d: Link) {
        d3.select(this).attr("stroke", "#3B82F6").attr("stroke-opacity", 1);
        
        // Show tooltip
        const tooltip = d3.select("body").append("div")
          .attr("class", "tooltip")
          .style("position", "absolute")
          .style("background", "rgba(0, 0, 0, 0.8)")
          .style("color", "white")
          .style("padding", "8px")
          .style("border-radius", "4px")
          .style("font-size", "12px")
          .style("pointer-events", "none")
          .style("z-index", "1000")
          .html(`
            <div><strong>${d.type.toUpperCase()}</strong></div>
            <div>Value: ${d.value.toFixed(2)} ETH</div>
            <div>Time: ${new Date(d.timestamp).toLocaleString()}</div>
          `);

        tooltip
          .style("left", (event.pageX + 10) + "px")
          .style("top", (event.pageY - 10) + "px");
      })
      .on("mouseout", function(this: SVGLineElement) {
        d3.select(this).attr("stroke", "#64748B").attr("stroke-opacity", 0.6);
        d3.selectAll(".tooltip").remove();
      });

    // Draw nodes
    const nodes = nodesGroup
      .selectAll("circle")
      .data(data.nodes)
      .enter()
      .append("circle")
      .attr("r", (d: Node) => nodeSizeScale(d.transactionCount))
      .attr("fill", (d: Node) => {
        // Use risk score for fill if available, otherwise use type
        return d.riskScore > 0.7 ? riskColorScale(d.riskScore) : nodeColorScale(d.type);
      })
      .attr("stroke", "#1F2937")
      .attr("stroke-width", 2)
      .style("cursor", "pointer")
      .on("click", (event: any, d: Node) => {
        event.stopPropagation();
        setSelectedNode(d);
        onNodeClick?.(d);
      })
      .on("mouseover", function(this: SVGCircleElement, event: any, d: Node) {
        d3.select(this).attr("stroke", "#3B82F6").attr("stroke-width", 3);
        
        // Show tooltip
        const tooltip = d3.select("body").append("div")
          .attr("class", "tooltip")
          .style("position", "absolute")
          .style("background", "rgba(0, 0, 0, 0.9)")
          .style("color", "white")
          .style("padding", "12px")
          .style("border-radius", "6px")
          .style("font-size", "12px")
          .style("pointer-events", "none")
          .style("z-index", "1000")
          .html(`
            <div><strong>${d.id}</strong></div>
            <div>Type: ${d.type.toUpperCase()}</div>
            <div>Address: ${d.address.slice(0, 10)}...</div>
            <div>Risk Score: ${(d.riskScore * 100).toFixed(1)}%</div>
            <div>Transactions: ${d.transactionCount.toLocaleString()}</div>
            ${d.balance ? `<div>Balance: ${d.balance.toFixed(2)} ETH</div>` : ''}
          `);

        tooltip
          .style("left", (event.pageX + 10) + "px")
          .style("top", (event.pageY - 10) + "px");
      })
      .on("mouseout", function(this: SVGCircleElement) {
        d3.select(this).attr("stroke", "#1F2937").attr("stroke-width", 2);
        d3.selectAll(".tooltip").remove();
      });

    // Add labels if enabled
    if (showLabels) {
      const labels = labelsGroup
        .selectAll("text")
        .data(data.nodes)
        .enter()
        .append("text")
        .text((d: Node) => d.id.slice(0, 8) + '...')
        .attr("font-size", "10px")
        .attr("fill", "#E5E7EB")
        .attr("text-anchor", "middle")
        .attr("dominant-baseline", "middle")
        .style("pointer-events", "none")
        .style("user-select", "none");
    }

    // Update positions on simulation tick
    if (simulationRef.current) {
      simulationRef.current.on("tick", () => {
        links
          .attr("x1", (d: any) => d.source.x)
          .attr("y1", (d: any) => d.source.y)
          .attr("x2", (d: any) => d.target.x)
          .attr("y2", (d: any) => d.target.y);

        nodes
          .attr("cx", (d: Node) => d.x!)
          .attr("cy", (d: Node) => d.y!);

        if (showLabels) {
          labelsGroup.selectAll("text")
            .attr("x", (d: any) => d.x)
            .attr("y", (d: any) => d.y + nodeSizeScale(d.transactionCount) + 12);
        }
      });

      simulationRef.current.on("end", () => {
        setIsSimulationRunning(false);
      });
    } else {
      // Static positioning
      links
        .attr("x1", (d: any) => d.source.x || 0)
        .attr("y1", (d: any) => d.source.y || 0)
        .attr("x2", (d: any) => d.target.x || 0)
        .attr("y2", (d: any) => d.target.y || 0);

      nodes
        .attr("cx", (d) => d.x!)
        .attr("cy", (d) => d.y!);

      if (showLabels) {
        labelsGroup.selectAll("text")
          .attr("x", (d: any) => d.x)
          .attr("y", (d: any) => d.y + nodeSizeScale(d.transactionCount) + 12);
      }
    }

    // Add drag behavior
    const drag = d3.drag<SVGCircleElement, Node>()
      .on("start", function(event, d) {
        if (simulationRef.current && !event.active) {
          simulationRef.current.alphaTarget(0.3).restart();
        }
        d.fx = d.x;
        d.fy = d.y;
      })
      .on("drag", function(event, d) {
        d.fx = event.x;
        d.fy = event.y;
      })
      .on("end", function(event, d) {
        if (simulationRef.current && !event.active) {
          simulationRef.current.alphaTarget(0);
        }
        d.fx = null;
        d.fy = null;
      });

    nodes.call(drag);

  }, [data, enablePhysics, showLabels, height, width, onNodeClick, onLinkClick]);

  useEffect(() => {
    initializeGraph();
    
    return () => {
      if (simulationRef.current) {
        simulationRef.current.stop();
      }
    };
  }, [initializeGraph]);

  // Generate sample data if none provided
  const sampleData: GraphData = {
    nodes: [
      { id: "wallet_1", address: "0x742E7a9D7D0f4e7B4C7D7A7C7A7B7C7D7E7F7A7B", type: "wallet", riskScore: 0.2, transactionCount: 150 },
      { id: "contract_1", address: "0xA0b86a33E6eF77e6C6A23bE1E1E6A0C0A0C0B0C0", type: "contract", riskScore: 0.1, transactionCount: 500 },
      { id: "exchange_1", address: "0x1111111111111111111111111111111111111111", type: "exchange", riskScore: 0.05, transactionCount: 10000 },
      { id: "wallet_2", address: "0x2222222222222222222222222222222222222222", type: "wallet", riskScore: 0.8, transactionCount: 75 },
      { id: "token_1", address: "0x3333333333333333333333333333333333333333", type: "token", riskScore: 0.3, transactionCount: 250 }
    ],
    links: [
      { source: "wallet_1", target: "contract_1", value: 10.5, type: "transfer", timestamp: new Date().toISOString() },
      { source: "contract_1", target: "exchange_1", value: 100.0, type: "transfer", timestamp: new Date().toISOString() },
      { source: "wallet_2", target: "wallet_1", value: 5.2, type: "transfer", timestamp: new Date().toISOString() },
      { source: "exchange_1", target: "token_1", value: 25.0, type: "interaction", timestamp: new Date().toISOString() }
    ]
  };

  const graphData = data || sampleData;

  return (
    <VStack spacing={4} align="stretch" height="100%">
      {/* Controls */}
      <HStack justify="space-between" px={4} py={2} bg="gray.800" borderRadius="md">
        <HStack spacing={2}>
          <Badge colorScheme="blue">Network Graph</Badge>
          <Badge colorScheme={isSimulationRunning ? "green" : "gray"}>
            {isSimulationRunning ? "Simulating" : "Static"}
          </Badge>
          <Text fontSize="sm" color="gray.400">
            {graphData.nodes.length} nodes • {graphData.links.length} edges
          </Text>
        </HStack>
        
        <HStack spacing={1}>
          <Tooltip label="Search Entities">
            <IconButton aria-label="Search" icon={<SearchIcon />} size="sm" variant="ghost" />
          </Tooltip>
          <Tooltip label="Graph Settings">
            <IconButton aria-label="Settings" icon={<SettingsIcon />} size="sm" variant="ghost" />
          </Tooltip>
          <Tooltip label="Export Graph">
            <IconButton aria-label="Download" icon={<DownloadIcon />} size="sm" variant="ghost" />
          </Tooltip>
          <Tooltip label="Fit to View">
            <IconButton aria-label="Fit View" icon={<ViewIcon />} size="sm" variant="ghost" />
          </Tooltip>
        </HStack>
      </HStack>

      {/* Graph Container */}
      <Box 
        flex="1" 
        bg="gray.900" 
        borderRadius="md" 
        border="1px solid" 
        borderColor="gray.600"
        position="relative"
        overflow="hidden"
      >
        <svg
          ref={svgRef}
          width="100%"
          height={height}
          style={{ background: '#111827' }}
        />
        
        {/* Selected Node Info */}
        {selectedNode && (
          <Box
            position="absolute"
            top={4}
            right={4}
            bg="rgba(0, 0, 0, 0.9)"
            color="white"
            p={3}
            borderRadius="md"
            minW="200px"
          >
            <Text fontSize="sm" fontWeight="bold">{selectedNode.id}</Text>
            <Text fontSize="xs" color="gray.300">Type: {selectedNode.type}</Text>
            <Text fontSize="xs" color="gray.300">Risk: {(selectedNode.riskScore * 100).toFixed(1)}%</Text>
            <Text fontSize="xs" color="gray.300">Txns: {selectedNode.transactionCount.toLocaleString()}</Text>
          </Box>
        )}
      </Box>
    </VStack>
  );
};

export default PalantirNetworkGraph;
