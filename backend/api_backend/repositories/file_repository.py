from flask import current_app
import mysql.connector
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)

class FileRepository:
    def __init__(self, conn_config):
        self.connection_pool = mysql.connector.pooling.MySQLConnectionPool(**conn_config)

    def create(**kwargs) -> int:
        """
        Inserta un nuevo registro en file_history.
        Retorna el ID del registro insertado.
        """
        connection = self.connection_pool.get_connection()
        cursor = connection.cursor()

        try:
            sql = """
            INSERT INTO file_history 
            (original_filename, original_path, processed_word, processed_word_path, 
             processed_word_count, processed_char_count, processed_file_size_mb, audio_path, status, session_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (
                kwargs.get('original_filename'),
                kwargs.get('original_path'),
                kwargs.get('processed_word'),
                kwargs.get('processed_word_path'),
                kwargs.get('processed_word_count'),
                kwargs.get('processed_char_count'),
                kwargs.get('processed_file_size_mb'),
                kwargs.get('audio_path', ''),  # Si no se ha generado el audio aún, se guarda como cadena vacía
                kwargs.get('status', 'uploaded'),
                kwargs.get('session_id', '')
            )
            cursor.execute(sql, values)
            connection.commit()
            return cursor.lastrowid
        except mysql.connector.Error as err:
            connection.rollback()
            raise Exception(f"Error al crear registro: {err}")
        finally:
            cursor.close()
            connection.close()
    
    def find_by_id(file_id: int) -> Optional[Dict]:
        """
        Busca un archivo por su ID.
        Retorna un diccionario con los datos o None si no existe.
        """
        connection = self.connection_pool.get_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM file_history WHERE id = %s", (file_id,))
            return cursor.fetchone()
        finally:
            cursor.close()
            connection.close()
    
    def update_audio_path(file_id: int, audio_path: str) -> bool:
        """
        Actualiza la ruta del audio generado.
        Retorna True si se actualizó correctamente.
        """
        connection = self.connection_pool.get_connection()
        cursor = connection.cursor()
        try:
            sql = """
            UPDATE file_history 
            SET audio_path = %s, status = 'audio_generated' 
            WHERE id = %s
            """
            cursor.execute(sql, (audio_path, file_id))
            connection.commit()
            return cursor.rowcount > 0
        except mysql.connector.Error as err:
            connection.rollback()
            raise Exception(f"Error al actualizar audio: {err}")
        finally:
            cursor.close()
            connection.close()
    
    def list_by_session(session_id: str, limit: int = 50) -> List[Dict]:
        """
        Lista los archivos de una sesión específica.
        """
        connection = self.connection_pool.get_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT * FROM file_history WHERE session_id = %s ORDER BY created_at DESC LIMIT %s",
                (session_id, limit)
            )
            return cursor.fetchall()
        finally:
            cursor.close()
            connection.close()