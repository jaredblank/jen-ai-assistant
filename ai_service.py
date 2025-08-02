"""
AI Service for Jen AI Assistant
Handles natural language processing and response generation
"""

import os
import json
import logging
import requests
import time
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

load_dotenv()
log = logging.getLogger("jen.ai")

class JenAI:
    """AI service for natural language processing and response generation"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
        self.model = os.getenv("OPENAI_MODEL", "openai/gpt-4o-mini")
        self.is_openrouter = "openrouter.ai" in self.base_url
        
        log.info(f"JenAI initialized - Provider: {'OpenRouter' if self.is_openrouter else 'OpenAI'}, Model: {self.model}")
        
        # Voice personality for Jen
        self.personality = {
            "name": "Jen",
            "tone": "friendly, professional, helpful",
            "style": "conversational but informative",
            "greeting": "Hi! I'm Jen, your AI assistant."
        }
    
    def health_check(self) -> bool:
        """Check if AI service is healthy"""
        return bool(self.api_key)
    
    async def generate_sql_query(self, question: str, user_type: str, user_id: str) -> Optional[str]:
        """Generate SQL query from natural language question"""
        
        if not self.api_key:
            log.error("No API key configured")
            return None
        
        # Check for cached queries first (instant response)
        cached_query = self._get_cached_query(question, user_type)
        if cached_query:
            log.info(f"Using cached query for: {question[:50]}...")
            return cached_query
        
        # Generate using AI service
        try:
            prompt = self._build_sql_prompt(question, user_type, user_id)
            
            if self.is_openrouter:
                return await self._generate_with_openrouter(prompt)
            else:
                return await self._generate_with_openai(prompt)
                
        except Exception as e:
            log.error(f"SQL generation failed: {e}")
            return None
    
    def _build_sql_prompt(self, question: str, user_type: str, user_id: str) -> str:
        """Build the SQL generation prompt"""
        
        return f"""You are Jen, an expert SQL query generator for a real estate brokerage system.

Generate a SQL query for this question: "{question}"

Database Schema:
- payroll_Queue_Archive: Main commission tracking table
  - USER_ID: Agent identifier (int)
  - Wire_Date: Payment date (datetime)  
  - NET_COMMISSION: Final commission paid to agent (decimal)
  - AMOUNT_1099_AM: Gross commission before deductions (decimal)
  - SalesPrice: Property sale price (decimal)
  - BuyerID: ID if agent represented buyer (int, >0 means valid)
  - ListingID: ID if agent had listing (int, >0 means valid)
  - CHECK_MEMO: Property address (varchar)
  - EQUITY_DIVISION_25_ID: Broker ID who gets 25% division (int)

- TBL_USER_CREATE: User accounts table
  - USER_ID: Primary key (int)
  - USTATUS: Active status (1=active, 0=inactive)
  - UTYPE_ID: User type (1=admin, 12=managingbroker, 14=agent, 15=broker, 16=designated broker)

- TBL_USER_DETAILS: User profile information  
  - USER_ID: Links to TBL_USER_CREATE (int)
  - F_NAME: First name (varchar)
  - L_NAME: Last name (varchar)
  - JOINED_DT: Join date (datetime)

- TBL_FEES_MASTER: Fee structure table
  - FEE_ID: Primary key (int)
  - EQUITY_DIVISION_25_ID: Broker who gets 25% (int)

Current Context:
- User Type: {user_type}
- User ID: {user_id}
- Only return actual transactions where BuyerID > 0 OR ListingID > 0

Instructions:
1. Use %s for ALL parameters (user_id, dates, etc.)
2. For agents: Always filter by USER_ID = %s 
3. For brokers/managingbrokers: Filter by EQUITY_DIVISION_25_ID = %s to see their team data
4. For admins: Can query across all users - no USER_ID filter required
5. Only include real transactions: WHERE (BuyerID > 0 OR ListingID > 0)
6. Return ONLY the SQL query, no explanations
7. Use appropriate date filtering for "this year", "last month", etc.
8. For "who" questions, JOIN with TBL_USER_DETAILS for names

SQL Query:"""
    
    async def _generate_with_openrouter(self, prompt: str) -> Optional[str]:
        """Generate SQL using OpenRouter API"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://equity-usa.net",
            "X-Title": "Jen AI Assistant"
        }
        
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
            "max_tokens": 800,
            "top_p": 1,
            "frequency_penalty": 0,
            "presence_penalty": 0
        }
        
        # Retry logic for reliability
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    sql = result["choices"][0]["message"]["content"].strip()
                    sql = self._clean_sql(sql)
                    log.info(f"Generated SQL via OpenRouter: {sql[:100]}...")
                    return sql
                else:
                    log.error(f"OpenRouter API error: {response.status_code} - {response.text[:200]}")
                    if attempt < max_retries - 1:
                        time.sleep(2)
                        continue
                    return None
                    
            except Exception as e:
                if attempt < max_retries - 1:
                    log.warning(f"OpenRouter attempt {attempt + 1} failed, retrying: {e}")
                    time.sleep(2)
                    continue
                else:
                    log.error(f"OpenRouter failed after {max_retries} attempts: {e}")
                    return None
        
        return None
    
    async def _generate_with_openai(self, prompt: str) -> Optional[str]:
        """Generate SQL using direct OpenAI API"""
        try:
            import openai
            client = openai.OpenAI(api_key=self.api_key)
            
            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=800
            )
            
            sql = response.choices[0].message.content.strip()
            sql = self._clean_sql(sql)
            log.info(f"Generated SQL via OpenAI: {sql[:100]}...")
            return sql
            
        except Exception as e:
            log.error(f"OpenAI generation failed: {e}")
            return None
    
    def _clean_sql(self, sql: str) -> str:
        """Clean and format the generated SQL"""
        if not sql:
            return sql
            
        # Remove markdown code blocks
        sql = sql.replace("```sql", "").replace("```", "")
        
        # Remove extra whitespace
        sql = sql.strip()
        
        # Ensure it ends with semicolon
        if not sql.endswith(";"):
            sql += ";"
            
        return sql
    
    def _get_cached_query(self, question: str, user_type: str) -> Optional[str]:
        """Get cached SQL query for common questions (instant response)"""
        
        q = question.lower().strip()
        
        # Income queries
        if any(word in q for word in ["total income", "how much money", "total commission", "income this year"]):
            return """
            SELECT SUM(NET_COMMISSION) as total_income
            FROM payroll_Queue_Archive 
            WHERE USER_ID = %s 
              AND YEAR(Wire_Date) = YEAR(GETDATE())
              AND (BuyerID > 0 OR ListingID > 0);
            """
        
        # Deal count queries
        if any(phrase in q for phrase in ["how many deals", "deal count", "number of deals"]):
            return """
            SELECT COUNT(*) as deal_count
            FROM payroll_Queue_Archive 
            WHERE USER_ID = %s 
              AND YEAR(Wire_Date) = YEAR(GETDATE())
              AND (BuyerID > 0 OR ListingID > 0);
            """
        
        # Worst month query
        if "worst month" in q:
            return """
            SELECT TOP 1 
                DATENAME(month, Wire_Date) + ' ' + CAST(YEAR(Wire_Date) as varchar) as month,
                SUM(NET_COMMISSION) as total 
            FROM payroll_Queue_Archive 
            WHERE USER_ID = %s 
              AND YEAR(Wire_Date) = YEAR(GETDATE())
              AND (BuyerID > 0 OR ListingID > 0)
            GROUP BY DATENAME(month, Wire_Date), YEAR(Wire_Date) 
            HAVING SUM(NET_COMMISSION) > 0
            ORDER BY total ASC;
            """
        
        # Best month query
        if "best month" in q:
            return """
            SELECT TOP 1 
                DATENAME(month, Wire_Date) + ' ' + CAST(YEAR(Wire_Date) as varchar) as month,
                SUM(NET_COMMISSION) as total 
            FROM payroll_Queue_Archive 
            WHERE USER_ID = %s 
              AND YEAR(Wire_Date) = YEAR(GETDATE())
              AND (BuyerID > 0 OR ListingID > 0)
            GROUP BY DATENAME(month, Wire_Date), YEAR(Wire_Date) 
            HAVING SUM(NET_COMMISSION) > 0
            ORDER BY total DESC;
            """
        
        # Average deal size
        if "average deal" in q or "average sale" in q:
            return """
            SELECT AVG(SalesPrice) as average_deal_size
            FROM payroll_Queue_Archive 
            WHERE USER_ID = %s 
              AND YEAR(Wire_Date) = YEAR(GETDATE())
              AND (BuyerID > 0 OR ListingID > 0)
              AND SalesPrice > 0;
            """
        
        # Broker and Managing Broker queries
        if user_type in ["broker", "managingbroker"]:
            if "how many agents" in q:
                return """
                SELECT COUNT(DISTINCT u.USER_ID) as agent_count
                FROM TBL_USER_CREATE u
                INNER JOIN TBL_FEES_MASTER f ON u.FEE_ID = f.FEE_ID
                WHERE f.EQUITY_DIVISION_25_ID = %s
                  AND u.USTATUS = 1
                  AND u.STATUS_ID NOT IN (2, 11)
                  AND u.UTYPE_ID = 14;
                """
            if "total income" in q or "how much" in q:
                return """
                SELECT SUM(NET_COMMISSION) as total_income
                FROM payroll_Queue_Archive 
                WHERE EQUITY_DIVISION_25_ID = %s
                  AND YEAR(Wire_Date) = YEAR(GETDATE())
                  AND (BuyerID > 0 OR ListingID > 0);
                """
        
        # Admin queries - can see system-wide statistics
        if user_type == "admin":
            if "total income" in q or "system" in q:
                return """
                SELECT SUM(NET_COMMISSION) as total_income
                FROM payroll_Queue_Archive 
                WHERE YEAR(Wire_Date) = YEAR(GETDATE())
                  AND (BuyerID > 0 OR ListingID > 0);
                """
            if "how many agents" in q or "agent count" in q:
                return """
                SELECT COUNT(DISTINCT USER_ID) as agent_count
                FROM TBL_USER_CREATE
                WHERE USTATUS = 1 
                  AND UTYPE_ID = 14;
                """
        
        return None  # No cached query found
    
    def generate_response(self, question: str, data: List[Dict[str, Any]], user_name: str, user_type: str) -> str:
        """Generate natural language response from query results"""
        
        if not data:
            return f"I couldn't find any data for your question. You might want to try asking about a different time period or check if you have any transactions recorded."
        
        question_lower = question.lower()
        
        # Handle income/money questions
        if any(word in question_lower for word in ["income", "money", "commission", "earned", "made"]):
            if len(data) == 1:
                value = None
                for key, val in data[0].items():
                    if key.lower() in ['total_income', 'total', 'net_commission', 'amount']:
                        value = val
                        break
                
                if value is not None and isinstance(value, (int, float)):
                    if value == 0:
                        return f"Hi {user_name.split()[0]}! Your total income this year is $0. You might want to check if all your transactions have been processed."
                    else:
                        return f"Hi {user_name.split()[0]}! Your total income this year is ${value:,.2f}. Great work!"
        
        # Handle count questions  
        if "how many" in question_lower or "count" in question_lower:
            if len(data) == 1:
                value = None
                for key, val in data[0].items():
                    if 'count' in key.lower() or 'number' in key.lower():
                        value = val
                        break
                
                if value is not None and isinstance(value, int):
                    if "deal" in question_lower:
                        if value == 0:
                            return f"Hi {user_name.split()[0]}! You haven't closed any deals this year yet. Keep pushing!"
                        else:
                            return f"Hi {user_name.split()[0]}! You've closed {value:,} deal{'s' if value != 1 else ''} this year. Excellent work!"
                    elif "agent" in question_lower and user_type in ["broker", "managingbroker"]:
                        return f"Hi {user_name.split()[0]}! You have {value:,} active agent{'s' if value != 1 else ''} in your team."
                    elif "agent" in question_lower and user_type == "admin":
                        return f"Hi {user_name.split()[0]}! There are {value:,} active agent{'s' if value != 1 else ''} in the system."
        
        # Handle "who" questions
        if "who" in question_lower and len(data) > 0:
            first_row = data[0]
            
            # Look for name fields
            name = None
            for key in ['agent_name', 'name', 'full_name', 'recipient_name', 'F_NAME']:
                if key in first_row and first_row[key]:
                    if key == 'F_NAME' and 'L_NAME' in first_row:
                        name = f"{first_row['F_NAME']} {first_row['L_NAME']}"
                    else:
                        name = first_row[key]
                    break
            
            if name:
                if "top" in question_lower and len(data) > 1:
                    names = []
                    for row in data[:5]:  # Top 5
                        if 'agent_name' in row:
                            names.append(row['agent_name'])
                        elif 'F_NAME' in row and 'L_NAME' in row:
                            names.append(f"{row['F_NAME']} {row['L_NAME']}")
                    return f"Hi {user_name.split()[0]}! Your top agents are: {', '.join(names)}."
                else:
                    return f"Hi {user_name.split()[0]}! The answer is {name}."
        
        # Handle month queries
        if "month" in question_lower and len(data) == 1:
            first_row = data[0]
            if "month" in first_row:
                month = first_row["month"]
                for key, val in first_row.items():
                    if key != "month" and isinstance(val, (int, float)):
                        if "worst" in question_lower:
                            return f"Hi {user_name.split()[0]}! Your lowest month was {month} with ${val:,.2f} in commissions."
                        elif "best" in question_lower:
                            return f"Hi {user_name.split()[0]}! Your best month was {month} with ${val:,.2f} in commissions. Outstanding!"
        
        # Handle average queries
        if "average" in question_lower and len(data) == 1:
            first_row = data[0]
            for key, val in first_row.items():
                if "average" in key.lower() and isinstance(val, (int, float)):
                    if val > 0:
                        return f"Hi {user_name.split()[0]}! Your average deal size is ${val:,.2f}."
        
        # Default response
        result_count = len(data)
        if result_count == 1:
            # Single result - try to extract the main value
            first_row = data[0]
            main_value = None
            
            for key, val in first_row.items():
                if isinstance(val, (int, float)) and val != 0:
                    main_value = val
                    break
            
            if main_value is not None:
                if isinstance(main_value, float):
                    return f"Hi {user_name.split()[0]}! The result is ${main_value:,.2f}."
                else:
                    return f"Hi {user_name.split()[0]}! The result is {main_value:,}."
        
        return f"Hi {user_name.split()[0]}! I found {result_count} result{'s' if result_count != 1 else ''} for your question."

# Global instance
jen_ai = JenAI()