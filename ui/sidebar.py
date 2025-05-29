"""
MBO評価管理システム - サイドバー管理
"""

import streamlit as st
from ui.base import BaseUI


class SidebarUI(BaseUI):
    """サイドバーUI管理クラス"""
    
    def render(self):
        """サイドバーを描画する"""
        with st.sidebar:
            st.header("📋 期間管理")
            
            # 新しい期間の作成
            self._render_create_period()
            
            # 現在の期間選択
            self._render_period_selector()
            
            # 統計情報表示
            self._render_statistics()
    
    def _render_create_period(self):
        """期間作成フォームを描画"""
        with st.expander("新しい期間を作成", expanded=False):
            new_period = st.text_input("期間名（例：2024年Q1）")
            if st.button("期間を作成"):
                if new_period:
                    if self.data_manager.create_period(new_period):
                        self.show_success(f"期間「{new_period}」を作成しました！")
                        st.rerun()
                    else:
                        self.show_error("期間の作成に失敗しました。")
                else:
                    self.show_warning("期間名を入力してください。")
    
    def _render_period_selector(self):
        """期間選択セレクトボックスを描画"""
        period_list = self.data_manager.get_period_list()
        if period_list:
            current_period = st.selectbox(
                "現在の期間",
                period_list,
                index=period_list.index(self.data_manager.data["current_period"]) 
                if self.data_manager.data["current_period"] in period_list else 0
            )
            
            if current_period != self.data_manager.data["current_period"]:
                self.data_manager.set_current_period(current_period)
                # Claude APIマネージャーを更新
                self.claude_manager.set_api_key(self.data_manager.get_claude_api_key())
                st.rerun()
    
    def _render_statistics(self):
        """統計情報を表示"""
        stats = self.data_manager.get_statistics()
        st.markdown("---")
        st.subheader("📈 現在の状況")
        st.metric("目標数", stats["total_goals"])
        st.metric("完了目標", f"{stats['completed_goals']}/{stats['total_goals']}")
        st.metric("部分達成", stats["partial_goals"])
        st.metric("達成率", f"{stats['achievement_rate']:.1f}%")
        st.metric("達成項目数", stats["total_achievement_items"])
