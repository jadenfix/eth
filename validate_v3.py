#!/usr/bin/env python3
"""
V3 Features Validation Script
Tests the new v3 alpha features implementation
"""

import os
import json
import time
from pathlib import Path
import subprocess

def print_section(title):
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print(f"{'='*60}")

def check_file_exists(filepath, description):
    """Check if a file exists and report status"""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} (MISSING)")
        return False

def check_syntax(filepath, language):
    """Check syntax for different file types"""
    try:
        if language == "python":
            subprocess.run(["python", "-m", "py_compile", filepath], 
                         check=True, capture_output=True)
            print(f"✅ Python syntax: {os.path.basename(filepath)}")
            return True
        elif language == "javascript":
            subprocess.run(["node", "-c", filepath], 
                         check=True, capture_output=True)
            print(f"✅ JavaScript syntax: {os.path.basename(filepath)}")
            return True
        elif language == "json":
            with open(filepath, 'r') as f:
                json.load(f)
            print(f"✅ JSON syntax: {os.path.basename(filepath)}")
            return True
    except Exception as e:
        print(f"❌ {language} syntax error in {os.path.basename(filepath)}: {str(e)[:100]}")
        return False

def validate_v3_features():
    print("🚀 V3 Alpha Features Validation")
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Branch: v3-alpha")
    
    # Track results
    results = {
        "patch_1_bidirectional_sync": {"status": "unknown", "components": []},
        "patch_2_zk_attestation": {"status": "unknown", "components": []},
        "patch_3_gemini_explainer": {"status": "unknown", "components": []},
        "patch_4_action_executor": {"status": "unknown", "components": []},
        "overall_status": "unknown"
    }
    
    print_section("PATCH 1: BIDIRECTIONAL GRAPH SYNC")
    
    # Check Patch 1 components
    patch1_files = [
        ("infra/gcp/dataflow_cdc.tf", "Dataflow CDC Infrastructure"),
        ("services/ontology/graph_api.py", "Enhanced Graph API"),
        ("services/ingestion/__init__.py", "BigQuery CDC Publisher")
    ]
    
    patch1_score = 0
    for filepath, desc in patch1_files:
        if check_file_exists(filepath, desc):
            patch1_score += 1
            results["patch_1_bidirectional_sync"]["components"].append({
                "name": desc,
                "status": "present"
            })
    
    # Validate Patch 1 code quality
    if os.path.exists("services/ontology/graph_api.py"):
        with open("services/ontology/graph_api.py", 'r') as f:
            content = f.read()
            if "stream_cdc_acknowledgements" in content:
                print("✅ CDC acknowledgement endpoint found")
                patch1_score += 0.5
            if "pubsub" in content.lower():
                print("✅ Pub/Sub integration found")
                patch1_score += 0.5
    
    results["patch_1_bidirectional_sync"]["status"] = "complete" if patch1_score >= 3 else "partial"
    print(f"\n📊 Patch 1 Score: {patch1_score}/4.0")
    
    print_section("PATCH 2: ZK-ATTESTED SIGNALS")
    
    # Check Patch 2 components
    patch2_files = [
        ("zk_attestation/circuit/model_poseidon.circom", "Model Hash Circuit"),
        ("zk_attestation/circuit/signal_hash.circom", "Signal Hash Circuit"),
        ("zk_attestation/prover/generate_proof.js", "Proof Generator"),
        ("zk_attestation/prover/package.json", "Prover Dependencies"),
        ("zk_attestation/api/verifier_service.py", "Verifier API"),
        ("contracts/ZKSignalVerifier.sol", "Solidity Verifier")
    ]
    
    patch2_score = 0
    for filepath, desc in patch2_files:
        if check_file_exists(filepath, desc):
            patch2_score += 1
            results["patch_2_zk_attestation"]["components"].append({
                "name": desc,
                "status": "present"
            })
    
    # Validate syntax
    syntax_files = [
        ("zk_attestation/prover/generate_proof.js", "javascript"),
        ("zk_attestation/prover/package.json", "json"),
        ("zk_attestation/api/verifier_service.py", "python")
    ]
    
    syntax_score = 0
    for filepath, lang in syntax_files:
        if os.path.exists(filepath):
            if check_syntax(filepath, lang):
                syntax_score += 1
    
    results["patch_2_zk_attestation"]["status"] = "complete" if patch2_score >= 5 else "partial"
    print(f"\n📊 Patch 2 Score: {patch2_score}/6.0")
    print(f"📊 Syntax Score: {syntax_score}/{len(syntax_files)}")
    
    print_section("PATCH 3: GEMINI 2-PRO EXPLAINABILITY")
    
    # Check Patch 3 components
    patch3_files = [
        ("ai_services/gemini_explain/service.py", "Gemini Explainer Service"),
        ("ai_services/gemini_explain/requirements.txt", "Gemini Dependencies"),
        ("ai_services/gemini_explain/Dockerfile", "Gemini Container"),
        ("infra/gcp/vertex_ai.tf", "Enhanced Vertex AI Infrastructure")
    ]
    
    patch3_score = 0
    for filepath, desc in patch3_files:
        if check_file_exists(filepath, desc):
            patch3_score += 1
            results["patch_3_gemini_explainer"]["components"].append({
                "name": desc,
                "status": "present"
            })
    
    # Check for Gemini-specific content
    if os.path.exists("ai_services/gemini_explain/service.py"):
        with open("ai_services/gemini_explain/service.py", 'r') as f:
            content = f.read()
            if "ExplanationResponse" in content:
                print("✅ Explanation response model found")
                patch3_score += 0.5
            if "explain_trading_signal" in content:
                print("✅ Signal explanation endpoint found")
                patch3_score += 0.5
    
    # Check enhanced Vertex AI
    if os.path.exists("infra/gcp/vertex_ai.tf"):
        with open("infra/gcp/vertex_ai.tf", 'r') as f:
            content = f.read()
            if "gemini_explainer" in content:
                print("✅ Gemini explainer infrastructure found")
                patch3_score += 0.5
    
    results["patch_3_gemini_explainer"]["status"] = "complete" if patch3_score >= 4 else "partial"
    print(f"\n📊 Patch 3 Score: {patch3_score}/5.0")
    
    print_section("PATCH 4: AUTONOMOUS ACTION EXECUTOR")
    
    # Check Patch 4 components
    patch4_files = [
        ("action_executor/dispatcher.py", "Action Dispatcher Service"),
        ("action_executor/playbooks/freeze_position.yaml", "Freeze Position Playbook"),
        ("action_executor/playbooks/hedge_liquidity.yaml", "Hedge Liquidity Playbook"),
        ("action_executor/playbooks/dex_arb.yaml", "DEX Arbitrage Playbook"),
        ("infra/k8s/agents/action-executor.yaml", "Kubernetes Deployment")
    ]
    
    patch4_score = 0
    for filepath, desc in patch4_files:
        if check_file_exists(filepath, desc):
            patch4_score += 1
            results["patch_4_action_executor"]["components"].append({
                "name": desc,
                "status": "present"
            })
    
    # Check for action executor specific content
    if os.path.exists("action_executor/dispatcher.py"):
        with open("action_executor/dispatcher.py", 'r') as f:
            content = f.read()
            if "ActionExecutor" in content:
                print("✅ Action executor class found")
                patch4_score += 0.5
            if "PlaybookEngine" in content:
                print("✅ Playbook engine found")
                patch4_score += 0.5
    
    results["patch_4_action_executor"]["status"] = "complete" if patch4_score >= 5 else "partial"
    print(f"\n📊 Patch 4 Score: {patch4_score}/6.0")
    
    print_section("INFRASTRUCTURE VALIDATION")
    
    # Check enhanced infrastructure
    infra_files = [
        "infra/gcp/main.tf",
        "infra/gcp/pubsub.tf", 
        "infra/gcp/bigquery.tf",
        "infra/gcp/dataflow_cdc.tf"
    ]
    
    infra_score = 0
    for filepath in infra_files:
        if os.path.exists(filepath):
            print(f"✅ Infrastructure: {filepath}")
            infra_score += 1
        else:
            print(f"❌ Infrastructure: {filepath}")
    
    print(f"\n📊 Infrastructure Score: {infra_score}/{len(infra_files)}")
    
    print_section("OVERALL ASSESSMENT")
    
    total_score = patch1_score + patch2_score + patch3_score + patch4_score + infra_score + syntax_score
    max_score = 4 + 6 + 5 + 6 + 4 + 3
    percentage = (total_score / max_score) * 100
    
    if percentage >= 80:
        results["overall_status"] = "excellent"
        status_icon = "🎉"
        status_text = "EXCELLENT"
    elif percentage >= 60:
        results["overall_status"] = "good"
        status_icon = "✅"
        status_text = "GOOD"
    elif percentage >= 40:
        results["overall_status"] = "partial"
        status_icon = "⚠️"
        status_text = "PARTIAL"
    else:
        results["overall_status"] = "needs_work"
        status_icon = "❌"
        status_text = "NEEDS WORK"
    
    print(f"\n{status_icon} V3 IMPLEMENTATION STATUS: {status_text}")
    print(f"📊 Overall Score: {total_score:.1f}/{max_score} ({percentage:.1f}%)")
    
    print(f"\n🎯 NEXT STEPS:")
    if results["patch_1_bidirectional_sync"]["status"] != "complete":
        print("   • Complete Patch 1: Bidirectional Graph Sync")
    if results["patch_2_zk_attestation"]["status"] != "complete":
        print("   • Complete Patch 2: ZK-Attested Signals") 
    if results["patch_3_gemini_explainer"]["status"] != "complete":
        print("   • Complete Patch 3: Gemini 2-Pro Explainability")
    if results["patch_4_action_executor"]["status"] != "complete":
        print("   • Complete Patch 4: Autonomous Action Executor")
    if infra_score < 4:
        print("   • Complete infrastructure setup")
    
    print("   • Implement Patch 3: Gemini 2-Pro Explainability")
    print("   • Implement Patch 4: Autonomous Action Executor")
    print("   • Implement Patch 5: Voice Operations Polish")
    
    # Save detailed results
    with open("v3_validation_report.json", "w") as f:
        json.dump({
            "timestamp": time.time(),
            "branch": "v3-alpha",
            "results": results,
            "scores": {
                "patch_1": patch1_score,
                "patch_2": patch2_score,
                "patch_3": patch3_score,
                "patch_4": patch4_score,
                "infrastructure": infra_score,
                "syntax": syntax_score,
                "total": total_score,
                "max": max_score,
                "percentage": percentage
            }
        }, f, indent=2)
    
    print(f"\n📁 Detailed report saved to: v3_validation_report.json")
    return results

if __name__ == "__main__":
    validate_v3_features()
