"""
Real-time Visualization Service Package

This package provides real-time visualization capabilities including:
- Real-time blockchain dashboard with WebSocket updates
- Interactive charts and graphs
- Live metrics display
- WebSocket-based data streaming

Modules:
- real_time_dashboard: Real-time dashboard with WebSocket support
"""

from .real_time_dashboard import app as dashboard_app

__all__ = [
    'dashboard_app'
] 