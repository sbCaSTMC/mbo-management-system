"""
MBO評価管理システム - 進捗確認タブ
"""

import streamlit as st
import pandas as pd
from ui.base import BaseUI
from ui.components import MetricsDisplay


class ProgressTab(BaseUI):
    """進捗確認タブ"""
    
    def render(self):
        """進捗確認タブを描画する"""
        st.header("進捗確認")
        
        if not self.requires_goals():
            return
        
        goals = self.data_manager.get_goals()
        achievements = self.data_manager.get_achievements()
        stats = self.data_manager.get_statistics()
        
        # メトリクス表示
        MetricsDisplay.render_statistics(stats)
        
        # グラフ表示
        self._render_charts(goals, achievements, stats)
        
        # 詳細テーブル
        self._render_detail_table(goals, achievements)
    
    def _render_charts(self, goals, achievements, stats):
        """グラフを表示"""
        st.subheader("📊 可視化")
        
        tab_charts = st.tabs(["達成率", "目標別状況", "重要度分布", "進捗ゲージ"])
        
        with tab_charts[0]:
            fig_pie = self.chart_manager.create_achievement_pie_chart(stats['achievement_rate'])
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with tab_charts[1]:
            fig_bar = self.chart_manager.create_goals_status_bar_chart(goals, achievements)
            st.plotly_chart(fig_bar, use_container_width=True)
        
        with tab_charts[2]:
            fig_weight = self.chart_manager.create_weight_distribution_chart(goals)
            st.plotly_chart(fig_weight, use_container_width=True)
        
        with tab_charts[3]:
            fig_gauge = self.chart_manager.create_progress_gauge(stats['achievement_rate'])
            st.plotly_chart(fig_gauge, use_container_width=True)
    
    def _render_detail_table(self, goals, achievements):
        """詳細テーブルを表示"""
        st.subheader("📋 目標別詳細")
        goal_data = []
        
        for goal in goals:
            goal_achievements = achievements.get(goal['id'], {})
            total_percentage = goal_achievements.get('total_percentage', 0.0)
            items_count = len(goal_achievements.get('items', []))
            
            if total_percentage >= 100.0:
                status = "✅ 完了"
            elif total_percentage > 0.0:
                status = f"🔄 進行中 ({total_percentage:.1f}%)"
            else:
                status = "⏳ 未着手"
            
            # 最新の達成内容を取得
            latest_achievement = ""
            items = goal_achievements.get('items', [])
            if items:
                latest_item = max(items, key=lambda x: x.get('created_at', ''))
                latest_achievement = latest_item['content'][:50] + "..." if len(latest_item['content']) > 50 else latest_item['content']
            
            goal_data.append({
                "目標": goal['title'],
                "重要度": f"{goal['weight']}/10",
                "期日": goal['deadline'],
                "達成率": f"{total_percentage:.1f}%",
                "項目数": f"{items_count}個",
                "状況": status,
                "最新達成内容": latest_achievement if latest_achievement else "未記入"
            })
        
        if goal_data:
            df = pd.DataFrame(goal_data)
            st.dataframe(df, use_container_width=True)
