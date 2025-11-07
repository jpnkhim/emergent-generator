from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import os
import logging
import json
from pathlib import Path
from pydantic import BaseModel
from typing import List
from datetime import datetime, timezone
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Telegram bot imports
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Import account generator
from utils.account_generator import EmergentAccountGenerator


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# JSON file for storing accounts
ACCOUNTS_FILE = ROOT_DIR / 'accounts.json'

# Create the main app
app = FastAPI()
api_router = APIRouter(prefix="/api")

# Thread pool for blocking operations
executor = ThreadPoolExecutor(max_workers=3)


# Models
class AccountResponse(BaseModel):
    email: str
    password: str
    created_at: str
    verified: bool
    message: str = ""


class AccountListResponse(BaseModel):
    total: int
    accounts: List[AccountResponse]


# JSON storage functions
def load_accounts() -> List[dict]:
    """Load accounts from JSON file"""
    if not ACCOUNTS_FILE.exists():
        return []
    try:
        with open(ACCOUNTS_FILE, 'r') as f:
            data = json.load(f)
            return data.get('accounts', [])
    except Exception as e:
        logging.error(f"Error loading accounts: {e}")
        return []


def save_account(account: dict) -> bool:
    """Save account to JSON file"""
    try:
        accounts = load_accounts()
        accounts.append(account)
        
        data = {
            'total': len(accounts),
            'last_updated': datetime.now(timezone.utc).isoformat(),
            'accounts': accounts
        }
        
        with open(ACCOUNTS_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        
        return True
    except Exception as e:
        logging.error(f"Error saving account: {e}")
        return False


# API Routes
@api_router.get("/")
async def root():
    return {"message": "Emergent Account Generator API"}


@api_router.post("/generate", response_model=AccountResponse)
async def generate_account():
    """Generate a new Emergent.sh account"""
    try:
        # Run generator in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        
        def run_generator():
            generator = EmergentAccountGenerator(debug=False)
            return generator.generate_account()
        
        result = await loop.run_in_executor(executor, run_generator)
        
        if not result['success']:
            raise HTTPException(
                status_code=500,
                detail=result.get('error', 'Account generation failed')
            )
        
        # Prepare account data
        account_data = {
            'email': result['email'],
            'password': result['password'],
            'created_at': datetime.now(timezone.utc).isoformat(),
            'verified': result.get('verified', False),
            'message': result.get('message', '')
        }
        
        # Save to JSON
        save_account(account_data)
        
        return AccountResponse(**account_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logging.exception("Error generating account")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/accounts", response_model=AccountListResponse)
async def get_accounts():
    """Get all generated accounts"""
    try:
        accounts = load_accounts()
        return AccountListResponse(
            total=len(accounts),
            accounts=[AccountResponse(**acc) for acc in accounts]
        )
    except Exception as e:
        logging.exception("Error fetching accounts")
        raise HTTPException(status_code=500, detail=str(e))


app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ==================== TELEGRAM BOT ====================

BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '8202105040:AAGALkbC7XPS2CoKCB2tWTRryjOOxuC7br4')


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler"""
    keyboard = [
        [InlineKeyboardButton("🎯 Buat Akun", callback_data='generate')],
        [InlineKeyboardButton("📋 Daftar Akun", callback_data='list_accounts')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        '👋 Selamat datang di Emergent Account Generator Bot!\n\n'
        '✨ Bot ini dapat membuat akun Emergent.sh secara otomatis.\n\n'
        'Pilih aksi:',
        reply_markup=reply_markup
    )


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'generate':
        await generate_account_telegram(update, context)
    elif query.data == 'list_accounts':
        await list_accounts_telegram(update, context)
    elif query.data == 'back_to_menu':
        keyboard = [
            [InlineKeyboardButton("🎯 Buat Akun", callback_data='generate')],
            [InlineKeyboardButton("📋 Daftar Akun", callback_data='list_accounts')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            '👋 Menu Utama\n\n'
            'Pilih aksi:',
            reply_markup=reply_markup
        )


async def generate_account_telegram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate account for Telegram bot"""
    query = update.callback_query
    
    # Show loading message
    await query.edit_message_text('⏳ Sedang membuat akun...\n\nProses ini membutuhkan waktu 30-60 detik.')
    
    try:
        # Generate account in thread pool
        loop = asyncio.get_event_loop()
        
        def run_generator():
            generator = EmergentAccountGenerator(debug=False)
            return generator.generate_account()
        
        result = await loop.run_in_executor(executor, run_generator)
        
        if result['success']:
            # Save account
            account_data = {
                'email': result['email'],
                'password': result['password'],
                'created_at': datetime.now(timezone.utc).isoformat(),
                'verified': result.get('verified', False),
                'message': result.get('message', '')
            }
            save_account(account_data)
            
            # Format message with copyable text
            message = (
                '✅ <b>Akun Berhasil Dibuat!</b>\n\n'
                f'📧 <b>Email:</b>\n<code>{result["email"]}</code>\n\n'
                f'🔐 <b>Password:</b>\n<code>{result["password"]}</code>\n\n'
                f'✨ Status: {"Verified" if result.get("verified") else "Created"}\n\n'
                '💡 <i>Tap pada email atau password untuk menyalin</i>'
            )
            
            keyboard = [
                [InlineKeyboardButton("🎯 Generate Akun Baru", callback_data='generate')],
                [InlineKeyboardButton("📋 Daftar Akun", callback_data='list_accounts')],
                [InlineKeyboardButton("🏠 Menu Utama", callback_data='back_to_menu')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                message,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
        else:
            error_msg = result.get('error', 'Unknown error')
            keyboard = [
                [InlineKeyboardButton("🔄 Coba Lagi", callback_data='generate')],
                [InlineKeyboardButton("🏠 Menu Utama", callback_data='back_to_menu')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                f'❌ <b>Gagal membuat akun</b>\n\n'
                f'Error: {error_msg}\n\n'
                f'Silakan coba lagi.',
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
            
    except Exception as e:
        logger.exception("Error in Telegram account generation")
        keyboard = [
            [InlineKeyboardButton("🔄 Coba Lagi", callback_data='generate')],
            [InlineKeyboardButton("🏠 Menu Utama", callback_data='back_to_menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f'❌ <b>Terjadi kesalahan</b>\n\n'
            f'Error: {str(e)}',
            reply_markup=reply_markup,
            parse_mode='HTML'
        )


async def list_accounts_telegram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all accounts for Telegram bot"""
    query = update.callback_query
    
    try:
        accounts = load_accounts()
        
        if not accounts:
            keyboard = [
                [InlineKeyboardButton("🎯 Buat Akun Pertama", callback_data='generate')],
                [InlineKeyboardButton("🏠 Menu Utama", callback_data='back_to_menu')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                '📋 <b>Daftar Akun</b>\n\n'
                'Belum ada akun yang dibuat.',
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
            return
        
        # Show first 5 accounts
        message = f'📋 <b>Daftar Akun</b> (Total: {len(accounts)})\n\n'
        
        for i, acc in enumerate(accounts[-5:], 1):
            message += (
                f'<b>{i}.</b>\n'
                f'📧 <code>{acc["email"]}</code>\n'
                f'🔐 <code>{acc["password"]}</code>\n'
                f'✨ {"Verified" if acc.get("verified") else "Created"}\n\n'
            )
        
        if len(accounts) > 5:
            message += f'<i>Menampilkan 5 akun terakhir dari {len(accounts)} akun</i>\n\n'
        
        keyboard = [
            [InlineKeyboardButton("🎯 Generate Akun Baru", callback_data='generate')],
            [InlineKeyboardButton("🏠 Menu Utama", callback_data='back_to_menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
        
    except Exception as e:
        logger.exception("Error listing accounts")
        await query.edit_message_text(f'❌ Error: {str(e)}')


# Initialize Telegram bot
telegram_application = None

async def init_telegram_bot():
    """Initialize and start Telegram bot"""
    global telegram_application
    
    telegram_application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    telegram_application.add_handler(CommandHandler("start", start))
    telegram_application.add_handler(CallbackQueryHandler(button_callback))
    
    # Initialize bot
    await telegram_application.initialize()
    await telegram_application.start()
    await telegram_application.updater.start_polling(allowed_updates=Update.ALL_TYPES)
    
    logger.info("Telegram bot started successfully")


@app.on_event("startup")
async def startup_event():
    """Start Telegram bot on app startup"""
    import asyncio
    
    # Start bot in background task
    asyncio.create_task(init_telegram_bot())
    logger.info("Telegram bot initialization started")


@app.on_event("shutdown")
async def shutdown_event():
    executor.shutdown(wait=False)
    
    # Stop telegram bot
    if telegram_application:
        try:
            await telegram_application.updater.stop()
            await telegram_application.stop()
            await telegram_application.shutdown()
            logger.info("Telegram bot stopped")
        except Exception as e:
            logger.error(f"Error stopping bot: {e}")
