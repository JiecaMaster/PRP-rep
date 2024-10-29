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

def read_and_group_ftp_lines(file_path, lines_per_group=20):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    # 按20行分组
    groups = [lines[i:i+lines_per_group] for i in range(0, len(lines), lines_per_group)]
    # 创建变量字典，存储每组数据
    variables = {}
    for index, group in enumerate(groups):
        variable_name = f'webstream{index + 1}'
        # 格式化存储方式
        formatted_group = ''.join([line for line in group])
        variables[variable_name] = formatted_group.strip()  # 去除最后一个换行符
    return variables

# 假设FTP文件位于同一目录下
file_path = 'conn_dos.txt'
webstream_data = read_and_group_ftp_lines(file_path)
 
os.environ["ZHIPUAI_API_KEY"] = "b5909780de2a33646ef57115b2a79c35.eglWqW3zhHIf2rGh"
llm = ChatZhipuAI(
    model="glm-4",
    temperature=0.73,
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

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一位水平高超的的网络流量分析专家，请你协助人类进行拒绝服务攻击的恶意流量识别。"),
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

first = True
for webstream, data in webstream_data.items():
    if first:
        # 对于webstream1的特殊处理
        print(chain_with_history.invoke(
            {"question": """我将提供一份zeek日志信息，我需要你关注日志信息中的内容，并根据特征判断其中是否包含dos攻击。以下为dos攻击的一些显著特征：
            连接状态 (conn_state)为RSTO：RSTO表示连接的状态为"reset observed"（观察到重置）。在DDoS攻击中，攻击者经常发送大量的恶意请求，而目标服务器会对其进行响应并尝试重置这些连接。因此，大量的RSTO状态可能表明目标服务器正在处理DoS攻击，并尝试通过重置连接来减轻攻击压力。
            历史记录 (history)字段通常以R结束：表明了攻击的各个阶段和连接状态，包括连接建立、数据传输、应用层数据和重置连接等；
            异常高的流量频率；
            同时满足以上特点的流量可以被判定为dos攻击。
            请根据以上特点分析记录，找到其中的dos攻击，并输出与攻击对应的时间戳、源IP、目标IP的信息，注意按照记录序号顺序进行，并且不要遗漏。请按照顺序分析每一条记录，并给出理由，无论是否可能包含攻击。
            连接记录如下：""" + data},
            config={"configurable": {"session_id": "conn_dos"}}
        ))
        first = False
    else:
        # 对于其他webstream的处理
        print(chain_with_history.invoke(
            {"question": "在前面结果的基础上，额外统计以下记录，注意按照记录序号由小到大进行分析，不要重复，也不要遗漏：" + data},
            config={"configurable": {"session_id": "conn_dos"}}
        ))
