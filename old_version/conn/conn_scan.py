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

print(store)  # noqa: T201

question="""我需要你关注上述日志信息中的内容，并根据特征判断其中是否包含端口扫描攻击。以下为端口扫描攻击的一些显著特征
            一般情况下扫描的绝大多数端口为未开放状态。
            当扫描到未开放端口时（绝大多数情况），流量信息会有以下特征：
            服务类型 (service)字段为空：端口扫描攻击通常不涉及实际的服务请求，因此不会填写具体的服务类型。
            持续时间 (duration)小于0.1毫秒(0.0001000)：端口扫描通常是非常快速的，只需极短的时间尝试连接目标端口并收集响应信息。
            源发送字节数 (orig_bytes)，目标发送字节数 (resp_bytes)与丢失字节数 (missed_bytes)都为0：端口扫描攻击通常不会发送实际数据，因此这些字段通常会是零。
            连接状态 (conn_state)大多数情况为为REJ或RSTO而且历史 (history)字段大多数情况为Sr或ShR：REJ 表示连接被拒绝，RSTO 表示连接被重置，这些状态表明目标主机对连接尝试做出了明确的反应；端口扫描攻击会尝试连接大量端口，大部分端口由于未开放或有防火墙等阻止机制，会导致这些状态。Sr 表示发送请求，这在端口扫描中是典型的历史记录。攻击者发送连接请求来探测端口的状态，例如是否开放或由防火墙保护。
            同时满足以上四个特点的流量可以被判定为端口扫描攻击。
            但请注意：扫描到少量开放端口时，流量信息可能不遵循以上特征。届时请根据是否与之前的攻击ip地址相同，来确定是否为端口扫描。也就是说：你还要关注流量的源IP，如果一条流量不符合以上特征但是与近期的一条被确定为端口扫描攻击的流量的源ip地址相同，那么这条流量大概率也是端口扫描。请将这样的流量定性为疑似端口扫描。
            请根据以上特点分析下列记录，找到其中的端口扫描攻击，并输出与攻击对应的时间戳、源IP、目标IP，请求端口的信息，注意按照记录序号顺序进行，并且不要遗漏。请按照顺序分析每一条记录，并给出理由，无论是否可能包含攻击。
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
                        config={"configurable": {"session_id": "conn_scan"}}
                    )
                    #print(store)

                    # 清空缓存，准备下一批数据
                    lines_buffer = []
        # 如果文件最后不足15行也需要处理
        if lines_buffer:
            webstream = '\n'.join(lines_buffer)
            response = chain_with_history.invoke(
                {"question": question + " " + webstream},
                config={"configurable": {"session_id": "conn_scan"}}
            )
            # print(store)
            lines_buffer = []

            #print(store)


prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一位水平高超的的网络流量分析专家，现在请你协助我进行恶意流量的识别以及种类判定。"),
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

file="conn_scan.txt"
batch=15
read_and_interact(file,batch)