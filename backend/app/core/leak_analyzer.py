"""
AI-powered Financial Leak Analyzer using Gemini API
Analyzes aggregated spending pattern evidence to identify financial leaks with reasoning & confidence.

NEW FLOW:
- AI reads from SpendingPatternStats (aggregated evidence, facts only)
- AI does NOT compute statistics
- AI does NOT detect patterns
- AI reasons over evidence to answer:
  * Why this might be a leak
  * How confident to be
  * How to explain it humanly
  * What options user has
"""

import os
import json
from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.models import SpendingPatternStats, User
import logging

logger = logging.getLogger(__name__)

# Try to import Gemini client (optional for development)
try:
    from google import genai
    from google.genai import types
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("google-genai not installed. AI analysis will be unavailable.")


# ==================== PYDANTIC SCHEMAS ====================

class FinancialLeak(BaseModel):
    """Represents AI reasoning over a spending pattern"""
    pattern_id: int = Field(description="Database ID of the spending pattern")
    merchant_hint: str = Field(description="Merchant name/identity")
    leak_category: str = Field(description="Type of leak: unused_subscription, excessive_habit, impulse_spending, etc.")
    leak_probability: float = Field(description="Confidence score from 0.0 to 1.0")
    reasoning: str = Field(description="Why this is (or isn't) a financial leak, based on evidence")
    actionable_step: str = Field(description="Clear, actionable advice for user")
    estimated_annual_saving: float = Field(description="Estimated annual savings if leak is reduced/stopped")


class LeakAnalysisResponse(BaseModel):
    """Complete leak analysis response"""
    leaks: List[FinancialLeak]
    total_estimated_annual_saving: float = Field(description="Sum of all potential annual savings")
    analysis_timestamp: str = Field(description="ISO timestamp of when analysis was performed")
    confidence_level: str = Field(description="Overall confidence: high, medium, low")

# ==================== LEAK ANALYZER ====================

class LeakAnalyzer:
    """AI-powered analyzer for financial leaks using Gemini
    
    NEW ARCHITECTURE:
    - Reads aggregated evidence from SpendingPatternStats table
    - Does NOT compute statistics or detect patterns
    - Reasons over evidence to identify potential leaks
    - Generates human-readable explanations
    - Estimates savings conservatively
    """
    
    # Fallback model list (in order of preference)
    FALLBACK_MODELS = [
        "gemini-2.5-flash",
        "gemini-3-flash",
        "gemini-2.5-flash-lite",
    ]
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the leak analyzer
        
        Args:
            api_key: Gemini API key. If None, will try to load from environment.
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.primary_model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
        self.fallback_models = self.FALLBACK_MODELS.copy()
        
        # Ensure primary model is at the front of fallback list
        if self.primary_model in self.fallback_models:
            self.fallback_models.remove(self.primary_model)
        self.fallback_models.insert(0, self.primary_model)
        
        self.enabled = GEMINI_AVAILABLE and bool(self.api_key)
        
        if self.enabled:
            logger.info(f"Gemini AI analyzer initialized with primary model: {self.primary_model}")
            logger.info(f"Fallback models: {', '.join(self.fallback_models[1:])}")
        else:
            raise ValueError("Gemini API not available. Cannot initialize analyzer without API key.")
    
    def format_patterns_for_analysis(self, patterns: List[Dict]) -> str:
        """Convert aggregated pattern stats to JSON for AI reasoning
        
        Args:
            patterns: List of SpendingPatternStats dicts from database
            
        Returns:
            JSON string representation of pattern evidence
            
        Note:
            Includes only aggregated EVIDENCE (facts), not conclusions.
            AI will reason over this evidence.
        """
        patterns_data = []
        for pattern in patterns:
            patterns_data.append({
                "id": pattern['id'],
                "merchant": pattern['merchant_hint'],
                "level_3_category": pattern['dominant_level_3_tag'],
                "category_confidence": float(pattern['level_3_confidence']) if pattern['level_3_confidence'] else 0.0,
                
                # Aggregated evidence (FACTS ONLY)
                "transaction_count": pattern['txn_count'],
                "total_spent": float(pattern['total_amount']),
                "average_per_transaction": float(pattern['avg_amount']) if pattern['avg_amount'] else 0.0,
                "amount_std_dev": float(pattern['amount_std']) if pattern['amount_std'] else 0.0,
                "min_amount": float(pattern['amount_min']) if pattern['amount_min'] else 0.0,
                "max_amount": float(pattern['amount_max']) if pattern['amount_max'] else 0.0,
                
                # Temporal evidence
                "active_duration_days": pattern['active_duration_days'],
                "average_gap_days": float(pattern['avg_gap_days']) if pattern['avg_gap_days'] else 0.0,
                "gap_std_dev": float(pattern['gap_std_days']) if pattern['gap_std_days'] else 0.0,
                "min_gap_days": float(pattern['gap_min_days']) if pattern['gap_min_days'] else 0.0,
                "max_gap_days": float(pattern['gap_max_days']) if pattern['gap_max_days'] else 0.0,
                "days_since_last_transaction": pattern['last_txn_days_ago'],
            })
        
        return json.dumps(patterns_data, indent=2)
    
    async def analyze_patterns(self, patterns: List[Dict]) -> LeakAnalysisResponse:
        """Analyze spending pattern evidence for financial leaks using AI reasoning
        
        AI RESPONSIBILITIES:
        - Read aggregated evidence from patterns
        - Reason whether pattern indicates a leak
        - Estimate confidence and annual savings
        - Generate human-readable explanation
        
        AI DOES NOT:
        - Compute statistics (already done)
        - Detect patterns (already done)
        - Filter patterns (all passed patterns analyzed)
        
        Args:
            patterns: List of pattern dicts with aggregated evidence from SpendingPatternStats
            
        Returns:
            LeakAnalysisResponse with AI reasoning
            
        Raises:
            ValueError: If patterns list is empty
            Exception: If all Gemini API models fail
        """
        if not patterns:
            raise ValueError("No patterns provided for analysis")
        
        if not self.enabled:
            raise ValueError("Gemini API not available. API key not configured.")
        
        # Format patterns for Gemini
        patterns_json = self.format_patterns_for_analysis(patterns)
        
        # System prompt for AI reasoning (NOT pattern detection)
        system_prompt = """You are a financial advisor assistant.

You will be given aggregated spending pattern EVIDENCE from a user's transaction data.
Each pattern represents repeatedly observed spending behavior with computed statistics.

YOUR TASK:
- Reason over the evidence to identify potential financial LEAKS
- Generate confidence scores (0.0 to 1.0) based on evidence strength
- Explain findings in clear, human-readable language
- Suggest actionable steps user can take
- Estimate conservative annual savings

IMPORTANT CONSTRAINTS:
- You MUST analyze EVERY pattern provided
- Do NOT invent or compute statistics (they're already provided)
- Do NOT re-detect patterns (they're already detected and aggregated)
- Base ALL reasoning only on the provided evidence
- Avoid alarmist language; be balanced and fair
- Be conservative with savings estimates

REASONING FRAMEWORK:
Consider these factors when assessing if a pattern is a leak:
- Frequency: How often does this spending occur?
- Predictability: Is the gap between transactions consistent?
- Recency: How recent is the last transaction?
- Amount: Is the amount stable or volatile?
- Category: What type of spending is it? (subscription services are often leaks)
- Necessity: Is this essential spending or discretionary?

A strong leak signal:
- Regular, predictable frequency (low gap variance)
- Discretionary category (OTT, FOOD, RETAIL vs UTILITIES)
- User might not be consciously tracking it
- Cancelable without immediate hardship"""

        # Create prompt for AI analysis
        user_prompt = f"""Analyze EVERY spending pattern below based on the provided evidence.

For each pattern, determine:
1. Is this a potential financial leak? (yes/no with reasoning)
2. What is your confidence? (0.0 to 1.0, higher = more certain)
3. Why? (explain based on the evidence provided)
4. What should user do? (specific, actionable advice)
5. How much could they save annually? (conservative estimate)

EVIDENCE (aggregated from transactions):
{patterns_json}

IMPORTANT: Include ALL patterns in your response.

Return valid JSON with structure:
{{
  "leaks": [
    {{
      "pattern_id": <id>,
      "merchant_hint": "<merchant>",
      "leak_category": "<type>",
      "leak_probability": <0.0-1.0>,
      "reasoning": "<explanation>",
      "actionable_step": "<advice>",
      "estimated_annual_saving": <amount>
    }}
  ],
  "total_estimated_annual_saving": <sum>,
  "analysis_timestamp": "<ISO datetime>",
  "confidence_level": "<high|medium|low>"
}}"""

        from datetime import datetime as dt
        
        # Try each fallback model
        last_error = None
        for attempt, model in enumerate(self.fallback_models[:3], 1):  # Try max 3 models
            try:
                logger.info(f"Attempt {attempt}/3: Calling Gemini API with model '{model}' for leak reasoning")
                
                client = genai.Client(api_key=self.api_key)
                response = client.models.generate_content(
                    model=model,
                    contents=user_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        temperature=0.3,  # Lower temperature for consistent reasoning
                        response_mime_type="application/json",
                        response_schema=LeakAnalysisResponse,
                    ),
                )
                
                # Parse response using Pydantic model validation
                analysis = LeakAnalysisResponse.model_validate_json(response.text)
                logger.info(f"✓ Leak reasoning successful with model '{model}'. Analyzed {len(analysis.leaks)} patterns.")
                return analysis
                
            except json.JSONDecodeError as e:
                last_error = f"JSON parsing error: {str(e)}"
                logger.warning(f"Attempt {attempt} - {last_error}")
                continue
            except Exception as e:
                last_error = f"{type(e).__name__}: {str(e)}"
                logger.warning(f"Attempt {attempt} - Model '{model}' failed: {last_error}")
                continue
        
        # All models failed
        error_msg = f"All 3 Gemini AI models failed. Last error: {last_error}"
        logger.error(error_msg)
        raise Exception(error_msg)


# ==================== FASTAPI ENDPOINTS ====================

from fastapi import APIRouter, Depends, HTTPException, status, Request
from app.database import get_db
from app.models import LeakInsight
from app.schema import LeakAnalysisResponseSchema, LeakInsightDB
from app.api.auth import get_current_user_from_token
from datetime import datetime

router = APIRouter(prefix="/api/leaks", tags=["leaks"])

# Initialize the leak analyzer
try:
    leak_analyzer = LeakAnalyzer()
except ValueError as e:
    logger.error(f"Failed to initialize LeakAnalyzer: {str(e)}")
    leak_analyzer = None


@router.post("/analyze")
async def analyze_for_leaks(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Trigger AI reasoning on user's spending pattern evidence to identify financial leaks
    
    NEW FLOW:
    1. Read aggregated patterns from SpendingPatternStats (evidence only)
    2. Send to AI for reasoning (NO pattern detection, NO stat computation)
    3. Store AI-generated LeakInsights
    
    Returns:
        LeakAnalysisResponseSchema with AI reasoning and leak insights
    """
    # Get authenticated user
    current_user: User = get_current_user_from_token(request, db)
    
    if not leak_analyzer:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI analyzer not initialized. Check that GEMINI_API_KEY is configured."
        )
    
    try:
        # Get all aggregated pattern stats for this user (SOURCE OF TRUTH for aggregated evidence)
        pattern_stats = db.query(SpendingPatternStats).filter(
            SpendingPatternStats.user_id == current_user.id
        ).all()
        
        if not pattern_stats:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No spending patterns found. Please upload transactions first."
            )
        
        # Convert ORM objects to dicts for AI analysis
        patterns_data = [
            {
                'id': p.id,
                'merchant_hint': p.merchant_hint,
                'dominant_level_3_tag': p.dominant_level_3_tag,
                'level_3_confidence': p.level_3_confidence,
                'txn_count': p.txn_count,
                'total_amount': p.total_amount,
                'avg_amount': p.avg_amount,
                'amount_std': p.amount_std,
                'amount_min': p.amount_min,
                'amount_max': p.amount_max,
                'active_duration_days': p.active_duration_days,
                'avg_gap_days': p.avg_gap_days,
                'gap_std_days': p.gap_std_days,
                'gap_min_days': p.gap_min_days,
                'gap_max_days': p.gap_max_days,
                'last_txn_days_ago': p.last_txn_days_ago,
            }
            for p in pattern_stats
        ]
        
        logger.info(f"Running AI reasoning on {len(patterns_data)} pattern stats for user {current_user.id}")
        
        # Run AI reasoning (NOT pattern detection, NOT stat computation)
        analysis_result = await leak_analyzer.analyze_patterns(patterns_data)
        
        # Store/update leak insights in database
        for leak in analysis_result.leaks:
            existing_insight = db.query(LeakInsight).filter(
                LeakInsight.pattern_id == leak.pattern_id,
                LeakInsight.user_id == current_user.id
            ).first()
            
            if not existing_insight:
                # Create new leak insight from AI reasoning
                new_insight = LeakInsight(
                    user_id=current_user.id,
                    pattern_id=leak.pattern_id,
                    leak_category=leak.leak_category,
                    leak_probability=leak.leak_probability,
                    reasoning=leak.reasoning,
                    actionable_step=leak.actionable_step,
                    estimated_annual_saving=leak.estimated_annual_saving,
                    analysis_timestamp=datetime.fromisoformat(analysis_result.analysis_timestamp)
                )
                db.add(new_insight)
            else:
                # Update existing insight with new AI reasoning
                existing_insight.leak_category = leak.leak_category
                existing_insight.leak_probability = leak.leak_probability
                existing_insight.reasoning = leak.reasoning
                existing_insight.actionable_step = leak.actionable_step
                existing_insight.estimated_annual_saving = leak.estimated_annual_saving
                existing_insight.analysis_timestamp = datetime.fromisoformat(analysis_result.analysis_timestamp)
                db.add(existing_insight)
        
        db.commit()
        
        logger.info(f"Stored/updated {len(analysis_result.leaks)} leak insights for user {current_user.id}")
        
        # Get statistics for response (total spend, transaction count from patterns)
        pattern_stats = db.query(SpendingPatternStats).filter(
            SpendingPatternStats.user_id == current_user.id
        ).all()
        
        # Create a map of pattern_id to pattern stats for easy lookup
        pattern_stats_map = {p.id: p for p in pattern_stats}
        
        # Enhance leak response with pattern statistics
        leaks_with_stats = []
        for leak in analysis_result.leaks:
            leak_dict = leak.model_dump()
            pattern = pattern_stats_map.get(leak.pattern_id)
            
            if pattern:
                leak_dict['transaction_count'] = pattern.txn_count
                leak_dict['total_spent'] = pattern.total_amount
                leak_dict['avg_per_transaction'] = pattern.avg_amount
                leak_dict['active_duration_days'] = pattern.active_duration_days
                leak_dict['avg_frequency_days'] = pattern.avg_gap_days
                leak_dict['last_transaction_days_ago'] = pattern.last_txn_days_ago
                leak_dict['dominant_level_1_tag'] = pattern.dominant_level_1_tag
                leak_dict['dominant_level_2_tag'] = pattern.dominant_level_2_tag
            
            leaks_with_stats.append(leak_dict)
        
        statistics = {
            "total_spend": sum(p.total_amount for p in pattern_stats),
            "transaction_count": sum(p.txn_count for p in pattern_stats),
            "transactions_stored": sum(p.txn_count for p in pattern_stats),
            "pattern_stats_stored": len(pattern_stats),
        }
        
        # Return analysis with statistics included
        response_dict = analysis_result.model_dump()
        response_dict['leaks'] = leaks_with_stats
        response_dict['statistics'] = statistics
        
        return response_dict
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error analyzing patterns: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI analysis service temporarily unavailable. All fallback models failed. Please try again later."
        )


@router.get("/latest")
async def get_latest_analysis(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Get the latest leak analysis for the current user
    Combines leak insights with statistics for dashboard restoration on page refresh
    
    Returns:
        Object with leaks array and statistics for dashboard display
    """
    current_user: User = get_current_user_from_token(request, db)
    
    try:
        # Get all unresolved leaks ordered by timestamp (most recent first)
        leaks = db.query(LeakInsight).filter(
            LeakInsight.user_id == current_user.id,
            LeakInsight.is_resolved == False
        ).order_by(LeakInsight.analysis_timestamp.desc()).all()
        
        if not leaks:
            return {"leaks": [], "statistics": {}, "total_estimated_annual_saving": 0}
        
        # Get statistics from spending patterns
        pattern_stats = db.query(SpendingPatternStats).filter(
            SpendingPatternStats.user_id == current_user.id
        ).all()
        
        statistics = {
            "total_spend": sum(p.total_amount for p in pattern_stats),
            "transaction_count": sum(p.txn_count for p in pattern_stats),
            "transactions_stored": sum(p.txn_count for p in pattern_stats),
            "pattern_stats_stored": len(pattern_stats),
        }
        
        total_saving = sum(l.estimated_annual_saving for l in leaks)
        
        # Create a map of pattern_id to pattern stats for easy lookup
        pattern_stats_map = {p.id: p for p in pattern_stats}
        
        # Format leaks for frontend with stats
        leaks_data = [
            {
                "id": leak.id,
                "pattern_id": leak.pattern_id,
                "merchant_hint": pattern_stats_map.get(leak.pattern_id).merchant_hint if leak.pattern_id in pattern_stats_map else "Unknown",
                "leak_category": leak.leak_category,
                "leak_probability": leak.leak_probability,
                "reasoning": leak.reasoning,
                "actionable_step": leak.actionable_step,
                "estimated_annual_saving": leak.estimated_annual_saving,
                "analysis_timestamp": leak.analysis_timestamp.isoformat(),
                "is_resolved": leak.is_resolved,
                # Add stats from pattern
                "transaction_count": pattern_stats_map.get(leak.pattern_id).txn_count if leak.pattern_id in pattern_stats_map else 0,
                "total_spent": pattern_stats_map.get(leak.pattern_id).total_amount if leak.pattern_id in pattern_stats_map else 0,
                "avg_per_transaction": pattern_stats_map.get(leak.pattern_id).avg_amount if leak.pattern_id in pattern_stats_map else 0,
                "active_duration_days": pattern_stats_map.get(leak.pattern_id).active_duration_days if leak.pattern_id in pattern_stats_map else 0,
                "avg_frequency_days": pattern_stats_map.get(leak.pattern_id).avg_gap_days if leak.pattern_id in pattern_stats_map else 0,
                "last_transaction_days_ago": pattern_stats_map.get(leak.pattern_id).last_txn_days_ago if leak.pattern_id in pattern_stats_map else 0,
                "dominant_level_1_tag": pattern_stats_map.get(leak.pattern_id).dominant_level_1_tag if leak.pattern_id in pattern_stats_map else None,
                "dominant_level_2_tag": pattern_stats_map.get(leak.pattern_id).dominant_level_2_tag if leak.pattern_id in pattern_stats_map else None,
            }
            for leak in leaks
        ]
        
        return {
            "leaks": leaks_data,
            "statistics": statistics,
            "total_estimated_annual_saving": total_saving,
        }
        
    except Exception as e:
        logger.error(f"Error retrieving latest analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve latest analysis"
        )


@router.get("/", response_model=list[LeakInsightDB])
async def get_user_leaks(
    request: Request,
    db: Session = Depends(get_db),
    is_resolved: bool = None
):
    """
    Get all leak insights for authenticated user
    
    Query Parameters:
        is_resolved: Filter by resolution status (true/false). If omitted, returns all.
    
    Returns:
        List of LeakInsightDB objects with leak details
    """
    current_user: User = get_current_user_from_token(request, db)
    
    try:
        query = db.query(LeakInsight).filter(LeakInsight.user_id == current_user.id)
        
        if is_resolved is not None:
            query = query.filter(LeakInsight.is_resolved == is_resolved)
        
        leaks = query.order_by(LeakInsight.analysis_timestamp.desc()).all()
        
        return leaks
        
    except Exception as e:
        logger.error(f"Error retrieving leaks: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve leaks"
        )


@router.get("/{leak_id}", response_model=LeakInsightDB)
async def get_leak_detail(
    leak_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific leak
    
    Path Parameters:
        leak_id: ID of the leak insight
    
    Returns:
        LeakInsightDB with full leak details
    """
    current_user: User = get_current_user_from_token(request, db)
    
    try:
        leak = db.query(LeakInsight).filter(
            LeakInsight.id == leak_id,
            LeakInsight.user_id == current_user.id
        ).first()
        
        if not leak:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Leak not found"
            )
        
        return leak
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving leak detail: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve leak details"
        )


@router.post("/{leak_id}/mark-resolved")
async def mark_leak_resolved(
    leak_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Mark a leak as resolved by the user
    
    Path Parameters:
        leak_id: ID of the leak to mark resolved
    
    Returns:
        Updated leak with resolved status
    """
    current_user: User = get_current_user_from_token(request, db)
    
    try:
        leak = db.query(LeakInsight).filter(
            LeakInsight.id == leak_id,
            LeakInsight.user_id == current_user.id
        ).first()
        
        if not leak:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Leak not found"
            )
        
        leak.is_resolved = True
        leak.resolved_at = datetime.utcnow()
        db.commit()
        db.refresh(leak)
        
        logger.info(f"Marked leak {leak_id} as resolved for user {current_user.id}")
        
        return {
            "message": "Leak marked as resolved",
            "leak": LeakInsightDB.from_orm(leak)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking leak as resolved: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark leak as resolved"
        )


@router.post("/{leak_id}/mark-unresolved")
async def mark_leak_unresolved(
    leak_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Mark a previously resolved leak as unresolved
    
    Path Parameters:
        leak_id: ID of the leak to mark unresolved
    
    Returns:
        Updated leak with resolved status
    """
    current_user: User = get_current_user_from_token(request, db)
    
    try:
        leak = db.query(LeakInsight).filter(
            LeakInsight.id == leak_id,
            LeakInsight.user_id == current_user.id
        ).first()
        
        if not leak:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Leak not found"
            )
        
        leak.is_resolved = False
        leak.resolved_at = None
        db.commit()
        db.refresh(leak)
        
        logger.info(f"Marked leak {leak_id} as unresolved for user {current_user.id}")
        
        return {
            "message": "Leak marked as unresolved",
            "leak": LeakInsightDB.from_orm(leak)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking leak as unresolved: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark leak as unresolved"
        )


@router.get("/stats/summary")
async def get_leak_summary(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Get summary statistics of leaks for authenticated user
    
    Returns:
        Summary with total leaks, resolved/unresolved counts, and total potential savings
    """
    current_user: User = get_current_user_from_token(request, db)
    
    try:
        all_leaks = db.query(LeakInsight).filter(
            LeakInsight.user_id == current_user.id
        ).all()
        
        resolved_leaks = [l for l in all_leaks if l.is_resolved]
        unresolved_leaks = [l for l in all_leaks if not l.is_resolved]
        
        total_potential_saving = sum(l.estimated_annual_saving for l in all_leaks)
        resolved_saving = sum(l.estimated_annual_saving for l in resolved_leaks)
        unresolved_saving = sum(l.estimated_annual_saving for l in unresolved_leaks)
        
        avg_leak_probability = sum(l.leak_probability for l in all_leaks) / len(all_leaks) if all_leaks else 0
        
        return {
            "total_leaks_detected": len(all_leaks),
            "resolved_leaks": len(resolved_leaks),
            "unresolved_leaks": len(unresolved_leaks),
            "total_potential_annual_saving": total_potential_saving,
            "resolved_saving": resolved_saving,
            "unresolved_saving": unresolved_saving,
            "average_leak_probability": round(avg_leak_probability, 2),
            "most_common_leak_category": (
                max(set(l.leak_category for l in all_leaks), key=lambda c: sum(1 for l in all_leaks if l.leak_category == c))
                if all_leaks else None
            )
        }
        
    except Exception as e:
        logger.error(f"Error retrieving leak summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve leak summary"
        )
