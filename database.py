"""
MTC Validator — database.py
SQLite database for storing validation history
"""

import sqlite3
from datetime import datetime
import os


DB_PATH = "mtc_history.db"


def init_db():
    """Initialize database with schema. Call on app startup."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS validaciones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fecha TEXT NOT NULL,
                    usuario TEXT NOT NULL,
                    empresa TEXT,
                    norma TEXT NOT NULL,
                    archivo TEXT,
                    n_total INTEGER,
                    n_aprobado INTEGER,
                    n_rechazado INTEGER,
                    veredicto TEXT,
                    elementos_fallidos TEXT,
                    metodo_ingreso TEXT,
                    pdf_report BLOB
                )
            """)
            conn.commit()
        return True
    except Exception as e:
        print(f"Error inicializando BD: {e}")
        return False


def save_validacion(usuario, norma, archivo, df_resultado, veredicto, metodo):
    """
    Save a completed validation to history.
    
    Args:
        usuario: str — username
        norma: str — norm key (e.g., 'SAE1045')
        archivo: str — original filename
        df_resultado: DataFrame with validation results
        veredicto: str — 'LOTE APROBADO' or 'LOTE RECHAZADO'
        metodo: str — 'excel', 'pdf_pdfplumber', 'pdf_mistral', 'manual'
    
    Returns:
        int — new row id, or None on error
    """
    try:
        n_total = len(df_resultado)
        n_aprobado = (df_resultado["resultado"] == "APROBADO").sum()
        n_rechazado = (df_resultado["resultado"] == "RECHAZADO").sum()
        
        elementos_fallidos = ",".join(
            df_resultado[df_resultado["resultado"] == "RECHAZADO"]["elemento"].tolist()
        )
        
        fecha = datetime.now().isoformat()
        
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO validaciones 
                (fecha, usuario, empresa, norma, archivo, n_total, n_aprobado, n_rechazado, 
                 veredicto, elementos_fallidos, metodo_ingreso)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                fecha, usuario, usuario, norma, archivo, n_total, n_aprobado, n_rechazado,
                veredicto, elementos_fallidos, metodo
            ))
            conn.commit()
            return cursor.lastrowid
    except Exception as e:
        print(f"Error guardando validación: {e}")
        return None


def get_historial(usuario=None, limit=50):
    """
    Get validation history.
    
    Args:
        usuario: str or None — if None, return all; else filter by usuario
        limit: int — max records to return
    
    Returns:
        list of dicts with validation history
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if usuario is None:
                cursor.execute("""
                    SELECT * FROM validaciones ORDER BY fecha DESC LIMIT ?
                """, (limit,))
            else:
                cursor.execute("""
                    SELECT * FROM validaciones 
                    WHERE usuario = ? 
                    ORDER BY fecha DESC LIMIT ?
                """, (usuario, limit))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    except Exception as e:
        print(f"Error obteniendo historial: {e}")
        return []


def get_stats(usuario=None):
    """
    Get validation statistics.
    
    Args:
        usuario: str or None
    
    Returns:
        dict with: total_validaciones, total_aprobados, total_rechazados, 
        norma_mas_usada, tasa_aprobacion (percentage)
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            
            if usuario is None:
                cursor.execute("SELECT COUNT(*) FROM validaciones")
                total_validaciones = cursor.fetchone()[0]
                
                cursor.execute("SELECT SUM(n_aprobado) FROM validaciones")
                total_aprobados = cursor.fetchone()[0] or 0
                
                cursor.execute("SELECT SUM(n_rechazado) FROM validaciones")
                total_rechazados = cursor.fetchone()[0] or 0
                
                cursor.execute("""
                    SELECT norma, COUNT(*) as count FROM validaciones 
                    GROUP BY norma ORDER BY count DESC LIMIT 1
                """)
                resultado = cursor.fetchone()
                norma_mas_usada = resultado[0] if resultado else "N/A"
            else:
                cursor.execute("SELECT COUNT(*) FROM validaciones WHERE usuario = ?", (usuario,))
                total_validaciones = cursor.fetchone()[0]
                
                cursor.execute("SELECT SUM(n_aprobado) FROM validaciones WHERE usuario = ?", (usuario,))
                total_aprobados = cursor.fetchone()[0] or 0
                
                cursor.execute("SELECT SUM(n_rechazado) FROM validaciones WHERE usuario = ?", (usuario,))
                total_rechazados = cursor.fetchone()[0] or 0
                
                cursor.execute("""
                    SELECT norma, COUNT(*) as count FROM validaciones 
                    WHERE usuario = ?
                    GROUP BY norma ORDER BY count DESC LIMIT 1
                """, (usuario,))
                resultado = cursor.fetchone()
                norma_mas_usada = resultado[0] if resultado else "N/A"
            
            total_evaluados = total_aprobados + total_rechazados
            tasa_aprobacion = round((total_aprobados / total_evaluados) * 100) if total_evaluados > 0 else 0
            
            return {
                "total_validaciones": total_validaciones,
                "total_aprobados": total_aprobados,
                "total_rechazados": total_rechazados,
                "norma_mas_usada": norma_mas_usada,
                "tasa_aprobacion": tasa_aprobacion,
            }
    except Exception as e:
        print(f"Error obteniendo estadísticas: {e}")
        return {
            "total_validaciones": 0,
            "total_aprobados": 0,
            "total_rechazados": 0,
            "norma_mas_usada": "N/A",
            "tasa_aprobacion": 0,
        }


def delete_validacion(id):
    """Delete a single validation record by id."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM validaciones WHERE id = ?", (id,))
            conn.commit()
            return cursor.rowcount > 0
    except Exception as e:
        print(f"Error eliminando validación: {e}")
        return False


def delete_all_usuario(usuario):
    """Delete all validations for a user."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM validaciones WHERE usuario = ?", (usuario,))
            conn.commit()
            return cursor.rowcount
    except Exception as e:
        print(f"Error eliminando historial: {e}")
        return 0
