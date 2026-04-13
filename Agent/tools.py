from langchain.agents import Tool
from FinancialGoals.RAGToSQL.FabricsRAG import ask_fabric
import json
from datetime import datetime
from .memory import save_user_memory
from .memory import get_portfolio_from_memory


def query_database(user_input: str) -> str:
    """Routes any data question to the Fabric database via Vanna AI."""
    try:
        if user_input.startswith('{'):
            try:
                parsed = json.loads(user_input)
                user_input = parsed.get("question", parsed.get("query", parsed.get("input", user_input)))
            except:
                pass
        
        result = ask_fabric(user_input)
        
        return json.dumps({
            "status": "success",
            "data": result
        })
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Database query failed: {str(e)}"
        })


def calculate_investment_plan(user_input: str) -> str:
    try:
        try:
            current_data = json.loads(user_input)
            client_id = current_data.get("client_id", "default_user")
        except json.JSONDecodeError:
            current_data = {"goal_data": {"type": user_input}}
            client_id = "default_user"

        portfolio_data = get_portfolio_from_memory(client_id)

        combined_data = {
            "portfolio_data": portfolio_data.get("portfolio_data", {}),
            "goal_data": current_data.get("goal_data", {})
        }

        stocks = combined_data["portfolio_data"].get("stocks", "No stock data")
        goal = combined_data["goal_data"].get("type", "No goal specified")

        return json.dumps({
            "status": "success",
            "plan": {
                "stocks": stocks,
                "goal": goal,
                "recommended_investment": "$10,000/year"
            }
        })

    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Error calculating plan: {str(e)}",
            "plan": None
        })


def ask_initial_question(user_input: str) -> str:
    return "What are you looking for in terms of financial analysis or investment advice?"


def get_stock_positioning(user_input: str) -> str:
    try:
        client_id = user_input

        if user_input == "None":
            return json.dumps({
                "status": "error",
                "message": "Please provide your client ID.",
                "portfolio_data": None
            })

        # Use ask_fabric to get real data
        client_data = ask_fabric(
            f"Fetch all details for the client id {client_id} including their portfolios and assets"
        )

        portfolio_data = {
            "status": "success",
            "portfolio_data": {
                "stocks": client_data,
                "last_updated": datetime.now().isoformat()
            }
        }

        save_user_memory(
            client_id,
            f"Fetching portfolio data for client {client_id}",
            "Portfolio data retrieved successfully",
            portfolio_data
        )

        return json.dumps(portfolio_data)

    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Error: {str(e)}",
            "portfolio_data": None
        })


def ask_financial_goal(user_input: str) -> str:
    try:
        existing_data = json.loads(user_input) if user_input else {}
        return json.dumps({
            "status": "success",
            "message": "What are your specific financial goals?",
            "previous_data": existing_data
        })
    except:
        return "What are your specific financial goals? Please include target amount and timeline."


def calculate_risk(user_input: str) -> str:
    return "Based on your portfolio, we calculate a risk score of 7/10 with moderate diversification metrics."


def suggest_risk_plan(user_input: str) -> str:
    return "To mitigate risks, we suggest diversifying further into bonds and international equities."


def suggest_investment_plan(user_input: str) -> str:
    return "Here's a suggested investment plan tailored to your goal. Let us know if it meets your expectations."


def handle_feedback(user_input: str) -> str:
    if "alternative" in user_input.lower():
        return "Here's an alternative plan: 40% stocks, 40% bonds, and 20% savings for a more conservative approach."
    return "Great! Let us know if you have any further questions or concerns."


def get_tools():
    return [
        Tool(
            name="Query Database",
            func=query_database,
            description=(
                "Use this tool to query the wealth management database for ANY data question. "
                "This includes questions about clients, portfolios, assets, transactions, advisors, "
                "portfolio values, asset allocations, wealth summaries, comparisons, rankings, "
                "totals, averages, and any other data-related question. "
                "Always use this tool instead of making up data. "
                "Input should be a natural language question about the data."
            )
        ),
        Tool(
            name="Get Stock Positioning",
            func=get_stock_positioning,
            description=(
                "Retrieves a specific client's portfolio data by their client ID number. "
                "Use when the user says 'I am client X' or asks about a specific client's portfolio."
            )
        ),
        Tool(
            name="Ask Financial Goal",
            func=ask_financial_goal,
            description="Queries the user about their financial goals, such as savings or retirement plans."
        ),
        Tool(
            name="Calculate Risk",
            func=calculate_risk,
            description="Analyzes the user's stock portfolio to calculate associated risks."
        ),
        Tool(
            name="Suggest Risk Plan",
            func=suggest_risk_plan,
            description="Provides a risk mitigation plan based on the calculated risks in the user's portfolio."
        ),
        Tool(
            name="Calculate Investment Plan",
            func=calculate_investment_plan,
            description="Creates a tailored investment plan based on user input and extracted portfolio data."
        ),
        Tool(
            name="Suggest Investment Plan",
            func=suggest_investment_plan,
            description="Recommends an investment plan aligned with the user's financial goals."
        ),
        Tool(
            name="Handle Feedback",
            func=handle_feedback,
            description="Processes user feedback and provides alternative plans or suggestions."
        ),
    ]