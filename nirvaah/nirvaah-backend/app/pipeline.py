# pipeline.py — orchestrates all 11 stages
# This stub is filled in by the AI Teammate

async def run_pipeline(sender_phone: str, audio_bytes: bytes = None,
                       image_bytes: bytes = None, text: str = None):
    """
    Entry point for all message processing.
    Returns: dict with extracted fields and status
    """
    print(f'Pipeline called from {sender_phone}')
    print(f'Text: {text}')
    print(f'Audio bytes: {len(audio_bytes) if audio_bytes else 0}')
    # Stub response for testing webhook
    return {'status': 'received', 'phone': sender_phone}