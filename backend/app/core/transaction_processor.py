"""
Transaction Upload & Pattern Detection Engine
Rule-based analysis for spending patterns from uploaded transaction files
"""

import io
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
import logging
import re
logger = logging.getLogger(__name__)


# ==================== CONFIGURATION ====================
class PatternConfig:
    """Configurable thresholds for pattern detection"""
    MIN_TRANSACTION_COUNT = 3          # Minimum txns to form pattern
    MAX_GAP_VARIANCE_MULTIPLIER = 3    # gap_std <= avg_gap * 3
    MIN_RECURRING_INTERVAL_DAYS = 7    # Min days between txns for recurring
    MAX_FILE_SIZE_MB = 50
    
    # Expected columns in CSV/Excel files
    EXPECTED_COLUMNS = ['Date', 'Narration', 'Withdrawal Amt.', 'Deposit Amt.']
    AMOUNT_COLUMNS = ['Withdrawal Amt.', 'Deposit Amt.']
    DATE_COLUMN = 'Date'
    NARRATION_COLUMN = 'Narration'


# ==================== FILE PARSER ====================
class FileParser:
    """Parse CSV and Excel files"""
    
    @staticmethod
    async def validate_file(file) -> Tuple[bool, Optional[str]]:
        """
        Validate file type and size
        Returns: (is_valid, error_message)
        """
        if not file:
            return False, "No file provided"
        
        filename = file.filename.lower() if hasattr(file, 'filename') else str(file).lower()
        
        # Check file extension
        valid_extensions = ['.csv', '.xlsx', '.xls']
        if not any(filename.endswith(ext) for ext in valid_extensions):
            return False, f"Invalid file type. Accepted: CSV, XLSX, XLS. Got: {filename}"
        
        # File size check - UploadFile doesn't provide direct size, skip for now
        return True, None
    
    @staticmethod
    async def parse_file(file) -> Tuple[Optional[pd.DataFrame], List[Dict]]:
        """
        Parse CSV or Excel file and validate expected columns
        Returns: (dataframe, errors_list)
        """
        errors = []
        try:
            filename = file.filename.lower() if hasattr(file, 'filename') else str(file).lower()
            
            # Read file content
            content = await file.read()
            
            if filename.endswith('.csv'):
                df = pd.read_csv(io.BytesIO(content))
            else:  # .xlsx, .xls
                df = pd.read_excel(io.BytesIO(content), sheet_name=0)  # Read first sheet
            
            # Validate expected columns exist
            missing_cols = [col for col in PatternConfig.EXPECTED_COLUMNS if col not in df.columns]
            if missing_cols:
                error_msg = f"Missing required columns: {missing_cols}. Expected: {PatternConfig.EXPECTED_COLUMNS}"
                logger.error(error_msg)
                errors.append({"error": error_msg})
                return None, errors
            
            logger.info(f"Successfully parsed file with {len(df)} rows and columns: {df.columns.tolist()}")
            return df, errors
            
        except Exception as e:
            error_msg = f"Failed to parse file: {str(e)}"
            logger.error(error_msg)
            errors.append({"error": error_msg})
            return None, errors


# ==================== DATA NORMALIZER ====================
class DataNormalizer:
    """Normalize and clean transaction data - hygiene only, no logic"""
    
    @staticmethod
    def normalize_amount_columns(df: pd.DataFrame, cols: List[str]) -> pd.DataFrame:
        """
        Normalize amount columns: remove commas, convert to numeric
        Handles currency symbols and whitespace
        """
        df = df.copy()
        for col in cols:
            if col not in df.columns:
                continue
            df[col] = (
                df[col]
                .astype(str)
                .str.replace(",", "", regex=False)
                .str.strip()
                .replace("", pd.NA)
            )
            df[col] = pd.to_numeric(df[col], errors="coerce")
        return df
    
    @staticmethod
    def normalize_date_column(df: pd.DataFrame, date_col: str) -> pd.DataFrame:
        """
        Parse date column to uniform datetime format
        """
        df = df.copy()
        if date_col in df.columns:
            df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
        return df
    
    @staticmethod
    def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply all hygiene normalizations to incoming CSV/Excel data
        - Normalize amount columns
        - Parse dates
        - Remove rows with critical missing values
        Returns: cleaned dataframe
        """
        df = df.copy()
        
        # Normalize amounts
        df = DataNormalizer.normalize_amount_columns(
            df, 
            cols=PatternConfig.AMOUNT_COLUMNS
        )
        
        # Parse dates
        df = DataNormalizer.normalize_date_column(
            df,
            date_col=PatternConfig.DATE_COLUMN
        )
        
        # Remove rows with missing critical columns
        critical_cols = [
            PatternConfig.DATE_COLUMN,
            PatternConfig.NARRATION_COLUMN
        ]
        df = df.dropna(subset=critical_cols, how='any')
        
        logger.info(f"Data cleaning complete: {len(df)} rows remaining")
        return df


# ==================== ENRICHMENT KEYWORDS & RULES ====================
class EnrichmentConfig:
    """Keyword mappings for transaction enrichment"""
    
    LEVEL_3_KEYWORDS = {
        "OTT": ["netflix", "hotstar", "zee5", "sony liv", "spotify", "apple music", "prime video"],
        "FOOD": ["swiggy", "zomato", "uber eats", "dominos", "pizza hut", "kfc", "mcdonald", "restaurant", "cafe", "burger king", "food delivery"],
        "FUEL": ["petrol", "diesel", "fuel", "hpcl", "bpcl", "indian oil", "shell"],
        "TRANSPORT": ["uber", "ola", "rapido", "metro", "irctc"],
        "RETAIL": ["amazon", "flipkart", "myntra", "ajio", "meesho", "big basket"],
        "HEALTH_FITNESS": ["gym", "cult", "fitness", "physio"],
        "UTILITIES": ["electricity", "water bill", "gas bill", "broadband", "wifi"],
    }
    
    NOISE_PATTERNS = [
        "upi", "imps", "neft", "rtgs", "hdfc", "sbi", "icici", "axis", "yesb",
        "bank", "sbipmopad", "yesb0yblupi", "paytm", "phonepe", "gpay", "googlepay", "vyapar", "merchant", "collect",
    ]


# ==================== TRANSACTION ENRICHER ====================
class TransactionEnricher:
    """Deterministic enrichment of transactions with rule-based tags and facts"""
    
    @staticmethod
    def get_money_flow(withdrawal_amount, deposit_amount) -> str:
        """
        Determines money flow direction based on amount columns.
        Returns: 'OUTFLOW', 'INFLOW', or 'UNKNOWN'
        """
        try:
            if pd.notna(withdrawal_amount) and withdrawal_amount > 0:
                return "OUTFLOW"
            if pd.notna(deposit_amount) and deposit_amount > 0:
                return "INFLOW"
            return "UNKNOWN"
        except (TypeError, ValueError):
            return "UNKNOWN"
    
    @staticmethod
    def add_money_flow(df: pd.DataFrame) -> pd.DataFrame:
        """Add money_flow column to dataframe"""
        df = df.copy()
        df["money_flow"] = df.apply(
            lambda r: TransactionEnricher.get_money_flow(
                r.get(PatternConfig.AMOUNT_COLUMNS[0]),
                r.get(PatternConfig.AMOUNT_COLUMNS[1])
            ),
            axis=1
        )
        return df
    
    @staticmethod
    def add_level_1_tag(df: pd.DataFrame, narration_col: str = "Narration") -> pd.DataFrame:
        """
        Adds Level-1 transaction tag based on payment rail / channel.
        Deterministic, rule-based, India-focused.
        """
        def normalize(text: str) -> str:
            if pd.isna(text):
                return ""
            return str(text).lower().strip()

        def tag_narration(narration: str) -> str:
            n = normalize(narration)

            # 1. Salary (override everything)
            if re.search(r"\b(salary|payroll|wages|ctc|employer)\b", n):
                return "SALARY"
            # 2. Interest / Dividend
            if re.search(r"\b(interest|dividend|fd int|rd int|tds)\b", n):
                return "INTEREST_DIVIDEND"
            # 3. Refund / Reversal
            if re.search(r"\b(refund|reversal|reversed|chargeback|failed|return)\b", n):
                return "REVERSAL_REFUND"
            # 4. Internal / Self transfer
            if re.search(r"\b(self|own|internal|to self)\b", n):
                return "INTERNAL_TRANSFER"
            # 5. UPI
            if re.search(r"\b(upi|@ybl|@ok|@axis|@hdfc|@sbi|@icici|paytm|phonepe|gpay|googlepay|amazonpay|bhim)\b", n):
                return "UPI"
            # 6. ACH / NACH / ECS
            if re.search(r"\b(ach|nach|ecs|mandate|auto debit|si)\b", n):
                return "ACH"
            # 7. IMPS
            if re.search(r"\b(imps|mmt|mobile transfer)\b", n):
                return "IMPS"
            # 8. NEFT
            if re.search(r"\b(neft|n-e-f-t|neft cr|neft dr)\b", n):
                return "NEFT"
            # 9. RTGS
            if re.search(r"\b(rtgs|r-t-g-s)\b", n):
                return "RTGS"
            # 10. Card
            if re.search(r"\b(pos|card|debit card|credit card|visa|mastercard|rupay|amex|ecom|online)\b", n):
                return "CARD"
            # 11. Cash / ATM
            if re.search(r"\b(cash|atm|atm wdl|cash wdl|cash dep|withdrawal)\b", n):
                return "CASH"
            # 12. Fallback
            return "UNKNOWN"

        df = df.copy()
        df["level_1_tag"] = df[narration_col].apply(tag_narration)
        return df
    
    @staticmethod
    def add_level_2_tag(
        df: pd.DataFrame,
        level_1_col: str = "level_1_tag",
        withdrawal_col: str = "Withdrawal Amt.",
        deposit_col: str = "Deposit Amt.",
    ) -> pd.DataFrame:
        """
        Adds Level-2 transaction classification:
        INCOME / EXPENSE / TRANSFER / ADJUSTMENT / UNKNOWN
        """
        def get_direction(row):
            withdrawal = row.get(withdrawal_col)
            deposit = row.get(deposit_col)

            if pd.notna(withdrawal) and withdrawal > 0 and pd.isna(deposit):
                return "DEBIT"
            if pd.notna(deposit) and deposit > 0 and pd.isna(withdrawal):
                return "CREDIT"
            return "UNKNOWN"

        def classify(row):
            level_1 = row[level_1_col]
            direction = get_direction(row)

            # 1. Adjustments
            if level_1 == "REVERSAL_REFUND":
                return "ADJUSTMENT"
            # 2. Transfers
            if level_1 == "INTERNAL_TRANSFER":
                return "TRANSFER"
            # 3. Income
            if direction == "CREDIT" and level_1 in {"SALARY", "INTEREST_DIVIDEND", "NEFT", "RTGS", "ACH"}:
                return "INCOME"
            # 4. Expense
            if direction == "DEBIT" and level_1 in {"UPI", "CARD", "CASH", "IMPS", "NEFT", "RTGS", "ACH"}:
                return "EXPENSE"
            # 5. Fallback
            return "UNKNOWN"

        df = df.copy()
        df["level_2_tag"] = df.apply(classify, axis=1)
        return df
    
    @staticmethod
    def add_level_3_tag(
        df: pd.DataFrame,
        narration_col: str = "Narration",
        level_2_col: str = "level_2_tag",
    ) -> pd.DataFrame:
        """
        Adds Level-3 coarse category tagging.
        Applies ONLY to EXPENSE rows.
        Conservative, keyword-based, rule-driven.
        """
        def normalize(text: str) -> str:
            if pd.isna(text):
                return ""
            return str(text).lower()

        def classify_level_3(row) -> str:
            # Level-3 applies only to expenses
            if row[level_2_col] != "EXPENSE":
                return "UNKNOWN"

            narration = normalize(row[narration_col])

            # Priority order matters
            for category, keywords in EnrichmentConfig.LEVEL_3_KEYWORDS.items():
                for kw in keywords:
                    if kw in narration:
                        return category

            return "UNKNOWN"

        df = df.copy()
        df["level_3_tag"] = df.apply(classify_level_3, axis=1)
        return df
    
    @staticmethod
    def normalize_text(text: str) -> str:
        """Normalize text for merchant extraction"""
        if pd.isna(text):
            return ""
        return re.sub(r"\s+", " ", text.lower()).strip()

    @staticmethod
    def is_noise_token(token: str) -> bool:
        """Check if token is noise and should be filtered"""
        if len(token) < 3:
            return True
        if any(pat in token for pat in EnrichmentConfig.NOISE_PATTERNS):
            return True
        if re.search(r"\d{4,}", token):  # long numeric sequences
            return True
        if "@" in token:  # UPI handles
            return True
        return False

    @staticmethod
    def extract_merchant_hint(narration: str) -> str:
        """Extract merchant identity from narration"""
        text = TransactionEnricher.normalize_text(narration)
        if not text:
            return "UNKNOWN"

        # Split by hyphen (candidate generator)
        tokens = [t.strip() for t in text.split("-") if t.strip()]

        candidates = []
        for token in tokens:
            if not TransactionEnricher.is_noise_token(token):
                candidates.append(token)

        if not candidates:
            return "UNKNOWN"

        # Prefer:
        # 1. tokens with spaces (human names / shop names)
        # 2. longer alphabetic tokens
        candidates.sort(
            key=lambda t: (
                " " in t,
                len(re.findall(r"[a-z]", t)),
                len(t)
            ),
            reverse=True
        )

        return candidates[0]

    @staticmethod
    def add_merchant_hint(
        df: pd.DataFrame,
        narration_col: str = "Narration"
    ) -> pd.DataFrame:
        """Add merchant_hint column"""
        df = df.copy()
        df["merchant_hint"] = df[narration_col].apply(TransactionEnricher.extract_merchant_hint)
        return df
    
    @staticmethod
    def enrich_transactions(df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply all enrichments to transactions.
        Deterministic, rule-based, no filtering.
        
        Adds columns:
        - money_flow (INFLOW / OUTFLOW / UNKNOWN)
        - level_1_tag (payment rail)
        - level_2_tag (transaction role)
        - level_3_tag (soft category)
        - merchant_hint (merchant identity)
        """
        df = df.copy()
        
        # Apply all enrichments in sequence
        df = TransactionEnricher.add_money_flow(df)
        df = TransactionEnricher.add_level_1_tag(df, narration_col=PatternConfig.NARRATION_COLUMN)
        df = TransactionEnricher.add_level_2_tag(df)
        df = TransactionEnricher.add_level_3_tag(df)
        df = TransactionEnricher.add_merchant_hint(df, narration_col=PatternConfig.NARRATION_COLUMN)
        
        logger.info(f"Transaction enrichment complete: {len(df)} rows enriched")
        return df
        
        return "Other"
    
    @staticmethod
    def normalize_and_enrich_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        """
        NEW WORKFLOW: Clean and enrich transactions (no detection)
        
        Steps:
        1. Clean dataframe (normalize amounts, dates, remove missing critical cols)
        2. Enrich with deterministic tags (money_flow, level_1/2/3, merchant_hint)
        
        Returns: fully enriched dataframe
        """
        # Step 1: Clean (hygiene only)
        df = DataNormalizer.clean_dataframe(df)
        
        # Step 2: Enrich (deterministic, rule-based)
        df = TransactionEnricher.enrich_transactions(df)
        
        logger.info(f"Normalize & enrich complete: {len(df)} rows processed")
        return df
    
    @staticmethod
    def convert_df_to_transaction_records(df: pd.DataFrame, file_upload_id: str) -> List[Dict]:
        """
        Convert enriched dataframe to transaction record dicts for persistence
        
        Maps columns:
        - Date → txn_date
        - Narration → narration
        - Withdrawal Amt. → withdrawal_amount
        - Deposit Amt. → deposit_amount
        - money_flow, level_1/2/3_tag, merchant_hint → as-is
        """
        records = []
        for idx, row in df.iterrows():
            try:
                record = {
                    "txn_date": row.get(PatternConfig.DATE_COLUMN),
                    "narration": row.get(PatternConfig.NARRATION_COLUMN),
                    "withdrawal_amount": row.get(PatternConfig.AMOUNT_COLUMNS[0]),
                    "deposit_amount": row.get(PatternConfig.AMOUNT_COLUMNS[1]),
                    "money_flow": row.get("money_flow", "UNKNOWN"),
                    "level_1_tag": row.get("level_1_tag", "UNKNOWN"),
                    "level_2_tag": row.get("level_2_tag", "UNKNOWN"),
                    "level_3_tag": row.get("level_3_tag", "UNKNOWN"),
                    "merchant_hint": row.get("merchant_hint", "UNKNOWN"),
                    "file_upload_id": file_upload_id,
                }
                records.append(record)
            except Exception as e:
                logger.error(f"Error converting row {idx} to record: {e}")
                continue
        
        return records


# ==================== PATTERN DETECTOR ====================
class PatternAggregator:
    """
    Aggregate enriched transactions into neutral pattern statistics.
    
    NEW FLOW:
    - Filter: level_2_tag == EXPENSE
    - Group by merchant_hint
    - Compute aggregated metrics (facts only, no judgment)
    - No filtering except txn_count >= 2
    - No recurring/one-time labels
    - No regularity thresholds
    """
    
    @staticmethod
    def group_by_merchant(transactions: List[Dict]) -> Dict[str, List[Dict]]:
        """Group transactions by merchant_hint (identity)"""
        groups = {}
        for txn in transactions:
            key = txn.get('merchant_hint', 'UNKNOWN')
            if key not in groups:
                groups[key] = []
            groups[key].append(txn)
        return groups
    
    @staticmethod
    def compute_aggregate_stats(group: List[Dict]) -> Dict:
        """
        Compute aggregated statistics for a merchant group.
        Pure facts, no judgment.
        
        Returns: stats dict with all metrics
        """
        # Sort by date
        sorted_group = sorted(group, key=lambda x: x['txn_date'])
        
        txn_count = len(sorted_group)
        first_date = sorted_group[0]['txn_date']
        last_date = sorted_group[-1]['txn_date']
        
        # Duration between first and last transaction
        active_duration_days = (last_date - first_date).days
        
        # Date gaps between consecutive transactions
        date_gaps = []
        for i in range(1, len(sorted_group)):
            gap = (sorted_group[i]['txn_date'] - sorted_group[i-1]['txn_date']).days
            if gap > 0:  # Only positive gaps
                date_gaps.append(gap)
        
        avg_gap_days = np.mean(date_gaps) if date_gaps else 0.0
        gap_std_days = np.std(date_gaps) if date_gaps else 0.0
        gap_min_days = min(date_gaps) if date_gaps else 0.0
        gap_max_days = max(date_gaps) if date_gaps else 0.0
        
        # Recency: days since last transaction
        last_txn_days_ago = (datetime.now() - last_date).days
        
        # Amount statistics
        # Determine which amount column to use (withdrawal or deposit)
        amounts = []
        for txn in sorted_group:
            if txn.get('money_flow') == 'OUTFLOW' and pd.notna(txn.get('withdrawal_amount')):
                amounts.append(txn['withdrawal_amount'])
            elif txn.get('money_flow') == 'INFLOW' and pd.notna(txn.get('deposit_amount')):
                amounts.append(txn['deposit_amount'])
        
        if not amounts:
            # Fallback: use whichever amount is available
            for txn in sorted_group:
                amt = txn.get('withdrawal_amount') or txn.get('deposit_amount')
                if pd.notna(amt) and amt > 0:
                    amounts.append(amt)
        
        total_amount = sum(amounts) if amounts else 0.0
        avg_amount = np.mean(amounts) if amounts else 0.0
        amount_std = np.std(amounts) if amounts else 0.0
        amount_min = min(amounts) if amounts else 0.0
        amount_max = max(amounts) if amounts else 0.0
        
        # Level-1 tag distribution
        level_1_tags = [txn.get('level_1_tag', 'UNKNOWN') for txn in sorted_group]
        level_1_counts = {}
        for tag in level_1_tags:
            level_1_counts[tag] = level_1_counts.get(tag, 0) + 1
        
        dominant_level_1_tag = 'UNKNOWN'
        if level_1_counts:
            dominant_level_1_tag = max(level_1_counts, key=level_1_counts.get)
        level_1_confidence = (level_1_counts.get(dominant_level_1_tag, 0) / txn_count) if txn_count > 0 else 0.0
        
        # Level-2 tag distribution
        level_2_tags = [txn.get('level_2_tag', 'UNKNOWN') for txn in sorted_group]
        level_2_counts = {}
        for tag in level_2_tags:
            level_2_counts[tag] = level_2_counts.get(tag, 0) + 1
        
        dominant_level_2_tag = 'UNKNOWN'
        if level_2_counts:
            dominant_level_2_tag = max(level_2_counts, key=level_2_counts.get)
        level_2_confidence = (level_2_counts.get(dominant_level_2_tag, 0) / txn_count) if txn_count > 0 else 0.0
        
        # Level-3 tag distribution
        level_3_tags = [txn.get('level_3_tag', 'UNKNOWN') for txn in sorted_group]
        level_3_counts = {}
        for tag in level_3_tags:
            level_3_counts[tag] = level_3_counts.get(tag, 0) + 1
        
        # Find dominant level_3_tag
        dominant_level_3_tag = 'UNKNOWN'
        if level_3_counts:
            dominant_level_3_tag = max(level_3_counts, key=level_3_counts.get)
        
        # Confidence: proportion of transactions with dominant tag
        level_3_confidence = (level_3_counts.get(dominant_level_3_tag, 0) / txn_count) if txn_count > 0 else 0.0
        
        return {
            # Identity
            "merchant_hint": group[0].get('merchant_hint', 'UNKNOWN'),
            
            # Aggregated evidence
            "txn_count": txn_count,
            "total_amount": round(total_amount, 2),
            "avg_amount": round(avg_amount, 2),
            "amount_std": round(amount_std, 2),
            "amount_min": round(amount_min, 2),
            "amount_max": round(amount_max, 2),
            
            "active_duration_days": active_duration_days,
            "avg_gap_days": round(avg_gap_days, 2),
            "gap_std_days": round(gap_std_days, 2),
            "gap_min_days": int(gap_min_days),
            "gap_max_days": int(gap_max_days),
            
            "last_txn_days_ago": last_txn_days_ago,
            
            # Soft metadata
            "dominant_level_1_tag": dominant_level_1_tag,
            "level_1_confidence": round(level_1_confidence, 4),
            "dominant_level_2_tag": dominant_level_2_tag,
            "level_2_confidence": round(level_2_confidence, 4),
            "dominant_level_3_tag": dominant_level_3_tag,
            "level_3_confidence": round(level_3_confidence, 4),
        }
    
    @staticmethod
    def aggregate_patterns(transactions: List[Dict]) -> List[Dict]:
        """
        Main entry point: aggregate transaction facts into neutral pattern stats.
        
        Steps:
        1. Filter: level_2_tag == EXPENSE only
        2. Group by merchant_hint
        3. Compute metrics (facts only)
        4. Filter: txn_count >= 2 only
        5. Return neutral stats (no judgment)
        
        Returns: list of pattern stat dicts
        """
        if not transactions:
            logger.info("No transactions to aggregate")
            return []
        
        # Step 1: Filter for EXPENSE only
        expenses = [txn for txn in transactions if txn.get('level_2_tag') == 'EXPENSE']
        logger.info(f"Filtered {len(expenses)} EXPENSE transactions from {len(transactions)} total")
        
        if not expenses:
            logger.warning("No EXPENSE transactions found for aggregation")
            return []
        
        # Step 2: Group by merchant
        groups = PatternAggregator.group_by_merchant(expenses)
        logger.info(f"Grouped into {len(groups)} merchant groups")
        
        patterns = []
        
        # Step 3 & 4: Compute stats and apply minimum filter
        for merchant_hint, group in groups.items():
            try:
                stats = PatternAggregator.compute_aggregate_stats(group)
                
                # Apply ONLY minimum filter: txn_count >= 2
                if stats['txn_count'] < 2:
                    logger.debug(f"Merchant '{merchant_hint}' filtered: only {stats['txn_count']} transaction(s)")
                    continue
                
                patterns.append(stats)
                logger.debug(f"Aggregated pattern: {merchant_hint} ({stats['txn_count']} txns, avg=${stats['avg_amount']})")
                
            except Exception as e:
                logger.error(f"Error aggregating pattern for merchant '{merchant_hint}': {e}", exc_info=True)
                continue
        
        logger.info(f"Pattern aggregation complete: {len(patterns)} patterns created")
        return patterns


# ==================== PERSISTENCE ====================
class TransactionPersistence:
    """Handle database persistence"""
    
    @staticmethod
    def persist_enriched_transactions(
        db: Session,
        user_id: int,
        transactions: List[Dict]
    ) -> int:
        """
        Persist enriched transactions to database
        
        Stores deterministic facts and enrichment tags:
        - Core facts: txn_date, narration, withdrawal_amount, deposit_amount
        - Deterministic tags: money_flow, level_1_tag, level_2_tag, level_3_tag, merchant_hint
        - Provenance: file_upload_id
        
        Returns: count of persisted transactions
        """
        from app.models import Transaction
        
        try:
            count = 0
            duplicates_skipped = 0
            
            for txn in transactions:
                # Check for duplicates before inserting
                # A duplicate is defined as: same user_id, date, narration, and amount
                # IMPORTANT: Must handle NULL amounts correctly (NULL == NULL is NULL in SQL, not TRUE)
                withdrawal_amt = txn.get('withdrawal_amount')
                deposit_amt = txn.get('deposit_amount')
                
                query = db.query(Transaction).filter(
                    Transaction.user_id == user_id,
                    Transaction.txn_date == txn['txn_date'],
                    Transaction.narration == txn['narration']
                )
                
                # Handle NULL comparison properly for withdrawal_amount
                if withdrawal_amt is None:
                    query = query.filter(Transaction.withdrawal_amount.is_(None))
                else:
                    query = query.filter(Transaction.withdrawal_amount == withdrawal_amt)
                
                # Handle NULL comparison properly for deposit_amount
                if deposit_amt is None:
                    query = query.filter(Transaction.deposit_amount.is_(None))
                else:
                    query = query.filter(Transaction.deposit_amount == deposit_amt)
                
                existing_txn = query.first()
                
                if existing_txn:
                    # Skip duplicate
                    duplicates_skipped += 1
                    logger.debug(f"Skipped duplicate transaction: {txn['narration']} on {txn['txn_date']}")
                    continue
                
                transaction = Transaction(
                    user_id=user_id,
                    # Core transaction facts
                    txn_date=txn['txn_date'],
                    narration=txn['narration'],
                    # Amount tracking
                    withdrawal_amount=txn.get('withdrawal_amount'),
                    deposit_amount=txn.get('deposit_amount'),
                    money_flow=txn['money_flow'],
                    # Deterministic enrichment
                    level_1_tag=txn['level_1_tag'],
                    level_2_tag=txn['level_2_tag'],
                    level_3_tag=txn.get('level_3_tag', 'UNKNOWN'),
                    merchant_hint=txn.get('merchant_hint', 'UNKNOWN'),
                    # Provenance
                    file_upload_id=txn['file_upload_id']
                )
                db.add(transaction)
                count += 1
            
            db.commit()
            logger.info(f"Persisted {count} enriched transactions for user {user_id} (skipped {duplicates_skipped} duplicates)")
            return count
            
        except Exception as e:
            logger.error(f"Error persisting enriched transactions: {e}", exc_info=True)
            db.rollback()
            raise
    
    @staticmethod
    def persist_pattern_stats(
        db: Session,
        user_id: int,
        pattern_stats: List[Dict]
    ) -> int:
        """
        Persist aggregated pattern statistics to database.
        
        Stores evidence (facts), not conclusions:
        - Aggregated metrics from transactions
        - Deterministic tags distribution
        - Temporal and amount statistics
        
        Handles upsert: if pattern exists for (user_id, merchant_hint), update it.
        This enables re-running aggregation without duplication.
        
        Returns: count of persisted/updated patterns
        """
        from app.models import SpendingPatternStats
        from sqlalchemy.exc import IntegrityError
        
        try:
            count = 0
            for stats in pattern_stats:
                merchant_hint = stats['merchant_hint']
                
                try:
                    # Check if pattern already exists for this user + merchant
                    existing = db.query(SpendingPatternStats).filter(
                        SpendingPatternStats.user_id == user_id,
                        SpendingPatternStats.merchant_hint == merchant_hint
                    ).first()
                    
                    if existing:
                        # Update existing pattern (re-running aggregation)
                        logger.debug(f"Updating existing pattern for merchant '{merchant_hint}'")
                        existing.txn_count = stats['txn_count']
                        existing.total_amount = stats['total_amount']
                        existing.avg_amount = stats['avg_amount']
                        existing.amount_std = stats['amount_std']
                        existing.amount_min = stats['amount_min']
                        existing.amount_max = stats['amount_max']
                        existing.active_duration_days = stats['active_duration_days']
                        existing.avg_gap_days = stats['avg_gap_days']
                        existing.gap_std_days = stats['gap_std_days']
                        existing.gap_min_days = stats['gap_min_days']
                        existing.gap_max_days = stats['gap_max_days']
                        existing.last_txn_days_ago = stats['last_txn_days_ago']
                        existing.dominant_level_1_tag = stats['dominant_level_1_tag']
                        existing.level_1_confidence = stats['level_1_confidence']
                        existing.dominant_level_2_tag = stats['dominant_level_2_tag']
                        existing.level_2_confidence = stats['level_2_confidence']
                        existing.dominant_level_3_tag = stats['dominant_level_3_tag']
                        existing.level_3_confidence = stats['level_3_confidence']
                        existing.updated_at = datetime.utcnow()
                        db.add(existing)
                    else:
                        # Create new pattern
                        logger.debug(f"Creating new pattern for merchant '{merchant_hint}'")
                        pattern_obj = SpendingPatternStats(
                            user_id=user_id,
                            merchant_hint=stats['merchant_hint'],
                            txn_count=stats['txn_count'],
                            total_amount=stats['total_amount'],
                            avg_amount=stats['avg_amount'],
                            amount_std=stats['amount_std'],
                            amount_min=stats['amount_min'],
                            amount_max=stats['amount_max'],
                            active_duration_days=stats['active_duration_days'],
                            avg_gap_days=stats['avg_gap_days'],
                            gap_std_days=stats['gap_std_days'],
                            gap_min_days=stats['gap_min_days'],
                            gap_max_days=stats['gap_max_days'],
                            last_txn_days_ago=stats['last_txn_days_ago'],
                            dominant_level_1_tag=stats['dominant_level_1_tag'],
                            level_1_confidence=stats['level_1_confidence'],
                            dominant_level_2_tag=stats['dominant_level_2_tag'],
                            level_2_confidence=stats['level_2_confidence'],
                            dominant_level_3_tag=stats['dominant_level_3_tag'],
                            level_3_confidence=stats['level_3_confidence']
                        )
                        db.add(pattern_obj)
                    
                    count += 1
                    
                except IntegrityError as e:
                    logger.warning(f"Integrity error for merchant '{merchant_hint}': {e}")
                    db.rollback()
                    # Continue with next pattern
                    continue
                except Exception as e:
                    logger.error(f"Error persisting pattern for merchant '{merchant_hint}': {e}", exc_info=True)
                    db.rollback()
                    continue
            
            db.commit()
            logger.info(f"Persisted/updated {count} pattern stats for user {user_id}")
            return count
            
        except Exception as e:
            logger.error(f"Error in persist_pattern_stats: {e}", exc_info=True)
            db.rollback()
            raise


# ==================== MAIN PROCESSOR ====================
class TransactionUploadProcessor:
    """Main orchestrator for transaction upload processing
    
    NEW FLOW (Updated):
    1. Validate file
    2. Parse CSV/Excel
    3. Clean dataframe (normalize dates, amounts)
    4. Enrich transactions (add deterministic tags)
    5. Store enriched transactions
    6. Aggregate into pattern stats
    7. Store pattern stats
    8. [Optional: Run AI analysis for leaks]
    """
    
    @staticmethod
    async def process_upload(
        file,
        user_id: int,
        db: Session
    ) -> Dict:
        """
        Main entry point: process entire file upload end-to-end
        
        Returns: response dict with statistics and results
        """
        file_upload_id = str(uuid.uuid4())
        logger.info(f"Starting transaction upload processing: upload_id={file_upload_id}, user_id={user_id}")
        
        try:
            # ==================== STEP 1: VALIDATE FILE ====================
            is_valid, error_msg = await FileParser.validate_file(file)
            if not is_valid:
                logger.warning(f"File validation failed: {error_msg}")
                return {
                    "status": "error",
                    "detail": error_msg
                }
            
            # ==================== STEP 2: PARSE FILE ====================
            df, parse_errors = await FileParser.parse_file(file)
            if df is None:
                logger.error("File parsing failed")
                return {
                    "status": "error",
                    "detail": "Failed to parse file",
                    "errors": parse_errors
                }
            
            total_rows = len(df)
            logger.info(f"File parsed: {total_rows} rows")
            
            # ==================== STEP 3: CLEAN DATAFRAME ====================
            # (Normalize amounts, parse dates, remove rows with missing critical columns)
            try:
                df_clean = DataNormalizer.clean_dataframe(df)
            except Exception as e:
                logger.error(f"Error cleaning dataframe: {e}", exc_info=True)
                return {
                    "status": "error",
                    "detail": f"Failed to clean transaction data: {str(e)}"
                }
            
            clean_rows = len(df_clean)
            if clean_rows == 0:
                logger.warning("No valid transactions after cleaning")
                return {
                    "status": "error",
                    "detail": "No valid transactions found in file (all rows filtered during cleaning)",
                    "statistics": {
                        "total_rows": total_rows,
                        "clean_rows": 0
                    }
                }
            
            logger.info(f"Cleaning complete: {clean_rows} valid rows from {total_rows}")
            
            # ==================== STEP 4: ENRICH TRANSACTIONS ====================
            # (Add money_flow, level_1/2/3_tag, merchant_hint - all deterministic)
            try:
                df_enriched = TransactionEnricher.enrich_transactions(df_clean)
            except Exception as e:
                logger.error(f"Error enriching transactions: {e}", exc_info=True)
                return {
                    "status": "error",
                    "detail": f"Failed to enrich transaction data: {str(e)}"
                }
            
            logger.info(f"Enrichment complete: {len(df_enriched)} transactions enriched")
            
            # ==================== STEP 5: CONVERT TO TRANSACTION RECORDS ====================
            # (Map dataframe columns to Transaction model fields)
            try:
                transaction_records = TransactionEnricher.convert_df_to_transaction_records(df_enriched, file_upload_id)
            except Exception as e:
                logger.error(f"Error converting to transaction records: {e}", exc_info=True)
                return {
                    "status": "error",
                    "detail": f"Failed to prepare transaction records: {str(e)}"
                }
            
            if not transaction_records:
                logger.warning("No transaction records after conversion")
                return {
                    "status": "error",
                    "detail": "No valid transaction records to store"
                }
            
            # ==================== STEP 6: STORE ENRICHED TRANSACTIONS ====================
            # (Persist to Transaction table - source of truth)
            try:
                txn_count = TransactionPersistence.persist_enriched_transactions(
                    db, user_id, transaction_records
                )
            except Exception as e:
                logger.error(f"Error persisting enriched transactions: {e}", exc_info=True)
                db.rollback()
                return {
                    "status": "error",
                    "detail": f"Failed to store transactions: {str(e)}"
                }
            
            logger.info(f"Stored {txn_count} enriched transactions")
            
            # ==================== STEP 7: AGGREGATE INTO PATTERN STATS ====================
            # (Filter EXPENSE only, group by merchant, compute aggregated metrics)
            try:
                pattern_stats = PatternAggregator.aggregate_patterns(transaction_records)
            except Exception as e:
                logger.error(f"Error aggregating patterns: {e}", exc_info=True)
                return {
                    "status": "error",
                    "detail": f"Failed to aggregate spending patterns: {str(e)}"
                }
            
            if not pattern_stats:
                logger.warning("No patterns aggregated (all filtered or no expenses)")
                pattern_count = 0
            else:
                # ==================== STEP 8: STORE PATTERN STATS ====================
                # (Persist aggregated evidence to SpendingPatternStats - upsertable)
                try:
                    pattern_count = TransactionPersistence.persist_pattern_stats(
                        db, user_id, pattern_stats
                    )
                except Exception as e:
                    logger.error(f"Error persisting pattern stats: {e}", exc_info=True)
                    db.rollback()
                    return {
                        "status": "error",
                        "detail": f"Failed to store pattern statistics: {str(e)}"
                    }
                
                logger.info(f"Stored {pattern_count} pattern statistics")
            
            # ==================== STEP 9: BUILD SUCCESS RESPONSE ====================
            response = {
                "status": "success",
                "upload_id": file_upload_id,
                "statistics": {
                    "total_rows": total_rows,
                    "clean_rows": clean_rows,
                    "transactions_stored": txn_count,
                    "patterns_aggregated": len(pattern_stats),
                    "pattern_stats_stored": pattern_count
                }
            }
            
            logger.info(f"Upload processing complete: {txn_count} txns, {pattern_count} pattern stats")
            return response
            
        except Exception as e:
            logger.error(f"Unexpected error during upload processing: {e}", exc_info=True)
            db.rollback()
            return {
                "status": "error",
                "detail": f"Unexpected error: {str(e)}"
            }
