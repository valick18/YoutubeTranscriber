from pydub import AudioSegment


def create_audio_chunks(audio_path, chunk_duration):
    audio_chunks = []
    audio = AudioSegment.from_file(audio_path, format="mp3")

    chunk_length_ms = chunk_duration * 60 * 1000  # Переводимо час чанка з хвилин у мілісекунди
    start_time = 0
    end_time = chunk_length_ms

    while start_time < len(audio):
        chunk = audio[start_time:end_time]
        chunk_path = f"chunk_{start_time}-{end_time}.mp3"
        chunk.export(chunk_path, format="mp3")
        audio_chunks.append(chunk_path)

        start_time += chunk_length_ms
        end_time += chunk_length_ms

    return audio_chunks
