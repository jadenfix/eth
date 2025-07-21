#!/usr/bin/env python3
"""
Visualization Layer Implementation Validator
Tests compliance with main.md and rules.md requirements
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple

class VisualizationValidator:
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        self.results = {"passed": 0, "failed": 0, "issues": []}
        
    def validate_file_structure(self) -> bool:
        """Validate directory structure matches newtree.md blueprint"""
        print("🔍 Validating file structure...")
        
        expected_paths = [
            "services/visualization/deckgl_explorer/index.tsx",
            "services/visualization/deckgl_explorer/styles.css", 
            "services/visualization/deckgl_explorer/Dockerfile",
            "services/visualization/timeseries_canvas/chart.ts",
            "services/visualization/timeseries_canvas/Dockerfile",
            "services/visualization/compliance_map/map.tsx",
            "services/visualization/compliance_map/Dockerfile", 
            "services/visualization/workspace/layout.json",
            "services/visualization/workspace/panels/workspace.tsx",
            "services/visualization/workspace/Dockerfile",
            "services/ui/nextjs-app/src/pages/explorer.tsx",
            "services/ui/nextjs-app/src/pages/canvas.tsx",
            "services/ui/nextjs-app/src/pages/compliance.tsx",
            "scripts/update_to_foundry.sh",
            "docs/system_architecture_v3.md",
            "docker-compose.visualization.yml",
            "infra/k8s/visualization/visualization-services.yaml"
        ]
        
        all_exist = True
        for path in expected_paths:
            full_path = self.workspace_path / path
            if not full_path.exists():
                self.results["issues"].append(f"❌ Missing required file: {path}")
                all_exist = False
            else:
                print(f"✅ Found: {path}")
                
        if all_exist:
            self.results["passed"] += 1
            print("✅ File structure validation PASSED")
        else:
            self.results["failed"] += 1
            print("❌ File structure validation FAILED")
            
        return all_exist
    
    def validate_architecture_compliance(self) -> bool:
        """Validate architecture follows main.md Palantir-grade requirements"""
        print("🏗️  Validating architecture compliance...")
        
        compliance_checks = []
        
        # Check for semantic fusion integration
        graph_api_path = self.workspace_path / "services/ontology/graph_api.py"
        if graph_api_path.exists():
            compliance_checks.append(("✅ Semantic Fusion Layer integration", True))
        else:
            compliance_checks.append(("❌ Missing Semantic Fusion Layer integration", False))
            
        # Check for entity resolution integration  
        entity_resolution_path = self.workspace_path / "services/entity_resolution"
        if entity_resolution_path.exists():
            compliance_checks.append(("✅ Entity Resolution integration", True))
        else:
            compliance_checks.append(("❌ Missing Entity Resolution integration", False))
            
        # Check for access control integration
        access_control_path = self.workspace_path / "services/access_control"
        if access_control_path.exists():
            compliance_checks.append(("✅ Access Control integration", True))
        else:
            compliance_checks.append(("❌ Missing Access Control integration", False))
            
        # Check for VoiceOps integration
        voiceops_path = self.workspace_path / "services/voiceops"
        if voiceops_path.exists():
            compliance_checks.append(("✅ VoiceOps integration", True))
        else:
            compliance_checks.append(("❌ Missing VoiceOps integration", False))
            
        # Validate workspace layout configuration
        layout_path = self.workspace_path / "services/visualization/workspace/layout.json"
        if layout_path.exists():
            try:
                with open(layout_path) as f:
                    layout = json.load(f)
                if "data_sources" in layout and "ontology_api" in layout["data_sources"]:
                    compliance_checks.append(("✅ Workspace integrates with Ontology API", True))
                else:
                    compliance_checks.append(("❌ Workspace missing Ontology API integration", False))
            except Exception as e:
                compliance_checks.append(("❌ Invalid workspace layout.json", False))
        
        passed = sum(1 for _, status in compliance_checks if status)
        total = len(compliance_checks)
        
        for message, status in compliance_checks:
            print(message)
            if not status:
                self.results["issues"].append(message)
        
        if passed == total:
            self.results["passed"] += 1
            print(f"✅ Architecture compliance PASSED ({passed}/{total})")
            return True
        else:
            self.results["failed"] += 1
            print(f"❌ Architecture compliance FAILED ({passed}/{total})")
            return False
    
    def validate_rules_compliance(self) -> bool:
        """Validate implementation follows rules.md coding standards"""
        print("📋 Validating rules compliance...")
        
        rules_checks = []
        
        # Rule 5-7: Code Quality & Style
        typescript_files = list(self.workspace_path.glob("services/visualization/**/*.tsx")) + \
                          list(self.workspace_path.glob("services/visualization/**/*.ts"))
        
        if typescript_files:
            rules_checks.append(("✅ TypeScript usage (Rule 6)", True))
            
            # Check for single-responsibility modules
            has_single_responsibility = True
            for ts_file in typescript_files[:3]:  # Sample check
                if ts_file.stat().st_size > 50000:  # > 50KB suggests multiple responsibilities
                    has_single_responsibility = False
                    break
            
            if has_single_responsibility:
                rules_checks.append(("✅ Single-responsibility modules (Rule 6)", True))
            else:
                rules_checks.append(("❌ Some modules too large, check single-responsibility (Rule 6)", False))
        else:
            rules_checks.append(("❌ Missing TypeScript files (Rule 6)", False))
        
        # Rule 11-13: Infrastructure as Code
        docker_files = list(self.workspace_path.glob("services/visualization/**/Dockerfile"))
        if len(docker_files) >= 4:  # Should have 4 services
            rules_checks.append(("✅ Dockerfiles for all services (Rule 11)", True))
        else:
            rules_checks.append(("❌ Missing Dockerfiles for some services (Rule 11)", False))
            
        k8s_manifest = self.workspace_path / "infra/k8s/visualization/visualization-services.yaml"
        if k8s_manifest.exists():
            rules_checks.append(("✅ Kubernetes manifests (Rule 12)", True))
        else:
            rules_checks.append(("❌ Missing Kubernetes manifests (Rule 12)", False))
        
        # Rule 14-16: API & Schema Governance  
        has_graphql_integration = False
        for tsx_file in typescript_files:
            try:
                with open(tsx_file) as f:
                    content = f.read()
                    if "GraphQL" in content or "graphql" in content:
                        has_graphql_integration = True
                        break
            except:
                pass
                
        if has_graphql_integration:
            rules_checks.append(("✅ GraphQL integration (Rule 15)", True))
        else:
            rules_checks.append(("❌ Missing GraphQL integration (Rule 15)", False))
        
        # Rule 23-25: Documentation
        readme_files = list(self.workspace_path.glob("services/visualization/**/README.md"))
        if len(readme_files) >= 1:
            rules_checks.append(("✅ Service documentation (Rule 23)", True))
        else:
            rules_checks.append(("❌ Missing service README files (Rule 23)", False))
            
        architecture_doc = self.workspace_path / "docs/system_architecture_v3.md"
        if architecture_doc.exists():
            rules_checks.append(("✅ Architecture documentation updated (Rule 24)", True))
        else:
            rules_checks.append(("❌ Missing updated architecture documentation (Rule 24)", False))
        
        passed = sum(1 for _, status in rules_checks if status)
        total = len(rules_checks)
        
        for message, status in rules_checks:
            print(message)
            if not status:
                self.results["issues"].append(message)
        
        if passed >= total * 0.8:  # 80% pass rate acceptable
            self.results["passed"] += 1
            print(f"✅ Rules compliance PASSED ({passed}/{total})")
            return True
        else:
            self.results["failed"] += 1  
            print(f"❌ Rules compliance FAILED ({passed}/{total})")
            return False
    
    def validate_visualization_features(self) -> bool:
        """Validate visualization features match newtree.md specifications"""
        print("🎨 Validating visualization features...")
        
        feature_checks = []
        
        # DeckGL Explorer features
        deckgl_file = self.workspace_path / "services/visualization/deckgl_explorer/index.tsx"
        if deckgl_file.exists():
            try:
                with open(deckgl_file) as f:
                    content = f.read()
                    if "ForceDirectedGraph" in content:
                        feature_checks.append(("✅ Force-directed graph layout", True))
                    else:
                        feature_checks.append(("❌ Missing force-directed graph layout", False))
                        
                    if "entity_type" in content and "risk_score" in content:
                        feature_checks.append(("✅ Entity type and risk scoring", True))  
                    else:
                        feature_checks.append(("❌ Missing entity type/risk features", False))
            except:
                feature_checks.append(("❌ Cannot read DeckGL Explorer file", False))
        else:
            feature_checks.append(("❌ Missing DeckGL Explorer component", False))
        
        # TimeSeries Canvas features
        timeseries_file = self.workspace_path / "services/visualization/timeseries_canvas/chart.ts"
        if timeseries_file.exists():
            try:
                with open(timeseries_file) as f:
                    content = f.read()
                    if "Plotly" in content and "d3" in content:
                        feature_checks.append(("✅ High-performance charting (Plotly + D3)", True))
                    else:
                        feature_checks.append(("❌ Missing high-performance charting libraries", False))
                        
                    if "WebSocket" in content or "websocket" in content:
                        feature_checks.append(("✅ Real-time data updates", True))
                    else:
                        feature_checks.append(("❌ Missing real-time update capability", False))
            except:
                feature_checks.append(("❌ Cannot read TimeSeries Canvas file", False))
        else:
            feature_checks.append(("❌ Missing TimeSeries Canvas component", False))
        
        # Compliance Map features
        compliance_file = self.workspace_path / "services/visualization/compliance_map/map.tsx"
        if compliance_file.exists():
            try:
                with open(compliance_file) as f:
                    content = f.read()
                    if "choropleth" in content and "sankey" in content:
                        feature_checks.append(("✅ Choropleth and Sankey visualization", True))
                    else:
                        feature_checks.append(("❌ Missing choropleth/Sankey features", False))
                        
                    if "sanctions" in content:
                        feature_checks.append(("✅ Sanctions highlighting", True))
                    else:
                        feature_checks.append(("❌ Missing sanctions features", False))
            except:
                feature_checks.append(("❌ Cannot read Compliance Map file", False))
        else:
            feature_checks.append(("❌ Missing Compliance Map component", False))
        
        # Workspace Builder features
        workspace_file = self.workspace_path / "services/visualization/workspace/panels/workspace.tsx"
        if workspace_file.exists():
            try:
                with open(workspace_file) as f:
                    content = f.read()
                    if "DndProvider" in content and "useDrag" in content:
                        feature_checks.append(("✅ Drag & drop functionality", True))
                    else:
                        feature_checks.append(("❌ Missing drag & drop functionality", False))
                        
                    if "Panel" in content and "layout" in content:
                        feature_checks.append(("✅ Panel management system", True))
                    else:
                        feature_checks.append(("❌ Missing panel management", False))
            except:
                feature_checks.append(("❌ Cannot read Workspace file", False))
        else:
            feature_checks.append(("❌ Missing Workspace component", False))
        
        passed = sum(1 for _, status in feature_checks if status)
        total = len(feature_checks)
        
        for message, status in feature_checks:
            print(message)
            if not status:
                self.results["issues"].append(message)
        
        if passed >= total * 0.7:  # 70% pass rate for features
            self.results["passed"] += 1
            print(f"✅ Visualization features PASSED ({passed}/{total})")
            return True
        else:
            self.results["failed"] += 1
            print(f"❌ Visualization features FAILED ({passed}/{total})")
            return False
    
    def validate_deployment_readiness(self) -> bool:
        """Validate deployment configuration is complete"""
        print("🚀 Validating deployment readiness...")
        
        deployment_checks = []
        
        # Check Docker Compose configuration
        docker_compose_viz = self.workspace_path / "docker-compose.visualization.yml"
        if docker_compose_viz.exists():
            try:
                with open(docker_compose_viz) as f:
                    content = f.read()
                    if "deckgl-explorer" in content and "timeseries-canvas" in content:
                        deployment_checks.append(("✅ Docker Compose services defined", True))
                    else:
                        deployment_checks.append(("❌ Incomplete Docker Compose services", False))
            except:
                deployment_checks.append(("❌ Invalid Docker Compose file", False))
        else:
            deployment_checks.append(("❌ Missing Docker Compose visualization file", False))
        
        # Check environment variables
        env_sample = self.workspace_path / ".env.sample"
        if env_sample.exists():
            try:
                with open(env_sample) as f:
                    content = f.read()
                    if "MAPBOX_TOKEN" in content and "WEBSOCKET_ENDPOINT" in content:
                        deployment_checks.append(("✅ Environment variables configured", True))
                    else:
                        deployment_checks.append(("❌ Missing visualization environment variables", False))
            except:
                deployment_checks.append(("❌ Cannot read .env.sample", False))
        else:
            deployment_checks.append(("❌ Missing .env.sample file", False))
        
        # Check script executability
        script_path = self.workspace_path / "scripts/update_to_foundry.sh"
        if script_path.exists() and os.access(script_path, os.X_OK):
            deployment_checks.append(("✅ Update script is executable", True))
        else:
            deployment_checks.append(("❌ Update script not executable", False))
        
        passed = sum(1 for _, status in deployment_checks if status)
        total = len(deployment_checks)
        
        for message, status in deployment_checks:
            print(message)
            if not status:
                self.results["issues"].append(message)
        
        if passed == total:
            self.results["passed"] += 1
            print(f"✅ Deployment readiness PASSED ({passed}/{total})")
            return True
        else:
            self.results["failed"] += 1
            print(f"❌ Deployment readiness FAILED ({passed}/{total})")
            return False
    
    def run_validation(self) -> Dict:
        """Run all validation tests"""
        print("🔍 Starting Visualization Layer Validation...")
        print("=" * 60)
        
        tests = [
            self.validate_file_structure,
            self.validate_architecture_compliance,  
            self.validate_rules_compliance,
            self.validate_visualization_features,
            self.validate_deployment_readiness
        ]
        
        for test in tests:
            try:
                test()
                print("-" * 40)
            except Exception as e:
                self.results["failed"] += 1
                self.results["issues"].append(f"❌ Test failed with error: {str(e)}")
                print(f"❌ Test failed: {str(e)}")
                print("-" * 40)
        
        return self.generate_report()
    
    def generate_report(self) -> Dict:
        """Generate final validation report"""
        total_tests = self.results["passed"] + self.results["failed"]
        pass_rate = (self.results["passed"] / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "=" * 60)
        print("🎯 VISUALIZATION LAYER VALIDATION REPORT")
        print("=" * 60)
        print(f"✅ Tests Passed: {self.results['passed']}")
        print(f"❌ Tests Failed: {self.results['failed']}")
        print(f"📊 Pass Rate: {pass_rate:.1f}%")
        print()
        
        if self.results["issues"]:
            print("🔍 Issues Found:")
            for issue in self.results["issues"]:
                print(f"   {issue}")
            print()
        
        if pass_rate >= 80:
            status = "PASS"
            emoji = "🎉"
            message = "Visualization layer is ready for deployment!"
        elif pass_rate >= 60:
            status = "PASS (with warnings)"
            emoji = "⚠️"
            message = "Visualization layer mostly ready, address warnings before production."
        else:
            status = "FAIL"
            emoji = "❌"
            message = "Visualization layer needs significant work before deployment."
        
        print(f"{emoji} OVERALL RESULT: {status}")
        print(f"📝 Summary: {message}")
        
        return {
            "status": status,
            "pass_rate": pass_rate,
            "passed": self.results["passed"],
            "failed": self.results["failed"],
            "issues": self.results["issues"],
            "ready_for_deployment": pass_rate >= 80
        }

if __name__ == "__main__":
    validator = VisualizationValidator("/Users/jadenfix/eth")
    report = validator.run_validation()
    
    # Exit with appropriate code
    exit(0 if report["ready_for_deployment"] else 1)
