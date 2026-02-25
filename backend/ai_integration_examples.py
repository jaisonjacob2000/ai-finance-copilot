"""
AI Integration Examples
This file contains example prompts and integration code for Claude/GPT APIs
"""

# ============================================================================
# EXAMPLE 1: Transaction Categorization
# ============================================================================

CATEGORIZATION_PROMPT = """
You are a financial transaction categorizer. Analyze the following transaction and categorize it.

Transaction Details:
- Merchant: {merchant}
- Amount: ${amount}
- Description: {description}

Categories to choose from:
- Dining (restaurants, cafes, food delivery)
- Groceries (supermarkets, food stores)
- Transport (rideshare, gas, parking, public transit)
- Entertainment (streaming, movies, games, events)
- Shopping (retail, online stores, clothing)
- Bills & Utilities (electric, internet, phone, insurance)
- Health & Fitness (gym, pharmacy, medical)
- Travel (flights, hotels, rentals)
- Other (anything that doesn't fit above)

Respond with ONLY a JSON object in this format:
{{
  "category": "category_name",
  "confidence": 0.95,
  "reasoning": "brief explanation"
}}
"""

async def categorize_with_claude(merchant: str, amount: float, description: str = ""):
    """Example using Claude API"""
    import anthropic
    import os
    
    client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
    
    prompt = CATEGORIZATION_PROMPT.format(
        merchant=merchant,
        amount=amount,
        description=description
    )
    
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=256,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    # Parse JSON response
    import json
    result = json.loads(message.content[0].text)
    return result


# ============================================================================
# EXAMPLE 2: Generate Spending Insights
# ============================================================================

INSIGHTS_PROMPT = """
You are a personal finance advisor. Analyze the following spending data and generate 5 actionable insights.

Spending Summary:
{spending_summary}

Category Breakdown:
{category_breakdown}

Transaction Patterns:
{transaction_patterns}

Generate insights that:
1. Identify spending patterns (by category, time, merchant)
2. Compare spending to typical budgets
3. Find opportunities for savings (specific dollar amounts)
4. Highlight unusual spending behavior
5. Provide concrete, actionable recommendations

Format each insight with an emoji and specific numbers. Examples:
- "🎯 Your dining spending ($450) is 30% above typical. Cooking 3 more meals/week could save $135/month"
- "💰 You have 5 recurring subscriptions totaling $67.45. Review Netflix and Hulu for potential savings of $25/month"

Respond with a JSON object:
{{
  "insights": [
    "insight 1 with emoji and numbers",
    "insight 2 with emoji and numbers",
    ...
  ],
  "total_savings_potential": 450.00,
  "priority_categories": ["category1", "category2"]
}}
"""

async def generate_insights_with_ai(transactions_summary: dict):
    """Example using Claude API for insights"""
    import anthropic
    import os
    import json
    
    client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
    
    # Format the data for the prompt
    prompt = INSIGHTS_PROMPT.format(
        spending_summary=json.dumps(transactions_summary['summary'], indent=2),
        category_breakdown=json.dumps(transactions_summary['categories'], indent=2),
        transaction_patterns=json.dumps(transactions_summary['patterns'], indent=2)
    )
    
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    result = json.loads(message.content[0].text)
    return result


# ============================================================================
# EXAMPLE 3: Generate Behavioral Nudges
# ============================================================================

NUDGES_PROMPT = """
You are a behavioral finance expert. Based on the spending data, create personalized "nudges" to improve financial behavior.

User Spending Profile:
{user_profile}

Create 3-5 nudges that:
1. Are specific and actionable
2. Include concrete dollar amounts
3. Use behavioral psychology principles (defaults, commitment, social proof)
4. Prioritize by impact (high/medium/low)
5. Feel personal, not generic

Good nudge examples:
- "Set a dining budget" → "You spent $450 on dining last month. Set a $350 budget this month and you'll save $100. Start by packing lunch 2 days/week."
- "Automate savings" → "Transfer $200 (10% of spending) to savings every payday. You won't miss it and you'll save $2,400/year."

Respond with JSON:
{{
  "nudges": [
    {{
      "title": "Specific actionable title",
      "description": "Detailed explanation with numbers and steps",
      "type": "budget|automation|optimization|behavioral",
      "priority": "high|medium|low",
      "potential_savings": 123.45,
      "timeframe": "daily|weekly|monthly|yearly"
    }}
  ]
}}
"""

async def generate_nudges_with_ai(user_profile: dict):
    """Example using Claude API for nudges"""
    import anthropic
    import os
    import json
    
    client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
    
    prompt = NUDGES_PROMPT.format(
        user_profile=json.dumps(user_profile, indent=2)
    )
    
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    result = json.loads(message.content[0].text)
    return result


# ============================================================================
# EXAMPLE 4: Using OpenAI GPT (Alternative)
# ============================================================================

async def categorize_with_gpt(merchant: str, amount: float, description: str = ""):
    """Example using OpenAI API"""
    import openai
    import os
    import json
    
    client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    prompt = CATEGORIZATION_PROMPT.format(
        merchant=merchant,
        amount=amount,
        description=description
    )
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a financial transaction categorizer."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=256
    )
    
    result = json.loads(response.choices[0].message.content)
    return result


# ============================================================================
# EXAMPLE 5: Batch Processing for Efficiency
# ============================================================================

async def batch_categorize_transactions(transactions: list):
    """Categorize multiple transactions in one API call"""
    import anthropic
    import os
    import json
    
    client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
    
    # Format all transactions
    transactions_text = "\n".join([
        f"{i+1}. {t['merchant']} - ${t['amount']}"
        for i, t in enumerate(transactions)
    ])
    
    prompt = f"""
    Categorize these {len(transactions)} transactions. Use the same categories as before.
    
    Transactions:
    {transactions_text}
    
    Respond with JSON array:
    [
      {{"transaction_number": 1, "category": "Dining", "confidence": 0.95}},
      {{"transaction_number": 2, "category": "Shopping", "confidence": 0.88}},
      ...
    ]
    """
    
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    results = json.loads(message.content[0].text)
    return results


# ============================================================================
# EXAMPLE 6: Streaming Responses (for long insights)
# ============================================================================

async def stream_insights(transactions_summary: dict):
    """Stream insights as they're generated"""
    import anthropic
    import os
    
    client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
    
    prompt = INSIGHTS_PROMPT.format(
        spending_summary="...",
        category_breakdown="...",
        transaction_patterns="..."
    )
    
    with client.messages.stream(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)


# ============================================================================
# EXAMPLE 7: Error Handling and Retries
# ============================================================================

import asyncio
from typing import Optional

async def safe_ai_call(prompt: str, max_retries: int = 3) -> Optional[dict]:
    """AI call with error handling and retries"""
    import anthropic
    import os
    import json
    
    client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
    
    for attempt in range(max_retries):
        try:
            message = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Try to parse JSON
            result = json.loads(message.content[0].text)
            return result
            
        except json.JSONDecodeError:
            # If JSON parsing fails, extract just the text
            return {"text": message.content[0].text}
            
        except anthropic.RateLimitError:
            # Wait before retrying
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
            else:
                raise
                
        except anthropic.APIError as e:
            print(f"API Error: {e}")
            return None
    
    return None


# ============================================================================
# EXAMPLE 8: Cost Optimization
# ============================================================================

def optimize_prompt_tokens(transactions: list, max_transactions: int = 50):
    """Reduce prompt size to save on API costs"""
    # Only send summary statistics, not all transactions
    summary = {
        "total_transactions": len(transactions),
        "total_spending": sum(t['amount'] for t in transactions),
        "top_categories": {},  # Summarize instead of full data
        "date_range": {
            "start": min(t['date'] for t in transactions),
            "end": max(t['date'] for t in transactions)
        }
    }
    
    # If many transactions, sample them
    if len(transactions) > max_transactions:
        import random
        transactions = random.sample(transactions, max_transactions)
    
    return summary, transactions


# ============================================================================
# INTEGRATION CHECKLIST
# ============================================================================

"""
To integrate real AI into your project:

1. Choose your provider:
   [ ] Anthropic Claude (recommended for this use case)
   [ ] OpenAI GPT-4
   [ ] Both (for comparison/fallback)

2. Get API key:
   [ ] Sign up at console.anthropic.com or platform.openai.com
   [ ] Copy your API key
   [ ] Add to .env file: ANTHROPIC_API_KEY=your_key

3. Update ai_service.py:
   [ ] Uncomment the AI API calls
   [ ] Replace rule-based logic with AI calls
   [ ] Add error handling

4. Test:
   [ ] Start with small dataset
   [ ] Monitor API costs
   [ ] Validate output quality
   [ ] Add caching to reduce calls

5. Monitor costs:
   [ ] Set up usage alerts
   [ ] Implement caching strategy
   [ ] Use batch processing when possible
   [ ] Consider using cheaper models for simple tasks

Estimated costs (Claude Sonnet):
- Categorization: ~$0.0003 per transaction
- Insights: ~$0.002 per analysis
- Nudges: ~$0.002 per generation

For 100 transactions/day: ~$0.30/day or ~$9/month
"""
