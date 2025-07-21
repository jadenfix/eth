/**
 * Compliance Map - Choropleth & Sankey diagrams for fund flows
 * Regulatory compliance visualization for blockchain transactions
 */

import React, { useState, useEffect, useMemo } from 'react';
import * as d3 from 'd3';
import { sankey, sankeyLinkHorizontal } from 'd3-sankey';
import { geoPath, geoNaturalEarth1 } from 'd3-geo';
import { feature } from 'topojson-client';

interface ComplianceData {
  transactions: TransactionFlow[];
  jurisdictions: JurisdictionRisk[];
  entities: ComplianceEntity[];
}

interface TransactionFlow {
  source: string;
  target: string;
  value: number;
  risk_level: 'low' | 'medium' | 'high' | 'critical';
  jurisdiction_source?: string;
  jurisdiction_target?: string;
  sanctions_hit?: boolean;
  timestamp: string;
}

interface JurisdictionRisk {
  jurisdiction: string;
  country_code: string;
  risk_score: number;
  total_volume: number;
  sanctions_list: boolean;
  regulatory_score: number;
}

interface ComplianceEntity {
  entity_id: string;
  name: string;
  entity_type: 'individual' | 'organization' | 'exchange' | 'service';
  jurisdiction: string;
  risk_level: 'low' | 'medium' | 'high' | 'critical';
  sanctions_hit: boolean;
  kyc_status: 'verified' | 'pending' | 'failed' | 'none';
}

interface ComplianceMapProps {
  data: ComplianceData;
  mapType: 'choropleth' | 'sankey';
  onEntityClick?: (entity: ComplianceEntity) => void;
  onFlowClick?: (flow: TransactionFlow) => void;
  width?: number;
  height?: number;
}

export default function ComplianceMap({
  data,
  mapType = 'choropleth',
  onEntityClick,
  onFlowClick,
  width = 1000,
  height = 600
}: ComplianceMapProps) {
  const [selectedEntity, setSelectedEntity] = useState<ComplianceEntity | null>(null);
  const [worldData, setWorldData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Load world map data
  useEffect(() => {
    fetch('https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json')
      .then(response => response.json())
      .then(world => {
        setWorldData(world);
        setIsLoading(false);
      })
      .catch(error => {
        console.error('Error loading world map:', error);
        setIsLoading(false);
      });
  }, []);

  // Color scales
  const riskColorScale = useMemo(() => 
    d3.scaleOrdinal<string, string>()
      .domain(['low', 'medium', 'high', 'critical'])
      .range(['#10b981', '#f59e0b', '#ef4444', '#dc2626']),
    []
  );

  const jurisdictionColorScale = useMemo(() => 
    d3.scaleSequential(d3.interpolateReds)
      .domain([0, d3.max(data.jurisdictions, d => d.risk_score) || 100]),
    [data.jurisdictions]
  );

  // Render choropleth map
  const renderChoropleth = () => {
    if (!worldData || isLoading) return null;

    const countries = feature(worldData, worldData.objects.countries);
    const projection = geoNaturalEarth1().fitSize([width, height], countries);
    const path = geoPath().projection(projection);

    return (
      <svg width={width} height={height} className="compliance-choropleth">
        <defs>
          {/* Gradient definitions for risk levels */}
          <linearGradient id="riskGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#10b981" />
            <stop offset="33%" stopColor="#f59e0b" />
            <stop offset="66%" stopColor="#ef4444" />
            <stop offset="100%" stopColor="#dc2626" />
          </linearGradient>
        </defs>

        {/* Country paths */}
        {countries.features.map((country: any) => {
          const jurisdiction = data.jurisdictions.find(
            j => j.country_code === country.properties.ISO_A2
          );
          
          return (
            <path
              key={country.id}
              d={path(country) || ''}
              fill={jurisdiction 
                ? jurisdictionColorScale(jurisdiction.risk_score)
                : '#f3f4f6'
              }
              stroke="#d1d5db"
              strokeWidth={0.5}
              className="country-path"
              style={{
                cursor: jurisdiction ? 'pointer' : 'default',
                opacity: jurisdiction?.sanctions_list ? 0.8 : 1
              }}
              onClick={() => {
                if (jurisdiction) {
                  console.log('Clicked jurisdiction:', jurisdiction);
                }
              }}
            >
              <title>
                {country.properties.NAME}
                {jurisdiction && (
                  ` - Risk Score: ${jurisdiction.risk_score}
Volume: $${(jurisdiction.total_volume / 1000000).toFixed(2)}M
${jurisdiction.sanctions_list ? 'SANCTIONS LIST' : ''}`
                )}
              </title>
            </path>
          );
        })}

        {/* Entity markers */}
        {data.entities.map((entity) => {
          const jurisdiction = data.jurisdictions.find(
            j => j.jurisdiction === entity.jurisdiction
          );
          
          if (!jurisdiction) return null;

          // Find country for projection
          const country = countries.features.find((c: any) => 
            c.properties.ISO_A2 === jurisdiction.country_code
          );
          
          if (!country) return null;

          const centroid = path.centroid(country);
          
          return (
            <circle
              key={entity.entity_id}
              cx={centroid[0]}
              cy={centroid[1]}
              r={entity.sanctions_hit ? 8 : 5}
              fill={riskColorScale(entity.risk_level)}
              stroke={entity.sanctions_hit ? '#dc2626' : '#fff'}
              strokeWidth={entity.sanctions_hit ? 3 : 1}
              className="entity-marker"
              style={{ cursor: 'pointer' }}
              onClick={() => {
                setSelectedEntity(entity);
                onEntityClick?.(entity);
              }}
            >
              <title>
                {entity.name}
                Type: {entity.entity_type}
                Risk: {entity.risk_level}
                KYC: {entity.kyc_status}
                {entity.sanctions_hit ? '\n⚠️ SANCTIONS HIT' : ''}
              </title>
            </circle>
          );
        })}
      </svg>
    );
  };

  // Render Sankey diagram
  const renderSankey = () => {
    const sankeyData = useMemo(() => {
      // Prepare nodes and links for Sankey
      const nodes = new Map();
      const links: any[] = [];

      // Add entities as nodes
      data.entities.forEach(entity => {
        nodes.set(entity.entity_id, {
          id: entity.entity_id,
          name: entity.name,
          category: entity.entity_type,
          risk_level: entity.risk_level,
          sanctions_hit: entity.sanctions_hit
        });
      });

      // Add transaction flows as links
      data.transactions.forEach((tx, index) => {
        if (nodes.has(tx.source) && nodes.has(tx.target)) {
          links.push({
            source: Array.from(nodes.keys()).indexOf(tx.source),
            target: Array.from(nodes.keys()).indexOf(tx.target),
            value: tx.value,
            risk_level: tx.risk_level,
            sanctions_hit: tx.sanctions_hit,
            flow_id: index
          });
        }
      });

      return {
        nodes: Array.from(nodes.values()),
        links
      };
    }, [data]);

    if (sankeyData.nodes.length === 0) {
      return (
        <div className="flex items-center justify-center h-full">
          <p className="text-gray-500">No transaction flows to display</p>
        </div>
      );
    }

    const sankeyGenerator = sankey<any, any>()
      .nodeWidth(20)
      .nodePadding(10)
      .extent([[1, 5], [width - 1, height - 5]]);

    const { nodes, links } = sankeyGenerator(sankeyData);

    return (
      <svg width={width} height={height} className="compliance-sankey">
        <defs>
          {/* Link gradients for different risk levels */}
          {['low', 'medium', 'high', 'critical'].map(risk => (
            <linearGradient
              key={`link-${risk}`}
              id={`link-${risk}`}
              gradientUnits="userSpaceOnUse"
            >
              <stop stopColor={riskColorScale(risk)} stopOpacity={0.3} />
              <stop offset="100%" stopColor={riskColorScale(risk)} stopOpacity={0.1} />
            </linearGradient>
          ))}
        </defs>

        {/* Links */}
        {links.map((link: any, i: number) => (
          <path
            key={i}
            d={sankeyLinkHorizontal()(link)}
            fill="none"
            stroke={`url(#link-${link.risk_level})`}
            strokeWidth={Math.max(1, link.width)}
            strokeOpacity={link.sanctions_hit ? 0.8 : 0.4}
            className="sankey-link"
            style={{ 
              cursor: 'pointer',
              strokeDasharray: link.sanctions_hit ? '5,5' : 'none'
            }}
            onClick={() => {
              const flow = data.transactions[link.flow_id];
              if (flow) {
                onFlowClick?.(flow);
              }
            }}
          >
            <title>
              Value: ${(link.value / 1000000).toFixed(2)}M
              Risk: {link.risk_level}
              {link.sanctions_hit ? '\n⚠️ SANCTIONS HIT' : ''}
            </title>
          </path>
        ))}

        {/* Nodes */}
        {nodes.map((node: any, i: number) => (
          <g key={i}>
            <rect
              x={node.x0}
              y={node.y0}
              width={node.x1 - node.x0}
              height={node.y1 - node.y0}
              fill={riskColorScale(node.risk_level)}
              stroke={node.sanctions_hit ? '#dc2626' : '#fff'}
              strokeWidth={node.sanctions_hit ? 2 : 1}
              className="sankey-node"
              style={{ cursor: 'pointer' }}
              onClick={() => {
                const entity = data.entities.find(e => e.entity_id === node.id);
                if (entity) {
                  setSelectedEntity(entity);
                  onEntityClick?.(entity);
                }
              }}
            >
              <title>
                {node.name}
                Category: {node.category}
                Risk: {node.risk_level}
                {node.sanctions_hit ? '\n⚠️ SANCTIONS HIT' : ''}
              </title>
            </rect>
            
            <text
              x={node.x0 < width / 2 ? node.x1 + 6 : node.x0 - 6}
              y={(node.y1 + node.y0) / 2}
              dy="0.35em"
              textAnchor={node.x0 < width / 2 ? "start" : "end"}
              fontSize={12}
              fill="#374151"
              className="node-label"
            >
              {node.name}
            </text>
          </g>
        ))}
      </svg>
    );
  };

  if (isLoading && mapType === 'choropleth') {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="compliance-map-container" style={{ width, height }}>
      {mapType === 'choropleth' ? renderChoropleth() : renderSankey()}
      
      {/* Selected Entity Panel */}
      {selectedEntity && (
        <div className="absolute bottom-4 left-4 bg-white p-4 rounded-lg shadow-lg max-w-sm">
          <h3 className="text-lg font-bold mb-2">Entity Details</h3>
          <div className="space-y-1 text-sm">
            <div><strong>Name:</strong> {selectedEntity.name}</div>
            <div><strong>Type:</strong> {selectedEntity.entity_type}</div>
            <div><strong>Jurisdiction:</strong> {selectedEntity.jurisdiction}</div>
            <div>
              <strong>Risk Level:</strong> 
              <span 
                className={`ml-2 px-2 py-1 rounded text-white text-xs
                  ${selectedEntity.risk_level === 'low' ? 'bg-green-500' :
                    selectedEntity.risk_level === 'medium' ? 'bg-yellow-500' :
                    selectedEntity.risk_level === 'high' ? 'bg-red-500' :
                    'bg-red-700'}`}
              >
                {selectedEntity.risk_level}
              </span>
            </div>
            <div><strong>KYC Status:</strong> {selectedEntity.kyc_status}</div>
            {selectedEntity.sanctions_hit && (
              <div className="text-red-600 font-bold">⚠️ SANCTIONS HIT</div>
            )}
          </div>
          <button
            className="mt-2 px-3 py-1 bg-gray-500 text-white rounded hover:bg-gray-600"
            onClick={() => setSelectedEntity(null)}
          >
            Close
          </button>
        </div>
      )}

      {/* Legend */}
      <div className="absolute top-4 right-4 bg-white p-4 rounded-lg shadow-lg">
        <h4 className="font-bold mb-2">Risk Levels</h4>
        <div className="space-y-1 text-sm">
          {['low', 'medium', 'high', 'critical'].map(level => (
            <div key={level} className="flex items-center">
              <div 
                className="w-4 h-4 rounded mr-2"
                style={{ backgroundColor: riskColorScale(level) }}
              />
              <span className="capitalize">{level}</span>
            </div>
          ))}
        </div>
        <div className="mt-2 pt-2 border-t text-xs text-gray-600">
          Dashed lines/borders indicate sanctions hits
        </div>
      </div>
    </div>
  );
}
