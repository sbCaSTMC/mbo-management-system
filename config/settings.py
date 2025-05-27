"""
MBO評価管理システム - 設定ファイル
"""

import os
from datetime import date

# ファイルパス設定
DATA_FILE = "mbo_data.json"
BACKUP_DIR = "backups"

# アプリケーション設定
APP_CONFIG = {
    "page_title": "MBO評価管理システム",
    "page_icon": "🎯",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# UI設定
UI_COLORS = {
    "primary": "#1f77b4",
    "gradient_start": "#667eea",
    "gradient_end": "#764ba2",
    "success": "#00cc96",
    "warning": "#ff6b6b",
    "info": "#36a2eb"
}

# Claude API設定
CLAUDE_CONFIG = {
    "model": "claude-3-sonnet-20240229",
    "max_tokens": 1000,
    "temperature": 0.7
}

# 報告書トーン設定
REPORT_TONES = {
    "ポジティブ": "非常にポジティブで、達成したことを称賛し、成長を強調する報告書を作成してください。",
    "バランス": "客観的でバランスの取れた、建設的なフィードバックを含む報告書を作成してください。",
    "厳しめ": "厳しく客観的な視点で、改善点を明確に指摘する報告書を作成してください。"
}

# バリデーション設定
VALIDATION = {
    "max_goal_title_length": 100,
    "max_description_length": 500,
    "max_achievement_length": 1000,
    "min_weight": 1,
    "max_weight": 10,
    "min_percentage": 0,
    "max_percentage": 100,
    "max_achievement_items": 20  # 1つの目標あたりの最大達成項目数
}

# デフォルト値
DEFAULTS = {
    "goal_weight": 5,
    "goal_deadline": date.today()
}
