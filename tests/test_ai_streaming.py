from app.api.ai_routes import _stream_word_chunks


def test_stream_word_chunks_preserves_the_message_for_incremental_rendering() -> None:
    message = "Olá, Vini!\nVamos organizar seu dia?"

    chunks = _stream_word_chunks(message)

    assert chunks == ["Olá, ", "Vini!\n", "Vamos ", "organizar ", "seu ", "dia?"]
    assert "".join(chunks) == message
