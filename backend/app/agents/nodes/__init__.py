from app.services.llm_service import llm_service
from .architect import ArchitectNode
from .coder import CoderNode
from .reviewer import ReviewerNode
from .router import RouterNode
from .chat import ChatNode

# Instantiate nodes and inject dependencies
architect_node = ArchitectNode(llm_service)
coder_node = CoderNode(llm_service)
reviewer_node = ReviewerNode(llm_service)
router_node = RouterNode(llm_service)
chat_node = ChatNode(llm_service)