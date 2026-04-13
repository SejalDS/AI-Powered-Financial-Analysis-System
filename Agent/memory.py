from langchain.memory import ConversationBufferWindowMemory

class SmartMemory(ConversationBufferWindowMemory):
    def save_context(self, inputs, outputs):
        # Truncate long outputs to prevent context overflow
        if "output" in outputs and len(outputs["output"]) > 500:
            outputs = {"output": outputs["output"][:500] + "... [data truncated]"}
        super().save_context(inputs, outputs)

def load_user_memory(user_id: str):
    memory = SmartMemory(
        memory_key="chat_history",
        k=3
    )
    return memory, None


def get_portfolio_from_memory(user_id: str) -> dict:
    return {}


def save_user_memory(user_id: str, input_text: str, output_text: str, portfolio_data: dict = None):
    pass