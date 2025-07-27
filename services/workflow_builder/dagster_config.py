from dagster import (
    job, op, graph, Config, In, Out, Nothing,
    DynamicOut, DynamicOutput, AssetKey, AssetIn, AssetOut
)
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
import os

@op
def fetch_blockchain_data(context) -> pd.DataFrame:
    """Fetch blockchain data for analysis"""
    # This would fetch real blockchain data
    # For now, return mock data
    
    mock_data = pd.DataFrame({
        'block_number': range(18500000, 18500100),
        'timestamp': pd.date_range(start='2024-01-01', periods=100, freq='12S'),
        'transaction_count': np.random.randint(100, 200, 100),
        'gas_price': np.random.uniform(20, 100, 100),
        'total_value': np.random.uniform(1000, 10000, 100)
    })
    
    context.log.info(f"Fetched {len(mock_data)} blockchain records")
    return mock_data

@op
def detect_anomalies(context, data: pd.DataFrame) -> pd.DataFrame:
    """Detect anomalies in blockchain data"""
    # Simple anomaly detection based on z-score
    for column in ['transaction_count', 'gas_price', 'total_value']:
        z_scores = np.abs((data[column] - data[column].mean()) / data[column].std())
        data[f'{column}_anomaly'] = z_scores > 2
    
    anomalies = data[
        data['transaction_count_anomaly'] | 
        data['gas_price_anomaly'] | 
        data['total_value_anomaly']
    ]
    
    context.log.info(f"Detected {len(anomalies)} anomalies")
    return anomalies

@op
def calculate_risk_scores(context, data: pd.DataFrame) -> pd.DataFrame:
    """Calculate risk scores for transactions"""
    # Simple risk scoring
    data['risk_score'] = (
        data['transaction_count'] / 1000 +
        data['gas_price'] / 100 +
        data['total_value'] / 10000
    )
    
    # Normalize to 0-1
    data['risk_score'] = (data['risk_score'] - data['risk_score'].min()) / \
                        (data['risk_score'].max() - data['risk_score'].min())
    
    context.log.info(f"Calculated risk scores for {len(data)} records")
    return data

@op
def generate_signals(context, anomalies: pd.DataFrame, risk_data: pd.DataFrame) -> List[Dict[str, Any]]:
    """Generate signals based on anomalies and risk scores"""
    signals = []
    
    # Combine anomaly and risk data
    combined_data = pd.merge(anomalies, risk_data, on='block_number', how='inner')
    
    for _, row in combined_data.iterrows():
        if row['risk_score'] > 0.7:  # High risk threshold
            signal = {
                'signal_id': f"signal_{row['block_number']}_{int(row['timestamp'].timestamp())}",
                'signal_type': 'HIGH_RISK_DETECTED',
                'block_number': row['block_number'],
                'timestamp': row['timestamp'].isoformat(),
                'risk_score': row['risk_score'],
                'anomaly_type': 'transaction_anomaly',
                'confidence_score': min(row['risk_score'] * 1.2, 1.0)
            }
            signals.append(signal)
    
    context.log.info(f"Generated {len(signals)} signals")
    return signals

@op
def trigger_actions(context, signals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Trigger automated actions based on signals"""
    actions = []
    
    for signal in signals:
        if signal['risk_score'] > 0.8:  # Very high risk
            action = {
                'action_id': f"action_{signal['signal_id']}",
                'action_type': 'FREEZE_POSITION',
                'target_address': f"0x{signal['block_number']:040x}",
                'signal_id': signal['signal_id'],
                'confidence_score': signal['confidence_score'],
                'metadata': {
                    'risk_score': signal['risk_score'],
                    'anomaly_type': signal['anomaly_type']
                }
            }
            actions.append(action)
        elif signal['risk_score'] > 0.6:  # Medium risk
            action = {
                'action_id': f"action_{signal['signal_id']}",
                'action_type': 'SEND_ALERT',
                'target_address': f"0x{signal['block_number']:040x}",
                'signal_id': signal['signal_id'],
                'confidence_score': signal['confidence_score'],
                'metadata': {
                    'risk_score': signal['risk_score'],
                    'anomaly_type': signal['anomaly_type']
                }
            }
            actions.append(action)
    
    context.log.info(f"Triggered {len(actions)} actions")
    return actions

@op
def store_results(context, signals: List[Dict[str, Any]], actions: List[Dict[str, Any]]):
    """Store results in database"""
    # Store signals
    context.log.info(f"Storing {len(signals)} signals")
    
    # Store actions
    context.log.info(f"Storing {len(actions)} actions")
    
    # In real implementation, this would store to BigQuery or similar
    return True

@graph
def blockchain_monitoring_workflow():
    """Main blockchain monitoring workflow"""
    # Fetch data
    data = fetch_blockchain_data()
    
    # Detect anomalies
    anomalies = detect_anomalies(data)
    
    # Calculate risk scores
    risk_data = calculate_risk_scores(data)
    
    # Generate signals
    signals = generate_signals(anomalies, risk_data)
    
    # Trigger actions
    actions = trigger_actions(signals)
    
    # Store results
    store_results(signals, actions)

# Create the job
blockchain_monitoring_job = blockchain_monitoring_workflow.to_job(
    name="blockchain_monitoring",
    description="Monitor blockchain for anomalies and trigger actions"
)

# Additional specialized workflows

@op
def fetch_mev_data(context) -> pd.DataFrame:
    """Fetch MEV-specific data"""
    # Mock MEV data
    mev_data = pd.DataFrame({
        'block_number': range(18500000, 18500100),
        'mev_type': np.random.choice(['sandwich', 'liquidation', 'arbitrage'], 100),
        'profit_estimate': np.random.uniform(0.1, 10, 100),
        'gas_used': np.random.randint(100000, 500000, 100)
    })
    
    context.log.info(f"Fetched {len(mev_data)} MEV records")
    return mev_data

@op
def analyze_mev_patterns(context, mev_data: pd.DataFrame) -> List[Dict[str, Any]]:
    """Analyze MEV patterns"""
    mev_signals = []
    
    # Group by MEV type
    for mev_type in mev_data['mev_type'].unique():
        type_data = mev_data[mev_data['mev_type'] == mev_type]
        
        # Calculate statistics
        avg_profit = type_data['profit_estimate'].mean()
        total_gas = type_data['gas_used'].sum()
        
        if avg_profit > 1.0:  # High profit threshold
            signal = {
                'signal_id': f"mev_{mev_type}_{int(pd.Timestamp.now().timestamp())}",
                'signal_type': 'MEV_DETECTED',
                'mev_type': mev_type,
                'avg_profit': avg_profit,
                'total_gas': total_gas,
                'confidence_score': min(avg_profit / 5, 1.0)
            }
            mev_signals.append(signal)
    
    context.log.info(f"Generated {len(mev_signals)} MEV signals")
    return mev_signals

@op
def fetch_whale_data(context) -> pd.DataFrame:
    """Fetch whale transaction data"""
    # Mock whale data
    whale_data = pd.DataFrame({
        'address': [f"0x{np.random.randint(1000000, 9999999):x}" for _ in range(50)],
        'transaction_value': np.random.uniform(100000, 10000000, 50),
        'transaction_count': np.random.randint(1, 100, 50),
        'timestamp': pd.date_range(start='2024-01-01', periods=50, freq='1H')
    })
    
    context.log.info(f"Fetched {len(whale_data)} whale records")
    return whale_data

@op
def detect_whale_activity(context, whale_data: pd.DataFrame) -> List[Dict[str, Any]]:
    """Detect significant whale activity"""
    whale_signals = []
    
    # Filter for large transactions
    large_transactions = whale_data[whale_data['transaction_value'] > 1000000]
    
    for _, row in large_transactions.iterrows():
        signal = {
            'signal_id': f"whale_{row['address']}_{int(row['timestamp'].timestamp())}",
            'signal_type': 'WHALE_ACTIVITY',
            'address': row['address'],
            'transaction_value': row['transaction_value'],
            'transaction_count': row['transaction_count'],
            'timestamp': row['timestamp'].isoformat(),
            'confidence_score': min(row['transaction_value'] / 10000000, 1.0)
        }
        whale_signals.append(signal)
    
    context.log.info(f"Generated {len(whale_signals)} whale signals")
    return whale_signals

@graph
def mev_monitoring_workflow():
    """MEV monitoring workflow"""
    mev_data = fetch_mev_data()
    mev_signals = analyze_mev_patterns(mev_data)
    actions = trigger_actions(mev_signals)
    store_results(mev_signals, actions)

@graph
def whale_monitoring_workflow():
    """Whale monitoring workflow"""
    whale_data = fetch_whale_data()
    whale_signals = detect_whale_activity(whale_data)
    actions = trigger_actions(whale_signals)
    store_results(whale_signals, actions)

# Create specialized jobs
mev_monitoring_job = mev_monitoring_workflow.to_job(
    name="mev_monitoring",
    description="Monitor for MEV activity and trigger actions"
)

whale_monitoring_job = whale_monitoring_workflow.to_job(
    name="whale_monitoring", 
    description="Monitor whale activity and trigger actions"
)

# Custom signal builder workflow
@op
def build_custom_signal(context) -> Dict[str, Any]:
    """Build custom signal based on configuration"""
    signal_type = 'CUSTOM_SIGNAL'
    conditions = {"threshold": 1000000}
    
    # Build signal based on conditions
    signal = {
        'signal_id': f"custom_{int(pd.Timestamp.now().timestamp())}",
        'signal_type': signal_type,
        'conditions': conditions,
        'timestamp': pd.Timestamp.now().isoformat(),
        'confidence_score': 0.5
    }
    
    context.log.info(f"Built custom signal: {signal['signal_id']}")
    return signal

@op
def validate_signal_conditions(context, signal: Dict[str, Any]) -> bool:
    """Validate signal conditions"""
    conditions = signal.get('conditions', {})
    
    # Validate conditions
    for condition, value in conditions.items():
        if not isinstance(value, (int, float, str, bool)):
            context.log.warning(f"Invalid condition type for {condition}")
            return False
    
    context.log.info("Signal conditions validated")
    return True

@graph
def custom_signal_workflow():
    """Custom signal building workflow"""
    signal = build_custom_signal()
    is_valid = validate_signal_conditions(signal)
    
    # Only proceed if signal is valid
    if is_valid:
        actions = trigger_actions([signal])
        store_results([signal], actions)

custom_signal_job = custom_signal_workflow.to_job(
    name="custom_signal_builder",
    description="Build and validate custom signals"
) 