"""
MBO評価管理システム - UIヘルパーモジュール
"""

import streamlit as st
from config.settings import UI_COLORS, UI_MESSAGES, DISPLAY_FORMAT
from typing import Any, Dict, Optional


class UIHelper:
    """UI表示のヘルパー関数を提供するクラス"""
    
    @staticmethod
    def metric_card(title: str, value: Any, icon: str = "") -> None:
        """メトリクスカードを表示する"""
        st.markdown(f"""
        <div class="metric-card">
            <h3>{icon} {title}</h3>
            <h2>{value}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def show_success(message_key: str, **kwargs) -> None:
        """成功メッセージを表示する"""
        message = UI_MESSAGES["success"].get(message_key, message_key)
        st.success(message.format(**kwargs))
    
    @staticmethod
    def show_error(message_key: str, **kwargs) -> None:
        """エラーメッセージを表示する"""
        message = UI_MESSAGES["error"].get(message_key, message_key)
        st.error(message.format(**kwargs))
    
    @staticmethod
    def show_warning(message_key: str, **kwargs) -> None:
        """警告メッセージを表示する"""
        message = UI_MESSAGES["warning"].get(message_key, message_key)
        st.warning(message.format(**kwargs))
    
    @staticmethod
    def show_info(message_key: str, **kwargs) -> None:
        """情報メッセージを表示する"""
        message = UI_MESSAGES["info"].get(message_key, message_key)
        st.info(message.format(**kwargs))
    
    @staticmethod
    def format_rate(value: float) -> str:
        """達成率をフォーマットする"""
        return DISPLAY_FORMAT["achievement_rate"].format(value)
    
    @staticmethod
    def format_weight(value: int) -> str:
        """重要度をフォーマットする"""
        return DISPLAY_FORMAT["weight"].format(value)
    
    @staticmethod
    def format_count(current: int, total: int) -> str:
        """カウントをフォーマットする"""
        return DISPLAY_FORMAT["metric_count"].format(current, total)
    
    @staticmethod
    def get_achievement_status(percentage: float) -> Dict[str, str]:
        """達成率に応じたステータス情報を返す"""
        if percentage >= 100.0:
            return {"status": "✅ 完了", "color": UI_COLORS["success"]}
        elif percentage >= 50.0:
            return {"status": f"🔄 進行中 ({percentage:.1f}%)", "color": UI_COLORS["info"]}
        elif percentage > 0.0:
            return {"status": f"⏳ 開始 ({percentage:.1f}%)", "color": UI_COLORS["warning"]}
        else:
            return {"status": "⏳ 未着手", "color": "#cccccc"}
    
    @staticmethod
    def get_progress_color(percentage: float) -> str:
        """進捗率に応じた色を返す"""
        if percentage >= 100:
            return "success"
        elif percentage >= 50:
            return "info"
        elif percentage > 0:
            return "warning"
        else:
            return "normal"
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 20) -> str:
        """テキストを指定長で切り詰める"""
        if len(text) > max_length:
            return text[:max_length] + "..."
        return text
    
    @staticmethod
    def session_state_manager(key: str, default: Any = None) -> Any:
        """セッション状態を管理する"""
        if key not in st.session_state:
            st.session_state[key] = default
        return st.session_state[key]
    
    @staticmethod
    def edit_mode_key(entity_id: str) -> str:
        """編集モードのキーを生成する"""
        return f"edit_mode_{entity_id}"
    
    @staticmethod
    def is_edit_mode(entity_id: str) -> bool:
        """編集モードかどうかを判定する"""
        return UIHelper.edit_mode_key(entity_id) in st.session_state
    
    @staticmethod
    def toggle_edit_mode(entity_id: str, enable: bool = True) -> None:
        """編集モードを切り替える"""
        key = UIHelper.edit_mode_key(entity_id)
        if enable:
            st.session_state[key] = True
        else:
            if key in st.session_state:
                del st.session_state[key]
