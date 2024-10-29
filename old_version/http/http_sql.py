from langchain_community.chat_models import ChatZhipuAI
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage,BaseMessage
from langchain_core.callbacks.manager import CallbackManager
from langchain_core.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_core.pydantic_v1 import BaseModel,Field
from langchain_core.runnables import (
    RunnableLambda,
    ConfigurableFieldSpec,
    RunnablePassthrough,
)
from operator import itemgetter
from typing import List
import os

os.environ["ZHIPUAI_API_KEY"] = "b5909780de2a33646ef57115b2a79c35.eglWqW3zhHIf2rGh"
llm = ChatZhipuAI(
    model="glm-4",
    temperature=0.7,
    max_tokens=4000,
    streaming=True,
    callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]),
)

class InMemoryHistory(BaseChatMessageHistory, BaseModel):
    """In memory implementation of chat message history."""

    messages: List[BaseMessage] = Field(default_factory=list)

    def add_messages(self, messages: List[BaseMessage]) -> None:
        """Add a list of messages to the store"""
        self.messages.extend(messages)

    def clear(self) -> None:
        self.messages = []

# Here we use a global variable to store the chat message history.
# This will make it easier to inspect it to see the underlying results.
store = {}

def get_by_session_id(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryHistory()
    return store[session_id]


question="""我会向你提供一批http连接的记录，其中包括时间戳，源IP，目标IP与请求uri，请你阅读并完成以下任务：
1.Sql注入攻击的uri中会出现请求参数中包含SQL语法元素的现象，如SELECT、UNION、INSERT、DROP等，这些通常不应出现在用户输入中，请你思考一下还有哪些语法元素可能会出现。
2.Sql注入攻击的uri中会出现逻辑运算符与恒等式，使用如OR '1'='1'这样的逻辑运算符尝试改变查询逻辑，因为'1'='1'的结果为真，而任意一个逻辑结果在与'真'进行OR操作之后，会恒得到真，从而使得Sql数据库认为用户访问的权限为真。
3.Sql注入攻击的URI会同时满足以上两个特点，请根据以上两个特点分析上述记录，找到其中的Sql注入攻击，并输出与攻击对应的时间戳、源IP、目标IP的信息，注意按照记录序号顺序进行，并且不要遗漏。请按照顺序分析每一条记录，并给出理由，无论是否可能包含Sql注入攻击。
"""

def read_and_interact(filename,batch):

    # 打开文件
    with open(filename, 'r') as file:
        lines_buffer = []
        line_count = 0

        # 逐行读取文件
        with open(filename, 'r', encoding='utf-8') as file:
            for line in file:
                lines_buffer.append(line.strip())
                line_count += 1
                print("****")
                # 每15行或文件结束时触发聊天
                if (line_count) % batch == 0 or line.strip() == "":
                    webstream = '\n'.join(lines_buffer)
                    # 调用聊天机器人处理这部分数据
                    response = chain_with_history.invoke(
                        {"question": question+" "+webstream},
                        config={"configurable": {"session_id": "http_sql"}}
                    )
                    #print(store)

                    # 清空缓存，准备下一批数据
                    lines_buffer = []
        # 如果文件最后不足15行也需要处理
        if lines_buffer:
            webstream = '\n'.join(lines_buffer)
            response = chain_with_history.invoke(
                {"question": question + " " + webstream},
                config={"configurable": {"session_id": "http_sql"}}
            )
            # print(store)
            lines_buffer = []

            #print(store)


prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一位水平高超的的网络流量分析专家，现在请你协助我进行Sql注入攻击的恶意流量识别。"),
    MessagesPlaceholder(variable_name='history'),
    ("user", "{question}")
])

output_parser = StrOutputParser()

chain = prompt | llm | output_parser

chain_with_history = RunnableWithMessageHistory(
    chain,
    # Uses the get_by_session_id function defined in the example
    # above.
    get_by_session_id,
    input_messages_key="question",
    history_messages_key="history",
)

file="http_sql.txt"
batch=15
read_and_interact(file,batch)