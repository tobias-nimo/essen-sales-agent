#!/usr/bin/env python3
"""
Essen Sales Agent - Terminal Interface

An interactive CLI for Essen sales consultants to create customized sales quotes.
"""

from agents.coordinator import coordinator

import os
import uuid
from langchain.messages import HumanMessage

def print_banner():
    """Print welcome banner"""
    banner = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║              🍳 ESSEN SALES AGENT 🍳                      ║
║                                                           ║
║        Asistente para Crear Presupuestos de Venta         ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)
    print("\nBienvenido! Este asistente te ayudará a crear presupuestos")
    print("de venta profesionales para tus clientes de Essen.\n")
    print("Comandos disponibles:")
    print("  - Escribe tu consulta naturalmente")
    print("  - 'salir' o 'exit' para terminar")
    print("  - 'nuevo' para iniciar un nuevo presupuesto")
    print("  - 'ayuda' para ver instrucciones\n")


def print_help():
    """Print help information"""
    help_text = """
═══════════════════════════════════════════════════════════
                        AYUDA
═══════════════════════════════════════════════════════════

Este asistente te guiará paso a paso para crear un presupuesto:

1. PRODUCTOS: Dile qué productos necesitas
   Ejemplo: "Necesito un presupuesto para una sartén de 24cm"

2. CANTIDAD: Confirma las cantidades

3. PAGO: Indica cómo pagará el cliente
   - Efectivo (cash)
   - Transferencia (wire)
   - Tarjeta de crédito (credit card)

4. PROMOCIONES: Si es con tarjeta, te ayudaré a encontrar
   las mejores promociones según el banco y tarjeta

5. DATOS DEL CLIENTE: Nombre, email y teléfono

6. GENERAR: El asistente creará el presupuesto final

═══════════════════════════════════════════════════════════
    """
    print(help_text)


def print_separator():
    """Print a visual separator"""
    print("\n" + "─" * 60 + "\n")


def main():
    """Main interaction loop"""

    # Check for model provider API keys
    print_banner()

    # Initialize session with a thread ID for conversation persistence
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    # Initialize state
    initial_state = {
        "products": {},
        "payment_method": None,
        "payment_plan": None,
        "customer_information": None,
        "total_amount": 0.0,
        "messages": []
    }

    print("🤖 Asistente: ¡Hola! ¿En qué puedo ayudarte hoy?")
    print_separator()

    while True:
        try:
            # Get user input
            user_input = input("👤 Tú: ").strip()

            if not user_input:
                continue

            # Handle special commands
            if user_input.lower() in ['salir', 'exit', 'quit']:
                print("\n🤖 Asistente: ¡Hasta luego! Que tengas un excelente día.\n")
                break

            if user_input.lower() == 'nuevo':
                print("\n🔄 Iniciando nuevo presupuesto...\n")
                thread_id = str(uuid.uuid4())
                config = {"configurable": {"thread_id": thread_id}}
                initial_state = {
                    "products": {},
                    "payment_method": None,
                    "payment_plan": None,
                    "customer_information": None,
                    "total_amount": 0.0,
                    "messages": []
                }
                print("🤖 Asistente: ¡Perfecto! Empecemos un nuevo presupuesto. ¿Qué productos necesitas?")
                print_separator()
                continue

            if user_input.lower() in ['ayuda', 'help']:
                print_help()
                print_separator()
                continue

            # Create message
            message = HumanMessage(content=user_input)

            # Invoke the coordinator agent
            print("\n🤖 Asistente: ", end="", flush=True)

            response = coordinator.invoke(
                {"messages": [message]},
                config=config
            )

            # Extract and print the assistant's response
            if response and "messages" in response:
                last_message = response["messages"][-1]
                if hasattr(last_message, 'content'):
                    print(last_message.content)
                else:
                    print("Procesado.")
            else:
                print("Lo siento, hubo un problema procesando tu solicitud.")

            print_separator()

        except KeyboardInterrupt:
            print("\n\n🤖 Asistente: ¡Hasta luego!")
            break

        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            print("Por favor, intenta de nuevo o escribe 'ayuda' para instrucciones.\n")
            print_separator()


if __name__ == "__main__":
    main()