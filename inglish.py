# Requiere: pip install python-telegram-bot --upgrade, pydub, pronouncing, googletrans==4.0.0-rc1, pyttsx3
# Además, ffmpeg debe estar instalado y en el PATH del sistema para la conversión de audio.
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import pronouncing
from googletrans import Translator
import pyttsx3
import os
from pydub import AudioSegment

translator = Translator()
engine = pyttsx3.init()
engine.setProperty('rate', 140)
engine.setProperty('voice', 'HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_EN-US_ZIRA_11.0')  # voz de Zira en Windows

TOKEN = 'Here is the token for bot Inglés Bot Fácil @EasyEnglishVoiceBot:

7869545317:AAF9TO7PS0VJK0zWIl3_IAwLlV6UhBfWC6I'  # <--- PON AQUÍ TU TOKEN REAL

def simplificar_fonetica(phones):
    equivalencias = {
        'AA': 'a', 'AE': 'a', 'AH': 'a', 'AO': 'o', 'AW': 'au',
        'AY': 'ai', 'B': 'b', 'CH': 'ch', 'D': 'd', 'DH': 'd',
        'EH': 'e', 'ER': 'er', 'EY': 'ei', 'F': 'f', 'G': 'g',
        'HH': 'j', 'IH': 'i', 'IY': 'i', 'JH': 'y', 'K': 'k',
        'L': 'l', 'M': 'm', 'N': 'n', 'NG': 'ng', 'OW': 'ou',
        'OY': 'oi', 'P': 'p', 'R': 'r', 'S': 's', 'SH': 'sh',
        'T': 't', 'TH': 'z', 'UH': 'u', 'UW': 'u', 'V': 'v',
        'W': 'w', 'Y': 'y', 'Z': 'z', 'ZH': 'sh'
    }
    return ''.join(equivalencias.get(p.replace('0','').replace('1','').replace('2',''), p.lower()) for p in phones.split())

async def procesar_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text
    palabras = texto.lower().split()
    fonetica = []
    for palabra in palabras:
        phones = pronouncing.phones_for_word(palabra)
        if phones:
            fonetica.append(simplificar_fonetica(phones[0]))
        else:
            fonetica.append(palabra)
    resultado_fonetica = ' '.join(fonetica)
    try:
        traduccion = translator.translate(texto, src='en', dest='es').text
    except Exception as e:
        traduccion = f"(No se pudo traducir: {e})"
    respuesta = f"""📘 *Inglés:*  \n{texto}\n\n🔊 *Fonética:*  \n{resultado_fonetica}\n\n🇲🇽 *Español:*  \n{traduccion}\n"""
    await update.message.reply_text(respuesta, parse_mode='Markdown')
    # Generar voz en WAV
    wav_filename = "voz.wav"
    ogg_filename = "voz.ogg"
    engine.save_to_file(texto, wav_filename)
    engine.runAndWait()
    # Convertir WAV a OGG/OPUS
    try:
        audio = AudioSegment.from_wav(wav_filename)
        audio.export(ogg_filename, format="ogg", codec="libopus")
        with open(ogg_filename, 'rb') as audio_file:
            await update.message.reply_voice(voice=audio_file)
    except Exception as e:
        await update.message.reply_text(f"Error al generar o enviar el audio: {e}")
    finally:
        if os.path.exists(wav_filename):
            os.remove(wav_filename)
        if os.path.exists(ogg_filename):
            os.remove(ogg_filename)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hola 👋, envíame una frase en inglés y te mostraré la pronunciación, traducción ¡y te la leeré!")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), procesar_mensaje))
    print("Bot iniciado...")
    app.run_polling()

if __name__ == '__main__':
    main()
