#!/usr/bin/env python3
"""
Essen Sales Agent - Terminal Interface

An interactive CLI for Essen sales consultants to create customized sales quotes.
"""

import os
import sys
import uuid
import threading
import itertools
import time
from datetime import datetime
from typing import Optional

from loguru import logger
from langchain.messages import HumanMessage

from agents.coordinator import coordinator
from agents.state import SalesQuoteState


# ═══════════════════════════════════════════════════════════════════════════════
# ANSI Color Codes
# ═══════════════════════════════════════════════════════════════════════════════

class Colors:
    """ANSI color codes for terminal styling"""
    # Reset
    RESET = "\033[0m"

    # Regular colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # Bright colors
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"

    # Styles
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"

    # Background
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"


# ═══════════════════════════════════════════════════════════════════════════════
# Spinner for Loading States
# ═══════════════════════════════════════════════════════════════════════════════

class Spinner:
    """Animated spinner for loading states"""

    def __init__(self, message: str = "Procesando"):
        self.message = message
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    def _spin(self):
        for frame in itertools.cycle(self.frames):
            if not self.running:
                break
            sys.stdout.write(f"\r{Colors.CYAN}{frame}{Colors.RESET} {Colors.DIM}{self.message}...{Colors.RESET}  ")
            sys.stdout.flush()
            time.sleep(0.1)

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._spin, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        sys.stdout.write("\r" + " " * 50 + "\r")
        sys.stdout.flush()


# ═══════════════════════════════════════════════════════════════════════════════
# Session State Display
# ═══════════════════════════════════════════════════════════════════════════════

def format_currency(amount: float) -> str:
    """Format amount as currency"""
    return f"${amount:,.2f}"


def get_status_indicator(value) -> str:
    """Return a status indicator based on whether a value is set"""
    if value:
        return f"{Colors.GREEN}●{Colors.RESET}"
    return f"{Colors.BRIGHT_BLACK}○{Colors.RESET}"


def display_quote_status(state: dict):
    """Display current quote status in a compact format"""
    products = state.get("products", {})
    payment_method = state.get("payment_method")
    payment_plan = state.get("payment_plan")
    customer = state.get("customer_information")
    total = state.get("total_amount", 0.0)

    product_count = len(products)

    print(f"\n{Colors.BRIGHT_BLACK}┌─ Estado del Presupuesto ─────────────────────────────┐{Colors.RESET}")

    # Products
    products_status = get_status_indicator(products)
    products_text = f"{product_count} producto(s)" if products else "Sin productos"
    print(f"{Colors.BRIGHT_BLACK}│{Colors.RESET} {products_status} Productos: {products_text}")

    # Payment
    payment_status = get_status_indicator(payment_method)
    payment_text = payment_method if payment_method else "No definido"
    print(f"{Colors.BRIGHT_BLACK}│{Colors.RESET} {payment_status} Pago: {payment_text}")

    # Payment Plan (only if credit card)
    if payment_method == "CREDIT_CARD":
        plan_status = get_status_indicator(payment_plan)
        if payment_plan:
            plan_text = f"{payment_plan.bank} {payment_plan.credit_card} - {payment_plan.installments} cuotas"
        else:
            plan_text = "No definido"
        print(f"{Colors.BRIGHT_BLACK}│{Colors.RESET} {plan_status} Plan: {plan_text}")

    # Customer
    customer_status = get_status_indicator(customer)
    customer_text = customer.name if customer else "No definido"
    print(f"{Colors.BRIGHT_BLACK}│{Colors.RESET} {customer_status} Cliente: {customer_text}")

    # Total
    print(f"{Colors.BRIGHT_BLACK}│{Colors.RESET}")
    print(f"{Colors.BRIGHT_BLACK}│{Colors.RESET} {Colors.BOLD}Total: {Colors.GREEN}{format_currency(total)}{Colors.RESET}")

    print(f"{Colors.BRIGHT_BLACK}└───────────────────────────────────────────────────────┘{Colors.RESET}\n")


# ═══════════════════════════════════════════════════════════════════════════════
# UI Components
# ═══════════════════════════════════════════════════════════════════════════════

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_banner():
    """Print welcome banner"""
    clear_screen()
    title = f"{Colors.BRIGHT_WHITE}ESSEN SALES AGENT{Colors.BRIGHT_CYAN}"
    sub_title = f"{Colors.DIM}Asistente de Presupuestos{Colors.RESET}{Colors.BRIGHT_CYAN}"
    banner = f"""
{Colors.BRIGHT_CYAN}
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║                       {title}                       ║
║                   {sub_title}                   ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
{Colors.RESET}
"""
    print(banner)
    print(f"{Colors.WHITE}Bienvenido! Este asistente te ayudará a crear presupuestos")
    print(f"de venta profesionales para tus clientes de Essen.{Colors.RESET}\n")


def print_commands():
    """Print available commands"""
    print(f"{Colors.BRIGHT_BLACK}─────────────────────────────────────────────────────────────────{Colors.RESET}")
    print(f"{Colors.BOLD}Comandos disponibles:{Colors.RESET}")
    print(f"  {Colors.CYAN}/nuevo{Colors.RESET}     Iniciar nuevo presupuesto")
    print(f"  {Colors.CYAN}/estado{Colors.RESET}    Ver estado del presupuesto actual")
    print(f"  {Colors.CYAN}/ayuda{Colors.RESET}     Ver instrucciones detalladas")
    print(f"  {Colors.CYAN}/limpiar{Colors.RESET}   Limpiar pantalla")
    print(f"  {Colors.CYAN}/salir{Colors.RESET}     Salir del programa")
    print(f"{Colors.BRIGHT_BLACK}─────────────────────────────────────────────────────────────────{Colors.RESET}\n")


def print_help():
    """Print detailed help information"""
    help_text = f"""
{Colors.BOLD}{Colors.CYAN}═══════════════════════════════════════════════════════════════════
                           AYUDA
═══════════════════════════════════════════════════════════════════{Colors.RESET}

{Colors.BOLD}Flujo para crear un presupuesto:{Colors.RESET}

{Colors.YELLOW}1. PRODUCTOS{Colors.RESET}
   Dile qué productos necesitas. Puedes usar lenguaje natural.
   {Colors.DIM}Ejemplo: "Necesito un presupuesto para una sartén de 24cm"{Colors.RESET}

{Colors.YELLOW}2. CANTIDAD{Colors.RESET}
   Confirma las cantidades de cada producto.

{Colors.YELLOW}3. MÉTODO DE PAGO{Colors.RESET}
   Indica cómo pagará el cliente:
   • Efectivo (CASH)
   • Transferencia bancaria (WIRE)
   • Tarjeta de crédito (CREDIT_CARD)

{Colors.YELLOW}4. PROMOCIONES{Colors.RESET} (solo para tarjeta de crédito)
   El asistente buscará las mejores promociones según:
   • Banco del cliente
   • Tipo de tarjeta
   • Cantidad de cuotas

{Colors.YELLOW}5. DATOS DEL CLIENTE{Colors.RESET}
   Proporciona: nombre, email y teléfono

{Colors.YELLOW}6. GENERAR PRESUPUESTO{Colors.RESET}
   El asistente creará el documento final.

{Colors.CYAN}═══════════════════════════════════════════════════════════════════{Colors.RESET}
"""
    print(help_text)


def print_separator():
    """Print a visual separator"""
    print(f"\n{Colors.BRIGHT_BLACK}─────────────────────────────────────────────────────────────────{Colors.RESET}\n")


def print_assistant_message(message: str):
    """Print assistant message with formatting"""
    print(f"\n{Colors.GREEN}▶{Colors.RESET} {Colors.BOLD}Asistente:{Colors.RESET}")
    print(f"  {message}")


def print_error(message: str):
    """Print error message"""
    print(f"\n{Colors.RED}✖ Error:{Colors.RESET} {message}")


def print_info(message: str):
    """Print info message"""
    print(f"\n{Colors.BLUE}ℹ{Colors.RESET} {message}")


def get_user_input() -> str:
    """Get user input with styled prompt"""
    try:
        prompt = f"{Colors.BLUE}▶{Colors.RESET} {Colors.BOLD}Tú:{Colors.RESET} "
        return input(prompt).strip()
    except EOFError:
        return "/salir"


# ═══════════════════════════════════════════════════════════════════════════════
# Session Management
# ═══════════════════════════════════════════════════════════════════════════════

class Session:
    """Manages the conversation session state"""

    def __init__(self):
        self.thread_id = str(uuid.uuid4())
        self.config = {"configurable": {"thread_id": self.thread_id}}
        self.state = {
            "products": {},
            "payment_method": None,
            "payment_plan": None,
            "customer_information": None,
            "total_amount": 0.0,
            "messages": []
        }
        self.start_time = datetime.now()
        logger.info(f"New session started: {self.thread_id}")

    def reset(self):
        """Reset session for a new quote"""
        old_thread = self.thread_id
        self.thread_id = str(uuid.uuid4())
        self.config = {"configurable": {"thread_id": self.thread_id}}
        self.state = {
            "products": {},
            "payment_method": None,
            "payment_plan": None,
            "customer_information": None,
            "messages": []
        }
        self.start_time = datetime.now()
        logger.info(f"Session reset: {old_thread} -> {self.thread_id}")


# ═══════════════════════════════════════════════════════════════════════════════
# Main REPL Loop
# ═══════════════════════════════════════════════════════════════════════════════

def handle_command(command: str, session: Session) -> bool:
    """
    Handle special commands.
    Returns True if should continue, False if should exit.
    """
    cmd = command.lower().strip()

    if cmd in ['/salir', '/exit', '/quit']:
        print(f"\n{Colors.CYAN}¡Hasta luego! Que tengas un excelente día.{Colors.RESET}\n")
        logger.info(f"Session ended by user: {session.thread_id}")
        return False

    if cmd in ['/nuevo', '/new']:
        session.reset()
        print_info("Nuevo presupuesto iniciado.")
        print_assistant_message("¡Perfecto! Empecemos un nuevo presupuesto. ¿Qué productos necesitas?")
        return True

    if cmd in ['/estado', '/status']:
        display_quote_status(session.state)
        return True

    if cmd in ['/ayuda', '/help']:
        print_help()
        return True

    if cmd in ['/limpiar', '/clear']:
        print_banner()
        print_commands()
        return True

    if cmd in ['/comandos', '/commands']:
        print_commands()
        return True

    return None  # Not a command


def process_message(user_input: str, session: Session) -> str:
    """Process user message through the coordinator agent"""
    logger.debug(f"Processing message: {user_input[:50]}...")

    message = HumanMessage(content=user_input)

    response = coordinator.invoke(
        {"messages": [message]},
        config=session.config
    )

    # Update local state if available
    if response:
        for key in ["products", "payment_method", "payment_plan", "customer_information", "total_amount"]:
            if key in response:
                session.state[key] = response[key]

    # Extract response message
    if response and "messages" in response:
        last_message = response["messages"][-1]
        if hasattr(last_message, 'content'):
            return last_message.content

    return "Lo siento, hubo un problema procesando tu solicitud."


def main():
    """Main REPL interaction loop"""

    # Configure logger
    logger.remove()
    logger.add(
        "logs/essen_agent_{time:YYYY-MM-DD}.log",
        rotation="1 day",
        retention="7 days",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}"
    )
    logger.add(
        sys.stderr,
        level="ERROR",
        format="{time:HH:mm:ss} | {level} | {message}"
    )

    logger.info("Essen Sales Agent starting...")

    # Initialize session
    session = Session()

    # Print welcome
    print_banner()
    print_commands()

    print_assistant_message("¡Hola! ¿En qué puedo ayudarte hoy?")
    print_separator()

    # Main loop
    while True:
        try:
            user_input = get_user_input()

            if not user_input:
                continue

            # Check if it's a command
            command_result = handle_command(user_input, session)
            if command_result is False:
                break
            elif command_result is True:
                print_separator()
                continue

            # Process through agent
            spinner = Spinner("Pensando")
            spinner.start()

            try:
                response = process_message(user_input, session)
                logger.debug(f"Agent response received: {len(response)} chars")
            finally:
                spinner.stop()

            print_assistant_message(response)
            print_separator()

        except KeyboardInterrupt:
            print(f"\n\n{Colors.CYAN}¡Hasta luego!{Colors.RESET}\n")
            logger.info("Session interrupted by user")
            break

        except Exception as e:
            logger.exception(f"Error processing request: {e}")
            print_error(str(e))
            print(f"{Colors.DIM}Por favor, intenta de nuevo o escribe /ayuda para instrucciones.{Colors.RESET}")
            print_separator()

    logger.info("Essen Sales Agent stopped")


if __name__ == "__main__":
    main()
