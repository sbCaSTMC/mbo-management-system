"""
MBO評価管理システム - 結果出力タブ
"""

import streamlit as st
import pandas as pd
import io
from datetime import datetime
from ui.base import BaseUI


class CsvExportTab(BaseUI):
    """結果出力タブ"""
    
    def render(self):
        """結果出力タブを描画する"""
        st.header("📄 結果出力")
        
        st.markdown("""
        ### 📊 CSVエクスポート機能
        最終的な結果をCSV形式で出力し、別システムへの登録やデータ分析にご活用ください。
        """)
        
        # エクスポート可能な期間のチェック
        available_periods = self.data_manager.get_available_periods_for_export()
        
        if not available_periods:
            self.show_warning("⚠️ エクスポート可能なデータがありません。まず目標を設定してください。")
            return
        
        # エクスポート設定
        col1, col2 = st.columns([1, 2])
        
        with col1:
            self._render_export_settings(available_periods)
        
        with col2:
            self._render_export_result()
    
    def _render_export_settings(self, available_periods):
        """エクスポート設定を表示"""
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
    
    def _render_export_result(self):
        """エクスポート結果を表示"""
        st.subheader("📄 エクスポート結果")
        
        if "csv_preview" in st.session_state:
            # メタデータ表示
            st.caption(f"📊 期間: {st.session_state['csv_period']} | 形式: {st.session_state['csv_format']} | 作成日: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            
            # CSVプレビュー表示
            st.markdown("### 📈 CSVプレビュー")
            
            # CSVデータをDataFrameで表示
            try:
                df = pd.read_csv(io.StringIO(st.session_state["csv_preview"]))
                st.dataframe(df, use_container_width=True, height=300)
                
                # 統計情報
                self.show_info(f"📊 **統計**: {len(df)}行 × {len(df.columns)}列")
                
            except Exception as e:
                self.show_error(f"❗ プレビューエラー: {str(e)}")
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
                    self.show_info("📆 Excelエクスポートには openpyxl が必要です")
                except Exception as e:
                    self.show_error(f"❗ Excelエクスポートエラー: {str(e)}")
            
            # 使用方法の説明
            self._render_usage_instructions()
        else:
            self.show_info("💡 左側の設定で期間と形式を選択し、「プレビュー」ボタンをクリックしてください。")
    
    def _render_usage_instructions(self):
        """使用方法を表示"""
        st.markdown("---")
        st.markdown("### 📜 使用方法")
        
        if st.session_state['csv_format'] == 'サマリー形式':
            self.show_info("📊 **サマリー形式**: 各目標の達成率と項目数を集約した形式です。全体の概観を把握するのに適しています。")
        else:
            self.show_info("🔍 **詳細形式**: 各達成項目を個別に表示した形式です。詳細な分析や別システムへのデータ移行に適しています。")
        
        st.markdown("""
        **活用例:**
        - 人事システムへのデータ移行
        - Excelでのさらなる分析
        - チーム全体の成果集約
        - 上司への報告資料作成
        """)
