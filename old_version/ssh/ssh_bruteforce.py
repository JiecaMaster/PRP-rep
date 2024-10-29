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
from langchain_community.chat_models import QianfanChatEndpoint
from langchain_core.language_models.chat_models import HumanMessage
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
file_path = 'ssh_bruteforce.txt'
webstream_data = read_and_group_ftp_lines(file_path)
 
os.environ["QIANFAN_AK"] = "Your_api_key"
os.environ["QIANFAN_SK"] = "You_secret_Key"
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
    ("system", "你是一名擅长使用python代码进行统计的分析助手，你会严格根据输入数据，并且可以直接运行python代码帮助人类进行统计工作，你的工作不是编写python代码，而是直接给出统计结果。"),
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
            {"question": "我将向你提供一份ssh连接的记录，其中包含源IP，目标IP与登录情况3个字段的信息。对于每条记录，请你进行以下操作：1.判断登录情况字段是否为“F”，这表示此次的登录尝试失败。如果不包含，则这条记录无需被统计；如果包含，则进行接下来的操作。2.检查这条连接的源IP与目标IP对是否曾经出现过：如果这对IP没有出现过，则在统计结果中添加这对IP，并将这对IP的计数增加到1；如果已经出现过了，则在统计结果中直接将这对IP的计数加1。注意按照记录序号由小到大进行统计，不要重复统计，也不要遗漏。ssh连接记录如下：" + data},
            config={"configurable": {"session_id": "ssh_bruteforce"}}
        ))
        first = False
    else:
        # 对于其他webstream的处理
        print(chain_with_history.invoke(
            {"question": "在前面结果的基础上，额外统计以下记录，注意按照记录序号由小到大进行统计，不要重复统计，也不要遗漏：" + data},
            config={"configurable": {"session_id": "ssh_bruteforce"}}
        ))

print(chain_with_history.invoke(
    {"question":"请根据统计的结果，将所有计数超过20的IP对输出.如果没有计数超过30或根本没有计数存在，则输出：ssh连接未受到暴力破解攻击。"},
    config={"configurable":{"session_id":"ssh_bruteforce"}}
))