"""
MBO評価管理システム - 達成内容入力タブ
"""

import streamlit as st
from typing import Dict, Any
from ui.base import BaseUI
from config.settings import VALIDATION


class AchievementInputTab(BaseUI):
    """達成内容入力タブ"""
    
    def render(self):
        """達成内容入力タブを描画する"""
        st.header("達成内容入力")
        
        if not self.requires_goals():
            return
        
        goals = self.data_manager.get_goals()
        achievements = self.data_manager.get_achievements()
        
        # 全体のサマリー
        overall_rate = self.data_manager.calculate_achievement_rate()
        self.show_info(f"📊 **全体達成率**: {overall_rate:.1f}% （重要度加重平均）")
        
        # 各目標の達成内容管理
        for i, goal in enumerate(goals):
            with st.expander(f"🎯 目標 {i+1}: {goal['title']}", expanded=True):
                self._render_single_goal_achievement(goal, achievements.get(goal['id'], {}))
    
    def _render_single_goal_achievement(self, goal: Dict[str, Any], goal_achievements: Dict[str, Any]):
        """個別目標の達成内容管理UI"""
        goal_id = goal['id']
        items = goal_achievements.get('items', [])
        total_percentage = goal_achievements.get('total_percentage', 0.0)
        
        # 目標情報表示
        col_info1, col_info2, col_info3 = st.columns([2, 1, 1])
        
        with col_info1:
            if goal['description']:
                st.write(f"**詳細**: {goal['description']}")
        with col_info2:
            st.write(f"**重要度**: {goal['weight']}/10")
        with col_info3:
            st.write(f"**期日**: {goal['deadline']}")
        
        # 達成率表示（プログレスバー）
        st.markdown(f"### 📈 目標達成率: {total_percentage:.1f}%")
        
        # Streamlitのプログレスバーでは100%を上限とする
        display_percentage = min(total_percentage / 100.0, 1.0)
        st.progress(display_percentage)
        
        # 既存の達成項目一覧
        if items:
            st.subheader("✅ 登録済み達成項目")
            self._render_achievement_items(goal_id, items)
        
        # 新しい達成項目追加フォーム
        if len(items) < VALIDATION["max_achievement_items"]:
            self._render_add_achievement_form(goal_id)
        else:
            self.show_info(f"ℹ️ 達成項目の上限数（{VALIDATION['max_achievement_items']}個）に達しています")
    
    def _render_achievement_items(self, goal_id: str, items: list):
        """達成項目一覧を表示"""
        for j, item in enumerate(items):
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    # 達成内容の表示・編集
                    if f"edit_content_{item['id']}" in st.session_state:
                        new_content = st.text_area(
                            f"達成内容 {j+1}",
                            value=item['content'],
                            key=f"edit_content_area_{item['id']}",
                            height=80,
                            max_chars=VALIDATION["max_achievement_length"]
                        )
                    else:
                        st.write(f"**達成内容 {j+1}**: {item['content']}")
                
                with col2:
                    # 達成率の表示・編集
                    if f"edit_content_{item['id']}" in st.session_state:
                        new_percentage = st.number_input(
                            f"達成率 {j+1} (%)",
                            min_value=float(VALIDATION["min_percentage"]),
                            max_value=float(VALIDATION["max_percentage"]),
                            value=float(item['percentage']),
                            step=1.0,
                            key=f"edit_percentage_{item['id']}"
                        )
                    else:
                        st.metric("達成率", f"{item['percentage']:.1f}%")
                
                with col3:
                    # アクションボタン
                    if f"edit_content_{item['id']}" in st.session_state:
                        # 編集モード
                        col_save, col_cancel = st.columns(2)
                        with col_save:
                            if st.button("💾 保存", key=f"save_{item['id']}"):
                                if self.data_manager.update_achievement_item(
                                    goal_id, item['id'], new_content, new_percentage
                                ):
                                    del st.session_state[f"edit_content_{item['id']}"]
                                    self.show_success("✅ 更新しました！")
                                    st.rerun()
                                else:
                                    self.show_error("❗ 更新に失敗しました")
                        with col_cancel:
                            if st.button("❌ キャンセル", key=f"cancel_{item['id']}"):
                                del st.session_state[f"edit_content_{item['id']}"]
                                st.rerun()
                    else:
                        # 通常モード
                        col_edit, col_delete = st.columns(2)
                        with col_edit:
                            if st.button("✏️ 編集", key=f"edit_{item['id']}"):
                                st.session_state[f"edit_content_{item['id']}"] = True
                                st.rerun()
                        with col_delete:
                            if st.button("🗑️ 削除", key=f"delete_{item['id']}"):
                                if self.data_manager.delete_achievement_item(goal_id, item['id']):
                                    self.show_success("✅ 削除しました！")
                                    st.rerun()
                                else:
                                    self.show_error("❗ 削除に失敗しました")
                
                st.markdown("---")
    
    def _render_add_achievement_form(self, goal_id: str):
        """達成項目追加フォームを表示"""
        st.subheader("➕ 新しい達成項目を追加")
        
        with st.form(f"add_achievement_{goal_id}"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                new_content = st.text_area(
                    "達成内容",
                    placeholder="この目標に対して達成した具体的な内容を記述してください",
                    height=100,
                    max_chars=VALIDATION["max_achievement_length"]
                )
            
            with col2:
                new_percentage = st.number_input(
                    "達成率 (%)",
                    min_value=float(VALIDATION["min_percentage"]),
                    max_value=float(VALIDATION["max_percentage"]),
                    value=0.0,
                    step=1.0,
                    help="この項目で達成した割合を入力してください"
                )
            
            submit_achievement = st.form_submit_button("💾 達成項目を追加", use_container_width=True)
            
            if submit_achievement and new_content.strip():
                if self.data_manager.add_achievement_item(goal_id, new_content, new_percentage):
                    self.show_success("✅ 達成項目を追加しました！")
                    st.rerun()
                else:
                    self.show_error("❗ 追加に失敗しました")
            elif submit_achievement and not new_content.strip():
                self.show_warning("⚠️ 達成内容を入力してください")
