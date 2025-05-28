"""
MBO評価管理システム - メインアプリケーション

Author: Claude
Date: 2025
Description: Streamlitベースの目標管理・評価システム
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
from typing import Dict, List, Any  # 型ヒント用のインポートを追加

# 自作モジュールのインポート
from models.data_manager import DataManager
from utils.claude_api import ClaudeAPIManager
from utils.charts import ChartManager
from config.settings import APP_CONFIG, UI_COLORS, DEFAULTS, VALIDATION, REPORT_TONES


class MBOApp:
    """MBO評価管理アプリケーションのメインクラス"""
    
    def __init__(self):
        self.data_manager = DataManager()
        self.chart_manager = ChartManager()
        self.claude_manager = ClaudeAPIManager(self.data_manager.get_claude_api_key())
        
        # ページ設定
        st.set_page_config(**APP_CONFIG)
        
        # カスタムCSS
        self._load_custom_css()
    
    def _load_custom_css(self):
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
    
    def run(self):
        """アプリケーションを実行する"""
        st.markdown('<h1 class="main-header">🎯 MBO評価管理システム</h1>', unsafe_allow_html=True)
        
        # サイドバーの処理
        self._render_sidebar()
        
        # メインコンテンツの処理
        if not self.data_manager.get_period_list():
            st.warning("⚠️ まず期間を作成してください。サイドバーから新しい期間を作成できます。")
            return
        
        # タブの作成
        tabs = st.tabs(["🎯 目標設定", "📝 達成内容入力", "📊 進捗確認", "📋 報告書生成", "📄 結果出力", "⚙️ 設定"])
        
        with tabs[0]:
            self._render_goal_setting_tab()
        
        with tabs[1]:
            self._render_achievement_input_tab()
        
        with tabs[2]:
            self._render_progress_tab()
        
        with tabs[3]:
            self._render_report_generation_tab()
        
        with tabs[4]:
            self._render_csv_export_tab()
        
        with tabs[5]:
            self._render_settings_tab()
    
    def _render_sidebar(self):
        """サイドバーを描画する"""
        with st.sidebar:
            st.header("📋 期間管理")
            
            # 新しい期間の作成
            with st.expander("新しい期間を作成", expanded=False):
                new_period = st.text_input("期間名（例：2024年Q1）")
                if st.button("期間を作成"):
                    if new_period:
                        if self.data_manager.create_period(new_period):
                            st.success(f"期間「{new_period}」を作成しました！")
                            st.rerun()
                        else:
                            st.error("期間の作成に失敗しました。")
                    else:
                        st.warning("期間名を入力してください。")
            
            # 現在の期間選択
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
            
            # 統計情報表示
            stats = self.data_manager.get_statistics()
            st.markdown("---")
            st.subheader("📈 現在の状況")
            st.metric("目標数", stats["total_goals"])
            st.metric("完了目標", f"{stats['completed_goals']}/{stats['total_goals']}")
            st.metric("部分達成", stats["partial_goals"])
            st.metric("達成率", f"{stats['achievement_rate']:.1f}%")
            st.metric("達成項目数", stats["total_achievement_items"])
    
    def _render_goal_setting_tab(self):
        """目標設定タブを描画する"""
        st.header("目標設定")
        
        # 目標追加フォーム
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
                    st.success("✅ 目標が追加されました！")
                    st.rerun()
                else:
                    st.error("目標の追加に失敗しました。")
        
        # 既存の目標表示
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
                                st.success("目標を削除しました。")
                                st.rerun()
                            else:
                                st.error("削除に失敗しました。")
        else:
            st.info("📝 まだ目標が設定されていません。上記のフォームから目標を追加してください。")
    
    def _render_achievement_input_tab(self):
        """達成内容入力タブを描画する（新形式）"""
        st.header("達成内容入力")
        
        goals = self.data_manager.get_goals()
        achievements = self.data_manager.get_achievements()
        
        if not goals:
            st.warning("⚠️ まず目標を設定してください。")
            return
        
        # 全体のサマリー
        overall_rate = self.data_manager.calculate_achievement_rate()
        st.info(f"📊 **全体達成率**: {overall_rate:.1f}% （重要度加重平均）")
        
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
        progress_color = "normal"
        if total_percentage >= 100:
            progress_color = "success"
        elif total_percentage >= 50:
            progress_color = "info"
        elif total_percentage > 0:
            progress_color = "warning"
        
        # Streamlitのプログレスバーでは100%を上限とする
        display_percentage = min(total_percentage / 100.0, 1.0)
        st.progress(display_percentage)
        
        # 既存の達成項目一覧
        if items:
            st.subheader("✅ 登録済み達成項目")
            
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
                                        st.success("✅ 更新しました！")
                                        st.rerun()
                                    else:
                                        st.error("❗ 更新に失敗しました")
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
                                        st.success("✅ 削除しました！")
                                        st.rerun()
                                    else:
                                        st.error("❗ 削除に失敗しました")
                    
                    st.markdown("---")
        
        # 新しい達成項目追加フォーム
        if len(items) < VALIDATION["max_achievement_items"]:
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
                        st.success("✅ 達成項目を追加しました！")
                        st.rerun()
                    else:
                        st.error("❗ 追加に失敗しました")
                elif submit_achievement and not new_content.strip():
                    st.warning("⚠️ 達成内容を入力してください")
        else:
            st.info(f"ℹ️ 達成項目の上限数（{VALIDATION['max_achievement_items']}個）に達しています")
    
    def _render_progress_tab(self):
        """進捗確認タブを描画する"""
        st.header("進捗確認")
        
        goals = self.data_manager.get_goals()
        if not goals:
            st.warning("⚠️ まず目標を設定してください。")
            return
        
        achievements = self.data_manager.get_achievements()
        stats = self.data_manager.get_statistics()
        
        # メトリクス表示
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>📈 全体達成率</h3>
                <h2>{stats['achievement_rate']:.1f}%</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h3>✅ 完了目標</h3>
                <h2>{stats['completed_goals']}/{stats['total_goals']}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h3>🔄 部分達成</h3>
                <h2>{stats['partial_goals']}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <h3>📝 達成項目数</h3>
                <h2>{stats['total_achievement_items']}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        # グラフ表示
        st.subheader("📊 可視化")
        
        tab_charts = st.tabs(["達成率", "目標別状況", "重要度分布", "進捗ゲージ"])
        
        with tab_charts[0]:
            fig_pie = self.chart_manager.create_achievement_pie_chart(stats['achievement_rate'])
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with tab_charts[1]:
            fig_bar = self.chart_manager.create_goals_status_bar_chart(goals, achievements)
            st.plotly_chart(fig_bar, use_container_width=True)
        
        with tab_charts[2]:
            fig_weight = self.chart_manager.create_weight_distribution_chart(goals)
            st.plotly_chart(fig_weight, use_container_width=True)
        
        with tab_charts[3]:
            fig_gauge = self.chart_manager.create_progress_gauge(stats['achievement_rate'])
            st.plotly_chart(fig_gauge, use_container_width=True)
        
        # 詳細テーブル
        st.subheader("📋 目標別詳細")
        goal_data = []
        
        for goal in goals:
            goal_achievements = achievements.get(goal['id'], {})
            total_percentage = goal_achievements.get('total_percentage', 0.0)
            items_count = len(goal_achievements.get('items', []))
            
            if total_percentage >= 100.0:
                status = "✅ 完了"
            elif total_percentage > 0.0:
                status = f"🔄 進行中 ({total_percentage:.1f}%)"
            else:
                status = "⏳ 未着手"
            
            # 最新の達成内容を取得
            latest_achievement = ""
            items = goal_achievements.get('items', [])
            if items:
                latest_item = max(items, key=lambda x: x.get('created_at', ''))
                latest_achievement = latest_item['content'][:50] + "..." if len(latest_item['content']) > 50 else latest_item['content']
            
            goal_data.append({
                "目標": goal['title'],
                "重要度": f"{goal['weight']}/10",
                "期日": goal['deadline'],
                "達成率": f"{total_percentage:.1f}%",
                "項目数": f"{items_count}個",
                "状況": status,
                "最新達成内容": latest_achievement if latest_achievement else "未記入"
            })
        
        if goal_data:
            df = pd.DataFrame(goal_data)
            st.dataframe(df, use_container_width=True)
    
    def _render_report_generation_tab(self):
        """報告書生成タブを描画する"""
        st.header("報告書生成")
        
        goals = self.data_manager.get_goals()
        if not goals:
            st.warning("⚠️ まず目標を設定してください。")
            return
        
        achievements = self.data_manager.get_achievements()
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("生成設定")
            
            tone = st.selectbox(
                "報告書のトーン",
                list(REPORT_TONES.keys()),
                help="報告書の評価スタイルを選択してください"
            )
            
            st.write("**選択されたトーン:**")
            st.info(REPORT_TONES[tone])
            
            if st.button("📄 報告書を生成", use_container_width=True):
                if not self.claude_manager.is_configured():
                    st.error("⚠️ Claude APIキーが設定されていません。設定タブでAPIキーを入力してください。")
                else:
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
        
        with col2:
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
                st.info("💡 左側の設定から報告書を生成してください。")
    
    def _render_settings_tab(self):
        """設定タブを描画する"""
        st.header("設定")
        
        # Claude API設定
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
                    st.success("✅ APIキーを保存しました！")
                else:
                    st.error("保存に失敗しました。")
        
        # API接続テスト
        if st.button("🔍 API接続テスト"):
            if self.claude_manager.is_configured():
                st.info("✅ Claude APIキーが設定されています。")
            else:
                st.warning("⚠️ Claude APIキーが設定されていません。")
        
        # データ管理
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
                        st.success("✅ データをインポートしました！")
                        st.rerun()
                    else:
                        st.error("❌ インポートに失敗しました。")
                except Exception as e:
                    st.error(f"❌ エラーが発生しました: {str(e)}")
        
        # アプリケーション情報
        st.subheader("ℹ️ アプリケーション情報")
        
        info_data = {
            "バージョン": "1.0.0",
            "作成者": "Claude AI",
            "作成日": "2025年5月",
            "フレームワーク": "Streamlit",
            "現在の期間": self.data_manager.data.get("current_period", "未設定"),
            "総期間数": len(self.data_manager.get_period_list()),
            "データファイル": self.data_manager.data_file
        }
        
        for key, value in info_data.items():
            st.write(f"**{key}:** {value}")
    
    def _render_csv_export_tab(self):
        """結果出力タブを描画する"""
        st.header("📄 結果出力")
        
        st.markdown("""
        ### 📊 CSVエクスポート機能
        最終的な結果をCSV形式で出力し、別システムへの登録やデータ分析にご活用ください。
        """)
        
        # エクスポート可能な期間のチェック
        available_periods = self.data_manager.get_available_periods_for_export()
        
        if not available_periods:
            st.warning("⚠️ エクスポート可能なデータがありません。まず目標を設定してください。")
            return
        
        # エクスポート設定
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("🔧 エクスポート設定")
            
            # 期間選択
            export_period = st.selectbox(
                "エクスポートする期間",
                available_periods,
                index=available_periods.index(self.data_manager.data["current_period"]) 
                if self.data_manager.data["current_period"] in available_periods else 0,
                help="出力したい期間を選択してください"
            )
            
            # エクスポート形式選択
            export_format = st.radio(
                "エクスポート形式",
                ["サマリー形式", "詳細形式"],
                help="サマリー：1目標て1行 / 詳細：1達成項目て1行"
            )
            
            # プレビューボタン
            if st.button("🔍 プレビュー", use_container_width=True):
                if export_format == "サマリー形式":
                    preview_data = self.data_manager.export_csv_summary(export_period)
                else:
                    preview_data = self.data_manager.export_csv_detailed(export_period)
                
                st.session_state["csv_preview"] = preview_data
                st.session_state["csv_format"] = export_format
                st.session_state["csv_period"] = export_period
        
        with col2:
            st.subheader("📄 エクスポート結果")
            
            if "csv_preview" in st.session_state:
                # メタデータ表示
                st.caption(f"📊 期間: {st.session_state['csv_period']} | 形式: {st.session_state['csv_format']} | 作成日: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
                
                # CSVプレビュー表示
                st.markdown("### 📈 CSVプレビュー")
                
                # CSVデータをDataFrameで表示
                import io
                try:
                    df = pd.read_csv(io.StringIO(st.session_state["csv_preview"]))
                    st.dataframe(df, use_container_width=True, height=300)
                    
                    # 統計情報
                    st.info(f"📊 **統計**: {len(df)}行 × {len(df.columns)}列")
                    
                except Exception as e:
                    st.error(f"❗ プレビューエラー: {str(e)}")
                    st.text_area("生 CSVデータ", st.session_state["csv_preview"], height=200)
                
                # ダウンロードボタン
                st.markdown("### 📥 ダウンロード")
                
                col_download1, col_download2 = st.columns(2)
                
                with col_download1:
                    # メインダウンロード
                    filename = f"MBO結果_{st.session_state['csv_period']}_{st.session_state['csv_format']}_{datetime.now().strftime('%Y%m%d')}.csv"
                    
                    st.download_button(
                        label="📄 CSVファイルをダウンロード",
                        data=st.session_state["csv_preview"],
                        file_name=filename,
                        mime="text/csv",
                        use_container_width=True
                    )
                
                with col_download2:
                    # Excel形式でのダウンロード（オプション）
                    try:
                        import io
                        from io import BytesIO
                        
                        df = pd.read_csv(io.StringIO(st.session_state["csv_preview"]))
                        
                        # Excelファイルをメモリで作成
                        excel_buffer = BytesIO()
                        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                            df.to_excel(writer, sheet_name='MBO結果', index=False)
                        
                        excel_filename = f"MBO結果_{st.session_state['csv_period']}_{st.session_state['csv_format']}_{datetime.now().strftime('%Y%m%d')}.xlsx"
                        
                        st.download_button(
                            label="📆 Excelファイルをダウンロード",
                            data=excel_buffer.getvalue(),
                            file_name=excel_filename,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                    except ImportError:
                        st.info("📆 Excelエクスポートには openpyxl が必要です")
                    except Exception as e:
                        st.error(f"❗ Excelエクスポートエラー: {str(e)}")
                
                # 使用方法の説明
                st.markdown("---")
                st.markdown("### 📜 使用方法")
                
                if st.session_state['csv_format'] == 'サマリー形式':
                    st.info("📊 **サマリー形式**: 各目標の達成率と項目数を集約した形式です。全体の概観を把握するのに適しています。")
                else:
                    st.info("🔍 **詳細形式**: 各達成項目を個別に表示した形式です。詳細な分析や別システムへのデータ移行に適しています。")
                
                st.markdown("""
                **活用例:**
                - 人事システムへのデータ移行
                - Excelでのさらなる分析
                - チーム全体の成果集約
                - 上司への報告資料作成
                """)
            else:
                st.info("💡 左側の設定で期間と形式を選択し、「プレビュー」ボタンをクリックしてください。")


def main():
    """メイン関数"""
    app = MBOApp()
    app.run()


if __name__ == "__main__":
    main()
