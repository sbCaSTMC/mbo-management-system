"""
MBO評価管理システム - メインアプリケーション

Author: Claude
Date: 2025
Description: Streamlitベースの目標管理・評価システム
Version: 2.0.0
"""

import streamlit as st

# 自作モジュールのインポート
from models.data_manager import DataManager
from utils.claude_api import ClaudeAPIManager
from utils.charts import ChartManager
from config.settings import APP_CONFIG

# UIモジュールのインポート
from ui.sidebar import SidebarUI
from ui.components import CustomCSS
from ui.tabs import (
    GoalSettingTab,
    AchievementInputTab,
    ProgressTab,
    ReportGenerationTab,
    CsvExportTab,
    SettingsTab
)


class MBOApp:
    """MBO評価管理アプリケーションのメインクラス"""
    
    def __init__(self):
        # マネージャーの初期化
        self.data_manager = DataManager()
        self.chart_manager = ChartManager()
        self.claude_manager = ClaudeAPIManager(self.data_manager.get_claude_api_key())
        
        # UIコンポーネントの初期化
        self.sidebar = SidebarUI(self.data_manager, self.claude_manager, self.chart_manager)
        self.goal_setting_tab = GoalSettingTab(self.data_manager, self.claude_manager, self.chart_manager)
        self.achievement_input_tab = AchievementInputTab(self.data_manager, self.claude_manager, self.chart_manager)
        self.progress_tab = ProgressTab(self.data_manager, self.claude_manager, self.chart_manager)
        self.report_generation_tab = ReportGenerationTab(self.data_manager, self.claude_manager, self.chart_manager)
        self.csv_export_tab = CsvExportTab(self.data_manager, self.claude_manager, self.chart_manager)
        self.settings_tab = SettingsTab(self.data_manager, self.claude_manager, self.chart_manager)
        
        # ページ設定
        st.set_page_config(**APP_CONFIG)
        
        # カスタムCSS
        CustomCSS.load()
    
    def run(self):
        """アプリケーションを実行する"""
        # ヘッダー
        st.markdown('<h1 class="main-header">🎯 MBO評価管理システム</h1>', unsafe_allow_html=True)
        
        # サイドバーの処理
        self.sidebar.render()
        
        # メインコンテンツの処理
        if not self.data_manager.get_period_list():
            st.warning("⚠️ まず期間を作成してください。サイドバーから新しい期間を作成できます。")
            return
        
        # タブの作成
        tabs = st.tabs([
            "🎯 目標設定", 
            "📝 達成内容入力", 
            "📊 進捗確認", 
            "📋 報告書生成", 
            "📄 結果出力", 
            "⚙️ 設定"
        ])
        
        # 各タブの描画
        with tabs[0]:
            self.goal_setting_tab.render()
        
        with tabs[1]:
            self.achievement_input_tab.render()
        
        with tabs[2]:
            self.progress_tab.render()
        
        with tabs[3]:
            self.report_generation_tab.render()
        
        with tabs[4]:
            self.csv_export_tab.render()
        
        with tabs[5]:
            self.settings_tab.render()


def main():
    """メイン関数"""
    app = MBOApp()
    app.run()


if __name__ == "__main__":
    main()
