"""
MBO評価管理システム - カスタムCSS管理
"""

import streamlit as st
from config.settings import UI_COLORS


class CustomCSS:
    """カスタムCSSを管理するクラス"""
    
    @staticmethod
    def load():
        """カスタムCSSを読み込む"""
        st.markdown(f"""
        <style>
            .main-header {{
                font-size: 2.5rem;
                font-weight: 700;
                color: {UI_COLORS["primary"]};
                text-align: center;
                margin-bottom: 2rem;
            }}
            .metric-card {{
                background: linear-gradient(135deg, {UI_COLORS["gradient_start"]} 0%, {UI_COLORS["gradient_end"]} 100%);
                padding: 1rem;
                border-radius: 10px;
                color: white;
                text-align: center;
                margin: 0.5rem 0;
            }}
            .success-message {{
                background-color: #d4edda;
                border: 1px solid #c3e6cb;
                color: #155724;
                padding: 0.75rem;
                border-radius: 0.375rem;
                margin: 1rem 0;
            }}
            .stButton > button {{
                background: linear-gradient(135deg, {UI_COLORS["gradient_start"]} 0%, {UI_COLORS["gradient_end"]} 100%);
                border: none;
                border-radius: 20px;
                color: white;
                font-weight: 600;
                padding: 0.5rem 1rem;
                transition: all 0.3s ease;
            }}
            .stButton > button:hover {{
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            }}
            .goal-card {{
                border: 1px solid #e0e0e0;
                border-radius: 10px;
                padding: 1rem;
                margin: 0.5rem 0;
                background-color: #f9f9f9;
            }}
        </style>
        """, unsafe_allow_html=True)
