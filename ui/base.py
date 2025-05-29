"""
MBO評価管理システム - UI基底クラスと共通処理
"""

import streamlit as st
from typing import Any
from models.data_manager import DataManager
from utils.claude_api import ClaudeAPIManager
from utils.charts import ChartManager


class BaseUI:
    """UI基底クラス - 共通処理を提供"""
    
    def __init__(self, data_manager: DataManager, claude_manager: ClaudeAPIManager, chart_manager: ChartManager):
        self.data_manager = data_manager
        self.claude_manager = claude_manager
        self.chart_manager = chart_manager
    
    def show_success(self, message: str):
        """成功メッセージを表示"""
        st.success(message)
    
    def show_error(self, message: str):
        """エラーメッセージを表示"""
        st.error(message)
    
    def show_warning(self, message: str):
        """警告メッセージを表示"""
        st.warning(message)
    
    def show_info(self, message: str):
        """情報メッセージを表示"""
        st.info(message)
    
    def requires_period(self) -> bool:
        """期間が設定されているかチェック"""
        if not self.data_manager.get_period_list():
            self.show_warning("⚠️ まず期間を作成してください。サイドバーから新しい期間を作成できます。")
            return False
        return True
    
    def requires_goals(self) -> bool:
        """目標が設定されているかチェック"""
        if not self.data_manager.get_goals():
            self.show_warning("⚠️ まず目標を設定してください。")
            return False
        return True
    
    def requires_api_key(self) -> bool:
        """Claude APIキーが設定されているかチェック"""
        if not self.claude_manager.is_configured():
            self.show_error("⚠️ Claude APIキーが設定されていません。設定タブでAPIキーを入力してください。")
            return False
        return True
