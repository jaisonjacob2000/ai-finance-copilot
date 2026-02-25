"""
AI Personal Finance Copilot - Backend API
Built with FastAPI and Claude AI
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
import json
from datetime import datetime
import io

app = FastAPI(title="Finance Copilot API")

# CORS middleware for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage (use database in production)
transactions_db = []

# Pydantic models
class Transaction(BaseModel):
    id: Optional[int] = None
    date: str
    merchant: str
    amount: float
    category: Optional[str] = None
    description: Optional[str] = None
    confidence: Optional[float] = None

class InsightResponse(BaseModel):
    insights: List[str]
    savings_potential: float
    spending_summary: dict

class NudgeResponse(BaseModel):
    nudges: List[dict]
    priority_actions: List[str]

@app.get("/")
async def root():
    return {
        "message": "AI Personal Finance Copilot API",
        "version": "1.0.0",
        "endpoints": {
            "transactions": "/api/transactions",
            "upload": "/api/upload",
            "insights": "/api/insights",
            "nudges": "/api/nudges",
            "categories": "/api/categories"
        }
    }

@app.get("/api/transactions")
async def get_transactions(category: Optional[str] = None):
    """Get all transactions, optionally filtered by category"""
    if category:
        filtered = [t for t in transactions_db if t.get('category') == category]
        return {"transactions": filtered, "count": len(filtered)}
    return {"transactions": transactions_db, "count": len(transactions_db)}

@app.post("/api/upload")
async def upload_transactions(file: UploadFile = File(...)):
    """Upload CSV file with transactions"""
    try:
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        # Validate required columns
        required_cols = ['date', 'merchant', 'amount']
        if not all(col in df.columns for col in required_cols):
            raise HTTPException(400, "CSV must contain: date, merchant, amount")
        
        # Clear existing data and load new
        transactions_db.clear()
        
        for idx, row in df.iterrows():
            transaction = {
                "id": idx + 1,
                "date": row['date'],
                "merchant": row['merchant'],
                "amount": float(row['amount']),
                "category": row.get('category', 'Uncategorized'),
                "description": row.get('description', ''),
                "confidence": None
            }
            transactions_db.append(transaction)
        
        return {
            "message": "Transactions uploaded successfully",
            "count": len(transactions_db)
        }
    except Exception as e:
        raise HTTPException(500, f"Error processing file: {str(e)}")

@app.get("/api/categories")
async def get_categories():
    """Get spending breakdown by category"""
    category_totals = {}
    
    for t in transactions_db:
        category = t.get('category', 'Uncategorized')
        category_totals[category] = category_totals.get(category, 0) + t['amount']
    
    total_spending = sum(category_totals.values())
    
    categories = [
        {
            "name": cat,
            "total": round(total, 2),
            "percentage": round((total / total_spending * 100), 1) if total_spending > 0 else 0
        }
        for cat, total in sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
    ]
    
    return {
        "categories": categories,
        "total_spending": round(total_spending, 2)
    }

@app.post("/api/categorize")
async def categorize_transaction(transaction: Transaction):
    """Categorize a single transaction using AI"""
    from ai_service import categorize_with_ai
    
    result = await categorize_with_ai(
        merchant=transaction.merchant,
        amount=transaction.amount,
        description=transaction.description or ""
    )
    
    return result

@app.get("/api/insights")
async def get_insights():
    """Generate AI-powered spending insights"""
    if not transactions_db:
        raise HTTPException(400, "No transactions found. Upload data first.")
    
    from ai_service import generate_insights
    
    insights = await generate_insights(transactions_db)
    return insights

@app.get("/api/nudges")
async def get_nudges():
    """Generate personalized behavioral nudges"""
    if not transactions_db:
        raise HTTPException(400, "No transactions found. Upload data first.")
    
    from ai_service import generate_nudges
    
    nudges = await generate_nudges(transactions_db)
    return nudges

@app.get("/api/stats")
async def get_stats():
    """Get overall spending statistics"""
    if not transactions_db:
        return {
            "total_transactions": 0,
            "total_spending": 0,
            "average_transaction": 0,
            "date_range": None
        }
    
    df = pd.DataFrame(transactions_db)
    
    return {
        "total_transactions": len(transactions_db),
        "total_spending": round(df['amount'].sum(), 2),
        "average_transaction": round(df['amount'].mean(), 2),
        "highest_transaction": round(df['amount'].max(), 2),
        "date_range": {
            "start": df['date'].min(),
            "end": df['date'].max()
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
