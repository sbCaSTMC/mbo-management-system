"""
MBO評価管理システム - 設定タブ
"""

import streamlit as st
from datetime import datetime
from ui.base import BaseUI


class SettingsTab(BaseUI):
    """設定タブ"""
    
    def render(self):
        """設定タブを描画する"""
        st.header("設定")
        
        # Claude API設定
        self._render_api_settings()
        
        # データ管理
        self._render_data_management()
        
        # アプリケーション情報
        self._render_app_info()
    
    def _render_api_settings(self):
        """API設定を表示"""
        st.subheader("🤖 Claude API設定")
        
        with st.form("api_settings_form"):
            api_key = st.text_input(
                "Claude APIキー",
                value=self.data_manager.get_claude_api_key(),
                type="password",
                help="Anthropic Claude APIキーを入力してください"
            )
            
            if st.form_submit_button("💾 APIキーを保存"):
                if self.data_manager.set_claude_api_key(api_key):
                    self.claude_manager.set_api_key(api_key)
                    self.show_success("✅ APIキーを保存しました！")
                else:
                    self.show_error("保存に失敗しました。")
        
        # API接続テスト
        if st.button("🔍 API接続テスト"):
            if self.claude_manager.is_configured():
                self.show_info("✅ Claude APIキーが設定されています。")
            else:
                self.show_warning("⚠️ Claude APIキーが設定されていません。")
    
    def _render_data_management(self):
        """データ管理を表示"""
        st.subheader("💾 データ管理")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**データエクスポート**")
            export_data = self.data_manager.export_data()
            
            st.download_button(
                label="📥 JSONファイルをダウンロード",
                data=export_data,
                file_name=f"mbo_data_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
        
        with col2:
            st.write("**データインポート**")
            uploaded_file = st.file_uploader("JSONファイルを選択", type="json")
            
            if uploaded_file and st.button("📤 インポート実行", use_container_width=True):
                try:
                    import_data = uploaded_file.read().decode('utf-8')
                    if self.data_manager.import_data(import_data):
                        self.show_success("✅ データをインポートしました！")
                        st.rerun()
                    else:
                        self.show_error("❌ インポートに失敗しました。")
                except Exception as e:
                    self.show_error(f"❌ エラーが発生しました: {str(e)}")
    
    def _render_app_info(self):
        """アプリケーション情報を表示"""
        st.subheader("ℹ️ アプリケーション情報")
        
        info_data = {
            "バージョン": "2.0.0",
            "作成者": "Claude AI",
            "作成日": "2025年5月",
            "フレームワーク": "Streamlit",
            "現在の期間": self.data_manager.data.get("current_period", "未設定"),
            "総期間数": len(self.data_manager.get_period_list()),
            "データファイル": self.data_manager.data_file
        }
        
        for key, value in info_data.items():
            st.write(f"**{key}:** {value}")
