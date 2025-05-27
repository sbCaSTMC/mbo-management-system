"""
MBO評価管理システム - Claude API処理モジュール
"""

from anthropic import Anthropic
from typing import List, Dict, Any
from config.settings import CLAUDE_CONFIG, REPORT_TONES


class ClaudeAPIManager:
    """Claude APIとの通信を管理するクラス"""
    
    def __init__(self, api_key: str = ""):
        self.api_key = api_key
        self.client = None
        if api_key:
            self.client = Anthropic(api_key=api_key)
    
    def set_api_key(self, api_key: str):
        """APIキーを設定する"""
        self.api_key = api_key
        if api_key:
            self.client = Anthropic(api_key=api_key)
        else:
            self.client = None
    
    def is_configured(self) -> bool:
        """APIキーが設定されているかチェック"""
        return self.client is not None and bool(self.api_key)
    
    def generate_report(self, goals: List[Dict[str, Any]], 
                       achievements: Dict[str, Dict[str, Any]], 
                       tone: str) -> str:
        """MBO報告書を生成する"""
        
        if not self.is_configured():
            return "⚠️ Claude APIキーが設定されていません。設定タブでAPIキーを入力してください。"
        
        try:
            # 目標と達成内容の整理
            goals_text = self._format_goals_and_achievements(goals, achievements)
            
            # プロンプトの作成
            prompt = self._create_report_prompt(goals_text, tone)
            
            # Claude APIを呼び出し
            message = self.client.messages.create(
                model=CLAUDE_CONFIG["model"],
                max_tokens=CLAUDE_CONFIG["max_tokens"],
                temperature=CLAUDE_CONFIG["temperature"],
                messages=[{"role": "user", "content": prompt}]
            )
            
            return message.content[0].text
            
        except Exception as e:
            return f"❌ 報告書の生成中にエラーが発生しました: {str(e)}"
    
    def _format_goals_and_achievements(self, goals: List[Dict[str, Any]], 
                                     achievements: Dict[str, Dict[str, Any]]) -> str:
        """目標と達成内容をテキスト形式でフォーマット（新形式対応）"""
        goals_text = ""
        
        for i, goal in enumerate(goals, 1):
            goal_achievement = achievements.get(goal['id'], {})
            total_percentage = goal_achievement.get('total_percentage', 0.0)
            items = goal_achievement.get('items', [])
            
            goals_text += f"目標{i}: {goal['title']} (重要度: {goal['weight']}/10, 期日: {goal['deadline']})\n"
            goals_text += f"達成率: {total_percentage:.1f}%\n"
            
            if items:
                goals_text += "達成内容:\n"
                for j, item in enumerate(items, 1):
                    goals_text += f"  {j}. {item['content']} ({item['percentage']:.1f}%)\n"
            else:
                goals_text += "達成内容: 未記入\n"
            
            goals_text += "\n"
        
        return goals_text
    
    def _create_report_prompt(self, goals_text: str, tone: str) -> str:
        """報告書生成用のプロンプトを作成"""
        tone_instruction = REPORT_TONES.get(tone, REPORT_TONES["バランス"])
        
        prompt = f"""
以下のMBO（目標管理）の情報を基に、{tone_instruction}

【目標と達成内容】
{goals_text}

【報告書の要件】
- 日本語で作成
- 各目標の評価と全体的な総評を含める
- 具体的な改善提案や次期への提言を含める
- 約300-500文字程度
- 読みやすい構成にする

報告書を作成してください。
"""
        return prompt
    
    def generate_goal_suggestions(self, role: str = "", department: str = "") -> str:
        """職種や部署に基づいた目標提案を生成する"""
        
        if not self.is_configured():
            return "⚠️ Claude APIキーが設定されていません。"
        
        try:
            context = ""
            if role:
                context += f"職種: {role}\n"
            if department:
                context += f"部署: {department}\n"
            
            prompt = f"""
以下の情報を基に、MBO（目標管理）の目標案を5つ提案してください。

{context}

【要件】
- 具体的で測定可能な目標
- SMART原則（具体的、測定可能、達成可能、関連性、期限）に従う
- 各目標に重要度（1-10）の推奨値を含める
- 日本語で作成

目標案を提案してください。
"""
            
            message = self.client.messages.create(
                model=CLAUDE_CONFIG["model"],
                max_tokens=CLAUDE_CONFIG["max_tokens"],
                temperature=0.8,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return message.content[0].text
            
        except Exception as e:
            return f"❌ 目標提案の生成中にエラーが発生しました: {str(e)}"
    
    def analyze_achievement_quality(self, goal_title: str, achievement_text: str) -> str:
        """達成内容の質を分析する"""
        
        if not self.is_configured():
            return "⚠️ Claude APIキーが設定されていません。"
        
        if not achievement_text.strip():
            return "達成内容が入力されていません。"
        
        try:
            prompt = f"""
以下の目標と達成内容について、達成度と内容の質を分析してください。

【目標】
{goal_title}

【達成内容】
{achievement_text}

【分析要件】
- 達成度の評価（0-100%）
- 達成内容の具体性
- 改善提案
- 100文字程度で簡潔に

分析結果を提供してください。
"""
            
            message = self.client.messages.create(
                model=CLAUDE_CONFIG["model"],
                max_tokens=500,
                temperature=0.5,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return message.content[0].text
            
        except Exception as e:
            return f"❌ 達成内容の分析中にエラーが発生しました: {str(e)}"
