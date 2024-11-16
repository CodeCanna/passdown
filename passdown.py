#!/usr/bin/env python3
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import telegram
import asyncio
import subprocess
import os
import yaml
import re
from pathlib import Path
import getpass
import subprocess
from errors import BadFileTypeException
import configparser

def get_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config['api-key']['key']
        
    
    

def is_markdown(file: str) -> bool:
    _, e = os.path.splitext(file)
    return True if e == '.md' else False

def file_exists(file: Path) -> bool:
    return True if os.path.isfile(file) else False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Hello, Beans!")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:  
        await context.bot.send_message(chat_id=update.effective_chat.id, text="File recieved")
        
        # Validate File
        if not is_markdown(update.message.document.file_name): raise BadFileTypeException("🚫 Unsupported File Type: Please upload a Markdown file (.md). Other file types are not accepted.")
        if file_exists(f"content/{update.message.document.file_name}"): raise FileExistsError("⚠️ Duplicate Post Detected: It looks like this blog post has already been uploaded. Please check your submissions and try again with a new post.")
        
        
        file = await context.bot.get_file(update.message.document.file_id)
        
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Downloading {update.message.document.file_name}")
        await file.download_to_drive(Path(f"content/{update.message.document.file_name}"))

        subprocess.run(["make", "html"], capture_output=True)
        subprocess.run(["make", "github"], capture_output=True)
        
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Blog updated!")
    except AttributeError:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="I cannot accept images.")
    except FileExistsError as e:
        await  context.bot.send_message(chat_id=update.effective_chat.id, text=str(e))
    except BadFileTypeException as e:
        await  context.bot.send_message(chat_id=update.effective_chat.id, text=e.message)

if __name__ == '__main__':
    application = ApplicationBuilder().token(get_config()).build()

    handlers = [
        CommandHandler('start', start),
        MessageHandler(filters.ATTACHMENT, handle_document),
    ]

    application.add_handlers(handlers=handlers)

    application.run_polling()