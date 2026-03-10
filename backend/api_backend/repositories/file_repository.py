# repositories/file_repository.py
from flask import current_app
import mysql.connector
from typing import Optional, Dict, List

class FileRepository:
    """Repositorio para manejar operaciones de la tabla file_history"""
    connection_pool = mysql.connector.pooling.MySQLConnectionPool(**current_app.config['DB_CONFIG'])

    def get_db_connection():
        return connection_pool.get_connection()


    @staticmethod
    def create(original_filename: str, original_path: str, **kwargs) -> int:
        """
        Inserta un nuevo registro en file_history.
        Retorna el ID del registro insertado.
        """
        connection = self.get_db_connection()
        cursor = connection.cursor()
        try:
            sql = """
            INSERT INTO file_history 
            (original_filename, original_path, processed_filename, processed_path, 
             ssml_word_count, ssml_char_count, ssml_file_size_mb, status, session_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (
                original_filename,
                original_path,
                kwargs.get('processed_filename'),
                kwargs.get('processed_path'),
                kwargs.get('ssml_word_count'),
                kwargs.get('ssml_char_count'),
                kwargs.get('ssml_file_size_mb'),
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
    
    @staticmethod
    def find_by_id(file_id: int) -> Optional[Dict]:
        """
        Busca un archivo por su ID.
        Retorna un diccionario con los datos o None si no existe.
        """
        connection = self.get_db_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM file_history WHERE id = %s", (file_id,))
            return cursor.fetchone()
        finally:
            cursor.close()
            connection.close()
    
    @staticmethod
    def update_audio_path(file_id: int, audio_path: str) -> bool:
        """
        Actualiza la ruta del audio generado.
        Retorna True si se actualizó correctamente.
        """
        connection = self.get_db_connection()
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
    
    @staticmethod
    def list_by_session(session_id: str, limit: int = 50) -> List[Dict]:
        """
        Lista los archivos de una sesión específica.
        """
        connection = self.get_db_connection()
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