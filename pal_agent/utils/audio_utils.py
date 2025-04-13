import os
import wave

from pydub import AudioSegment

def pcm2file(pcm_data: bytes, output_file: str, channels=1, sample_rate=48000, sample_width=2):
    """
    Convert raw PCM data to a specified audio file format based on the output file extension.

    :param pcm_data: Raw PCM byte data.
    :param output_file: Path to save the audio file.
    :param channels: Number of audio channels.
    :param rate: Sample rate (Hz).
    :param sample_width: Sample width in bytes.
    """
    # Extract file format from the output file extension
    file_format = os.path.splitext(output_file)[1][1:].lower()

    # Check if the format is supported
    supported_formats = ['wav', 'mp3', 'aac', 'flac', 'ogg', 'aiff', 'wma']
    if file_format not in supported_formats:
        raise ValueError(f"Unsupported file format: {file_format}. Supported formats are: {', '.join(supported_formats)}.")

    # Create an AudioSegment from PCM data
    audio = AudioSegment(
        data=pcm_data,
        sample_width=sample_width,
        frame_rate=sample_rate,
        channels=channels
    )

    # Export the audio in the specified format
    try:
        audio.export(output_file, format=file_format)
        logger.info(f"{file_format.upper()} file saved at {output_file}")
    except Exception as e:
        logger.error(f"Error saving {file_format.upper()} file: {e}")


def read_wav_file(input_file: str):
    with wave.open(input_file, "rb") as wav_file:
        pcm_data = wav_file.readframes(wav_file.getnframes())
        sample_rate = wav_file.getframerate()

    return pcm_data, sample_rate


# Example usage
if __name__ == "__main__":

    from pal_agent import constants
    pcm_data, sample_rate = read_wav_file(constants.AUDIO_TEST_FILE_PATH)

    pcm2file(pcm_data=pcm_data, sample_rate=sample_rate, output_file="tmp/output.wav")  # Convert PCM to WAV, replace with desired format
