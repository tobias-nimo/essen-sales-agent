# Essen Sales Agent

An intelligent multi-agent system to help Essen entrepreneurs (sales consultants) create customized sales quotes for their customers.

## Overview

Essen is a premium Argentine cookware brand that sells mainly through a direct sales consultant network. This agent system assists consultants in building professional sales quotes by:

- Searching the product catalog
- Finding the best promotional offers
- Calculating pricing for different payment methods
- Generating professional quote documents

## Architecture

This is a **multi-agent system** built with LangChain, LangGraph, and LangSmith:

### 🤖 Coordinator Agent
The main agent that orchestrates the quote creation process. It:
- Interacts with the user
- Manages the sales quote state
- Delegates tasks to specialized sub-agents
- Generates the final quote document

### 📚 Catalog Agent
A specialized agent that:
- Searches the product catalog
- Retrieves product details and pricing
- Provides information on available products

### 🎁 Promotions Agent
A specialized agent that:
- Searches for available credit card promotions
- Filters promotions by bank, card, and installments
- Provides promotional pricing information

## Features

- **Natural Language Interface**: Interact conversationally to build quotes
- **Intelligent Product Search**: Find products by name or description
- **Promotion Discovery**: Automatically find the best credit card promotions
- **Multiple Payment Methods**: Support for cash, wire transfer, and credit cards
- **Flexible Installment Plans**: 6, 9, or 12-month payment options
- **State Management**: Maintains conversation context and quote state
- **Quote Generation**: Creates downloadable quote documents

## Project Structure

```
essen-sales-agent/
├── src/
│   ├── main.py                         # Terminal interface
│   └── agents/
│       ├── state.py                    # State schema definitions
│       ├── coordinator.py              # Main coordinator agent
│       ├── catalog_agent.py            # Product catalog agent
│       ├── promotions_agent.py         # Promotions agent
│       ├── prompts/
│       │   ├── coordinator_agent.md    # Coordinator system prompt
│       │   ├── product_agent.md        # Catalog agent prompt
│       │   └── promotions_agent.md     # Promotions agent prompt
│       └── tools/
│           ├── coordinator.py          # Coordinator tools
│           ├── search_catalog.py       # Catalog search tools
│           └── query_promotions.py     # Promotions query tools
├── data/
│   ├── catalog.csv                     # Product catalog
│   ├── price_list.csv                  # Product pricing
│   └── promotions.json                 # Available promotions
├── output/                             # Generated quotes (created on first run)
├── pyproject.toml                      # Project dependencies
└── README.md                           # This file
```

## Installation

### Prerequisites

- Python 3.9 or higher
- [UV](https://docs.astral.sh/uv/) for dependency management
- OpenAI API key

### Setup

1. **Clone the repository:**
   ```bash
   cd essen-sales-agent
   ```

2. **Create virtual environment and install dependencies:**
   ```bash
   uv venv
   uv sync
   ```

3. **Activate the virtual environment:**
   ```bash
   source .venv/bin/activate  # On Linux/macOS
   # or
   .venv\Scripts\activate     # On Windows
   ```

4. **Set up environment variables:**
   ```bash
   # Required: OpenAI API key
   export OPENAI_API_KEY='your-openai-api-key'

   # Optional: LangSmith (for tracing and monitoring)
   export LANGCHAIN_TRACING_V2='true'
   export LANGCHAIN_API_KEY='your-langsmith-api-key'
   export LANGCHAIN_PROJECT='essen-sales-agent'
   ```

## Usage

### Starting the Agent

Make sure your virtual environment is activated, then run:

```bash
python src/main.py
```

Or if you made it executable:

```bash
./src/main.py
```

### Example Conversation

```
🤖 Asistente: ¡Hola! ¿En qué puedo ayudarte hoy?

👤 Tú: Necesito un presupuesto para una sartén de 24cm

🤖 Asistente: Claro, déjame buscar sartenes de 24cm en nuestro catálogo...
[Shows available products]

👤 Tú: La primera opción, una unidad

🤖 Asistente: Perfecto, agregué COMBO ESSEN+ REIN & SARTEN 24 CAPRI al carrito.
¿Cómo va a pagar el cliente? Efectivo, transferencia o tarjeta de crédito?

👤 Tú: Tarjeta de crédito con Banco Galicia

🤖 Asistente: ¿Qué tarjeta tiene el cliente? (Visa, Mastercard, Amex, etc.)

👤 Tú: Visa, en 12 cuotas

🤖 Asistente: Excelente! Encontré promociones disponibles...
[Shows promotion options and sets up payment plan]

👤 Tú: Perfecto. El cliente es Juan Pérez, email juan@example.com, teléfono 1234567890

🤖 Asistente: ¡Listo! Todos los datos están completos.
¿Te gustaría que genere el presupuesto?

👤 Tú: Sí, genera el presupuesto

🤖 Asistente: ¡Presupuesto generado exitosamente!
Archivo guardado en: /path/to/output/quote_20260112_143022.json
```

### Commands

- Type naturally to interact with the agent
- `nuevo` - Start a new quote
- `ayuda` - Show help information
- `salir` or `exit` - Exit the application

## Data Files

### catalog.csv
List of available products with:
- `id`: Unique product identifier
- `description`: Product description

### price_list.csv
Pricing information for products:
- `id`: Product identifier
- `base_price`: Base price for promotional calculations
- `cash_price`: Price for cash/wire payments
- `installments_12`: Monthly price for 12-month plan
- `installments_9`: Monthly price for 9-month plan
- `installments_6`: Monthly price for 6-month plan

### promotions.json
Available credit card promotions with:
- `id`: Promotion identifier
- `name`: Promotion name
- `banks`: Eligible banks
- `credit_cards`: Accepted card brands
- `installments`: Available installment options
- `availability`: Time period when valid
- `wallets`: Digital wallet requirements
- `reimbursement`: Cashback terms

## State Schema

The system maintains a `SalesQuoteState` with:

```python
{
    "products": {                        # Cart products
        "product_id": ProductLine(...)
    },
    "payment_method": "CASH|WIRE|CREDIT_CARD",
    "payment_plan": PaymentPlan(...),    # For credit card payments
    "customer_information": CustomerInformation(...),
    "total_amount": float,
    "messages": [...]                    # Conversation history
}
```

## Agent Tools

### Coordinator Tools
- `lookup_products`: Search catalog via catalog agent
- `get_available_promotions`: Search promotions via promotions agent
- `add_product_to_cart`: Add product to cart
- `set_payment_method`: Set payment method
- `set_payment_plan`: Configure credit card payment plan
- `set_customer_information`: Save customer details
- `generate_quote_pdf`: Create final quote document

### Catalog Agent Tools
- `search_products`: Search by keyword
- `get_product_by_id`: Get specific product details
- `get_multiple_products`: Batch product lookup

### Promotions Agent Tools
- `search_promotions`: Filter by bank/card/installments
- `get_promotion_by_id`: Get specific promotion details
- `list_all_promotions`: List all available promotions

## Development

### Technology Stack

- **Python 3.9+**: Backend language
- **UV**: Fast Python package installer and virtual environment manager
- **LangChain**: Agent framework and tool management
- **LangGraph**: Multi-agent orchestration and state management
- **LangSmith**: Tracing and monitoring (optional)
- **OpenAI**: LLM provider (GPT-4o-mini)

### Adding New Products

Edit `data/catalog.csv` and `data/price_list.csv`:

```csv
# catalog.csv
id,description
80012345,NEW PRODUCT DESCRIPTION

# price_list.csv
id,base_price,cash_price,installments_12,installments_9,installments_6
80012345,5000000,0,625000,750000,958333
```

### Adding New Promotions

Edit `data/promotions.json`:

```json
{
  "id": "099",
  "name": "PROMO_NEW",
  "banks": ["BANK_NAME"],
  "credit_cards": ["VISA", "MASTERCARD"],
  "installments": [3, 6, 9, 12],
  "availability": {"type": "always"},
  "wallets": [],
  "reimbursement": null
}
```

## Roadmap

Future enhancements:

- [ ] Generate actual PDF documents (currently outputs JSON)
- [ ] Add web UI interface
- [ ] Support for multiple currencies
- [ ] Email quote delivery
- [ ] Quote history and tracking
- [ ] Analytics dashboard
- [ ] Integration with CRM systems
- [ ] Multi-language support

## Contributing

This is a private project for Essen sales consultants. For questions or issues, contact the development team.

## License

Proprietary - Essen Argentina

---

**Built with ❤️ for Essen entrepreneurs**
