"""
MBO評価管理システム - データ管理モジュール
"""

import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from config.settings import DATA_FILE


class DataManager:
    """データの読み込み、保存、管理を行うクラス"""
    
    def __init__(self):
        self.data_file = DATA_FILE
        self.data = self.load_data()
    
    def get_default_data(self) -> Dict[str, Any]:
        """デフォルトデータ構造を返す"""
        return {
            "periods": {},
            "current_period": None,
            "settings": {
                "claude_api_key": ""
            },
            "version": "2.0"  # 新しいデータ形式のバージョン
        }
    
    def load_data(self) -> Dict[str, Any]:
        """データファイルからデータを読み込み、必要に応じて移行する"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 古い形式から新しい形式への移行
                if not data.get("version") or data.get("version") == "1.0":
                    data = self._migrate_data_v1_to_v2(data)
                    self.data = data
                    self.save_data()  # 移行後のデータを保存
                
                return data
            except (json.JSONDecodeError, FileNotFoundError):
                return self.get_default_data()
        return self.get_default_data()
    
    def _migrate_data_v1_to_v2(self, old_data: Dict[str, Any]) -> Dict[str, Any]:
        """v1.0からv2.0へのデータ移行"""
        print("データ形式を新しいバージョンに移行中...")
        
        new_data = self.get_default_data()
        new_data["settings"] = old_data.get("settings", {})
        new_data["current_period"] = old_data.get("current_period")
        
        # 期間データの移行
        for period_name, period_data in old_data.get("periods", {}).items():
            new_data["periods"][period_name] = {
                "goals": period_data.get("goals", []),
                "achievements": {},
                "created_at": period_data.get("created_at", datetime.now().isoformat())
            }
            
            # 達成内容の移行（文字列 → 新しい構造）
            old_achievements = period_data.get("achievements", {})
            for goal_id, achievement_text in old_achievements.items():
                if achievement_text and achievement_text.strip():
                    new_data["periods"][period_name]["achievements"][goal_id] = {
                        "items": [
                            {
                                "id": str(uuid.uuid4()),
                                "content": achievement_text,
                                "percentage": 100.0,  # 既存データは100%として移行
                                "created_at": datetime.now().isoformat()
                            }
                        ],
                        "total_percentage": 100.0
                    }
                else:
                    new_data["periods"][period_name]["achievements"][goal_id] = {
                        "items": [],
                        "total_percentage": 0.0
                    }
        
        print("データ移行が完了しました。")
        return new_data
    
    def save_data(self) -> bool:
        """現在のデータをファイルに保存する"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"データ保存エラー: {e}")
            return False
    
    def create_period(self, period_name: str) -> bool:
        """新しい期間を作成する"""
        if period_name and period_name not in self.data["periods"]:
            self.data["periods"][period_name] = {
                "goals": [],
                "achievements": {},
                "created_at": datetime.now().isoformat()
            }
            self.data["current_period"] = period_name
            return self.save_data()
        return False
    
    def get_current_period_data(self) -> Optional[Dict[str, Any]]:
        """現在の期間のデータを取得する"""
        if self.data["current_period"] and self.data["current_period"] in self.data["periods"]:
            return self.data["periods"][self.data["current_period"]]
        return None
    
    def set_current_period(self, period_name: str) -> bool:
        """現在の期間を設定する"""
        if period_name in self.data["periods"]:
            self.data["current_period"] = period_name
            return self.save_data()
        return False
    
    def add_goal(self, title: str, weight: int, deadline: str, description: str = "") -> bool:
        """新しい目標を追加する"""
        current_data = self.get_current_period_data()
        if current_data is None:
            return False
        
        goal_id = str(uuid.uuid4())
        new_goal = {
            "id": goal_id,
            "title": title,
            "weight": weight,
            "deadline": deadline,
            "description": description,
            "created_at": datetime.now().isoformat()
        }
        
        current_data["goals"].append(new_goal)
        
        # 新しい目標の達成内容を初期化
        current_data["achievements"][goal_id] = {
            "items": [],
            "total_percentage": 0.0
        }
        
        return self.save_data()
    
    def delete_goal(self, goal_id: str) -> bool:
        """目標を削除する"""
        current_data = self.get_current_period_data()
        if current_data is None:
            return False
        
        # 目標を削除
        current_data["goals"] = [g for g in current_data["goals"] if g['id'] != goal_id]
        
        # 対応する達成内容も削除
        if goal_id in current_data["achievements"]:
            del current_data["achievements"][goal_id]
        
        return self.save_data()
    
    def add_achievement_item(self, goal_id: str, content: str, percentage: float) -> bool:
        """達成項目を追加する"""
        current_data = self.get_current_period_data()
        if current_data is None:
            return False
        
        # 目標が存在するかチェック
        goal_exists = any(goal['id'] == goal_id for goal in current_data["goals"])
        if not goal_exists:
            return False
        
        # 達成内容の初期化（存在しない場合）
        if goal_id not in current_data["achievements"]:
            current_data["achievements"][goal_id] = {
                "items": [],
                "total_percentage": 0.0
            }
        
        # 新しい達成項目を追加
        new_item = {
            "id": str(uuid.uuid4()),
            "content": content,
            "percentage": float(percentage),
            "created_at": datetime.now().isoformat()
        }
        
        current_data["achievements"][goal_id]["items"].append(new_item)
        
        # 総達成率を再計算
        self._recalculate_goal_percentage(goal_id)
        
        return self.save_data()
    
    def update_achievement_item(self, goal_id: str, item_id: str, content: str, percentage: float) -> bool:
        """達成項目を更新する"""
        current_data = self.get_current_period_data()
        if current_data is None or goal_id not in current_data["achievements"]:
            return False
        
        # 該当項目を更新
        for item in current_data["achievements"][goal_id]["items"]:
            if item["id"] == item_id:
                item["content"] = content
                item["percentage"] = float(percentage)
                item["updated_at"] = datetime.now().isoformat()
                break
        else:
            return False
        
        # 総達成率を再計算
        self._recalculate_goal_percentage(goal_id)
        
        return self.save_data()
    
    def delete_achievement_item(self, goal_id: str, item_id: str) -> bool:
        """達成項目を削除する"""
        current_data = self.get_current_period_data()
        if current_data is None or goal_id not in current_data["achievements"]:
            return False
        
        # 該当項目を削除
        items = current_data["achievements"][goal_id]["items"]
        current_data["achievements"][goal_id]["items"] = [
            item for item in items if item["id"] != item_id
        ]
        
        # 総達成率を再計算
        self._recalculate_goal_percentage(goal_id)
        
        return self.save_data()
    
    def _recalculate_goal_percentage(self, goal_id: str):
        """目標の総達成率を再計算する"""
        current_data = self.get_current_period_data()
        if current_data is None or goal_id not in current_data["achievements"]:
            return
        
        items = current_data["achievements"][goal_id]["items"]
        total_percentage = sum(item["percentage"] for item in items)
        
        # 100%を上限とする
        total_percentage = min(total_percentage, 100.0)
        
        current_data["achievements"][goal_id]["total_percentage"] = total_percentage
    
    def get_goals(self) -> List[Dict[str, Any]]:
        """現在の期間の目標一覧を取得する"""
        current_data = self.get_current_period_data()
        return current_data["goals"] if current_data else []
    
    def get_achievements(self) -> Dict[str, Dict[str, Any]]:
        """現在の期間の達成内容を取得する（新形式）"""
        current_data = self.get_current_period_data()
        if not current_data:
            return {}
        
        achievements = current_data.get("achievements", {})
        
        # 全ての目標に対して達成内容を初期化
        for goal in current_data.get("goals", []):
            if goal["id"] not in achievements:
                achievements[goal["id"]] = {
                    "items": [],
                    "total_percentage": 0.0
                }
        
        return achievements
    
    def get_goal_achievement_items(self, goal_id: str) -> List[Dict[str, Any]]:
        """特定の目標の達成項目一覧を取得する"""
        achievements = self.get_achievements()
        return achievements.get(goal_id, {}).get("items", [])
    
    def get_goal_total_percentage(self, goal_id: str) -> float:
        """特定の目標の総達成率を取得する"""
        achievements = self.get_achievements()
        return achievements.get(goal_id, {}).get("total_percentage", 0.0)
    
    def calculate_achievement_rate(self) -> float:
        """全体達成率を計算する（重要度加重平均）"""
        goals = self.get_goals()
        achievements = self.get_achievements()
        
        if not goals:
            return 0.0
        
        total_weighted_percentage = 0.0
        total_weight = 0.0
        
        for goal in goals:
            goal_percentage = achievements.get(goal['id'], {}).get("total_percentage", 0.0)
            weighted_percentage = goal['weight'] * goal_percentage
            
            total_weighted_percentage += weighted_percentage
            total_weight += goal['weight']
        
        return (total_weighted_percentage / total_weight) if total_weight > 0 else 0.0
    
    def get_claude_api_key(self) -> str:
        """Claude APIキーを取得する"""
        return self.data["settings"].get("claude_api_key", "")
    
    def set_claude_api_key(self, api_key: str) -> bool:
        """Claude APIキーを設定する"""
        self.data["settings"]["claude_api_key"] = api_key
        return self.save_data()
    
    def export_data(self) -> str:
        """データをJSON文字列として出力する"""
        return json.dumps(self.data, ensure_ascii=False, indent=2)
    
    def import_data(self, json_data: str) -> bool:
        """JSON文字列からデータをインポートする"""
        try:
            imported_data = json.loads(json_data)
            
            # 古い形式の場合は移行
            if not imported_data.get("version") or imported_data.get("version") == "1.0":
                imported_data = self._migrate_data_v1_to_v2(imported_data)
            
            self.data = imported_data
            return self.save_data()
        except json.JSONDecodeError:
            return False
    
    def get_period_list(self) -> List[str]:
        """期間一覧を取得する"""
        return list(self.data["periods"].keys())
    
    def export_csv_summary(self, period_name: str = None) -> str:
        """指定期間の結果をCSV形式で出力する"""
        import io
        import csv
        
        if period_name is None:
            period_name = self.data["current_period"]
        
        if not period_name or period_name not in self.data["periods"]:
            return ""
        
        period_data = self.data["periods"][period_name]
        goals = period_data.get("goals", [])
        achievements = period_data.get("achievements", {})
        
        # CSVデータの準備
        output = io.StringIO()
        writer = csv.writer(output)
        
        # ヘッダー行
        writer.writerow([
            "期間", "目標ID", "目標タイトル", "重要度", "期日", "目標詳細",
            "達成率(%)", "達成項目数", "達成項目詳細", "作成日"
        ])
        
        # データ行
        for goal in goals:
            goal_id = goal['id']
            goal_achievements = achievements.get(goal_id, {})
            total_percentage = goal_achievements.get('total_percentage', 0.0)
            items = goal_achievements.get('items', [])
            
            # 達成項目詳細の結合
            achievement_details = []
            for i, item in enumerate(items, 1):
                achievement_details.append(f"{i}. {item['content']} ({item['percentage']:.1f}%)")
            
            achievement_details_str = " | ".join(achievement_details) if achievement_details else "未記入"
            
            writer.writerow([
                period_name,
                goal_id,
                goal['title'],
                goal['weight'],
                goal['deadline'],
                goal.get('description', ''),
                f"{total_percentage:.1f}",
                len(items),
                achievement_details_str,
                goal.get('created_at', '')[:10]  # 日付部分のみ
            ])
        
        return output.getvalue()
    
    def export_csv_detailed(self, period_name: str = None) -> str:
        """指定期間の詳細結果をCSV形式で出力する（達成項目別）"""
        import io
        import csv
        
        if period_name is None:
            period_name = self.data["current_period"]
        
        if not period_name or period_name not in self.data["periods"]:
            return ""
        
        period_data = self.data["periods"][period_name]
        goals = period_data.get("goals", [])
        achievements = period_data.get("achievements", {})
        
        # CSVデータの準備
        output = io.StringIO()
        writer = csv.writer(output)
        
        # ヘッダー行
        writer.writerow([
            "期間", "目標ID", "目標タイトル", "目標重要度", "目標期日", "目標詳細",
            "達成項目ID", "達成項目内容", "達成項目率(%)", "達成項目作成日", "目標全体達成率(%)"
        ])
        
        # データ行
        for goal in goals:
            goal_id = goal['id']
            goal_achievements = achievements.get(goal_id, {})
            total_percentage = goal_achievements.get('total_percentage', 0.0)
            items = goal_achievements.get('items', [])
            
            if items:
                # 達成項目がある場合は各項目を行として出力
                for item in items:
                    writer.writerow([
                        period_name,
                        goal_id,
                        goal['title'],
                        goal['weight'],
                        goal['deadline'],
                        goal.get('description', ''),
                        item['id'],
                        item['content'],
                        f"{item['percentage']:.1f}",
                        item.get('created_at', '')[:10],
                        f"{total_percentage:.1f}"
                    ])
            else:
                # 達成項目がない場合は目標のみ出力
                writer.writerow([
                    period_name,
                    goal_id,
                    goal['title'],
                    goal['weight'],
                    goal['deadline'],
                    goal.get('description', ''),
                    "",
                    "未記入",
                    "0.0",
                    "",
                    "0.0"
                ])
        
        return output.getvalue()
    
    def get_available_periods_for_export(self) -> List[str]:
        """エクスポート可能な期間一覧を取得する"""
        return [period for period, data in self.data["periods"].items() 
                if data.get("goals", [])  # 目標があるもののみ
               ]
    
    def get_statistics(self) -> Dict[str, Any]:
        """統計情報を取得する"""
        goals = self.get_goals()
        achievements = self.get_achievements()
        
        if not goals:
            return {
                "total_goals": 0,
                "completed_goals": 0,
                "partial_goals": 0,
                "total_weight": 0,
                "achievement_rate": 0.0,
                "total_achievement_items": 0
            }
        
        completed_goals = 0
        partial_goals = 0
        total_achievement_items = 0
        
        for goal in goals:
            goal_percentage = achievements.get(goal['id'], {}).get("total_percentage", 0.0)
            goal_items = len(achievements.get(goal['id'], {}).get("items", []))
            
            total_achievement_items += goal_items
            
            if goal_percentage >= 100.0:
                completed_goals += 1
            elif goal_percentage > 0.0:
                partial_goals += 1
        
        total_weight = sum(goal['weight'] for goal in goals)
        achievement_rate = self.calculate_achievement_rate()
        
        return {
            "total_goals": len(goals),
            "completed_goals": completed_goals,
            "partial_goals": partial_goals,
            "total_weight": total_weight,
            "achievement_rate": achievement_rate,
            "total_achievement_items": total_achievement_items
        }
