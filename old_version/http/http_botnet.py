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


question="""我将提供一份zeek日志信息，我需要你关注日志信息中的内容，并根据特征判断其中是否包含botnet攻击。以下为botnet攻击的一些显著特征：
事务深度（trans_depth）的值通常为1：被感染主机往往与攻击者主机直接通信。
User-Agent字段含有"python"：botnet的被感染主机往往通过python自动化脚本向攻击者发送信息，因此请求头User-Agent字段往往含有"python"。
感染主机会定期向攻击者主机发送请求。也就是botnet控制通信中，流量的流向一般是从受害者主机发向攻击者主机的。这些请求的URI的前缀通常是相同的，通信内容有以下几种：
1.
	1）URI字段中，带有"botid=[主机唯一标识符]&sysinfo=[操作系统信息]"这样的字段：主机周期性地向控制服务器（攻击者）发送这种请求，以获取关于自身的信息或指令。
	2）http方法字段 (method)通常为GET。
2.
	1）URI字段中，带有"upload"或"report"这样的字段，且前缀与上面的信息获取请求相同：受害者主机上传数据，文件或活动的报告到控制服务器（攻击者）。
	2）http方法字段 (method)通常为POST。
同时满足以上特点的流量可以被判定为botnet通信。
请根据以上特点分析下列记录，找到其中的botnet通信，并输出与攻击对应的时间戳、源IP、目标IP的信息，注意按照记录序号顺序进行，并且不要遗漏。请按照顺序分析每一条记录，并给出理由，无论是否可能包含攻击。
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
                        config={"configurable": {"session_id": "http_botnet"}}
                    )
                    #print(store)

                    # 清空缓存，准备下一批数据
                    lines_buffer = []
        # 如果文件最后不足15行也需要处理
        if lines_buffer:
            webstream = '\n'.join(lines_buffer)
            response = chain_with_history.invoke(
                {"question": question + " " + webstream},
                config={"configurable": {"session_id": "http_botnet"}}
            )
            # print(store)
            lines_buffer = []

            #print(store)


prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一位水平高超的的网络流量分析专家，现在请你协助我进行僵尸网络恶意流量的识别。"),
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

file="http_botnet.txt"
batch=15
read_and_interact(file,batch)