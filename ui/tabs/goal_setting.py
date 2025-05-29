"""
MBO評価管理システム - 目標設定タブ
"""

import streamlit as st
from ui.base import BaseUI
from config.settings import VALIDATION, DEFAULTS


class GoalSettingTab(BaseUI):
    """目標設定タブ"""
    
    def render(self):
        """目標設定タブを描画する"""
        st.header("目標設定")
        
        # 目標追加フォーム
        self._render_goal_form()
        
        # 既存の目標表示
        self._render_existing_goals()
    
    def _render_goal_form(self):
        """目標追加フォームを描画"""
        with st.form("goal_form"):
            col1, col2 = st.columns([3, 1])
            with col1:
                goal_title = st.text_input(
                    "目標タイトル", 
                    placeholder="例：営業売上の20%向上",
                    max_chars=VALIDATION["max_goal_title_length"]
                )
            with col2:
                goal_weight = st.number_input(
                    "重要度", 
                    min_value=VALIDATION["min_weight"], 
                    max_value=VALIDATION["max_weight"], 
                    value=DEFAULTS["goal_weight"],
                    step=1
                )
            
            goal_deadline = st.date_input("期日", value=DEFAULTS["goal_deadline"])
            goal_description = st.text_area(
                "目標詳細", 
                placeholder="具体的な目標内容を記述してください",
                max_chars=VALIDATION["max_description_length"]
            )
            
            submit_goal = st.form_submit_button("目標を追加", use_container_width=True)
            
            if submit_goal and goal_title:
                if self.data_manager.add_goal(
                    goal_title, 
                    goal_weight, 
                    goal_deadline.isoformat(), 
                    goal_description
                ):
                    self.show_success("✅ 目標が追加されました！")
                    st.rerun()
                else:
                    self.show_error("目標の追加に失敗しました。")
    
    def _render_existing_goals(self):
        """既存の目標を表示"""
        goals = self.data_manager.get_goals()
        if goals:
            st.subheader("登録済み目標")
            
            for i, goal in enumerate(goals):
                with st.expander(f"目標 {i+1}: {goal['title']}", expanded=False):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        st.write(f"**詳細:** {goal['description'] if goal['description'] else '詳細なし'}")
                    with col2:
                        st.write(f"**重要度:** {goal['weight']}/10")
                    with col3:
                        st.write(f"**期日:** {goal['deadline']}")
                    
                    col_edit, col_delete = st.columns([1, 1])
                    
                    with col_delete:
                        if st.button(f"🗑️ 削除", key=f"delete_{goal['id']}"):
                            if self.data_manager.delete_goal(goal['id']):
                                self.show_success("目標を削除しました。")
                                st.rerun()
                            else:
                                self.show_error("削除に失敗しました。")
        else:
            self.show_info("📝 まだ目標が設定されていません。上記のフォームから目標を追加してください。")
