import { ChatBubbleLeftEllipsisIcon } from "@heroicons/react/24/outline";

export default function ChatHistory({ chats, startNewChat, loadChat, activeChat }) {
  return (
    <div className="w-64 bg-gray-900 text-white p-4 flex flex-col">
      <h2 className="text-lg font-semibold mb-4 flex items-center">
        <ChatBubbleLeftEllipsisIcon className="w-5 h-5 mr-2" /> Chat History
      </h2>
      <button onClick={startNewChat} className="w-full bg-green-500 py-2 rounded mb-4 hover:bg-green-600">
        + New Chat
      </button>
      <div className="flex-grow overflow-y-auto">
        {chats.map((chat) => (
          <div
            key={chat.id}
            className={`p-2 mb-2 cursor-pointer rounded ${activeChat?.id === chat.id ? "bg-green-700" : "bg-gray-800"} hover:bg-gray-700`}
            onClick={() => loadChat(chat)}
          >
            {chat.title}
          </div>
        ))}
      </div>
    </div>
  );
}
