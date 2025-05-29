"""
MBO評価管理システム - メトリクス表示コンポーネント
"""

import streamlit as st
from typing import Dict, Any


class MetricsDisplay:
    """メトリクス表示コンポーネント"""
    
    @staticmethod
    def render_metric_card(title: str, value: str, icon: str = ""):
        """メトリクスカードを表示"""
        html = f"""
        <div class="metric-card">
            <h3>{icon} {title}</h3>
            <h2>{value}</h2>
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)
    
    @staticmethod
    def render_statistics(stats: Dict[str, Any]):
        """統計情報を表示"""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            MetricsDisplay.render_metric_card(
                "全体達成率",
                f"{stats['achievement_rate']:.1f}%",
                "📈"
            )
        
        with col2:
            MetricsDisplay.render_metric_card(
                "完了目標",
                f"{stats['completed_goals']}/{stats['total_goals']}",
                "✅"
            )
        
        with col3:
            MetricsDisplay.render_metric_card(
                "部分達成",
                f"{stats['partial_goals']}",
                "🔄"
            )
        
        with col4:
            MetricsDisplay.render_metric_card(
                "達成項目数",
                f"{stats['total_achievement_items']}",
                "📝"
            )
