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
file_path = 'notice.txt'
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

print(store)  # noqa: T201

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一名擅长阅读分析zeek日志的网络流量专家"),
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

print(chain_with_history.invoke(
    {"question": "我将向你提供一份由zeek处理得到的notice.log部分的记录，请你阅读记录中的警报内容，输出其中异常与攻击的信息："},
    config={"configurable": {"session_id": "notice"}}
))


first = True
for webstream, data in webstream_data.items():
    if first:
        # 对于webstream1的特殊处理
        print(chain_with_history.invoke(
            {"question": "notice记录如下：" + data},
            config={"configurable": {"session_id": "notice"}}
        ))
        first = False
    else:
        # 对于其他webstream的处理
        print(chain_with_history.invoke(
            {"question": "请额外阅读以下记录，并输出其中异常与攻击的信息：" + data},
            config={"configurable": {"session_id": "notice"}}
        ))
