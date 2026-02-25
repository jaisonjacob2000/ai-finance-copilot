"""
AI Service Module - WITH REAL CLAUDE API
Handles AI-powered categorization, insights, and nudges
"""

import json
from typing import List, Dict
import pandas as pd
from datetime import datetime
import os

# CRITICAL: Load environment variables FIRST
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("🔄 Loading environment variables...")
except ImportError:
    print("⚠️ python-dotenv not installed")

# Get API key
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

# Check if API key is available
USE_AI = ANTHROPIC_API_KEY is not None and len(ANTHROPIC_API_KEY) > 0

if USE_AI:
    try:
        import anthropic
        print("✅ Claude AI is enabled!")
        print(f"   API Key found (starts with: {ANTHROPIC_API_KEY[:15]}...)")
    except ImportError:
        print("⚠️ anthropic package not installed. Run: pip install anthropic")
        USE_AI = False
else:
    print("ℹ️ No API key found. Using rule-based categorization.")
    print("   To enable AI: Create backend/.env with ANTHROPIC_API_KEY=your-key")


async def categorize_with_ai(merchant: str, amount: float, description: str = "") -> dict:
    """
    Categorize a transaction using AI (or fallback to rules)
    """
    
    if USE_AI:
        try:
            client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
            
            prompt = f"""Categorize this transaction into ONE of these categories: Dining, Groceries, Transport, Entertainment, Shopping, Bills & Utilities, Health & Fitness, Travel, Other.

Transaction:
- Merchant: {merchant}
- Amount: ${amount}
- Description: {description}

Respond ONLY with valid JSON in this format (no markdown, no backticks):
{{"category": "category_name", "confidence": 0.95}}"""

            message = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=100,
                messages=[{"role": "user", "content": prompt}]
            )
            
            result = json.loads(message.content[0].text)
            return {
                "category": result.get("category", "Other"),
                "confidence": result.get("confidence", 0.9),
                "merchant": merchant,
                "amount": amount
            }
        except Exception as e:
            print(f"AI categorization error: {e}, falling back to rules")
    
    # Fallback: Rule-based categorization
    return _rule_based_categorization(merchant, amount)


def _rule_based_categorization(merchant: str, amount: float) -> dict:
    """Rule-based categorization as fallback"""
    merchant_lower = merchant.lower()
    
    category_rules = {
        'Dining': ['restaurant', 'cafe', 'coffee', 'pizza', 'burger', 'starbucks', 'chipotle', 'mcdonalds', 'subway', 'doordash', 'ubereats', 'grubhub', 'nobu', 'eataly', 'sweetgreen'],
        'Groceries': ['grocery', 'market', 'whole foods', 'trader joe', 'walmart', 'target', 'costco', 'kroger', 'safeway', 'publix', 'aldi', 'sprouts'],
        'Transport': ['uber', 'lyft', 'gas', 'shell', 'chevron', 'bp', 'parking', 'transit', 'metro', 'ventra', 'metra', 'bird', 'lime'],
        'Entertainment': ['netflix', 'spotify', 'hulu', 'disney', 'hbo', 'theater', 'cinema', 'concert', 'game', 'steam', 'playstation', 'peloton'],
        'Shopping': ['amazon', 'ebay', 'etsy', 'nike', 'adidas', 'zara', 'h&m', 'best buy', 'apple store', 'nordstrom', 'sephora', 'lululemon'],
        'Bills & Utilities': ['electric', 'water', 'internet', 'phone', 'verizon', 'at&t', 'comcast', 'insurance', 'comed', 'xfinity', 'geico'],
        'Health & Fitness': ['gym', 'fitness', 'pharmacy', 'cvs', 'walgreens', 'doctor', 'medical', 'health', 'equinox', 'soulcycle', 'yoga'],
        'Travel': ['airline', 'hotel', 'airbnb', 'expedia', 'booking', 'delta', 'american airlines', 'marriott', 'hyatt'],
    }
    
    category = 'Other'
    confidence = 0.6
    
    for cat, keywords in category_rules.items():
        if any(keyword in merchant_lower for keyword in keywords):
            category = cat
            confidence = 0.95
            break
    
    return {
        "category": category,
        "confidence": confidence,
        "merchant": merchant,
        "amount": amount
    }


async def generate_insights(transactions: List[dict]) -> dict:
    """
    Generate AI-powered spending insights
    """
    
    df = pd.DataFrame(transactions)
    
    # Calculate metrics
    total_spending = df['amount'].sum()
    category_spending = df.groupby('category')['amount'].sum().to_dict()
    top_categories = sorted(category_spending.items(), key=lambda x: x[1], reverse=True)[:3]
    
    if USE_AI and len(transactions) > 10:
        try:
            print("🤖 Generating insights with Claude AI...")
            client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
            
            # Prepare summary for AI
            summary = {
                "total_spending": round(total_spending, 2),
                "transaction_count": len(transactions),
                "top_categories": {cat: round(amt, 2) for cat, amt in top_categories},
                "date_range": {
                    "start": df['date'].min(),
                    "end": df['date'].max()
                }
            }
            
            prompt = f"""You are a financial advisor analyzing spending patterns. Generate 5 specific, actionable insights with exact dollar amounts.

Spending Summary:
{json.dumps(summary, indent=2)}

Category Breakdown:
{json.dumps({k: round(v, 2) for k, v in category_spending.items()}, indent=2)}

Generate insights that:
1. Identify the highest spending category with specific amounts
2. Find savings opportunities with calculated dollar amounts  
3. Recognize good habits worth continuing
4. Spot unusual patterns
5. Provide actionable next steps

Format each insight to start with an emoji (🎯💰🍽️💳📅🛍️) and include specific dollar amounts.

Respond with ONLY valid JSON (no markdown, no backticks):
{{"insights": ["insight 1", "insight 2", "insight 3", "insight 4", "insight 5"], "savings_potential": 450.00}}"""

            message = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )
            
            result = json.loads(message.content[0].text)
            print("✅ AI insights generated!")
            
            return {
                "insights": result.get("insights", []),
                "savings_potential": result.get("savings_potential", 0),
                "spending_summary": summary
            }
            
        except Exception as e:
            print(f"AI insights error: {e}, falling back to rule-based")
    
    # Fallback: Rule-based insights
    return _generate_rule_based_insights(df, total_spending, category_spending, top_categories)


def _generate_rule_based_insights(df, total_spending, category_spending, top_categories):
    """Rule-based insights as fallback"""
    insights = []
    
    if top_categories:
        top_cat, top_amount = top_categories[0]
        percentage = (top_amount / total_spending) * 100
        insights.append(
            f"🎯 Your highest spending category is {top_cat} at ${top_amount:.2f} "
            f"({percentage:.1f}% of total spending)"
        )
    
    dining_spending = category_spending.get('Dining', 0)
    if dining_spending > 0:
        avg_meal = dining_spending / len(df[df['category'] == 'Dining'])
        insights.append(
            f"🍽️ You spent ${dining_spending:.2f} on dining out. "
            f"Average meal cost: ${avg_meal:.2f}. "
            f"Cooking at home 2 more times per week could save ~${dining_spending * 0.3:.2f}/month"
        )
    
    subscriptions = ['netflix', 'spotify', 'hulu', 'disney', 'hbo', 'apple', 'amazon prime']
    subscription_transactions = df[df['merchant'].str.lower().str.contains('|'.join(subscriptions), na=False)]
    
    if len(subscription_transactions) > 0:
        sub_total = subscription_transactions['amount'].sum()
        insights.append(
            f"💳 You have ${sub_total:.2f} in recurring subscriptions. "
            f"Review unused services to potentially save ${sub_total * 0.4:.2f}/month"
        )
    
    df['date'] = pd.to_datetime(df['date'])
    df['dayofweek'] = df['date'].dt.dayofweek
    weekend_spending = df[df['dayofweek'].isin([5, 6])]['amount'].sum()
    weekday_spending = df[~df['dayofweek'].isin([5, 6])]['amount'].sum()
    
    if weekend_spending > weekday_spending * 0.4:
        insights.append(
            f"📅 Weekend spending (${weekend_spending:.2f}) is significantly higher than weekdays. "
            f"Plan weekend activities in advance to reduce impulse spending"
        )
    
    potential_savings = dining_spending * 0.3 + category_spending.get('Entertainment', 0) * 0.2
    if potential_savings > 100:
        insights.append(
            f"💰 Potential monthly savings: ${potential_savings:.2f} by optimizing dining and entertainment"
        )
    
    return {
        "insights": insights,
        "savings_potential": round(potential_savings, 2),
        "spending_summary": {
            "total": round(total_spending, 2),
            "by_category": {k: round(v, 2) for k, v in category_spending.items()},
            "average_transaction": round(df['amount'].mean(), 2),
            "transaction_count": len(df)
        }
    }


async def generate_nudges(transactions: List[dict]) -> dict:
    """
    Generate personalized behavioral nudges
    """
    
    df = pd.DataFrame(transactions)
    category_spending = df.groupby('category')['amount'].sum().to_dict()
    
    if USE_AI and len(transactions) > 10:
        try:
            print("🤖 Generating nudges with Claude AI...")
            client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
            
            summary = {
                "total_spending": round(df['amount'].sum(), 2),
                "categories": {k: round(v, 2) for k, v in category_spending.items()}
            }
            
            prompt = f"""You are a behavioral finance expert. Create 4-5 actionable "nudges" to improve financial behavior.

Spending Profile:
{json.dumps(summary, indent=2)}

Create nudges that:
1. Are specific and actionable (not generic advice)
2. Include concrete dollar amounts for potential savings
3. Use behavioral psychology principles
4. Have clear priority levels (high/medium/low)
5. Feel personal and encouraging

Respond with ONLY valid JSON (no markdown, no backticks):
{{
  "nudges": [
    {{
      "title": "Specific actionable title",
      "description": "Detailed explanation with numbers and specific steps",
      "type": "budget|automation|optimization|behavioral",
      "priority": "high|medium|low",
      "potential_savings": 123.45
    }}
  ]
}}"""

            message = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )
            
            result = json.loads(message.content[0].text)
            nudges = result.get("nudges", [])
            print("✅ AI nudges generated!")
            
            return {
                "nudges": nudges,
                "priority_actions": [n["title"] for n in nudges if n["priority"] == "high"][:3],
                "total_potential_savings": round(sum(n["potential_savings"] for n in nudges), 2)
            }
            
        except Exception as e:
            print(f"AI nudges error: {e}, falling back to rule-based")
    
    # Fallback: Rule-based nudges
    return _generate_rule_based_nudges(df, category_spending)


def _generate_rule_based_nudges(df, category_spending):
    """Rule-based nudges as fallback"""
    nudges = []
    priority_actions = []
    
    dining_total = category_spending.get('Dining', 0)
    if dining_total > 300:
        nudges.append({
            "title": "Set a Dining Budget",
            "description": f"You spent ${dining_total:.2f} on dining. Try setting a ${dining_total * 0.8:.2f} budget for next month.",
            "type": "budget",
            "priority": "high",
            "potential_savings": round(dining_total * 0.2, 2)
        })
        priority_actions.append("Set dining budget")
    
    subscriptions = ['netflix', 'spotify', 'hulu', 'disney', 'hbo']
    sub_count = len(df[df['merchant'].str.lower().str.contains('|'.join(subscriptions), na=False)]['merchant'].unique())
    
    if sub_count >= 3:
        nudges.append({
            "title": "Audit Your Subscriptions",
            "description": f"You have {sub_count} active subscriptions. Cancel unused ones to save money.",
            "type": "optimization",
            "priority": "medium",
            "potential_savings": 50
        })
        priority_actions.append("Review subscriptions")
    
    total_spending = df['amount'].sum()
    if total_spending > 1000:
        savings_amount = total_spending * 0.1
        nudges.append({
            "title": "Automate Your Savings",
            "description": f"Set up automatic transfer of ${savings_amount:.2f} (10% of spending) to savings each month",
            "type": "savings",
            "priority": "high",
            "potential_savings": round(savings_amount, 2)
        })
        priority_actions.append("Set up auto-save")
    
    nudges.append({
        "title": "Use Cashback Credit Cards",
        "description": f"Earn 2-5% cashback on ${category_spending.get('Groceries', 0):.2f} in grocery spending",
        "type": "rewards",
        "priority": "medium",
        "potential_savings": round(category_spending.get('Groceries', 0) * 0.03, 2)
    })
    
    return {
        "nudges": nudges,
        "priority_actions": priority_actions[:3],
        "total_potential_savings": round(sum(n["potential_savings"] for n in nudges), 2)
    }