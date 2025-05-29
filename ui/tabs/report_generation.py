"""
MBO評価管理システム - 報告書生成タブ
"""

import streamlit as st
import json
from datetime import datetime
from ui.base import BaseUI
from config.settings import REPORT_TONES


class ReportGenerationTab(BaseUI):
    """報告書生成タブ"""
    
    def render(self):
        """報告書生成タブを描画する"""
        st.header("報告書生成")
        
        if not self.requires_goals():
            return
        
        goals = self.data_manager.get_goals()
        achievements = self.data_manager.get_achievements()
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            self._render_generation_settings(goals, achievements)
        
        with col2:
            self._render_generation_result()
    
    def _render_generation_settings(self, goals, achievements):
        """生成設定を表示"""
        st.subheader("生成設定")
        
        tone = st.selectbox(
            "報告書のトーン",
            list(REPORT_TONES.keys()),
            help="報告書の評価スタイルを選択してください"
        )
        
        st.write("**選択されたトーン:**")
        st.info(REPORT_TONES[tone])
        
        if st.button("📄 報告書を生成", use_container_width=True):
            if not self.requires_api_key():
                return
            
            with st.spinner("🤖 Claude APIで報告書を生成中..."):
                report = self.claude_manager.generate_report(goals, achievements, tone)
                st.session_state["generated_report"] = report
                st.session_state["report_metadata"] = {
                    "period": self.data_manager.data["current_period"],
                    "generated_at": datetime.now().isoformat(),
                    "tone": tone,
                    "goals_count": len(goals),
                    "achievement_rate": self.data_manager.calculate_achievement_rate()
                }
    
    def _render_generation_result(self):
        """生成結果を表示"""
        st.subheader("生成結果")
        
        if "generated_report" in st.session_state:
            # メタデータ表示
            if "report_metadata" in st.session_state:
                metadata = st.session_state["report_metadata"]
                st.caption(f"期間: {metadata['period']} | 生成日時: {metadata['generated_at'][:19]} | トーン: {metadata['tone']}")
            
            # 報告書本文
            st.markdown("### 📋 MBO評価報告書")
            st.markdown(st.session_state["generated_report"])
            
            # ダウンロードボタン
            col_download1, col_download2 = st.columns(2)
            
            with col_download1:
                st.download_button(
                    label="📄 テキストファイルでダウンロード",
                    data=st.session_state["generated_report"],
                    file_name=f"MBO報告書_{self.data_manager.data['current_period']}_{datetime.now().strftime('%Y%m%d')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            
            with col_download2:
                # JSON形式でメタデータ付きダウンロード
                report_with_metadata = {
                    "metadata": st.session_state.get("report_metadata", {}),
                    "content": st.session_state["generated_report"]
                }
                
                st.download_button(
                    label="📊 JSON形式でダウンロード",
                    data=json.dumps(report_with_metadata, ensure_ascii=False, indent=2),
                    file_name=f"MBO報告書_詳細_{self.data_manager.data['current_period']}_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json",
                    use_container_width=True
                )
        else:
            self.show_info("💡 左側の設定から報告書を生成してください。")
