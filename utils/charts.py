"""
MBO評価管理システム - グラフ生成モジュール
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import List, Dict, Any
from config.settings import UI_COLORS


class ChartManager:
    """グラフ生成を管理するクラス"""
    
    def __init__(self):
        self.colors = UI_COLORS
    
    def create_achievement_pie_chart(self, achievement_rate: float) -> go.Figure:
        """達成率の円グラフを作成"""
        achieved = achievement_rate
        remaining = 100 - achieved
        
        fig = go.Figure(data=[go.Pie(
            labels=['達成済み', '未達成'],
            values=[achieved, remaining],
            hole=0.4,
            marker_colors=[self.colors["success"], self.colors["warning"]]
        )])
        
        fig.update_layout(
            title="全体達成率",
            font=dict(size=14),
            height=300,
            showlegend=True
        )
        
        return fig
    
    def create_goals_status_bar_chart(self, goals: List[Dict[str, Any]], 
                                    achievements: Dict[str, Dict[str, Any]]) -> go.Figure:
        """目標別達成状況の棒グラフを作成"""
        if not goals:
            # 空のグラフを返す
            fig = go.Figure()
            fig.update_layout(
                title="目標別達成状況",
                xaxis_title="目標",
                yaxis_title="達成状況",
                height=300
            )
            return fig
        
        goal_names = [
            goal['title'][:20] + "..." if len(goal['title']) > 20 else goal['title'] 
            for goal in goals
        ]
        
        # 新しい達成率ベースのステータス
        achievement_percentages = [
            achievements.get(goal['id'], {}).get('total_percentage', 0.0)
            for goal in goals
        ]
        
        # 達成率に応じた色分け
        colors = []
        status_texts = []
        for percentage in achievement_percentages:
            if percentage >= 100.0:
                colors.append(self.colors["success"])  # 緑：完了
                status_texts.append(f'完了({percentage:.0f}%)')
            elif percentage >= 50.0:
                colors.append(self.colors["info"])     # 青：部分達成
                status_texts.append(f'進行中({percentage:.0f}%)')
            elif percentage > 0.0:
                colors.append(self.colors["warning"])  # オレンジ：低進捗
                status_texts.append(f'開始({percentage:.0f}%)')
            else:
                colors.append("#cccccc")               # グレー：未着手
                status_texts.append('未着手(0%)')
        
        fig = go.Figure(data=[
            go.Bar(
                x=goal_names,
                y=achievement_percentages,
                marker_color=colors,
                text=status_texts,
                textposition='inside'
            )
        ])
        
        fig.update_layout(
            title="目標別達成状況",
            xaxis_title="目標",
            yaxis_title="達成率(%)",
            height=300,
            yaxis=dict(range=[0, 105])  # 100%を上限として少し余裕をもたせる
        )
        
        return fig
    
    def create_weight_distribution_chart(self, goals: List[Dict[str, Any]]) -> go.Figure:
        """重要度分布のグラフを作成"""
        if not goals:
            fig = go.Figure()
            fig.update_layout(
                title="重要度分布",
                height=300
            )
            return fig
        
        weights = [goal['weight'] for goal in goals]
        goal_names = [
            goal['title'][:15] + "..." if len(goal['title']) > 15 else goal['title'] 
            for goal in goals
        ]
        
        fig = go.Figure(data=[
            go.Bar(
                x=goal_names,
                y=weights,
                marker_color=px.colors.sequential.Viridis,
                text=weights,
                textposition='inside'
            )
        ])
        
        fig.update_layout(
            title="目標別重要度",
            xaxis_title="目標",
            yaxis_title="重要度",
            height=300,
            yaxis=dict(range=[0, 10])
        )
        
        return fig
    
    def create_timeline_chart(self, goals: List[Dict[str, Any]], 
                            achievements: Dict[str, Dict[str, Any]]) -> go.Figure:
        """期日タイムラインのガントチャートを作成"""
        if not goals:
            fig = go.Figure()
            fig.update_layout(
                title="目標期日タイムライン",
                height=300
            )
            return fig
        
        # データの準備
        chart_data = []
        for goal in goals:
            goal_percentage = achievements.get(goal['id'], {}).get('total_percentage', 0.0)
            
            if goal_percentage >= 100.0:
                status = "完了"
                color = self.colors["success"]
            elif goal_percentage > 0.0:
                status = "進行中"
                color = self.colors["warning"]
            else:
                status = "未着手"
                color = "#cccccc"
            
            chart_data.append({
                "Task": goal['title'][:20] + "..." if len(goal['title']) > 20 else goal['title'],
                "Start": goal.get('created_at', '2024-01-01')[:10],
                "Finish": goal['deadline'],
                "Status": status,
                "Color": color
            })
        
        df = pd.DataFrame(chart_data)
        
        fig = px.timeline(
            df, 
            x_start="Start", 
            x_end="Finish", 
            y="Task",
            color="Status",
            title="目標期日タイムライン",
            color_discrete_map={"完了": self.colors["success"], "進行中": self.colors["warning"], "未着手": "#cccccc"}
        )
        
        fig.update_layout(height=300)
        
        return fig
    
    def create_progress_gauge(self, achievement_rate: float) -> go.Figure:
        """進捗ゲージチャートを作成"""
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = achievement_rate,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "全体進捗率"},
            delta = {'reference': 100},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': self.colors["primary"]},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "gray"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        fig.update_layout(height=300)
        
        return fig
    
    def create_comparison_radar_chart(self, goals: List[Dict[str, Any]], 
                                    achievements: Dict[str, Dict[str, Any]]) -> go.Figure:
        """目標達成状況のレーダーチャートを作成"""
        if not goals or len(goals) < 3:
            fig = go.Figure()
            fig.update_layout(
                title="目標達成レーダーチャート（3つ以上の目標が必要）",
                height=400
            )
            return fig
        
        categories = [goal['title'][:10] + "..." if len(goal['title']) > 10 else goal['title'] 
                     for goal in goals[:6]]  # 最大6つまで表示
        
        values = []
        for goal in goals[:6]:
            goal_percentage = achievements.get(goal['id'], {}).get('total_percentage', 0.0)
            # レーダーチャート用に適切なスケールに調整
            scaled_value = (goal_percentage / 100.0) * goal['weight']
            values.append(scaled_value)
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name='達成状況',
            line_color=self.colors["primary"]
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 10]
                )),
            showlegend=True,
            title="目標達成レーダーチャート",
            height=400
        )
        
        return fig
