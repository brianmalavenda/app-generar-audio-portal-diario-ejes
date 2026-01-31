main() {
    python setup_structure.py

    pip install -e .

    python -c "try:
        import gcloud_tts
        print('✅ gcloud_tts importado')
        print(f'Versión: {gcloud_tts.__version__}')
    except ImportError as e:
        print(f'❌ Error: {e}')
    "
}

# Ejecutar menú principal
main