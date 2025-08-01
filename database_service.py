"""
Database Service for Jen AI Assistant
Handles all database operations with proper connection management
"""

import os
import logging
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, date

import pyodbc
from dotenv import load_dotenv

load_dotenv()
log = logging.getLogger("jen.database")

class DatabaseService:
    """Database service for Jen AI Assistant"""
    
    def __init__(self):
        self.host = os.getenv("SQLSERVER_HOST", "104.42.175.206")
        self.database = os.getenv("SQLSERVER_DB", "Broker_Mgmt")
        self.user = os.getenv("SQLSERVER_USER", "Jared")
        self.password = os.getenv("SQLSERVER_PASSWORD", "N1ch0las1!")
        self.port = int(os.getenv("SQLSERVER_PORT", "1433"))
        
        log.info(f"Database service initialized - Host: {self.host}, DB: {self.database}")
    
    def get_connection(self):
        """Get a database connection"""
        try:
            connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={self.host},{self.port};DATABASE={self.database};UID={self.user};PWD={self.password};Connection Timeout=30"
            conn = pyodbc.connect(connection_string)
            return conn
        except Exception as e:
            log.error(f"Database connection failed: {e}")
            raise
    
    async def health_check(self) -> bool:
        """Check database health"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            conn.close()
            return result is not None
        except Exception as e:
            log.error(f"Database health check failed: {e}")
            return False
    
    async def execute_query(self, sql: str, params: List[Any] = None) -> List[Dict[str, Any]]:
        """Execute a SQL query and return results"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            
            # Get column names
            columns = [col[0] for col in cursor.description] if cursor.description else []
            
            # Fetch all results
            rows = cursor.fetchall()
            
            # Convert to list of dictionaries
            results = []
            for row in rows:
                row_dict = {}
                for i, value in enumerate(row):
                    col_name = columns[i]
                    
                    # Handle different data types
                    if isinstance(value, (date, datetime)):
                        row_dict[col_name] = value.isoformat()
                    elif hasattr(value, '__float__'):  # Decimal types
                        row_dict[col_name] = float(value)
                    else:
                        row_dict[col_name] = value
                
                results.append(row_dict)
            
            conn.close()
            log.info(f"Query executed successfully - {len(results)} rows returned")
            return results
            
        except Exception as e:
            log.error(f"Query execution failed: {e}")
            log.error(f"SQL: {sql}")
            log.error(f"Params: {params}")
            raise
    
    async def get_user_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user information by ID"""
        try:
            sql = """
            SELECT 
                u.USER_ID,
                d.F_NAME,
                d.L_NAME,
                d.F_NAME + ' ' + d.L_NAME as full_name,
                u.UTYPE_ID,
                CASE 
                    WHEN u.UTYPE_ID = 14 THEN 'agent'
                    WHEN u.UTYPE_ID IN (15, 16) THEN 'broker'
                    ELSE 'user'
                END as user_type,
                d.JOINED_DT,
                u.USTATUS
            FROM TBL_USER_CREATE u
            INNER JOIN TBL_USER_DETAILS d ON u.USER_ID = d.USER_ID
            WHERE u.USER_ID = %s
              AND u.USTATUS = 1
            """
            
            results = await self.execute_query(sql, [user_id])
            
            if results:
                user_info = results[0]
                return {
                    "user_id": user_info["USER_ID"],
                    "name": user_info["full_name"],
                    "first_name": user_info["F_NAME"],
                    "last_name": user_info["L_NAME"],
                    "user_type": user_info["user_type"],
                    "joined_date": user_info["JOINED_DT"],
                    "status": "active" if user_info["USTATUS"] == 1 else "inactive"
                }
            
            return None
            
        except Exception as e:
            log.error(f"Failed to get user info for {user_id}: {e}")
            return None
    
    async def find_user_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Find user by name (fuzzy matching)"""
        try:
            # Try exact match first
            sql = """
            SELECT TOP 5
                u.USER_ID,
                d.F_NAME,
                d.L_NAME,
                d.F_NAME + ' ' + d.L_NAME as full_name,
                CASE 
                    WHEN u.UTYPE_ID = 14 THEN 'agent'
                    WHEN u.UTYPE_ID IN (15, 16) THEN 'broker'
                    ELSE 'user'
                END as user_type
            FROM TBL_USER_CREATE u
            INNER JOIN TBL_USER_DETAILS d ON u.USER_ID = d.USER_ID
            WHERE u.USTATUS = 1
              AND (
                LOWER(d.F_NAME + ' ' + d.L_NAME) LIKE LOWER(%s)
                OR LOWER(d.F_NAME) LIKE LOWER(%s)
                OR LOWER(d.L_NAME) LIKE LOWER(%s)
              )
            ORDER BY 
                CASE 
                    WHEN LOWER(d.F_NAME + ' ' + d.L_NAME) = LOWER(%s) THEN 1
                    WHEN LOWER(d.F_NAME + ' ' + d.L_NAME) LIKE LOWER(%s) THEN 2
                    ELSE 3
                END
            """
            
            name_pattern = f"%{name}%"
            results = await self.execute_query(sql, [name_pattern, name_pattern, name_pattern, name, name_pattern])
            
            if results:
                # Return the best match
                user_info = results[0]
                return {
                    "user_id": str(user_info["USER_ID"]),
                    "name": user_info["full_name"],
                    "first_name": user_info["F_NAME"],
                    "last_name": user_info["L_NAME"],
                    "user_type": user_info["user_type"]
                }
            
            return None
            
        except Exception as e:
            log.error(f"Failed to find user by name '{name}': {e}")
            return None
    
    async def get_usage_analytics(self) -> Dict[str, Any]:
        """Get usage analytics for dashboard"""
        try:
            # This would typically come from a usage tracking table
            # For now, return mock data
            return {
                "total_queries": 1247,
                "active_users": 156,
                "avg_response_time": 0.8,
                "success_rate": 97.3,
                "top_questions": [
                    {"question": "What is my total income?", "count": 234},
                    {"question": "How many deals did I close?", "count": 189},
                    {"question": "What was my worst month?", "count": 145},
                    {"question": "Show me my commission", "count": 98},
                    {"question": "How many agents do I have?", "count": 76}
                ]
            }
        except Exception as e:
            log.error(f"Failed to get analytics: {e}")
            return {}

# Global instance
db_service = DatabaseService()